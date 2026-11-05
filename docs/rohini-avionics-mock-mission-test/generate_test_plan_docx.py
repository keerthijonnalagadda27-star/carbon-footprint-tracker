#!/usr/bin/env python3
"""Generate ROH-AVI-MTP-001 Rohini Avionics Mock Mission Test Plan (DOCX)."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Inches, Pt, RGBColor


OUT = Path(__file__).with_name("ROH-AVI-MTP-001_Rohini_Avionics_Mock_Mission_Test_Plan_v1.docx")


def set_run_font(run, size=11, bold=False, italic=False, color=None):
    run.bold = bold
    run.italic = italic
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color


def add_para(doc, text, *, size=11, bold=False, italic=False, space_after=8, space_before=0, align=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading_custom(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        set_run_font(run, size={1: 16, 2: 13, 3: 12}.get(level, 11), bold=True)
    return h


def shade_cell(cell, fill="1F4E79"):
    tc = cell._tePr if hasattr(cell, "_tePr") else cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def set_cell_text(cell, text, *, bold=False, size=9, color=None, center=False):
    cell.text = ""
    p = cell.paragraphs[0]
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color)


def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_text(hdr[i], h, bold=True, size=9, color=RGBColor(255, 255, 255), center=True)
        shade_cell(hdr[i], "1F4E79")
    for r_i, row in enumerate(rows):
        cells = table.rows[r_i + 1].cells
        for c_i, val in enumerate(row):
            set_cell_text(cells[c_i], str(val), size=9)
            if r_i % 2 == 1:
                shade_cell(cells[c_i], "F2F2F2")
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)
    doc.add_paragraph()
    return table


def bullet(doc, text, level=0):
    p = doc.add_paragraph(text, style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Inches(0.25 + 0.2 * level)
    for run in p.runs:
        set_run_font(run, size=11)
    return p


def numbered(doc, text):
    p = doc.add_paragraph(text, style="List Number")
    p.paragraph_format.space_after = Pt(2)
    for run in p.runs:
        set_run_font(run, size=11)
    return p


def hrule_note(doc, text):
    add_para(doc, text, size=10, italic=True, space_after=10)


def test_case(
    doc,
    *,
    tid,
    title,
    criticality,
    objective,
    why,
    importance,
    prerequisites,
    configuration,
    procedure,
    rubrics,
    data_products,
    abort_criteria,
    duration,
):
    add_heading_custom(doc, f"{tid} — {title}", level=2)
    add_table(
        doc,
        ["Field", "Content"],
        [
            ["Test ID", tid],
            ["Title", title],
            ["Criticality", criticality],
            ["Nominal duration", duration],
            ["Test lead", "Avionics Test Conductor (ATC)"],
            ["Witness / QA", "Systems / Quality Assurance"],
        ],
        col_widths=[1.6, 5.4],
    )

    add_heading_custom(doc, "Objective", level=3)
    add_para(doc, objective)

    add_heading_custom(doc, "Why this test exists", level=3)
    add_para(doc, why)

    add_heading_custom(doc, "Why this test is mission-critical", level=3)
    add_para(doc, importance)

    add_heading_custom(doc, "Prerequisites / entry criteria", level=3)
    for item in prerequisites:
        bullet(doc, item)

    add_heading_custom(doc, "Test configuration", level=3)
    for item in configuration:
        bullet(doc, item)

    add_heading_custom(doc, "Procedure", level=3)
    for i, step in enumerate(procedure, 1):
        numbered(doc, f"Step {i}: {step}")

    add_heading_custom(doc, "Pass / Fail rubrics (acceptance criteria)", level=3)
    add_table(
        doc,
        ["ID", "Metric / Observable", "Pass criteria", "Fail / retest trigger", "Evidence"],
        rubrics,
        col_widths=[0.7, 1.7, 1.8, 1.6, 1.2],
    )

    add_heading_custom(doc, "Required data products", level=3)
    for item in data_products:
        bullet(doc, item)

    add_heading_custom(doc, "Abort / hold criteria", level=3)
    for item in abort_criteria:
        bullet(doc, item)

    add_para(doc, "Sign-off: ATC ________  Systems ________  QA ________  Date ________", size=10, italic=True)
    add_para(doc, "")


def build():
    doc = Document()

    section = doc.sections[0]
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.85)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

    # Cover
    add_para(doc, "CATALYX SPACE — ROHINI MISSION", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "AVIONICS MOCK MISSION TEST PLAN", size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12)
    add_para(
        doc,
        "End-to-End Avionics / Ground Station / Payload Closed-Loop Rehearsal",
        size=12,
        italic=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    add_para(doc, "")
    add_table(
        doc,
        ["Attribute", "Value"],
        [
            ["Document number", "ROH-AVI-MTP-001"],
            ["Revision", "A (Draft for execution readiness)"],
            ["Classification", "INTERNAL — Mission Critical"],
            ["Mission", "Rohini (ReX-class avionics / EDL / TPS pathfinder)"],
            ["System under test", "Rohini Avionics Stack + ReX-3 Electrical Interfaces + GS + Payload"],
            ["Test type", "Mission-level Mock Test / FlatSat / Hardware-in-the-Loop (HITL)"],
            ["Governing reviews", "Avionics Mission-Level SRR Draft A; Ground Station SRR v1"],
            ["Primary ICD", "ReX-3 Electrical Interface Control Document v1"],
            ["Payload baseline", "Rohini Payload Design Document"],
            ["Mission architecture", "ROHINI MISSION architecture (drawio)"],
            ["Prepared for", "Avionics · Systems · Ground Station · Payload · QA"],
            ["Intent", "Treat as a flight-critical system test campaign, not a casual bench check"],
        ],
        col_widths=[2.2, 4.8],
    )
    add_para(
        doc,
        "WARNING: No pyrotechnic, deployment actuator, or RF high-power transmission shall be armed "
        "unless the specific test case explicitly authorizes it and all inhibits are independently verified.",
        size=10,
        bold=True,
    )
    doc.add_page_break()

    # Rev history / TOC-ish
    add_heading_custom(doc, "0. Document Control", level=1)
    add_heading_custom(doc, "0.1 Revision history", level=2)
    add_table(
        doc,
        ["Rev", "Date", "Author", "Description"],
        [
            ["A", "2026-11-05", "Avionics / Test Engineering", "Initial complete mock-mission test plan derived from Rohini SRR set, ReX-3 EICD, payload design, and mission architecture."],
        ],
        col_widths=[0.6, 1.1, 1.6, 3.7],
    )

    add_heading_custom(doc, "0.2 Applicable / reference documents", level=2)
    add_table(
        doc,
        ["Ref", "Document", "Use in this plan"],
        [
            ["AD-01", "GS_SRR_ROH_v1 — Ground Station System Requirements Review", "GS functions, telemetry ingest, commanding, timing, logging, and operator displays"],
            ["AD-02", "Rohini_Avionics_Mission_Level_SRR_DraftA — Avionics Mission-Level SRR", "Mission modes, avionics requirements, FDIR, event timeline, success criteria"],
            ["AD-03", "ReX-3 Electrical Interface Control Document v1", "Power, signal, connector, grounding, timing, and electrical pass/fail limits"],
            ["AD-04", "Rohini_Payload_Design_Document", "Payload power/data/thermal interfaces and science/ops success metrics"],
            ["AD-05", "ROHINI MISSION.drawio — Mission architecture", "End-to-end segment boundaries, data flows, and sequence of events"],
            ["RD-01", "Catalyx ReX public mission baseline (drop test / EDL heritage)", "Context for OBC, sensors, real-time comms, parachute / recovery validation heritage"],
        ],
        col_widths=[0.8, 2.8, 3.4],
    )
    hrule_note(
        doc,
        "Values marked [ICD-TBD] or [SRR-TBD] must be filled from AD-01…AD-05 before cold/hot fire execution. "
        "Do not invent electrical limits at the console.",
    )

    add_heading_custom(doc, "0.3 Definitions & acronyms", level=2)
    add_table(
        doc,
        ["Term", "Definition"],
        [
            ["ATC", "Avionics Test Conductor — owns the run, callouts, and go/no-go"],
            ["BIT / IBIT", "Built-In Test / Initiated Built-In Test"],
            ["EDL", "Entry, Descent, and Landing"],
            ["EGSE / GSE", "Electrical / Ground Support Equipment"],
            ["FDIR", "Fault Detection, Isolation, and Recovery"],
            ["FlatSat", "Electrically integrated flight-like avionics without full mechanical vehicle"],
            ["GS", "Ground Station"],
            ["HITL", "Hardware-in-the-Loop"],
            ["OBC", "On-Board Computer"],
            ["TPS", "Thermal Protection System (deployable heat shield path)"],
            ["UUT", "Unit / System Under Test"],
            ["Mock Mission", "Time-synchronized rehearsal of flight modes using flight software + EGSE stimuli"],
        ],
        col_widths=[1.4, 5.6],
    )

    # 1 Purpose
    add_heading_custom(doc, "1. Purpose, scope, and criticality statement", level=1)
    add_heading_custom(doc, "1.1 Purpose", level=2)
    add_para(
        doc,
        "This document defines the Avionics Mock Mission Test Plan for Rohini: a flight-critical, "
        "closed-loop rehearsal that proves the avionics stack can power up safely, talk to every required "
        "electrical interface (per ReX-3 EICD), exchange telemetry/commands with the Ground Station, "
        "drive payload and EDL/TPS logic through a mission timeline, detect and contain faults, and produce "
        "audit-quality evidence that the team is ready for higher-risk integrated or flight tests.",
    )
    add_para(
        doc,
        "This is not a component smoke test. It is treated as a mission dress rehearsal for the avionics "
        "segment: same seriousness as a launch countdown rehearsal, with written rubrics, holds, aborts, "
        "and signed evidence packs.",
    )

    add_heading_custom(doc, "1.2 Scope — in", level=2)
    for item in [
        "Avionics power architecture, sequencing, and brownout behavior (ReX-3 electrical interfaces)",
        "OBC boot, flight software mode machine, time sync, and logging",
        "Sensor suite acquisition, validity flags, and navigation/state estimation health",
        "RF / telemetry downlink and command uplink with Ground Station (AD-01)",
        "Payload electrical/data interface and mission data products (AD-04)",
        "EDL / TPS / recovery event logic with safe inhibits (arming logic verification without unauthorized energy release)",
        "FDIR responses to injected faults",
        "End-to-end mock mission timeline from pre-launch through recovery beacon",
        "Configuration control, anomaly process, and test evidence package",
    ]:
        bullet(doc, item)

    add_heading_custom(doc, "1.3 Scope — out (unless explicitly added by test change notice)", level=2)
    for item in [
        "Live pyrotechnic firing or mortar deployment (requires separate hazardous-ops procedure)",
        "Full aerodynamic / structural vehicle qualification",
        "Range safety flight termination system live arming beyond interface continuity checks",
        "Customer science data analysis beyond payload interface acceptance",
        "Ocean recovery logistics (covered only as beacon/telemetry success criteria)",
    ]:
        bullet(doc, item)

    add_heading_custom(doc, "1.4 Why this campaign is critical", level=2)
    add_para(
        doc,
        "Rohini exists to mature Catalyx ReX-pathfinder behaviors that later flights will stake cargo and "
        "vehicle survival on: onboard compute, sensing, real-time communications, deployment/EDL sequencing, "
        "and ground visibility. A mock mission that fails to catch a wrong connector pin, a silent telemetry "
        "gap, a mode-machine race, or an unsafe arming path is how teams discover those defects on the pad "
        "or in flight. Therefore every test case below carries an explicit criticality rationale and "
        "measurable rubric. A 'looks fine on the serial console' is not a pass.",
    )

    add_heading_custom(doc, "1.5 Success definition for the overall mock mission", level=2)
    add_table(
        doc,
        ["Level", "Definition"],
        [
            ["FULL SUCCESS", "All CRITICAL and MAJOR test cases PASS; no open P1/P2 anomalies; evidence pack complete and signed; go recommendation for next integrated test gate."],
            ["CONDITIONAL SUCCESS", "All CRITICAL PASS; MAJOR failures have approved waivers with compensatory controls; retest plan baselined before next gate."],
            ["FAIL", "Any CRITICAL fail, unresolved safe-to-arm discrepancy, data integrity loss that prevents reconstruction, or uncontrolled hazardous energy event."],
        ],
        col_widths=[1.8, 5.2],
    )

    # 2 System under test
    add_heading_custom(doc, "2. System under test and architecture", level=1)
    add_heading_custom(doc, "2.1 Segments", level=2)
    add_table(
        doc,
        ["Segment", "Contents (baseline)", "Primary truth source"],
        [
            ["Flight avionics", "OBC, power distribution, sensors/IMU/baro/GNSS as flown, radios, deployment/EDL drivers (inhibited), logging", "AD-02, AD-03"],
            ["Payload", "Rohini payload electronics, sensors/compute as designed, data interface to avionics", "AD-04"],
            ["Ground Station", "Antenna / modem path (or EGSE RF substitute), telemetry decoder, command uplink, operator UI, archive", "AD-01"],
            ["EGSE / FlatSat harness", "Flight-like harness per EICD, breakout / inhibit boxes, current shunts, stimulus boxes, time source", "AD-03, AD-05"],
            ["Safety inhibits", "Independent arm/inhibit keys, shorting plugs, RF attenuators, load banks for actuators", "Hazardous ops / AD-03"],
        ],
        col_widths=[1.6, 3.2, 2.2],
    )

    add_heading_custom(doc, "2.2 Mission modes exercised", level=2)
    add_para(
        doc,
        "Mode names below are logical. Map exact mode IDs/strings to AD-02 before execution.",
    )
    add_table(
        doc,
        ["Mode", "Intent in mock mission", "Key observables"],
        [
            ["BOOT / INIT", "Deterministic power-on and BIT", "Boot reason, BIT bitmap, time sync"],
            ["PRELAUNCH / PAD", "Idle power, GS link, inhibit status", "Current draw, inhibit telemetry, cmd ACKs"],
            ["ASCENT / COAST (sim)", "Timeline advance under ascent profile stimulus", "Mode transitions, sensor validity"],
            ["TPS DEPLOY ARM/EXECUTE (inhibited)", "Logic path for heat-shield deploy", "Arm flags, inhibit gates, command rejects when unsafe"],
            ["EDL / CHUTE SEQUENCE (inhibited)", "Drogue/main or recovery sequence logic", "Event table vs timeline, pyro continuity only"],
            ["RECOVERY / BEACON", "Post-landing visibility", "Beacon TM, last-known state archive"],
            ["SAFE / ABORT", "Contingency containment", "All actuators de-energized, GS alert"],
        ],
        col_widths=[2.2, 2.5, 2.3],
    )

    add_heading_custom(doc, "2.3 Electrical interface classes (from ReX-3 EICD)", level=2)
    add_para(
        doc,
        "Every powered interface exercised in this plan shall be traced to a connector/pin set in AD-03. "
        "Do not proceed if the as-built harness traveler does not match the EICD revision under test.",
    )
    for item in [
        "Primary / secondary power feeds and returns (voltage, ripple, inrush, UVLO/OVP behavior) — limits [ICD-TBD]",
        "Power distribution enables / load switches / sequenced rails",
        "Digital buses (UART/SPI/I2C/CAN/RS-4xx as applicable) with timing and termination per ICD",
        "Discrete GPIO: arm, inhibit, separation, deployment sense, thermistors, continuity loops",
        "RF chain interfaces (modem, PA enable, coax continuity / VSWR EGSE checks)",
        "Payload power + data + sync lines",
        "EGSE-only breakouts for current sense, fault injection, and safe loads",
    ]:
        bullet(doc, item)

    # 3 Organization
    add_heading_custom(doc, "3. Roles, responsibilities, and communications", level=1)
    add_table(
        doc,
        ["Role", "Responsibility"],
        [
            ["Test Director (TD)", "Overall authority; declares test day go/no-go; owns holds that span segments"],
            ["Avionics Test Conductor (ATC)", "Runs the procedure callouts; owns UUT configuration; first voice on avionics anomalies"],
            ["Ground Station Operator (GSO)", "GS software, RF path, command uplink, TM archive integrity"],
            ["Payload Engineer (PE)", "Payload power/data health and science/ops success metrics"],
            ["EGSE / Electrical Lead", "Harness, power supplies, inhibits, metering, fault-injection hardware"],
            ["Flight Software (FSW)", "Build identity, mode table, log decode, patch control"],
            ["Systems Engineer", "Requirements traceability, waiver disposition, next-gate recommendation"],
            ["Quality / Safety", "Procedure compliance, hazardous energy control, evidence retention"],
            ["Scribe", "Time-synced event log; captures callouts, anomalies, and configuration deltas"],
        ],
        col_widths=[2.2, 4.8],
    )
    add_heading_custom(doc, "3.1 Voice loop discipline", level=2)
    for item in [
        "Single ATC speaks procedure steps; others respond with 'GO', 'NO-GO', or 'HOLD' plus reason",
        "Any person may call HOLD for safety; only TD/ATC clear a HOLD after checklist",
        "Command uplinks require two-person verify when arming-related or mode-forcing",
        "All times logged in UTC and local; mission elapsed time (MET) from mock T-0",
    ]:
        bullet(doc, item)

    # 4 Prerequisites global
    add_heading_custom(doc, "4. Global prerequisites and readiness gates", level=1)
    add_heading_custom(doc, "4.1 Documentation & configuration gate (Gate G0)", level=2)
    for item in [
        "AD-01…AD-05 frozen for this test campaign; revision numbers recorded on cover sheet",
        "As-built avionics serial numbers, harness traveler, and EICD connector matrix attached",
        "FSW version, CRC/hash, and configuration item list recorded; no unlogged local builds",
        "GS software version and decoder dictionary matching FSW telemetry map",
        "Open anomaly list reviewed; no open P1; P2 have mitigations accepted by TD",
        "This procedure signed as released for use (or redlines approved by TD before step 1)",
    ]:
        bullet(doc, item)

    add_heading_custom(doc, "4.2 Facility & safety gate (Gate G1)", level=2)
    for item in [
        "ESD controls active; wrist straps verified; humidity/temperature logged",
        "Power supplies current-limited to ICD inrush + margin; crowbar / e-stop functional",
        "All deployment/pyro paths inhibited with independent shorting plugs / safing keys installed and photographed",
        "RF: either conducted EGSE path or radiated path with cleared keep-out and attenuators as planned",
        "Eye/hearing PPE and hazardous-ops brief complete if any actuator loads will be energized later",
        "Fire extinguisher / first aid / buddy rule in place for powered extended runs",
    ]:
        bullet(doc, item)

    add_heading_custom(doc, "4.3 EGSE calibration gate (Gate G2)", level=2)
    for item in [
        "DMM / scope / current probe calibration stickers in date",
        "Power supply sense lines verified; voltage at UUT connector within [ICD-TBD] of setpoint",
        "Time source (GPS-disciplined or NTP-verified) within 50 ms of GS clock before T-0",
        "Fault-injection box continuity and default-safe state verified (relays open / loads safe)",
        "Telemetry archive disk space > planned run + 50% margin; write test passed",
    ]:
        bullet(doc, item)

    add_heading_custom(doc, "4.4 Team readiness gate (Gate G3)", level=2)
    for item in [
        "Roles assigned; backups named; communications check complete",
        "Dry-run tabletop of abort paths completed within 7 days",
        "Everyone can locate e-stop, inhibit keys, and SAFE mode command path",
    ]:
        bullet(doc, item)

    # 5 Schedule
    add_heading_custom(doc, "5. Recommended campaign structure", level=1)
    add_table(
        doc,
        ["Day / Block", "Focus", "Exit before continuing"],
        [
            ["Block A", "G0–G3 readiness + harness / power integrity (TC-01…TC-03)", "No electrical non-compliance"],
            ["Block B", "Boot, BIT, sensors, buses (TC-04…TC-06)", "Stable PAD mode with valid sensor set"],
            ["Block C", "GS closed-loop TM/TC (TC-07…TC-08)", "Commanded ACK + archive hash OK"],
            ["Block D", "Payload interface (TC-09)", "Payload power/data rubrics PASS"],
            ["Block E", "Mission timeline rehearsal inhibited (TC-10…TC-12)", "Mode table matches expected events"],
            ["Block F", "FDIR / power stress / link stress (TC-13…TC-15)", "SAFE containment proven"],
            ["Block G", "Full dress rehearsal + evidence pack (TC-16…TC-17)", "FULL or CONDITIONAL SUCCESS declared"],
        ],
        col_widths=[1.3, 3.2, 2.5],
    )

    # 6 General rules
    add_heading_custom(doc, "6. General execution rules", level=1)
    for item in [
        "Never bypass an inhibit to 'just see if it works.' Issue a written test change notice first.",
        "Record actual values, not only PASS. Rubrics need numbers for future trend analysis.",
        "On first FAIL of a CRITICAL rubric: HOLD, preserve logs, photograph setup, do not power-cycle unless ATC orders it for safety.",
        "Configuration changes mid-run reopen Gate G0 for the affected CI.",
        "Use only the command dictionary under configuration control; no ad-hoc debug pokes during scored runs.",
        "Score each rubric independently; partial credit is CONDITIONAL at campaign level only via waiver.",
    ]:
        bullet(doc, item)

    add_heading_custom(doc, "6.1 Severity classes for anomalies", level=2)
    add_table(
        doc,
        ["Class", "Meaning", "Action"],
        [
            ["P1", "Safety risk, uncontrolled energy, or loss of primary mission evidence", "Abort block; TD + Safety disposition required"],
            ["P2", "CRITICAL rubric fail or loss of major function with workaround unknown", "HOLD; root-cause before resume"],
            ["P3", "MAJOR rubric fail with known workaround", "Log; may continue with TD approval"],
            ["P4", "Cosmetic / process / documentation", "Log; fix before evidence pack close"],
        ],
        col_widths=[0.8, 3.4, 2.8],
    )

    doc.add_page_break()

    # ===================== TEST CASES =====================
    add_heading_custom(doc, "7. Detailed test cases", level=1)
    add_para(
        doc,
        "Each case is written so a new ATC can execute it without tribal knowledge: why it exists, "
        "why it matters, what must already be true, exact scoring rubrics, and abort rules.",
    )

    test_case(
        doc,
        tid="TC-01",
        title="As-built configuration audit & inhibit proof",
        criticality="CRITICAL",
        objective="Prove the UUT on the bench is the configuration we claim to be testing, and that all hazardous energy paths are independently inhibited before applying power.",
        why="Most 'mysterious' avionics failures in integrated test are configuration escapes: wrong harness revision, wrong FSW image, missing shorting plug, or GS dictionary mismatch. This test kills those escapes before they corrupt later results.",
        importance="If this fails and you continue, every later PASS is unverifiable. Configuration integrity is the foundation of flight-critical evidence.",
        prerequisites=[
            "Gates G0–G1 complete",
            "Printed/ electronic CI list available at the rack",
            "Camera available for inhibit photography",
        ],
        configuration=[
            "UUT unpowered",
            "All EGSE connected mechanically but supplies OUTPUT OFF",
            "Inhibit keys / shorting plugs installed per hazardous matrix",
        ],
        procedure=[
            "ATC reads CI list aloud; EGSE Lead verifies serials on hardware against traveler.",
            "FSW engineer verifies image hash on load media matches CI list; record hash.",
            "GSO verifies GS build + TM dictionary version matches CI list.",
            "Walk every deployment/pyro/actuator connector: confirm shorting plug or safe-load and photograph.",
            "Verify arm keys are REMOVED / SAFE and tagged; scribe logs tag IDs.",
            "Confirm no unauthorized breakout jumpers vs EICD.",
            "TD declares TC-01 complete only after rubric table filled.",
        ],
        rubrics=[
            ["R01-1", "CI serial match", "100% match to traveler", "Any mismatch", "Marked CI list"],
            ["R01-2", "FSW hash", "Exact match to CI", "Mismatch", "Hash screenshot/log"],
            ["R01-3", "GS dictionary", "Exact match to FSW map", "Mismatch", "Version page"],
            ["R01-4", "Inhibit photo set", "All hazardous paths photographed & tagged", "Missing path", "Photo pack"],
            ["R01-5", "Arm key state", "SAFE / removed as required", "Any armed key", "Scribe log"],
        ],
        data_products=["CI verification sheet", "Photo pack", "Hash printout", "Scribe log excerpt"],
        abort_criteria=["Any unknown connector", "Missing inhibit on a hazardous line", "FSW/GS dictionary mismatch not resolved"],
        duration="45–90 min",
    )

    test_case(
        doc,
        tid="TC-02",
        title="Harness continuity, isolation, and EICD pin audit",
        criticality="CRITICAL",
        objective="Verify flight harness and EGSE breakouts meet ReX-3 Electrical ICD continuity/isolation requirements before energizing.",
        why="Wrong pin maps and marginal isolation are classic root causes of lost boards and false sensor data. Finding them unpowered is mandatory.",
        importance="Energizing a crossed power/return or bus pin can destroy flight avionics and invalidate the entire campaign.",
        prerequisites=["TC-01 PASS", "EICD connector matrices printed", "Calibrated DMM / hipot policy per Safety"],
        configuration=["UUT disconnected from power supplies", "Breakout access as needed", "ESD controls on"],
        procedure=[
            "For each connector in the test set: perform pin-to-pin continuity against EICD.",
            "Perform isolation checks between power nets, between power and chassis (per ICD), and between unrelated buses.",
            "Verify shield terminations and drain wires per EICD grounding scheme.",
            "Record any temporary EGSE adapters; confirm they are approved.",
            "Resolve all discrepancies before TC-03.",
        ],
        rubrics=[
            ["R02-1", "Continuity of required nets", "Per AD-03 ohms limit [ICD-TBD]", "Open/high resistance", "Cont. sheet"],
            ["R02-2", "Isolation between nets", "Per AD-03 Mohm/hipot [ICD-TBD]", "Below limit", "Iso sheet"],
            ["R02-3", "Connector keying / clocking", "Matches EICD mechanical notes", "Force-fit or wrong clocking", "Photo"],
            ["R02-4", "Shield/ground scheme", "Per AD-03", "Floating/incorrect shield", "Measurement log"],
        ],
        data_products=["Continuity/isolation sheets keyed to EICD table IDs", "Discrepancy list"],
        abort_criteria=["Any power-to-signal short", "Unknown net", "Failed isolation on primary power"],
        duration="2–6 hr depending on harness complexity",
    )

    test_case(
        doc,
        tid="TC-03",
        title="Power application, inrush, rail sequencing, and steady-state budget",
        criticality="CRITICAL",
        objective="Apply power per ICD sequence; verify inrush, UVLO, rail order, ripple, and steady currents against budget.",
        why="Avionics that brown-out mid-timeline or over-draw bus power will drop RF, corrupt logs, or reset during EDL — unrecoverable in flight.",
        importance="Power integrity is a common-cause failure for every later function. This test is the electrical backbone of the mock mission.",
        prerequisites=["TC-02 PASS", "Gate G2 complete", "Current probe on primary feed", "Supply current limit set"],
        configuration=[
            "Supplies set to nominal ICD voltage [ICD-TBD]",
            "Current limit = expected inrush + margin [ICD-TBD]",
            "Scope on primary rail at UUT connector",
        ],
        procedure=[
            "Confirm inhibits still SAFE (spot check).",
            "Enable supplies in the ICD-specified order; capture inrush waveform.",
            "Measure steady-state current in BOOT and PRELAUNCH/PAD modes.",
            "Measure rail voltages at UUT pins under load; compare to ICD.",
            "Introduce a controlled ±% voltage sweep within ICD allowable; confirm no reset [ICD-TBD].",
            "Command a controlled power-down; verify sequencing and no backfeed anomalies.",
            "Record thermal spot checks on regulators after soak [SRR-TBD minutes].",
        ],
        rubrics=[
            ["R03-1", "Inrush peak / duration", "Within AD-03 envelope", "Exceeds envelope or trips limit", "Scope shot"],
            ["R03-2", "Rail voltage at pin", "Within AD-03 tolerance", "Out of tolerance", "DMM log"],
            ["R03-3", "Steady current PAD", "Within power budget + margin [SRR-TBD]", "Over budget", "Shunt log"],
            ["R03-4", "No unexpected resets", "0 resets during sweep", "Any reset", "OBC log"],
            ["R03-5", "Power-down behavior", "Clean sequence; no reverse bias symptoms", "Anomaly", "Scope + log"],
        ],
        data_products=["Scope captures", "Power budget sheet", "OBC boot log"],
        abort_criteria=["Smell/smoke", "Overcurrent trip unexplained", "Rail > absolute max", "Inhibit telemetry disagreement"],
        duration="1.5–3 hr",
    )

    test_case(
        doc,
        tid="TC-04",
        title="OBC boot determinism, BIT, and time synchronization",
        criticality="CRITICAL",
        objective="Demonstrate repeatable boot, initiated BIT results, and time sync with GS within mission tolerance.",
        why="Non-deterministic boot or failed BIT that is ignored produces unreproducible flight software behavior and false confidence.",
        importance="If boot/BIT/time are wrong, telemetry timelines cannot be correlated to events — mission reconstruction fails.",
        prerequisites=["TC-03 PASS", "GS clock source available"],
        configuration=["UUT powered in PAD", "GS connected via planned TM path (even if later RF tests use EGSE)"],
        procedure=[
            "Cold boot 3× from full power removal (wait ICD discharge time).",
            "Warm reboot 3× via commanded reset.",
            "On each boot record: boot reason, BIT bitmap, FSW version, clock status.",
            "Synchronize time using mission method (GNSS, GS time msg, etc.).",
            "Compare OBC time vs GS archive timestamps under concurrent TM.",
            "Force a BIT fail via EGSE if supported (optional diagnostic); confirm FDIR flag — then restore.",
        ],
        rubrics=[
            ["R04-1", "Cold boot success", "3/3 boot to PAD without hang", "<3/3", "Boot logs"],
            ["R04-2", "BIT result", "All mandatory BIT bits PASS per AD-02", "Any mandatory fail", "BIT telemetry"],
            ["R04-3", "FSW identity", "Matches CI hash/version", "Mismatch", "TM field"],
            ["R04-4", "Time sync error", "≤ [SRR-TBD] ms vs GS", "Out of limit", "Time delta log"],
            ["R04-5", "Boot time", "≤ [SRR-TBD] s to PAD ready", "Over limit", "MET stamp"],
        ],
        data_products=["Boot matrix", "BIT decode", "Time delta plot"],
        abort_criteria=["Hang requiring hard unplug repeatedly", "BIT fail on safety-critical item without explanation"],
        duration="1–2 hr",
    )

    test_case(
        doc,
        tid="TC-05",
        title="Sensor suite validity and state estimation health",
        criticality="CRITICAL",
        objective="Verify IMU/baro/GNSS/other flight sensors produce valid, ranged, time-aligned data and that estimators report healthy status in PAD and under mild stimulus.",
        why="EDL and deploy triggers depend on sensing. Invalid sensors that still look 'alive' are more dangerous than hard fails.",
        importance="False apogee/deploy triggers or silent sensor freeze can lose the vehicle. This test proves validity logic, not just that packets exist.",
        prerequisites=["TC-04 PASS", "Sensor stimulus method available (tilt, pressure chamber, GNSS view or simulator)"],
        configuration=["Flight sensors powered", "No actuator arming"],
        procedure=[
            "Log static PAD sensor baseline for [SRR-TBD] minutes; check freeze detection.",
            "Apply known stimulus to each sensor class; confirm directionality/sign conventions per ICD/mech frame.",
            "Verify validity flags transition correctly when stimulus removed or sensor disconnected (EGSE fault).",
            "Confirm estimator / navigation health flags behave per AD-02.",
            "Check sampling rates and gap counters against TM map.",
        ],
        rubrics=[
            ["R05-1", "Packet rate", "Within TM map ± tolerance", "Underrun/gaps", "GS rate meter"],
            ["R05-2", "Range / units", "Physical ranges plausible; units per ICD", "Out of range without flag", "Archive sample"],
            ["R05-3", "Validity flags", "Agree with stimulus/fault state", "Disagree", "Fault log"],
            ["R05-4", "Frame / sign", "Matches mechanical frame notes", "Inverted axis uncaught", "Stimulus sheet"],
            ["R05-5", "Freeze detect", "Detects stuck values per AD-02", "No detection", "Injected freeze"],
        ],
        data_products=["Sensor health report", "Stimulus response plots", "Flag truth table"],
        abort_criteria=["Unexplained estimator divergence that commands mode change", "Safety sensor fail without SAFE response when required"],
        duration="2–4 hr",
    )

    test_case(
        doc,
        tid="TC-06",
        title="Internal data bus and peripheral communications stress",
        criticality="MAJOR",
        objective="Prove avionics internal buses and peripheral links remain reliable under mission-like traffic.",
        why="Intermittent bus errors often appear only when TM + logging + payload traffic coincide — exactly flight conditions.",
        importance="Bus faults can drop deployment commands or corrupt logs without a clean crash.",
        prerequisites=["TC-04 PASS", "Ability to generate high TM/logging load"],
        configuration=["Full avionics stack powered", "Payload may be on if already cleared"],
        procedure=[
            "Baseline error counters on all buses.",
            "Command high-rate logging + full TM + payload traffic for soak [SRR-TBD].",
            "Monitor retries, CRC errors, restarts.",
            "Power-cycle peripherals (if supported) and confirm recovery.",
        ],
        rubrics=[
            ["R06-1", "Bus CRC/error count", "≤ [SRR-TBD] over soak", "Above limit", "Counter log"],
            ["R06-2", "No unplanned resets", "0", "Any", "Boot reason"],
            ["R06-3", "Recovery after peripheral cycle", "Auto-recover ≤ [SRR-TBD] s", "Hang", "Event log"],
        ],
        data_products=["Bus error counters", "Soak summary"],
        abort_criteria=["Error avalanche", "Loss of ATC ability to command SAFE"],
        duration="1–3 hr soak + setup",
    )

    test_case(
        doc,
        tid="TC-07",
        title="Ground Station telemetry closed-loop (RF or conducted)",
        criticality="CRITICAL",
        objective="Establish end-to-end telemetry from UUT through GS decode, display, and archive with bit-level integrity.",
        why="Without trustworthy TM, the mock mission cannot be scored and flight ops will be blind.",
        importance="GS is part of the mission system. Avionics-only success with broken GS still fails Rohini ops readiness (AD-01).",
        prerequisites=["TC-04 PASS", "AD-01 TM requirements mapped", "Archive path verified"],
        configuration=["Planned RF path with attenuators OR conducted modem EGSE", "GSO on console"],
        procedure=[
            "Bring up link per GS procedure; record RSSI/SNR/EbN0 as applicable.",
            "Verify all mandatory channels decode with correct engineering units.",
            "Run link for [SRR-TBD] minutes; measure packet loss / dropout statistics.",
            "Pull archive; verify hash continuity and no gaps exceeding AD-01.",
            "Confirm operator displays match raw archive for spot-checked fields (anti-UI-bug check).",
        ],
        rubrics=[
            ["R07-1", "Link acquisition", "Acquired ≤ [SRR-TBD] s", "Fail to acquire", "GSO log"],
            ["R07-2", "Mandatory channel set", "100% present & decoded", "Missing channel", "Channel checklist"],
            ["R07-3", "Packet loss", "≤ [AD-01 limit]", "Above limit", "Stats export"],
            ["R07-4", "Archive integrity", "Continuous; hash OK", "Gap/corrupt", "Archive report"],
            ["R07-5", "UI vs archive", "Spot checks match", "Mismatch", "Screenshot+raw"],
        ],
        data_products=["Link stats", "Archive segment", "Channel checklist"],
        abort_criteria=["Inability to monitor inhibit/arm discretes via TM", "Archive write failure"],
        duration="1–2 hr",
    )

    test_case(
        doc,
        tid="TC-08",
        title="Command uplink, authentication/validation, and reject paths",
        criticality="CRITICAL",
        objective="Prove GS can command the vehicle safely: valid commands ACKed and executed; invalid/unsafe commands rejected with clear telemetry.",
        why="A command system that accepts garbage or arming commands while inhibited is a mission-ending hazard.",
        importance="Uplink is a safety-critical control path. Rubrics here protect against inadvertent mode changes and unsafe arming.",
        prerequisites=["TC-07 PASS", "Command dictionary under CI", "Two-person verify briefed"],
        configuration=["UUT in PAD", "All hazardous inhibits installed", "Arm keys SAFE"],
        procedure=[
            "Send benign no-op / ping command; verify ACK and latency.",
            "Send mode query / pad keepalive commands; verify state unchanged except intended.",
            "Send deliberately invalid CRC / unknown opcode; verify reject + counter increment.",
            "Attempt arm-related command while inhibited; verify REJECT and no discrete change.",
            "Verify command audit log on GS matches onboard accepted/rejected counts.",
        ],
        rubrics=[
            ["R08-1", "Valid cmd ACK", "ACK ≤ [SRR-TBD] s", "Timeout/NACK unexplained", "Cmd log"],
            ["R08-2", "Invalid cmd reject", "Rejected; no state change", "Accepted or state change", "Cmd+TM"],
            ["R08-3", "Inhibited arm reject", "Reject; arm discrete remains SAFE", "Any arm attempt success", "Discrete TM"],
            ["R08-4", "Audit consistency", "GS log == OBC counters", "Mismatch", "Both logs"],
        ],
        data_products=["Command audit export", "Reject proof screenshots"],
        abort_criteria=["Any unexpected arm discrete true", "Loss of command authority without SAFE fallback"],
        duration="1–2 hr",
    )

    test_case(
        doc,
        tid="TC-09",
        title="Payload power, data interface, and mission data products",
        criticality="CRITICAL (if payload is mission success criteria) / MAJOR otherwise",
        objective="Verify Rohini payload electrical and data interfaces per payload design document and avionics ICD allocations.",
        why="Payload is often why the mission flies. Interface mistakes show up late if not rehearsed under flight-like avionics control.",
        importance="A healthy avionics stack that starves, resets, or corrupts payload data still fails mission-level success.",
        prerequisites=["TC-03 PASS", "TC-07 recommended", "Payload safe-to-power checklist complete"],
        configuration=["Payload connected per AD-04", "Thermal attention if enclosed"],
        procedure=[
            "Enable payload power via flight-like path (not a random bench supply bypass unless explicitly allowed).",
            "Verify payload current and voltage within AD-04.",
            "Establish data link; verify sync, rates, and packet structure.",
            "Run payload ops mode for soak; confirm avionics still meets TM/cmd rubrics.",
            "Disable payload; confirm clean power-down and no bus lockup.",
        ],
        rubrics=[
            ["R09-1", "Payload rail", "Within AD-04", "Out of limit", "Meter+TM"],
            ["R09-2", "Data link up", "Per AD-04 ≤ time", "Fail", "PE log"],
            ["R09-3", "Data integrity", "CRC/loss within limit", "Above limit", "Payload archive"],
            ["R09-4", "Avionics coexistence", "No PAD regressions vs TC-07", "Regressions", "Compare stats"],
            ["R09-5", "Clean power-down", "No hang; bus recovers", "Hang/reset loop", "Event log"],
        ],
        data_products=["Payload interface report", "Sample science/ops file", "Power log"],
        abort_criteria=["Payload overcurrent", "Smoke/thermal runaway", "Bus lock that blocks SAFE"],
        duration="2–4 hr",
    )

    test_case(
        doc,
        tid="TC-10",
        title="Mission mode machine rehearsal (ascent → coast → pre-EDL) with inhibits",
        criticality="CRITICAL",
        objective="Drive the flight software through the Rohini mission mode timeline using EGSE stimulus / time acceleration and verify event tables without releasing hazardous energy.",
        why="Mode transitions are where latent logic bugs live: off-by-one timers, missing guards, wrong sensor sources.",
        importance="ReX-pathfinder missions depend on correct sequencing for TPS/EDL. This is the software heart of the mock mission.",
        prerequisites=["TC-05 PASS", "TC-08 PASS", "Timeline table from AD-02/AD-05 baselined"],
        configuration=["Inhibits installed", "Stimulus profiles loaded", "Scribe ready with expected event sheet"],
        procedure=[
            "Start MET clock at mock T-0; ATC calls timeline.",
            "Inject ascent profile stimulus (accel/pressure/time) per test script.",
            "At each expected mode transition, verify TM mode ID, guards, and inhibit states.",
            "Verify no arming occurs unless the script explicitly tests arm logic under SAFE loads.",
            "Hold at pre-EDL; dump event table and compare to expected.",
        ],
        rubrics=[
            ["R10-1", "Transition set", "All expected transitions occurred once", "Missed/extra", "Event table"],
            ["R10-2", "Transition time error", "Within [SRR-TBD] of expected", "Out of window", "MET log"],
            ["R10-3", "Guard conditions", "No transition with failed guards", "Illegal transition", "FSW log"],
            ["R10-4", "Inhibit integrity", "Hazardous energize = 0", "Any energize", "Current sense"],
        ],
        data_products=["Annotated event table", "MET timeline plot", "FSW mode log"],
        abort_criteria=["Illegal transition toward deploy/pyro energy", "Loss of GS visibility mid-timeline"],
        duration="2–3 hr",
    )

    test_case(
        doc,
        tid="TC-11",
        title="TPS / heat-shield deployment logic (inhibited / safe-loaded)",
        criticality="CRITICAL",
        objective="Validate arming interlocks and command path for deployable TPS without deploying flight hardware unsafely.",
        why="Deployable heat shield is a defining ReX technology risk. Logic and interlocks must be proven before any live deploy test.",
        importance="A single false deploy or deploy without preconditions can destroy the article or create a hazardous whip/energy event on the bench.",
        prerequisites=["TC-10 PASS", "Safe loads or actuator disconnect confirmed", "Dedicated Safety presence"],
        configuration=["Flight deploy driver connected only to approved safe load or open with continuity monitor per Safety", "Arm keys still controlled"],
        procedure=[
            "Verify telemetry shows DEPLOY_INHIBITED / equivalent true.",
            "Attempt deploy command — expect reject.",
            "Enable only the logical arm states allowed by procedure while keeping physical energy inhibited; verify state machine.",
            "If authorized: install safe-load, follow hazardous checklist, perform a single commanded safe-load pulse; measure pulse width/current against ICD.",
            "Return all inhibits; photograph SAFE state.",
        ],
        rubrics=[
            ["R11-1", "Reject while inhibited", "Command rejected; 0 current on deploy driver", "Current seen", "Shunt scope"],
            ["R11-2", "Interlock telemetry", "Matches physical inhibit truth", "Mismatch", "Truth table"],
            ["R11-3", "Safe-load pulse (if exec)", "Width/amplitude within AD-03", "Out of limit", "Scope"],
            ["R11-4", "Return to SAFE", "All arm flags false; keys SAFE", "Residual arm", "Photo+TM"],
        ],
        data_products=["Interlock truth table", "Scope of safe-load pulse (if any)", "Safety checklist"],
        abort_criteria=["Unexpected current on deploy channel", "Inability to clear arm flags", "Any personnel near potential motion path during pulse"],
        duration="1–3 hr",
    )

    # Fix procedure list item that accidentally nested
    # We'll handle in post - actually I put a list inside procedure which is wrong. Let me fix the generator - I'll rewrite TC-11 procedure as all strings.

    test_case(
        doc,
        tid="TC-12",
        title="EDL / parachute recovery sequence logic (inhibited)",
        criticality="CRITICAL",
        objective="Rehearse drogue/main/recovery event logic and continuity monitoring without live pyrotechnics.",
        why="Drop-test heritage shows parachutes and EDL timing are among the hardest empirical systems; avionics timing/guards must be proven before hazardous live fires.",
        importance="Late or early chute events are classic mission failures. Mock mission must prove the event table and inhibits.",
        prerequisites=["TC-10 PASS", "Pyro continuity EGSE available", "Shorting plugs confirmed"],
        configuration=["Pyro lines on continuity/safe EGSE only", "No live initiators on the line"],
        procedure=[
            "Confirm pyro continuity states read as expected (present/safe).",
            "Advance timeline into EDL; verify predicted event order vs AD-02.",
            "Verify each fire request is gated by altitude/speed/time/sensor sources as specified.",
            "Confirm physical outputs remain inhibited (0 fire current).",
            "Simulate one missed sensor validity and confirm FDIR inhibits fire.",
        ],
        rubrics=[
            ["R12-1", "Event order", "Exact match to baselined table", "Wrong order", "Event log"],
            ["R12-2", "Gate logic", "No fire request with failed gates", "Ungated request", "FSW log"],
            ["R12-3", "Output energy", "0 fire current throughout", "Any current", "Shunt"],
            ["R12-4", "Sensor-fail inhibit", "Fire inhibited on injected invalidity", "Still requests fire", "FDIR log"],
        ],
        data_products=["EDL event proof pack", "Continuity log", "FDIR inject result"],
        abort_criteria=["Any fire current", "Continuity anomaly suggesting live device attached"],
        duration="1.5–3 hr",
    )

    test_case(
        doc,
        tid="TC-13",
        title="FDIR fault injection campaign",
        criticality="CRITICAL",
        objective="Inject representative faults and verify detection, isolation, recovery, and SAFE behaviors per AD-02.",
        why="Happy-path passes do not prove mission survivability. FDIR is how avionics earns trust under failure.",
        importance="In flight, faults are not optional. If FDIR is wrong, minor failures become vehicle losses.",
        prerequisites=["TC-08 PASS", "Fault injection matrix approved by Systems/Safety"],
        configuration=["EGSE fault box", "Inhibits installed", "Rapid SAFE path verified"],
        procedure=[
            "Execute approved inject matrix one fault at a time; restore between cases.",
            "Minimum set: TM dropout, command flood, sensor invalid, rail UVLO transient (within safe limits), peripheral bus stall, payload overcurrent trip simulation.",
            "For each: record detect time, isolation action, operator alert, recoverability.",
            "Confirm no hazardous arming as a side effect of any fault.",
        ],
        rubrics=[
            ["R13-1", "Detection latency", "≤ [SRR-TBD] per fault class", "Over limit", "Timed log"],
            ["R13-2", "Correct isolation", "Matches FDIR table", "Wrong action", "FSW log"],
            ["R13-3", "Operator alert", "GS alert raised", "Silent fail", "GSO log"],
            ["R13-4", "No unsafe side effects", "Arm/deploy remain SAFE", "Side effect", "Discrete TM"],
            ["R13-5", "Recoverability", "Per design (recover or stay SAFE)", "Unexpected state", "Post-fault dump"],
        ],
        data_products=["FDIR results matrix", "Alert screenshots", "Post-fault dumps"],
        abort_criteria=["Fault causes uncontrolled energy", "SAFE command fails"],
        duration="3–6 hr",
    )

    test_case(
        doc,
        tid="TC-14",
        title="Link stress, multipath/dropout, and autonomous behavior",
        criticality="MAJOR",
        objective="Characterize avionics behavior during TM/TC dropouts and restored links.",
        why="Real flights lose link. Vehicle must not do something stupid while blind, and must reacquire cleanly.",
        importance="Prevents reset storms, command buffer hazards, and silent mode changes during dropout.",
        prerequisites=["TC-07 PASS", "TC-08 PASS"],
        configuration=["Attenuator / disconnect method to drop link"],
        procedure=[
            "Establish healthy link baseline.",
            "Induce dropout for durations per AD-01/AD-02 cases.",
            "Observe onboard autonomy (continue timeline vs SAFE) matches spec.",
            "Restore link; verify reacquire, backlog/TM catch-up policy, and command sanity.",
        ],
        rubrics=[
            ["R14-1", "Onboard behavior during dropout", "Matches AD-02", "Unexpected mode", "OBC log"],
            ["R14-2", "Reacquire time", "≤ [SRR-TBD]", "Over", "GSO log"],
            ["R14-3", "No command replay hazard", "No duplicate unsafe exec", "Duplicate exec", "Cmd audit"],
        ],
        data_products=["Dropout test sheet", "Reacquire stats"],
        abort_criteria=["Uncommanded deploy/arm attempt during dropout"],
        duration="1–2 hr",
    )

    test_case(
        doc,
        tid="TC-15",
        title="Power contingency: brownout, load dump, and recovery",
        criticality="CRITICAL",
        objective="Verify UVLO/brownout handling and recovery without corruption or unsafe defaults.",
        why="Batteries and buses sag. Avionics must fail safe and recover predictably.",
        importance="Brownout-induced partial writes and half-armed states are nightmare failure modes.",
        prerequisites=["TC-03 PASS", "TC-13 partially complete recommended"],
        configuration=["Programmable supply", "Logging of rails + OBC state"],
        procedure=[
            "From PAD, ramp voltage down to UVLO; capture behavior.",
            "Hold below UVLO; confirm SAFE defaults on outputs.",
            "Restore voltage; confirm boot reason and state per design.",
            "Repeat with fast transient sag if ICD requires.",
        ],
        rubrics=[
            ["R15-1", "UVLO trip point", "Within AD-03", "Out of limit", "Scope"],
            ["R15-2", "Outputs on UVLO", "All hazardous outputs SAFE", "Any assert", "Driver sense"],
            ["R15-3", "Recovery state", "Per AD-02 expected", "Wrong mode/corrupt config", "Boot log"],
            ["R15-4", "Filesystem/log integrity", "No critical corruption", "Corrupt CI/logs", "fsck/log"],
        ],
        data_products=["Brownout scope pack", "Recovery boot logs"],
        abort_criteria=["Hazardous output asserts on sag", "Unrecoverable filesystem"],
        duration="1–2 hr",
    )

    test_case(
        doc,
        tid="TC-16",
        title="Full dress rehearsal — end-to-end mock mission",
        criticality="CRITICAL",
        objective="Execute a single continuous Rohini mock mission from prelaunch through recovery beacon with full team, scoring all mandatory observables.",
        why="Piecewise passes can still fail at seams: handoffs, long-duration thermal, operator workload, archive rotation.",
        importance="This is the gate that says the avionics-side mission mock is real. Treat countdown discipline as flight-like.",
        prerequisites=[
            "TC-01…TC-15 complete to required level (CRITICAL all PASS; MAJOR waived only with TD approval)",
            "Gates G0–G3 re-verified same day",
            "Dress-rehearsal script printed; roles staffed",
        ],
        configuration=["Full FlatSat + GS + payload as baselined", "Inhibits installed", "All recorders rolling before T-30 min"],
        procedure=[
            "T-30 min: poll GO/NO-GO by role; start recorders; verify inhibits.",
            "T-10 min: final CI/hash spot check; link health; payload health.",
            "T-0: start MET; execute timeline script through ascent/coast/pre-EDL/EDL-logic/recovery.",
            "Perform one approved fault inject mid-run if Systems requests (optional, pre-briefed).",
            "At end: recovery beacon/TM success; command SAFE; stop clocks.",
            "Do not tear down until ATC confirms raw archives flushed and hashed.",
        ],
        rubrics=[
            ["R16-1", "Countdown discipline", "No unlogged procedure skips", "Skipped critical step", "Scribe log"],
            ["R16-2", "Timeline completion", "All mandatory events scored", "Missed mandatory", "Event table"],
            ["R16-3", "Link + archive", "Meet TC-07 rubrics across full run", "Fail", "Archive report"],
            ["R16-4", "Safety", "0 unplanned hazardous energy", "Any", "Shunt continuous log"],
            ["R16-5", "Team abort readiness", "One HOLD drill cleared properly (pre-briefed)", "Confusion/unsafe clear", "Scribe"],
            ["R16-6", "Post-run hash", "All primary archives hashed < [SRR-TBD] min", "Lost/unhashed", "Hash list"],
        ],
        data_products=["Full mission evidence pack", "MET annotated timeline", "GO/NO-GO poll sheet", "Hash manifest"],
        abort_criteria=["P1 anomaly", "Loss of SAFE authority", "Inhibit compromise"],
        duration="Half-day including brief/debrief",
    )

    test_case(
        doc,
        tid="TC-17",
        title="Evidence pack, anomaly closure, and next-gate recommendation",
        criticality="CRITICAL (process)",
        objective="Close the campaign with a reconstructible evidence pack and a written go / conditional / no-go recommendation.",
        why="A test that cannot be audited did not happen for flight certification purposes.",
        importance="Downstream integrated tests and flight reviews will demand this pack. Incomplete closure blocks the program honestly — which is the point.",
        prerequisites=["TC-16 executed (PASS or FAIL)", "All raw data on controlled storage"],
        configuration=["N/A — desk + data systems"],
        procedure=[
            "Assemble evidence pack per Section 8 checklist.",
            "Triage anomalies; assign owners and due dates.",
            "Systems maps results to AD-02 requirements IDs.",
            "TD issues recommendation: FULL SUCCESS / CONDITIONAL / FAIL.",
            "QA stamps retention location and retention duration.",
        ],
        rubrics=[
            ["R17-1", "Pack completeness", "100% of Section 8 required items", "Missing item", "Checklist"],
            ["R17-2", "Requirements trace", "Every CRITICAL req has result", "Orphan/missing", "RTM excerpt"],
            ["R17-3", "Anomaly dispositions", "All P1/P2 dispositioned", "Open P1/P2", "AR list"],
            ["R17-4", "Signed recommendation", "TD/Systems/QA signed", "Unsigned", "Signature page"],
        ],
        data_products=["ROH-AVI-MTP-001 Evidence Pack", "Next Gate Memo"],
        abort_criteria=["N/A — process failure means campaign remains OPEN"],
        duration="4–8 hr",
    )

    doc.add_page_break()

    # 8 Evidence
    add_heading_custom(doc, "8. Evidence pack checklist", level=1)
    add_para(doc, "The mock mission is not closed until this pack exists on controlled storage.")
    for item in [
        "Released procedure PDF/DOCX + redline log",
        "CI list with serials, harness traveler, FSW hash, GS dictionary version",
        "Inhibit photo pack and hazardous energy matrix",
        "Continuity/isolation sheets (TC-02)",
        "Power scope captures and budget sheet (TC-03)",
        "Boot/BIT/time matrix (TC-04)",
        "Sensor health + stimulus plots (TC-05)",
        "GS link stats + archive segments + hash manifest (TC-07/16)",
        "Command audit logs including reject proofs (TC-08)",
        "Payload interface report (TC-09)",
        "Mode/EDL/TPS event tables (TC-10…12)",
        "FDIR injection matrix results (TC-13)",
        "Brownout pack (TC-15)",
        "Dress rehearsal scribe log + GO/NO-GO polls (TC-16)",
        "Anomaly reports and waivers",
        "Requirements traceability matrix excerpt",
        "Signed next-gate recommendation",
    ]:
        bullet(doc, item)

    # 9 Traceability
    add_heading_custom(doc, "9. Requirements traceability (template)", level=1)
    add_para(
        doc,
        "Fill requirement IDs from AD-01 and AD-02. Do not mark a CRITICAL requirement satisfied without a rubric ID.",
    )
    add_table(
        doc,
        ["Req ID (from SRR)", "Req summary", "Test case(s)", "Rubric ID(s)", "Result", "Evidence pointer"],
        [
            ["[AD-02-…]", "Deterministic boot / BIT", "TC-04", "R04-*", "", ""],
            ["[AD-02-…]", "Mission mode timeline", "TC-10, TC-16", "R10-*, R16-*", "", ""],
            ["[AD-02-…]", "FDIR / SAFE", "TC-13, TC-15", "R13-*, R15-*", "", ""],
            ["[AD-02-…]", "TPS deploy interlocks", "TC-11", "R11-*", "", ""],
            ["[AD-02-…]", "EDL event logic", "TC-12", "R12-*", "", ""],
            ["[AD-01-…]", "TM archive integrity", "TC-07, TC-16", "R07-*, R16-3", "", ""],
            ["[AD-01-…]", "Command reject/audit", "TC-08", "R08-*", "", ""],
            ["[AD-03-…]", "Power / connector limits", "TC-02, TC-03", "R02-*, R03-*", "", ""],
            ["[AD-04-…]", "Payload interface", "TC-09", "R09-*", "", ""],
        ],
        col_widths=[1.2, 1.6, 1.2, 1.1, 0.8, 1.1],
    )

    # 10 Anomaly
    add_heading_custom(doc, "10. Anomaly & waiver process", level=1)
    for item in [
        "Anyone may open an anomaly; ATC assigns initial severity.",
        "P1: stop hazardous ops immediately; preserve state; notify TD/Safety.",
        "Root cause required before closing P1/P2; 'could not reproduce' needs TD acceptance to defer.",
        "Waivers for MAJOR fails require compensatory test or operational constraint written into next-gate memo.",
        "No silent retest loops — each attempt gets a run ID.",
    ]:
        bullet(doc, item)

    # 11 Risks
    add_heading_custom(doc, "11. Test risks and mitigations", level=1)
    add_table(
        doc,
        ["Risk", "Mitigation"],
        [
            ["Damage from incorrect harnessing", "TC-01/02 mandatory before power; current limits"],
            ["Inadvertent deploy/pyro energy", "Independent inhibits; photo proof; Safe-load only under Safety checklist"],
            ["RF exposure / interference", "Conducted path preferred; attenuators; cleared keep-out if radiated"],
            ["Irreproducible results from config drift", "Hash locks; no ad-hoc FSW; Gate G0 reopen rules"],
            ["False PASS from UI-only monitoring", "Archive vs UI spot checks; raw counters required"],
            ["Incomplete evidence", "TC-17 gate; QA ownership of retention"],
        ],
        col_widths=[2.8, 4.2],
    )

    # 12 Sign-off
    add_heading_custom(doc, "12. Approval & campaign sign-off", level=1)
    add_table(
        doc,
        ["Role", "Name", "Signature", "Date"],
        [
            ["Author / Avionics Test Engineering", "", "", ""],
            ["Avionics Lead", "", "", ""],
            ["Ground Station Lead", "", "", ""],
            ["Payload Lead", "", "", ""],
            ["Systems Engineer", "", "", ""],
            ["Quality / Safety", "", "", ""],
            ["Test Director", "", "", ""],
        ],
        col_widths=[2.4, 1.6, 1.6, 1.4],
    )

    add_heading_custom(doc, "12.1 Post-campaign declaration", level=2)
    add_para(doc, "Campaign result (circle one):  FULL SUCCESS    /    CONDITIONAL SUCCESS    /    FAIL")
    add_para(doc, "Next gate authorized: ________________________________")
    add_para(doc, "Constraints / waivers in force: ________________________________")
    add_para(doc, "TD signature: ______________________  Date: ________")

    # Appendix
    doc.add_page_break()
    add_heading_custom(doc, "Appendix A — Daily run sheet (copy per run)", level=1)
    add_table(
        doc,
        ["Field", "Entry"],
        [
            ["Run ID", "ROH-AVI-RUN-____"],
            ["Date / location", ""],
            ["Procedure rev", "ROH-AVI-MTP-001 Rev A"],
            ["ATC / TD / GSO / PE / EGSE", ""],
            ["FSW hash", ""],
            ["GS dictionary", ""],
            ["Harness traveler", ""],
            ["Tests planned today", ""],
            ["Open anomalies carried in", ""],
            ["Pre-run Gate G0–G3", "PASS / FAIL"],
            ["Result summary", ""],
            ["New anomalies", ""],
            ["Archives hash manifest path", ""],
            ["ATC signature", ""],
        ],
        col_widths=[2.4, 4.6],
    )

    add_heading_custom(doc, "Appendix B — Go/No-Go poll card (dress rehearsal)", level=1)
    add_table(
        doc,
        ["Role", "T-30", "T-10", "T-0", "Notes"],
        [
            ["TD", "", "", "", ""],
            ["ATC", "", "", "", ""],
            ["GSO", "", "", "", ""],
            ["PE", "", "", "", ""],
            ["EGSE", "", "", "", ""],
            ["FSW", "", "", "", ""],
            ["Safety/QA", "", "", "", ""],
        ],
        col_widths=[1.4, 1.0, 1.0, 1.0, 2.6],
    )

    add_heading_custom(doc, "Appendix C — Minimum instrument list", level=1)
    for item in [
        "Programmable power supply with remote sense + current limit",
        "Current probe / shunt + oscilloscope (≥ bandwidth for inrush)",
        "Calibrated DMM",
        "EGSE breakout / inhibit / safe-load box",
        "Fault injection relays (dry contacts) as approved",
        "GS modem path (conducted or radiated with attenuators)",
        "Time source (GPSDO or verified NTP)",
        "Camera for inhibit photos",
        "Controlled storage for archives",
    ]:
        bullet(doc, item)

    add_heading_custom(doc, "Appendix D — Open items to close from source docs before execution", level=1)
    add_para(
        doc,
        "These placeholders must be replaced with numbers/names from AD-01…AD-05. "
        "Upload/attach those files to regenerate a values-filled Rev B.",
    )
    for item in [
        "[ICD-TBD] Primary bus voltage, tolerance, absolute max, inrush envelope, UVLO/OVP",
        "[ICD-TBD] Connector tables and continuity/isolation limits",
        "[ICD-TBD] Deploy/pyro pulse width and current limits for safe-load tests",
        "[SRR-TBD] Boot time limit; time sync error limit; soak durations",
        "[SRR-TBD] Mode IDs and exact mission event table with MET stamps",
        "[SRR-TBD] FDIR detection latency by fault class",
        "[AD-01] Packet loss limits, archive gap limits, cmd latency limits",
        "[AD-04] Payload rail limits, data rates, success metrics",
        "[AD-05] Confirm segment boundaries and RF vs conducted options for Rohini mock",
    ]:
        bullet(doc, item)

    add_heading_custom(doc, "Appendix E — Document provenance note", level=1)
    add_para(
        doc,
        "This Rev A was authored as a flight-critical mock-mission test plan structure mapped to the Rohini "
        "document set named by the program (GS SRR, Avionics Mission-Level SRR Draft A, ReX-3 EICD v1, "
        "Payload Design Document, Mission drawio) and to Catalyx ReX-pathfinder public context "
        "(OBC/sensors/real-time comms, EDL/parachute validation, deployable TPS development path). "
        "Electrical numeric limits and exact mode/event IDs remain intentionally marked TBD pending "
        "ingestion of the controlled source files.",
    )

    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
