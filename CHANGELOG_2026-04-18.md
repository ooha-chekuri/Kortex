# Kortex Changelog - April 18, 2026

## Summary
Fixed critical orchestration bugs that caused "Failed to fetch" errors with 0 sources and 0% confidence.

## Bugs Fixed

### 1. Planning Agent Method Outside Class
**File:** `backend/agents/planning_agent.py`
**Issue:** `_parse_response` method was defined outside the class due to wrong indentation
**Fix:** Rewrote method with correct class-level indentation

### 2. Parser Captured Last Action Instead of First
**File:** `backend/agents/planning_agent.py`
**Issue:** Parser used `elif` which overwrote first action with last (LLM outputs 3 actions)
**Fix:** Modified to capture first occurrence using flag variables

### 3. No Contexts / Sources Returned
**File:** `backend/core/orchestrator.py`
**Issue:** LLM skipped retrieval and returned early without executing doc_search
**Fix:** Added fallback to force `doc_search` when contexts empty + check requiring contexts before accepting answer

### 4. Confidence Showing 0.0
**File:** `backend/core/orchestrator.py`
**Issue:** Validation not run when planner returns early with final_answer
**Fix:** Added automatic validation after synthesis + validation when planner returns early

### 5. Generic Placeholder Answers
**File:** `backend/agents/synthesis_agent.py`, `backend/core/orchestrator.py`
**Issue:** LLM outputs "list of items" instead of extracting ticket details
**Fix:** 
- Improved synthesis prompts for ticket detail extraction
- Added fallback trigger for generic placeholder phrases
- Blocked placeholder answers in orchestrator

## Other Improvements
- Added `SystemLogs.jsx` component for live XAI debugging
- Better ticket context formatting for synthesis agent
- Improved RAG flow to properly return sources

## Test Results

| Query | Before | After |
|-------|--------|-------|
| Kafka consumer lag | 0 sources, 0.0 confidence | 5 sources, 0.26+ confidence |
| Kubernetes CrashLoopBackOff | 0 sources, escalated | 5 sources, 0.26+ confidence |
| SSO login loops | 0 sources, escalated | 3 tickets, 0.40 confidence |

## Files Changed
- `backend/agents/planning_agent.py`
- `backend/agents/synthesis_agent.py`
- `backend/core/orchestrator.py`
- `backend/main.py`
- `frontend/src/App.jsx`
- `frontend/src/components/SystemLogs.jsx` (new)
- `package.json`

## Commit
`e83b4d3` - fix: resolve orchestration bugs and improve answer quality