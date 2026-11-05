# Rohini Avionics Mock Mission Test Plan

**Document:** `ROH-AVI-MTP-001`  
**File:** [ROH-AVI-MTP-001_Rohini_Avionics_Mock_Mission_Test_Plan_v1.docx](./ROH-AVI-MTP-001_Rohini_Avionics_Mock_Mission_Test_Plan_v1.docx)  
**Revision:** A (execution-ready structure; numeric ICD/SRR limits marked TBD)

## What this is

A flight-critical **avionics-side mock mission / FlatSat / HITL dress rehearsal plan** for Rohini. It is written to be executed like a real countdown rehearsal — not a casual bench checklist.

Each test case includes:

- Why the test exists  
- Why it is mission-critical  
- Prerequisites / entry criteria  
- Configuration  
- Step procedure  
- Pass/fail rubrics with evidence requirements  
- Abort / hold criteria  
- Sign-off line  

## Governing source documents (program-provided)

| Ref | Document |
|---|---|
| AD-01 | `GS_SRR_ROH_v1` — Ground Station SRR |
| AD-02 | `Rohini_Avionics_Mission_Level_SRR_DraftA` |
| AD-03 | `ReX-3 Electrical Interface Control Document v1` |
| AD-04 | `Rohini_Payload_Design_Document` |
| AD-05 | `ROHINI MISSION.drawio` |

> **Rev B note:** Local Mac paths were not transferable into this cloud workspace. Values marked `[ICD-TBD]` / `[SRR-TBD]` must be filled from the files above. Attach/upload them and regenerate for a numbers-complete Rev B.

## Campaign blocks

| Block | Tests | Exit before continuing |
|---|---|---|
| A — Readiness / power integrity | TC-01…TC-03 | No electrical non-compliance |
| B — Boot / sensors / buses | TC-04…TC-06 | Stable PAD + valid sensors |
| C — GS closed-loop | TC-07…TC-08 | Cmd ACK + archive hash OK |
| D — Payload | TC-09 | Payload rubrics PASS |
| E — Timeline / TPS / EDL (inhibited) | TC-10…TC-12 | Event table matches |
| F — FDIR / stress | TC-13…TC-15 | SAFE containment proven |
| G — Dress rehearsal + closeout | TC-16…TC-17 | FULL or CONDITIONAL SUCCESS |

## Test case index

| ID | Title | Criticality |
|---|---|---|
| TC-01 | As-built configuration audit & inhibit proof | CRITICAL |
| TC-02 | Harness continuity, isolation, EICD pin audit | CRITICAL |
| TC-03 | Power application, inrush, sequencing, budget | CRITICAL |
| TC-04 | OBC boot determinism, BIT, time sync | CRITICAL |
| TC-05 | Sensor suite validity & state estimation health | CRITICAL |
| TC-06 | Internal bus / peripheral stress | MAJOR |
| TC-07 | Ground Station telemetry closed-loop | CRITICAL |
| TC-08 | Command uplink, validation, reject paths | CRITICAL |
| TC-09 | Payload power / data / mission data products | CRITICAL/MAJOR |
| TC-10 | Mission mode machine rehearsal (inhibited) | CRITICAL |
| TC-11 | TPS / heat-shield deploy logic (inhibited) | CRITICAL |
| TC-12 | EDL / parachute recovery logic (inhibited) | CRITICAL |
| TC-13 | FDIR fault injection campaign | CRITICAL |
| TC-14 | Link stress / dropout autonomy | MAJOR |
| TC-15 | Brownout / load dump / recovery | CRITICAL |
| TC-16 | Full dress rehearsal — end-to-end mock mission | CRITICAL |
| TC-17 | Evidence pack, anomaly closure, next-gate memo | CRITICAL (process) |

## Regeneration

```bash
python3 generate_test_plan_docx.py
```

Requires `python-docx`.
