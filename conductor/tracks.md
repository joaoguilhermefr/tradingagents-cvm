# Project Tracks

This file tracks all major tracks (features, enhancements, bug fixes) for the TradingAgents project.

A **track** is a major unit of work that typically spans multiple tasks and may take days or weeks to complete. Each track has:
- A specification document (`spec.md`) — detailed requirements
- A implementation plan (`plan.md`) — step-by-step development tasks
- Acceptance criteria from the spec

---

## Active Tracks

### [ ] Track: Stabilize and Document CVM Market Adapter
*Link: [./conductor/tracks/cvm-adapter/](./conductor/tracks/cvm-adapter/)*

Consolidate recent Brazilian market (CVM) adaptation work, ensure clean integration with core framework, improve configuration handling, and provide comprehensive documentation. Includes code refactoring, comprehensive testing, and user guides.

**Priority:** High | **Effort:** 5-7 days | **Status:** New

---

## Completed Tracks

(Track completion records will appear here)

---

## Reference

For details on a specific track, see the `tracks/` directory:
```
tracks/
├── <track-id>/
│   ├── spec.md          # Track specification
│   ├── plan.md          # Implementation plan
│   ├── metadata.json    # Track metadata
│   └── index.md         # Track index
└── ...
```

**Track Status Values:**
- `new` — Not yet started
- `in_progress` — Currently being worked on
- `completed` — Finished and merged
- `blocked` — Waiting on dependencies
- `paused` — Temporarily on hold
