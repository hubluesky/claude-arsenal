# Multi-Model Dispatch

When a task is complex enough to benefit from specialized models at different phases, use this dispatch strategy.

**When to use:** Multi-file changes, deep debugging, performance-sensitive workflows where you want to optimize cost vs. quality.

**When NOT to use:** Simple single-file changes, obvious fixes, tasks where the overhead of spawning agents exceeds the benefit.

## Model Assignment

| Phase | Model | Reason |
|-------|-------|--------|
| Phase 0: Collect Ground Truth | **haiku** (via Agent) | Pure file reading and grep, no deep reasoning needed |
| Phase 1: Compare and Clarify | **main model** (no dispatch) | Needs user interaction, subagent can't AskUserQuestion |
| Phase 2: Root Cause Investigation | **opus** (via Agent) | Needs strongest reasoning for root cause analysis |
| Phase 3: Plan and Checklist | **main model** (no dispatch) | Needs user interaction for plan confirmation |
| Phase 4: Execute | **sonnet** (via Agent) | Executing a known plan, doesn't need strongest reasoning |
| Phase 5: Verify Before Done | **haiku** (via Agent) | Pure command running and output checking |

## Dispatch Rules

1. Use `Agent(model: "haiku"/"opus"/"sonnet")` to spawn subagents for delegated phases
2. Main model phases run directly in current context (because they need user interaction)
3. Dispatch prompts must include: full phase instructions, relevant file paths, user's problem description, key findings from prior phases
4. After each dispatch returns, the main model must review the result before proceeding

## Phase 0 Dispatch Template

```
Agent(model: "haiku", description: "Collect ground truth for quick-fix", prompt: """
You are the Phase 0 executor for quick-fix. Task: collect factual evidence for the following problem.

**User problem:** {description}
**Files involved:** {file list}

Steps:
1. Read all involved files, note key code segments (function signatures, call chains, type definitions)
2. Grep to trace call chains (callers and callees)
3. Run relevant commands to get actual error output (if applicable)
4. Confirm that APIs/functions/flags mentioned by user actually exist

Output format:
- **File summaries:** Key code segments and line numbers per file
- **Call chain:** A → B → C complete paths
- **Actual errors:** Command output (if any)
- **API existence:** Confirmed/denied list
""")
```

## Phase 2 Dispatch Template

```
Agent(model: "opus", description: "Root cause analysis", prompt: """
You are the Phase 2 root cause analysis expert.

**User problem:** {description}
**Phase 0 facts:** {Phase 0 subagent results}
**Phase 1 clarifications:** {confirmed conclusions}

Steps:
1. Trace full data flow from source to symptom
2. List all possible hypotheses, eliminate one by one
3. In multi-component systems, check boundary inputs/outputs
4. Find similar working code in the codebase for comparison
5. Identify which layer the root cause belongs to (data source/logic/presentation)

Output format:
- **Root cause:** One sentence summary
- **Evidence chain:** Data flow trace path
- **Eliminated hypotheses:** List with reasons
- **Fix direction:** Which layer to fix and why
""")
```

## Phase 4 Dispatch Template

```
Agent(model: "sonnet", description: "Execute quick-fix plan", prompt: """
You are the Phase 4 executor. Follow the plan strictly, do not expand scope.

**Fix plan:** {confirmed plan from Phase 3}
**Root cause:** {Phase 2 conclusion}
**Files involved:** {file list}

Rules:
1. Re-Read each file before editing
2. Write complete code, no placeholder comments
3. Preserve all existing functionality
4. Keep type definitions in sync
5. Check for duplicate imports
6. Stop and report if you discover new problems

Output format:
- **Modified files:** File path + change summary
- **Added/deleted:** If any
- **Incomplete items:** If any (with reasons)
""")
```

## Phase 5 Dispatch Template

```
Agent(model: "haiku", description: "Verify quick-fix results", prompt: """
You are the Phase 5 verifier. Run ALL verification items and fill the verification table. Do NOT modify any code.

**Modified files:** {Phase 4 file list}
**Project directory:** {working directory}
**Phase 3 change checklist:** {checklist content}

You have 5 verification items. Execute all of them, skip none.

### Item 1: Build
Run the project's build command. Record full output.

### Item 2: Lint / TypeCheck
Run lint or typecheck command. Record full output.

### Item 3: Tests
Run test command (if project has tests). If no tests, write "No tests, skipped". Record full output.

### Item 4: Checklist review
Compare against each Phase 3 checklist item:
- Is it implemented? (Read file to confirm)
- Does implementation match the plan?

### Item 5: Regression check
Check if modifications introduced new errors/warnings.

### Output format (mandatory)

| # | Item | Status | Command | Evidence |
|---|------|--------|---------|----------|
| 1 | Build | PASS/FAIL/SKIP | actual command | key output lines |
| 2 | Lint/TypeCheck | PASS/FAIL/SKIP | actual command | key output lines |
| 3 | Tests | PASS/FAIL/SKIP | actual command | key output lines |
| 4 | Checklist review | PASS/FAIL | per-item Read | confirmation per item |
| 5 | Regression check | PASS/FAIL | comparison | new issues or "none" |

**Conclusion (mandatory):**
- All PASS → "Verification passed"
- Any FAIL → "Verification failed: [list]"
- Any SKIP → Must state reason
""")
```
