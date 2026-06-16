"""Cross-platform TTS notification hook for Claude Code.

Reads hook event JSON from stdin and speaks a context-aware Chinese phrase.

Two engines, tried in order:
  1. edge-tts (optional): neural voice, generates an MP3 (cached), played via a
     platform-native player. Used when the `edge_tts` package is importable and
     generation + playback succeed.
  2. System TTS (fallback, zero-install): Windows SAPI / macOS `say` /
     Linux espeak-ng|spd-say. Synthesized live, not cached.

No ffmpeg dependency. Works on Windows, macOS and Linux.
"""

import sys
import json
import hashlib
import os
import re
import asyncio
import subprocess
import time

# --- Platform ---
if sys.platform.startswith("win"):
    PLATFORM = "win"
elif sys.platform == "darwin":
    PLATFORM = "mac"
else:
    PLATFORM = "linux"

# --- Config ---
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".claude", "cache", "tts-notify")
CACHE_MAX = 50
TTS_TIMEOUT = 2.5
VOICE = "zh-CN-XiaoxiaoNeural"

# Preferred Chinese voice for macOS system TTS fallback (`say -v`).
MAC_VOICE = "Tingting"

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


def read_last_assistant_message(transcript_path: str) -> str:
    """Extract the last assistant text from the session JSONL transcript."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return ""
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            # {"type": "assistant", "message": {"content": [{"type": "text", "text": "..."}]}}
            if obj.get("type") == "assistant":
                content = obj.get("message", {}).get("content", [])
                if isinstance(content, list):
                    texts = [c["text"] for c in content
                             if isinstance(c, dict) and c.get("type") == "text" and c.get("text")]
                    if texts:
                        return "\n".join(texts)
                elif isinstance(content, str) and content:
                    return content
            # {"role": "assistant", "content": ...}
            elif obj.get("role") == "assistant":
                content = obj.get("content", "")
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    texts = [c["text"] for c in content
                             if isinstance(c, dict) and c.get("type") == "text" and c.get("text")]
                    return "\n".join(texts)
    except Exception:
        pass
    return ""


def get_text_for_event(data: dict) -> str:
    event = data.get("hook_event_name", "")

    if event in ("Stop", "SubagentStop"):
        msg = read_last_assistant_message(data.get("transcript_path", ""))
        return extract_stop_text(msg)

    return FIXED_TEXTS.get(event, "处理完成了")


def cache_path_for(text: str) -> str:
    h = hashlib.md5(text.encode("utf-8", errors="replace")).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.mp3")


def enforce_cache_limit():
    """LRU eviction: keep at most CACHE_MAX files."""
    try:
        files = []
        for f in os.listdir(CACHE_DIR):
            if f.endswith(".mp3") or f.endswith(".wav"):
                fp = os.path.join(CACHE_DIR, f)
                files.append((os.stat(fp).st_atime, fp))
        if len(files) <= CACHE_MAX:
            return
        files.sort()  # oldest access first
        for _, fp in files[: len(files) - CACHE_MAX]:
            os.remove(fp)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Engine 1: edge-tts (optional neural voice)
# ---------------------------------------------------------------------------

def edgetts_available() -> bool:
    try:
        import edge_tts  # noqa: F401
        return True
    except Exception:
        return False


async def _edgetts_save(text: str, mp3_path: str) -> bool:
    import edge_tts
    try:
        comm = edge_tts.Communicate(text, VOICE)
        await asyncio.wait_for(comm.save(mp3_path), timeout=TTS_TIMEOUT)
        return os.path.isfile(mp3_path) and os.path.getsize(mp3_path) > 0
    except Exception:
        return False


def synth_edgetts(text: str, mp3_path: str) -> bool:
    """Generate an MP3 via edge-tts. Returns True on success."""
    tmp = mp3_path + ".tmp"
    try:
        ok = asyncio.run(_edgetts_save(text, tmp))
    except Exception:
        ok = False
    if ok:
        try:
            os.replace(tmp, mp3_path)
            return True
        except OSError:
            pass
    if os.path.exists(tmp):
        try:
            os.remove(tmp)
        except OSError:
            pass
    return False


# ---------------------------------------------------------------------------
# MP3 playback (platform-native, no ffmpeg)
# ---------------------------------------------------------------------------

# PowerShell snippet: play an MP3 via WPF MediaPlayer (ships with .NET on
# Windows), blocking until playback finishes. No external binary needed.
_WIN_PLAY_PS = (
    "Add-Type -AssemblyName PresentationCore;"
    "$p = New-Object System.Windows.Media.MediaPlayer;"
    "$p.Open([uri]$env:TTS_MP3_URI);"
    "$n = 0;"
    "while (-not $p.NaturalDuration.HasTimeSpan -and $n -lt 60) "
    "{ Start-Sleep -Milliseconds 50; $n++ };"
    "$ms = if ($p.NaturalDuration.HasTimeSpan) "
    "{ $p.NaturalDuration.TimeSpan.TotalMilliseconds } else { 4000 };"
    "$p.Play();"
    "Start-Sleep -Milliseconds ([int]$ms + 300);"
    "$p.Stop(); $p.Close()"
)


def _which(name: str) -> bool:
    from shutil import which
    return which(name) is not None


def play_mp3(path: str) -> bool:
    """Play an MP3 using a platform-native player. Returns True on success."""
    if not os.path.isfile(path):
        return False
    try:
        if PLATFORM == "win":
            uri = "file:///" + os.path.abspath(path).replace("\\", "/")
            env = dict(os.environ, TTS_MP3_URI=uri)
            r = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Sta",
                 "-Command", _WIN_PLAY_PS],
                capture_output=True, timeout=15, env=env,
            )
            return r.returncode == 0
        if PLATFORM == "mac":
            r = subprocess.run(["afplay", path], capture_output=True, timeout=15)
            return r.returncode == 0
        # linux: try common players in order
        for player in ("mpg123", "ffplay", "cvlc", "mpv"):
            if not _which(player):
                continue
            if player == "mpg123":
                cmd = ["mpg123", "-q", path]
            elif player == "ffplay":
                cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path]
            elif player == "cvlc":
                cmd = ["cvlc", "--play-and-exit", "--intf", "dummy", path]
            else:  # mpv
                cmd = ["mpv", "--no-video", "--really-quiet", path]
            r = subprocess.run(cmd, capture_output=True, timeout=15)
            return r.returncode == 0
        return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Engine 2: system TTS (fallback, zero-install, live synthesis)
# ---------------------------------------------------------------------------

# PowerShell SAPI: pick a Chinese voice if available, then speak (blocking).
_WIN_SPEAK_PS = (
    "Add-Type -AssemblyName System.Speech;"
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
    "$zh = $s.GetInstalledVoices() | "
    "Where-Object { $_.VoiceInfo.Culture.Name -like 'zh*' };"
    "if ($zh) { $s.SelectVoice($zh[0].VoiceInfo.Name) };"
    "$s.Speak($env:TTS_TEXT); $s.Dispose()"
)


def _voice_exists_mac(voice: str) -> bool:
    try:
        r = subprocess.run(["say", "-v", "?"], capture_output=True, timeout=5, text=True)
        return voice.lower() in (r.stdout or "").lower()
    except Exception:
        return False


def speak_system(text: str) -> bool:
    """Speak text via the OS built-in TTS. Returns True on success."""
    try:
        if PLATFORM == "win":
            env = dict(os.environ, TTS_TEXT=text)
            r = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive",
                 "-Command", _WIN_SPEAK_PS],
                capture_output=True, timeout=15, env=env,
            )
            return r.returncode == 0
        if PLATFORM == "mac":
            cmd = ["say", "-v", MAC_VOICE, text] if _voice_exists_mac(MAC_VOICE) else ["say", text]
            r = subprocess.run(cmd, capture_output=True, timeout=15)
            return r.returncode == 0
        # linux
        if _which("spd-say"):
            r = subprocess.run(
                ["spd-say", "-w", "-l", "zh", text], capture_output=True, timeout=15
            )
            if r.returncode == 0:
                return True
        if _which("espeak-ng"):
            r = subprocess.run(
                ["espeak-ng", "-v", "zh", text], capture_output=True, timeout=15
            )
            return r.returncode == 0
        if _which("espeak"):
            r = subprocess.run(
                ["espeak", "-v", "zh", text], capture_output=True, timeout=15
            )
            return r.returncode == 0
        return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def notify(text: str):
    """Speak `text`: prefer edge-tts (cached MP3), fall back to system TTS."""
    if edgetts_available():
        os.makedirs(CACHE_DIR, exist_ok=True)
        mp3 = cache_path_for(text)
        if os.path.isfile(mp3):
            try:
                os.utime(mp3, (time.time(), os.stat(mp3).st_mtime))
            except OSError:
                pass
            if play_mp3(mp3):
                return
        else:
            if synth_edgetts(text, mp3):
                enforce_cache_limit()
                if play_mp3(mp3):
                    return
    # Fallback: system TTS
    speak_system(text)


def prewarm():
    """Pre-generate edge-tts MP3 for all fixed phrases."""
    if not edgetts_available():
        print("edge-tts not installed; nothing to prewarm (system TTS is live).")
        return
    os.makedirs(CACHE_DIR, exist_ok=True)
    texts = list(FIXED_TEXTS.values()) + [DEFAULT_PREFIX.rstrip("，")]
    for text in texts:
        mp3 = cache_path_for(text)
        if os.path.isfile(mp3):
            print(f"[cached] {text}")
            continue
        print(f"[generating] {text} ...", end=" ", flush=True)
        ok = synth_edgetts(text, mp3)
        print("OK" if ok else "FAIL")
    enforce_cache_limit()
    print("Prewarm done.")


def main():
    if "--prewarm" in sys.argv:
        prewarm()
        return

    # Read event JSON from stdin
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    text = get_text_for_event(data)
    notify(text)


if __name__ == "__main__":
    main()
