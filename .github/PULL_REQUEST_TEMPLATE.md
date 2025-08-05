<!--
  🔍  vverb – Pull-Request Checklist
  Copyright 2025 Bibhuti Bhusan Panda
  License: Apache 2.0
  Tick the boxes that apply; placeholders left unchanged may cause the
  “PR-template-lint” workflow to fail.
-->

## 📝 PR Overview

### 🔎 Problem statement (what & why)
<!-- Describe the user impact / bug / feature need -->

### 🛠️ Solution summary (how)
<!-- High-level approach & key files touched -->

### 📊 Before / after evidence
<!-- Screenshots, benchmark numbers, or logs -->

### 🚑 Risk / rollback plan
<!-- Feature flag? DB migration? Simple revert? -->

### 👀 Reviewer guide
<!-- e.g. “Start with `adapters/pgvector/core.py`; the rest is tests.” -->

---

## ✅ Checklist

### 🏗️ CI & Build
- [ ] **All automated checks green** (unit, integration, lint, type-check, security)
- [ ] **Branch up-to-date** with `main` (or target) and conflicts resolved

### 👁️‍🗨️ Self-Review
- [ ] Diff scanned line-by-line  
  - [ ] No debug logs, TODOs, or commented-out code left behind  
  - [ ] Variable / function names convey intent
- [ ] **Scope sanity-check** – each changed file belongs to this PR

### 📝 Code Clarity
- [ ] Inline docs / docstrings added for non-obvious logic
- [ ] Public APIs have clear parameter & return docs
- [ ] Error handling and edge-cases considered

### 🧪 Tests
- [ ] New tests for any new control-flow branches
- [ ] Regression tests for bug fixes
- [ ] *What’s NOT covered & why*: `<!-- intentionally omitted … because … -->`

<!-- Optional, advanced items – feel free to ignore if the PR is trivial -->
<!--
### 📚 Project Docs
- [ ] Architecture / design docs updated
- [ ] README / ADR captures new flags, env vars, run-books, diagrams

### 🔄 Follow-ups
- [ ] Tech-debt tickets created for anything pushed out of scope
- [ ] Changelog entry drafted (if repo uses one)
-->