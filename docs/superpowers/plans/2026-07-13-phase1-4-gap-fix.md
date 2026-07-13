# Phase 1-4 Gap Fix Plan

> **Goal:** Fix all 19 deficiencies and gaps identified in the Phase 1-4 audit.

## Tasks

### Task F1: record_feedback Agent Tool

**Files:**
- Create: `backend/packages/harness/deerflow/tools/influencer/record_feedback.py`

**Deliverable:** Factory function `build_record_feedback_tool()` that creates a LangChain tool for submitting feedback. Registers via existing registry.

### Task F2: Missing API Endpoints (report, compare, feedback/{id})

**Files:**
- Modify: `backend/app/influencer/routers/influencers.py`

**Deliverable:**
- `GET /selections/{id}/report` — returns the latest report for a selection
- `GET /selections/{id}/compare` — returns structured comparison data for candidates
- `GET /feedbacks/{id}` — returns single feedback detail

### Task F3: 6.3 Analytics Endpoints (scores, weights, trends)

**Files:**
- Modify: `backend/app/influencer/routers/influencers.py`

**Deliverable:**
- `GET /scores/{id}` — influencer score details
- `POST /scores/batch` — batch refresh scores
- `GET /analytics/weights` — current weight config
- `GET /analytics/trends` — time-series feedback trends

### Task F4: Skill Definition

**Files:**
- Create: `skills/public/influencer/SKILL.md`

**Deliverable:** DeerFlow skill definition with frontmatter metadata

### Task F5: result_summary Persistence

**Files:**
- Modify: `backend/app/influencer/routers/influencers.py` (analyze endpoint)

**Deliverable:** After analyze, save report summary to `selection.result_summary`

### Task F6: Fix Scoring Threshold + Service Error Types

**Files:**
- Modify: `backend/app/influencer/services/feedback.py`
- Create: `backend/app/influencer/services/errors.py`

**Deliverable:**
- Change `_MIN_CONFIDENCE` from 0.3 to 0.6 per spec
- Define `DataPlatformError`, `MatchingError`, `ScoringError` exception classes

### Task F7: Radar Charts in InfluencerDetail + CompareDrawer

**Files:**
- Create: `frontend/src/components/workspace/influencer/radar-chart.tsx`
- Modify: `frontend/src/components/workspace/influencer/influencer-detail.tsx`
- Modify: `frontend/src/components/workspace/influencer/compare-drawer.tsx`

**Deliverable:** SVG-based 4-dimension radar chart replacing progress bars in both detail and compare drawer

### Task F8: Backend Integration Tests

**Files:**
- Create: `backend/tests/influencer/test_integration.py`

**Deliverable:** End-to-end test: search → create selection → add candidates → analyze → feedback → verify scores

### Task F9: Verify + Commit

Run `pnpm check` + `pytest` → all green → commit and push.
