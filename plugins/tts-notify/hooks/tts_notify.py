"""Dynamic TTS notification hook for Claude Code.

Reads hook event JSON from stdin, generates context-aware speech via edge-tts,
caches WAV files, and plays them with winsound. Falls back to static WAV on failure.
"""

import sys

if sys.platform != "win32":
    sys.exit(0)

import json
import hashlib
import os
import re
import asyncio
import subprocess
import tempfile
import winsound
import time

# --- Config ---
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".claude", "cache", "tts-notify")
HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_MAX = 50
TTS_TIMEOUT = 2.5
VOICE = "zh-CN-XiaoxiaoNeural"

FALLBACK_WAV = {
    "Stop": os.path.join(HOOKS_DIR, "complete_xiaoxiao_pcm.wav"),
    "Notification": os.path.join(HOOKS_DIR, "notify_xiaoxiao_pcm.wav"),
    "PreToolUse": os.path.join(HOOKS_DIR, "notify_xiaoxiao_pcm.wav"),
    "PermissionRequest": os.path.join(HOOKS_DIR, "permission_xiaoxiao_pcm.wav"),
}

FIXED_TEXTS = {
    "Notification": "需要你来看一下",
    "PreToolUse": "有个问题想问你",
    "PermissionRequest": "请确认一下",
}

STOP_PREFIXES = [
    (r"commit|push|提交", "代码已提交，"),
    (r"error|fail|错误", "执行出错了，"),
    (r"creat|wrote|写入|创建", "文件已创建，"),
    (r"test|测试", "测试跑完了，"),
    (r"fix|修复", "修复完成了，"),
    (r"delet|删除|removed", "已经删掉了，"),
    (r"install|依赖|package|npm|pip", "安装完成了，"),
    (r"refactor|重构", "重构完成了，"),
    (r"deploy|部署|发布", "部署完成了，"),
    (r"review|审查|code.review", "审查完成了，"),
    (r"plan|计划|方案|设计", "方案写好了，"),
    (r"search|搜索|查找|探索", "查完了，"),
    (r"updat|更新|升级", "更新完成了，"),
    (r"config|配置|设置", "配置好了，"),
]
DEFAULT_PREFIX = "处理完成了，"
DESC_MAX_LEN = 50

# Patterns for extracting summary lines from assistant messages
_SUMMARY_PATTERNS = re.compile(
    r"(completed|done|finished|完成|搞定|已经|修好|写好|改好)", re.I
)
_TITLE_PATTERNS = re.compile(
    r"^(?:#{1,3}\s+|task\s*[:：]|任务\s*[:：]|\*\*)", re.I
)


def _strip_markdown(line: str) -> str:
    """Remove markdown formatting from a line."""
    line = re.sub(r'^[#*\->`~\s]+', '', line)
    line = re.sub(r'[*`~]+', '', line)
    return line.strip()


def _is_noise_line(line: str) -> bool:
    """Check if a line is noise (code, paths, tool output, etc.)."""
    stripped = line.strip()
    if not stripped:
        return True
    # File paths
    if re.match(r'^[\w/\\]+(\.[\w]+)+[:/]', stripped):
        return True
    # Pure punctuation or very short
    if len(stripped) <= 2:
        return True
    # Looks like code or data
    if stripped.startswith(('import ', 'from ', 'const ', 'let ', 'var ',
                           '{', '[', '(', '//', '/*', '```')):
        return True
    return False


def extract_stop_text(message: str) -> str:
    if not message:
        return DEFAULT_PREFIX.rstrip("，")

    msg_lower = message.lower()

    # Determine prefix
    prefix = DEFAULT_PREFIX
    for pattern, pfx in STOP_PREFIXES:
        if re.search(pattern, msg_lower):
            prefix = pfx
            break

    # Split into lines, skip code blocks
    lines = message.splitlines()
    clean_lines = []
    in_code_block = False
    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        clean_lines.append(line)

    # Strategy 1: Find a summary sentence (lines with completion keywords)
    for line in clean_lines:
        stripped = _strip_markdown(line)
        if stripped and _SUMMARY_PATTERNS.search(stripped) and not _is_noise_line(line):
            desc = stripped
            if len(desc) > DESC_MAX_LEN:
                desc = desc[:DESC_MAX_LEN] + "..."
            return prefix + desc

    # Strategy 2: Find a title/heading line
    for line in clean_lines:
        if _TITLE_PATTERNS.match(line.strip()):
            stripped = _strip_markdown(line)
            if stripped and not _is_noise_line(line):
                desc = stripped
                if len(desc) > DESC_MAX_LEN:
                    desc = desc[:DESC_MAX_LEN] + "..."
                return prefix + desc

    # Strategy 3: Fallback to first meaningful non-empty line
    for line in clean_lines:
        if _is_noise_line(line):
            continue
        stripped = _strip_markdown(line)
        if stripped:
            desc = stripped
            if len(desc) > DESC_MAX_LEN:
                desc = desc[:DESC_MAX_LEN] + "..."
            return prefix + desc

    return prefix.rstrip("，")


def get_text_for_event(data: dict) -> str:
    event = data.get("hook_event_name", "")

    if event == "Stop":
        msg = data.get("last_assistant_message", "")
        return extract_stop_text(msg)

    return FIXED_TEXTS.get(event, "处理完成了")


def cache_path_for(text: str) -> str:
    h = hashlib.md5(text.encode("utf-8", errors="replace")).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.wav")


def enforce_cache_limit():
    """LRU eviction: keep at most CACHE_MAX files."""
    try:
        files = []
        for f in os.listdir(CACHE_DIR):
            if f.endswith(".wav"):
                fp = os.path.join(CACHE_DIR, f)
                files.append((os.stat(fp).st_atime, fp))
        if len(files) <= CACHE_MAX:
            return
        files.sort()  # oldest access first
        for _, fp in files[: len(files) - CACHE_MAX]:
            os.remove(fp)
    except OSError:
        pass


async def generate_tts(text: str, wav_path: str) -> bool:
    """Generate WAV via edge-tts + ffmpeg. Returns True on success."""
    import edge_tts

    tmp_mp3 = wav_path + ".tmp.mp3"
    try:
        comm = edge_tts.Communicate(text, VOICE)
        await asyncio.wait_for(comm.save(tmp_mp3), timeout=TTS_TIMEOUT)

        # Convert to WAV with ffmpeg
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_mp3, "-ar", "24000", "-ac", "1",
             "-sample_fmt", "s16", wav_path],
            capture_output=True, timeout=3,
        )
        return result.returncode == 0
    except Exception:
        return False
    finally:
        if os.path.exists(tmp_mp3):
            try:
                os.remove(tmp_mp3)
            except OSError:
                pass


def play_wav(path: str):
    if os.path.isfile(path):
        try:
            winsound.PlaySound(path, winsound.SND_FILENAME)
        except Exception:
            pass


def play_fallback(event: str):
    fb = FALLBACK_WAV.get(event, FALLBACK_WAV["Stop"])
    play_wav(fb)


def prewarm():
    """Pre-generate WAV for all fixed phrases."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    texts = list(FIXED_TEXTS.values()) + [DEFAULT_PREFIX.rstrip("，")]
    for text in texts:
        wp = cache_path_for(text)
        if os.path.isfile(wp):
            print(f"[cached] {text}")
            continue
        print(f"[generating] {text} ...", end=" ", flush=True)
        ok = asyncio.run(generate_tts(text, wp))
        print("OK" if ok else "FAIL")
    enforce_cache_limit()
    print("Prewarm done.")


def main():
    if "--prewarm" in sys.argv:
        prewarm()
        return

    os.makedirs(CACHE_DIR, exist_ok=True)

    # Read event JSON from stdin
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    event = data.get("hook_event_name", "Stop")
    text = get_text_for_event(data)
    wp = cache_path_for(text)

    # Cache hit → play directly
    if os.path.isfile(wp):
        # Touch access time for LRU
        try:
            os.utime(wp, (time.time(), os.stat(wp).st_mtime))
        except OSError:
            pass
        play_wav(wp)
        return

    # Cache miss → generate
    ok = asyncio.run(generate_tts(text, wp))
    if ok and os.path.isfile(wp):
        enforce_cache_limit()
        play_wav(wp)
    else:
        play_fallback(event)


if __name__ == "__main__":
    main()
