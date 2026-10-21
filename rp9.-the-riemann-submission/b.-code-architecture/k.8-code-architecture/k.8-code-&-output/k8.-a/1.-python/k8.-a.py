#!/usr/bin/env python3
# RP9_CODE_ID: C.0095
# =============================================================================
# RP9. CODE IDENTITY
#
# REPOSITORY: RP9. RH. Z0
#     RP9. RIEMANN SUBMISSION
#
# PYTHON CODE ID: K8. A
# OFFICIAL CODE TITLE: K8. P.B.F. ↔ BINARY PULSE OPERATOR IDENTITY VALIDATOR
#
# REPOSITORY POSITION:
# PRIMARY SUBMISSION — SUBJECT OF EXAMINATION AND REVIEW
# =============================================================================
"""
P.B.F. ↔ BINARY PULSE OPERATOR IDENTITY VALIDATOR
=================================================

Version: 2.0.0

PURPOSE
-------
Test whether the operational core described as:

    P.B.F.

and the operational core described as:

    BINARY PULSE

are functionally identical under two different representations.

The validator separates three layers:

    1. COMMON SEED / CANDIDATE FIELD
    2. OPERATOR EXECUTION
    3. STATE CLASSIFICATION

LOCK CONDITION
--------------
The identity is considered locked only if both independent implementations produce:

    - the same candidate field
    - the same projected hits
    - the same closure positions
    - the same reproduced positions
    - the same state classification for every tested position
    - the same recursive operator sequence
    - zero first deviation

SOURCE FUNCTIONAL BASIS
-----------------------
P.B.F. side:
    fixed field
    -> primary positions 2, 3
    -> recurrent two-direction positions around 6-step centers
    -> sequential addition 2p, 3p, 4p, ...
    -> coincidence / no coincidence
    -> REPRODUCED / CLOSURE

Binary Pulse side:
    same six-step seed
    -> recurrent 6-step organization
    -> two-direction projection
    -> same repeated translation / pulse propagation
    -> hit / no-hit switching
    -> CLOSED / REPRODUCED state

The two implementations intentionally use different function names and internal
control flow so that equality is not produced by reusing the same function.

OUTPUT
------
Creates:

    2. OUTPUT/

containing:

    K8.A_CONTROL.txt
    K8.A_DATA.json
    K8.A_TRACE.json
    K8.A_REPORT.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List


PYTHON_CODE_ID = "K8. A"
FILE_NAME = "K8. A.py"
OFFICIAL_CODE_TITLE = "K8. P.B.F. ↔ BINARY PULSE OPERATOR IDENTITY VALIDATOR"
VERSION = "2.0.0"

DEFAULT_LIMIT = 1_000_000

OUTPUT_DIR_NAME = "2. OUTPUT"
DATA_FILE = "K8.A_DATA.json"
TRACE_FILE = "K8.A_TRACE.json"
CONTROL_FILE = "K8.A_CONTROL.txt"
REPORT_FILE = "K8.A_REPORT.md"

CLOSURE = 1
REPRODUCED = 2


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def base_dir() -> Path:
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_text(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ============================================================================
# P.B.F. IMPLEMENTATION
# ============================================================================

def pbf_candidate_field(limit: int) -> bytearray:
    """
    P.B.F. locked observation field.

    Primary positions:
        2, 3

    Recurrent directional positions:
        center - 1
        center + 1

    where:
        center = 6, 12, 18, 24, ...

    No modulo classification is used.
    """
    field = bytearray(limit + 1)

    if limit >= 2:
        field[2] = 1
    if limit >= 3:
        field[3] = 1

    center = 6
    while center <= limit + 1:
        left = center - 1
        right = center + 1

        if 5 <= left <= limit:
            field[left] = 1

        if 5 <= right <= limit:
            field[right] = 1

        center += 6

    return field


def pbf_project_reference(
    reference: int,
    limit: int,
    field: bytearray,
    hit: bytearray,
) -> None:
    """
    Sequential genealogy:
        2p, 3p, 4p, ...
    """
    x = reference + reference

    while x <= limit:
        if field[x]:
            hit[x] = 1
        x += reference


def run_pbf(limit: int) -> Dict[str, object]:
    field = pbf_candidate_field(limit)
    hit = bytearray(limit + 1)
    state = bytearray(limit + 1)

    references: List[int] = []

    for p in (2, 3):
        if p <= limit and field[p]:
            references.append(p)
            state[p] = CLOSURE
            pbf_project_reference(p, limit, field, hit)

    position = 5

    while position <= limit:
        if field[position]:
            if hit[position]:
                state[position] = REPRODUCED
            else:
                state[position] = CLOSURE
                references.append(position)
                pbf_project_reference(position, limit, field, hit)

        position += 1

    return {
        "field": field,
        "hit": hit,
        "state": state,
        "references": references,
        "observation_count": int(sum(field)),
        "closure_count": len(references),
        "reproduced_count": int(sum(field)) - len(references),
    }


# ============================================================================
# BINARY PULSE IMPLEMENTATION
# ============================================================================

def binary_pulse_field(limit: int) -> bytearray:
    """
    Independent implementation of the same stated six-step field.

    The field is built as a 6-step pulse lattice.

    Each pulse center creates two directional observation positions:

        left  = center - 1
        right = center + 1

    with primary establishing positions 2 and 3.
    """
    pulse = bytearray(limit + 1)

    if limit >= 2:
        pulse[2] = 1

    if limit >= 3:
        pulse[3] = 1

    cycle = 1

    while True:
        center = cycle * 6
        left = center - 1
        right = center + 1

        if left > limit and right > limit:
            break

        if 5 <= left <= limit:
            pulse[left] = 1

        if 5 <= right <= limit:
            pulse[right] = 1

        cycle += 1

    return pulse


def binary_pulse_emit(
    origin: int,
    limit: int,
    pulse_field: bytearray,
    switched: bytearray,
) -> None:
    """
    Binary Pulse propagation.

    Start from one established origin and repeat the same directed span:

        origin + origin
        + origin
        + origin
        ...

    Only positions inside the pulse field can switch to HIT.
    """
    step = origin
    endpoint = origin * 2

    while endpoint <= limit:
        if pulse_field[endpoint]:
            switched[endpoint] = 1

        endpoint += step


def run_binary_pulse(limit: int) -> Dict[str, object]:
    field = binary_pulse_field(limit)

    switched = bytearray(limit + 1)
    state = bytearray(limit + 1)

    closures: List[int] = []

    establishing = [2, 3]

    for origin in establishing:
        if origin <= limit and field[origin]:
            closures.append(origin)
            state[origin] = CLOSURE
            binary_pulse_emit(
                origin,
                limit,
                field,
                switched,
            )

    cursor = 5

    while cursor <= limit:
        if not field[cursor]:
            cursor += 1
            continue

        pulse_is_present = bool(switched[cursor])

        if pulse_is_present:
            state[cursor] = REPRODUCED

        else:
            state[cursor] = CLOSURE
            closures.append(cursor)

            binary_pulse_emit(
                cursor,
                limit,
                field,
                switched,
            )

        cursor += 1

    observation_count = int(sum(field))

    return {
        "field": field,
        "hit": switched,
        "state": state,
        "references": closures,
        "observation_count": observation_count,
        "closure_count": len(closures),
        "reproduced_count": observation_count - len(closures),
    }


# ============================================================================
# IDENTITY COMPARISON
# ============================================================================

def first_difference(a: bytearray, b: bytearray) -> int | None:
    limit = min(len(a), len(b))

    for i in range(limit):
        if a[i] != b[i]:
            return i

    if len(a) != len(b):
        return limit

    return None


def list_first_difference(a: List[int], b: List[int]) -> Dict[str, object] | None:
    limit = min(len(a), len(b))

    for i in range(limit):
        if a[i] != b[i]:
            return {
                "index": i,
                "pbf_value": a[i],
                "binary_pulse_value": b[i],
            }

    if len(a) != len(b):
        return {
            "index": limit,
            "pbf_value": a[limit] if limit < len(a) else None,
            "binary_pulse_value": b[limit] if limit < len(b) else None,
        }

    return None


def compare_implementations(
    pbf: Dict[str, object],
    pulse: Dict[str, object],
) -> Dict[str, object]:

    field_diff = first_difference(
        pbf["field"],
        pulse["field"],
    )

    hit_diff = first_difference(
        pbf["hit"],
        pulse["hit"],
    )

    state_diff = first_difference(
        pbf["state"],
        pulse["state"],
    )

    reference_diff = list_first_difference(
        pbf["references"],
        pulse["references"],
    )

    checks = {
        "candidate_field_equal": field_diff is None,
        "projected_hits_equal": hit_diff is None,
        "state_classification_equal": state_diff is None,
        "closure_sequence_equal": reference_diff is None,
        "observation_count_equal":
            pbf["observation_count"] == pulse["observation_count"],
        "closure_count_equal":
            pbf["closure_count"] == pulse["closure_count"],
        "reproduced_count_equal":
            pbf["reproduced_count"] == pulse["reproduced_count"],
    }

    global_identity = all(checks.values())

    return {
        "checks": checks,
        "first_deviation": {
            "candidate_field": field_diff,
            "projected_hits": hit_diff,
            "state_classification": state_diff,
            "closure_sequence": reference_diff,
        },
        "global_identity": global_identity,
        "status": "PASS" if global_identity else "FAIL",
    }


# ============================================================================
# TRACE / REPORT
# ============================================================================

def build_trace(
    limit: int,
    pbf: Dict[str, object],
    pulse: Dict[str, object],
    identity: Dict[str, object],
) -> List[Dict[str, object]]:

    return [
        {
            "step": 1,
            "operation": "pbf_generation",
            "result": {
                "observation_count": pbf["observation_count"],
                "closure_count": pbf["closure_count"],
                "reproduced_count": pbf["reproduced_count"],
            },
            "status": "PASS",
        },
        {
            "step": 2,
            "operation": "binary_pulse_generation",
            "result": {
                "observation_count": pulse["observation_count"],
                "closure_count": pulse["closure_count"],
                "reproduced_count": pulse["reproduced_count"],
            },
            "status": "PASS",
        },
        {
            "step": 3,
            "operation": "operator_identity_comparison",
            "result": identity,
            "status": identity["status"],
        },
        {
            "step": 4,
            "operation": "k8_t01_terminal_lock",
            "result": {
                "operator_identity_locked":
                    identity["global_identity"],
                "terminal_lock": identity["global_identity"],
            },
            "status": identity["status"],
        },
    ]


def build_report(
    limit: int,
    pbf: Dict[str, object],
    pulse: Dict[str, object],
    identity: Dict[str, object],
) -> str:

    terminal_lock = identity["global_identity"]

    lines: List[str] = []

    lines.extend([
        "> [!info] **RP9. CODE IDENTITY**",
        "> ",
        "> - ### REPOSITORY: _**RP9. RH. Z0**_",
        ">     ",
        ">     - #### **RP9. RIEMANN SUBMISSION**",
        ">",
        ">---",
        f"> - PYTHON CODE 🆔: **{PYTHON_CODE_ID}**",
        "> ",
        f"> - OFFICIAL CODE TITLE: **{OFFICIAL_CODE_TITLE}**",
        "> ",
        ">---",
        ">> - #### *REPOSITORY POSITION:*  ",
        ">> ",
        ">>    🔍 **_PRIMARY SUBMISSION — SUBJECT OF EXAMINATION AND REVIEW_**",
        "",
        "# P.B.F. ↔ BINARY PULSE OPERATOR IDENTITY VALIDATION",
        "",
        f"**Version:** `{VERSION}`",
        "",
        f"**Limit:** `{limit:,}`",
        "",
    ])

    lines.append("---")
    lines.append("")
    lines.append("## FUNCTIONAL TEST")
    lines.append("")
    lines.append("```text")
    lines.append("P.B.F.")
    lines.append("│")
    lines.append("├── fixed six-step field")
    lines.append("├── sequential addition")
    lines.append("├── coincidence detection")
    lines.append("└── CLOSURE / REPRODUCED")
    lines.append("")
    lines.append("            ?")
    lines.append("")
    lines.append("BINARY PULSE")
    lines.append("│")
    lines.append("├── same six-step field")
    lines.append("├── repeated pulse translation")
    lines.append("├── hit / no-hit switching")
    lines.append("└── CLOSURE / REPRODUCED")
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## OPERATOR IDENTITY")
    lines.append("")
    lines.append("| Check | Result |")
    lines.append("|---|:---:|")

    for name, passed in identity["checks"].items():
        lines.append(
            f"| `{name}` | **{'PASS' if passed else 'FAIL'}** |"
        )

    lines.append("")
    lines.append(
        f"**OPERATOR IDENTITY STATUS: {identity['status']}**"
    )
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## STATE COUNTS")
    lines.append("")
    lines.append("| Implementation | Observation | Closure | Reproduced |")
    lines.append("|---|---:|---:|---:|")
    lines.append(
        f"| P.B.F. | {pbf['observation_count']:,} | "
        f"{pbf['closure_count']:,} | "
        f"{pbf['reproduced_count']:,} |"
    )
    lines.append(
        f"| Binary Pulse | {pulse['observation_count']:,} | "
        f"{pulse['closure_count']:,} | "
        f"{pulse['reproduced_count']:,} |"
    )
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## FIRST DEVIATION")
    lines.append("")

    deviation = identity["first_deviation"]

    if all(value is None for value in deviation.values()):
        lines.append("**NONE**")
    else:
        lines.append("```json")
        lines.append(
            json.dumps(
                deviation,
                indent=2,
                ensure_ascii=False,
            )
        )
        lines.append("```")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## LOCK RESULT")
    lines.append("")

    lines.append("```text")
    lines.append("P.B.F.")
    lines.append("        ╲")
    lines.append("         ╲")
    lines.append("          SAME OPERATOR")
    lines.append("         ╱")
    lines.append("        ╱")
    lines.append("BINARY PULSE")
    lines.append("        │")
    lines.append("        ▼")
    lines.append("CLOSURE / REPRODUCED")
    lines.append("```")
    lines.append("")

    if terminal_lock:
        lines.append(
            "> **K8-T01 OPERATOR IDENTITY LOCK: PASS**"
        )
        lines.append("")
        lines.append(
            "> The independently implemented P.B.F. and Binary Pulse "
            "operators produce identical candidate fields, identical "
            "projection states, identical closure/reproduced classifications "
            "and identical closure sequences across the complete tested domain."
        )
    else:
        lines.append(
            "> **K8-T01 OPERATOR IDENTITY LOCK: FAIL**"
        )
        lines.append("")
        lines.append(
            "> At least one operator-identity condition deviated."
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## VALIDATION BOUNDARY")
    lines.append("")
    lines.append(
        "The operator identity result applies to the complete executed domain."
    )
    lines.append("")
    lines.append(
        "The test does not establish operator identity by shared code reuse: "
        "the two execution paths are implemented independently."
    )

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=(
            "Maximum numerical position to execute. "
            f"Default: {DEFAULT_LIMIT:,}"
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    limit = int(args.limit)

    if limit < 10:
        raise ValueError("limit must be >= 10")

    root = base_dir()
    output_dir = root / OUTPUT_DIR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = now_iso()

    print("=" * 92)
    print("P.B.F. ↔ BINARY PULSE OPERATOR IDENTITY VALIDATOR")
    print("=" * 92)
    print(f"LIMIT: {limit:,}")
    print()

    print("[1/3] Running independent P.B.F. implementation...")
    pbf = run_pbf(limit)

    print("[2/3] Running independent Binary Pulse implementation...")
    pulse = run_binary_pulse(limit)

    print("[3/3] Comparing operator outputs...")
    identity = compare_implementations(
        pbf,
        pulse,
    )

    terminal_lock = identity["global_identity"]

    payload = {
        "metadata": {
            "repository": "RP9. RH. Z0",
            "repository_branch": "RP9. RIEMANN SUBMISSION",
            "python_code_id": PYTHON_CODE_ID,
            "filesystem_name": FILE_NAME,
            "official_code_title": OFFICIAL_CODE_TITLE,
            "repository_position": "PRIMARY SUBMISSION — SUBJECT OF EXAMINATION AND REVIEW",
            "version": VERSION,
            "timestamp": timestamp,
            "python_version": sys.version,
            "limit": limit,
        },
        "pbf": {
            "observation_count": pbf["observation_count"],
            "closure_count": pbf["closure_count"],
            "reproduced_count": pbf["reproduced_count"],
        },
        "binary_pulse": {
            "observation_count": pulse["observation_count"],
            "closure_count": pulse["closure_count"],
            "reproduced_count": pulse["reproduced_count"],
        },
        "operator_identity": identity,
        "summary": {
            "operator_identity_locked":
                identity["global_identity"],
            "k8_t01_terminal_lock":
                terminal_lock,
            "global_status":
                "PASS" if terminal_lock else "FAIL",
        },
    }

    trace = build_trace(
        limit,
        pbf,
        pulse,
        identity,
    )

    report = build_report(
        limit,
        pbf,
        pulse,
        identity,
    )

    control_lines = [
        "P.B.F. ↔ BINARY PULSE OPERATOR IDENTITY — CONTROL LOG",
        "=" * 84,
        f"Python Code ID          : {PYTHON_CODE_ID}",
        f"Official Code Title     : {OFFICIAL_CODE_TITLE}",
        f"File                    : {FILE_NAME}",
        f"Version                 : {VERSION}",
        f"Timestamp               : {timestamp}",
        f"Limit                   : {limit:,}",
        "",
        "P.B.F.",
        "-" * 84,
        f"Observation positions   : {pbf['observation_count']:,}",
        f"Closures                : {pbf['closure_count']:,}",
        f"Reproduced              : {pbf['reproduced_count']:,}",
        "",
        "BINARY PULSE",
        "-" * 84,
        f"Observation positions   : {pulse['observation_count']:,}",
        f"Closures                : {pulse['closure_count']:,}",
        f"Reproduced              : {pulse['reproduced_count']:,}",
        "",
        "OPERATOR IDENTITY",
        "-" * 84,
    ]

    for key, passed in identity["checks"].items():
        control_lines.append(
            f"{key:<40}: {'PASS' if passed else 'FAIL'}"
        )

    control_lines.extend(
        [
            "",
            f"First deviation         : "
            f"{'NONE' if all(v is None for v in identity['first_deviation'].values()) else identity['first_deviation']}",
            f"Operator identity       : {identity['status']}",
            "",
            "FINAL",
            "-" * 84,
            f"K8-T01 OPERATOR IDENTITY LOCK: {'PASS' if terminal_lock else 'FAIL'}",
        ]
    )

    write_json(
        output_dir / DATA_FILE,
        payload,
    )

    write_json(
        output_dir / TRACE_FILE,
        trace,
    )

    write_text(
        output_dir / CONTROL_FILE,
        control_lines,
    )

    (
        output_dir / REPORT_FILE
    ).write_text(
        report,
        encoding="utf-8",
    )

    print()
    print("-" * 92)
    print(f"OPERATOR IDENTITY : {identity['status']}")
    print(
        "K8-T01 STATUS     : "
        f"{'PASS' if terminal_lock else 'FAIL'}"
    )
    print("-" * 92)
    print(f"OUTPUT DIRECTORY  : {output_dir}")
    print("=" * 92)

    return 0 if terminal_lock else 1


if __name__ == "__main__":
    raise SystemExit(main())
