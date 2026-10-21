#!/usr/bin/env python3
# RP9_CODE_ID: C.0096
# =============================================================================
# RP9. CODE IDENTITY
#
# REPOSITORY: RP9. RH. Z0
#     RP9. RIEMANN SUBMISSION
#
# PYTHON CODE ID: K8. B
# OFFICIAL CODE TITLE: K8. P.B.F. BINARY-SCALE INVARIANCE VALIDATOR
#
# REPOSITORY POSITION:
# PRIMARY SUBMISSION — SUBJECT OF EXAMINATION AND REVIEW
# =============================================================================
"""
P.B.F. BINARY-SCALE INVARIANCE VALIDATOR
========================================

Version: 2.1.0

FUNCTION
--------
Tests whether the following relational identities remain exact
through binary scale expansion:

    1/2  ->  2/4  ->  4/8  ->  8/16  -> ...
    3/4  ->  6/8  -> 12/16 -> 24/32  -> ...
    1/4  ->  2/8  ->  4/16 ->  8/32  -> ...

The validator uses exact rational arithmetic through fractions.Fraction.

No floating-point tolerance is used.

PRIMARY TESTS
-------------
1. HALF INVARIANCE
2. THREE-QUARTER INVARIANCE
3. ONE-QUARTER INVARIANCE
4. COMPLEMENT RELATION:
       3/4 + 1/4 = 1
5. BINARY SCALE DOUBLING
6. RELATIONAL CONSISTENCY ACROSS ALL TESTED FAMILIES

OUTPUTS
-------
Creates:

    2. OUTPUT/

containing:

    K8.B_CONTROL.txt
    K8.B_DATA.json
    K8.B_REPORT.md
"""

from __future__ import annotations

import json
from datetime import datetime
from fractions import Fraction
from pathlib import Path


PYTHON_CODE_ID = "K8. B"
FILE_NAME = "K8. B.py"
OFFICIAL_CODE_TITLE = "K8. P.B.F. BINARY-SCALE INVARIANCE VALIDATOR"
VERSION = "2.1.0"

OUTPUT_DIR_NAME = "2. OUTPUT"
DATA_FILE = "K8.B_DATA.json"
REPORT_FILE = "K8.B_REPORT.md"
CONTROL_FILE = "K8.B_CONTROL.txt"

# Number of binary scale levels.
# Level 0 begins at denominator 4 for the 3/4 : 1/4 relation.
LEVEL_COUNT = 8


def base_dir() -> Path:
    """Return the validator's own directory, independent of terminal CWD."""
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def expanded_fraction(base_num: int, base_den: int, scale: int) -> tuple[int, int]:
    """
    Expand a fraction without reducing it.

    Example:
        3/4, scale=1 -> 6/8
        3/4, scale=2 -> 12/16
    """
    factor = 2 ** scale
    return base_num * factor, base_den * factor


def build_level(level: int) -> dict:
    """
    Build one exact binary scale level.
    """

    factor = 2 ** level

    # ---------------------------------------------------------
    # HALF FAMILY
    # 1/2 -> 2/4 -> 4/8 -> 8/16 ...
    # ---------------------------------------------------------

    half_num = factor
    half_den = 2 * factor
    half_fraction = Fraction(half_num, half_den)

    # ---------------------------------------------------------
    # THREE-QUARTER FAMILY
    # 3/4 -> 6/8 -> 12/16 -> 24/32 ...
    # ---------------------------------------------------------

    three_quarter_num, three_quarter_den = expanded_fraction(3, 4, level)
    three_quarter_fraction = Fraction(three_quarter_num, three_quarter_den)

    # ---------------------------------------------------------
    # ONE-QUARTER FAMILY
    # 1/4 -> 2/8 -> 4/16 -> 8/32 ...
    # ---------------------------------------------------------

    one_quarter_num, one_quarter_den = expanded_fraction(1, 4, level)
    one_quarter_fraction = Fraction(one_quarter_num, one_quarter_den)

    # ---------------------------------------------------------
    # EXACT TESTS
    # ---------------------------------------------------------

    half_invariant = half_fraction == Fraction(1, 2)
    three_quarter_invariant = three_quarter_fraction == Fraction(3, 4)
    one_quarter_invariant = one_quarter_fraction == Fraction(1, 4)

    complement_sum = three_quarter_fraction + one_quarter_fraction
    complement_relation = complement_sum == Fraction(1, 1)

    same_denominator = three_quarter_den == one_quarter_den

    binary_denominator = three_quarter_den == 4 * (2 ** level)

    three_to_one_ratio = Fraction(three_quarter_num, one_quarter_num)
    three_to_one_ratio_pass = three_to_one_ratio == Fraction(3, 1)

    # Full binary frame:
    #
    # three-quarter + one-quarter
    # 3/4   + 1/4 = 1
    #
    full_frame_num = three_quarter_num + one_quarter_num
    full_frame_den = three_quarter_den

    full_frame_pass = full_frame_num == full_frame_den

    status = all(
        [
            half_invariant,
            three_quarter_invariant,
            one_quarter_invariant,
            complement_relation,
            same_denominator,
            binary_denominator,
            three_to_one_ratio_pass,
            full_frame_pass,
        ]
    )

    return {
        "level": level,
        "binary_factor": factor,

        "half_expression": f"{half_num}/{half_den}",
        "half_exact": fraction_text(half_fraction),

        "three_quarter_expression": f"{three_quarter_num}/{three_quarter_den}",
        "three_quarter_exact": fraction_text(three_quarter_fraction),

        "one_quarter_expression": f"{one_quarter_num}/{one_quarter_den}",
        "one_quarter_exact": fraction_text(one_quarter_fraction),

        "full_frame_expression": f"{full_frame_num}/{full_frame_den}",

        "half_invariant": half_invariant,
        "three_quarter_invariant": three_quarter_invariant,
        "one_quarter_invariant": one_quarter_invariant,
        "complement_relation": complement_relation,
        "same_denominator": same_denominator,
        "binary_denominator": binary_denominator,
        "three_to_one_ratio": fraction_text(three_to_one_ratio),
        "three_to_one_ratio_pass": three_to_one_ratio_pass,
        "full_frame_pass": full_frame_pass,

        "status": "PASS" if status else "FAIL",
    }


def validate_transition(previous: dict, current: dict) -> dict:
    """
    Verify exact x2 binary scale progression between adjacent levels.
    """

    prev_half_num, prev_half_den = map(
        int, previous["half_expression"].split("/")
    )
    curr_half_num, curr_half_den = map(
        int, current["half_expression"].split("/")
    )

    prev_three_quarter_num, prev_three_quarter_den = map(
        int, previous["three_quarter_expression"].split("/")
    )
    curr_three_quarter_num, curr_three_quarter_den = map(
        int, current["three_quarter_expression"].split("/")
    )

    prev_one_quarter_num, prev_one_quarter_den = map(
        int, previous["one_quarter_expression"].split("/")
    )
    curr_one_quarter_num, curr_one_quarter_den = map(
        int, current["one_quarter_expression"].split("/")
    )

    half_num_x2 = curr_half_num == prev_half_num * 2
    half_den_x2 = curr_half_den == prev_half_den * 2

    three_quarter_num_x2 = curr_three_quarter_num == prev_three_quarter_num * 2
    three_quarter_den_x2 = curr_three_quarter_den == prev_three_quarter_den * 2

    one_quarter_num_x2 = curr_one_quarter_num == prev_one_quarter_num * 2
    one_quarter_den_x2 = curr_one_quarter_den == prev_one_quarter_den * 2

    status = all(
        [
            half_num_x2,
            half_den_x2,
            three_quarter_num_x2,
            three_quarter_den_x2,
            one_quarter_num_x2,
            one_quarter_den_x2,
        ]
    )

    return {
        "from_level": previous["level"],
        "to_level": current["level"],
        "half_numerator_x2": half_num_x2,
        "half_denominator_x2": half_den_x2,
        "three_quarter_numerator_x2": three_quarter_num_x2,
        "three_quarter_denominator_x2": three_quarter_den_x2,
        "one_quarter_numerator_x2": one_quarter_num_x2,
        "one_quarter_denominator_x2": one_quarter_den_x2,
        "status": "PASS" if status else "FAIL",
    }


def write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_report(
    levels: list[dict],
    transitions: list[dict],
    global_status: str,
) -> str:

    lines = []

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
        "# P.B.F. BINARY-SCALE INVARIANCE",
        "",
        f"**Version:** `{VERSION}`",
        "",
        f"**Global Status:** **{global_status}**",
        "",
    ])

    lines.append("---")
    lines.append("")
    lines.append("## PRIMARY RELATION")
    lines.append("")

    lines.append("```text")
    lines.append("BINARY SCALE")
    lines.append("↓")
    lines.append("4 → 8 → 16 → 32 → ...")
    lines.append("")
    lines.append("THREE-QUARTER RELATION")
    lines.append("↓")
    lines.append("3/4 → 6/8 → 12/16 → 24/32 → ...")
    lines.append("")
    lines.append("ONE-QUARTER RELATION")
    lines.append("↓")
    lines.append("1/4 → 2/8 → 4/16 → 8/32 → ...")
    lines.append("")
    lines.append("THREE-QUARTER + ONE-QUARTER")
    lines.append("=")
    lines.append("FULL FRAME")
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## EXECUTED SCALE TABLE")
    lines.append("")
    lines.append("| Level | Half | Three-quarter | One-quarter | Full Frame | Status |")
    lines.append("|---:|---:|---:|---:|---:|:---:|")

    for row in levels:
        lines.append(
            f"| {row['level']} "
            f"| `{row['half_expression']}` "
            f"| `{row['three_quarter_expression']}` "
            f"| `{row['one_quarter_expression']}` "
            f"| `{row['full_frame_expression']}` "
            f"| **{row['status']}** |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## EXACT INVARIANTS")
    lines.append("")

    lines.append("```text")
    lines.append("1/2 = 2/4 = 4/8 = 8/16 = ...")
    lines.append("")
    lines.append("3/4 = 6/8 = 12/16 = 24/32 = ...")
    lines.append("")
    lines.append("1/4 = 2/8 = 4/16 = 8/32 = ...")
    lines.append("")
    lines.append("3/4 + 1/4 = 1")
    lines.append("6/8 + 2/8 = 1")
    lines.append("12/16 + 4/16 = 1")
    lines.append("24/32 + 8/32 = 1")
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## SCALE TRANSITIONS")
    lines.append("")
    lines.append("| From | To | Half x2 | Three-quarter x2 | One-quarter x2 | Status |")
    lines.append("|---:|---:|:---:|:---:|:---:|:---:|")

    for row in transitions:
        half_pass = row["half_numerator_x2"] and row["half_denominator_x2"]
        three_quarter_pass = row["three_quarter_numerator_x2"] and row["three_quarter_denominator_x2"]
        one_quarter_pass = row["one_quarter_numerator_x2"] and row["one_quarter_denominator_x2"]
        lines.append(
            f"| {row['from_level']} | {row['to_level']} "
            f"| **{'PASS' if half_pass else 'FAIL'}** "
            f"| **{'PASS' if three_quarter_pass else 'FAIL'}** "
            f"| **{'PASS' if one_quarter_pass else 'FAIL'}** "
            f"| **{row['status']}** |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## OPERATIONAL COMPRESSION")
    lines.append("")

    lines.append("```text")
    lines.append("BINARY FRAME")
    lines.append("4/4")
    lines.append("│")
    lines.append("├── THREE-QUARTER")
    lines.append("│   3/4")
    lines.append("│")
    lines.append("└── ONE-QUARTER")
    lines.append("    1/4")
    lines.append("")
    lines.append("        ↓ x2")
    lines.append("")
    lines.append("BINARY FRAME")
    lines.append("8/8")
    lines.append("│")
    lines.append("├── THREE-QUARTER")
    lines.append("│   6/8")
    lines.append("│")
    lines.append("└── ONE-QUARTER")
    lines.append("    2/8")
    lines.append("")
    lines.append("        ↓ x2")
    lines.append("")
    lines.append("BINARY FRAME")
    lines.append("16/16")
    lines.append("│")
    lines.append("├── THREE-QUARTER")
    lines.append("│   12/16")
    lines.append("│")
    lines.append("└── ONE-QUARTER")
    lines.append("    4/16")
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## RESULT")
    lines.append("")

    if global_status == "PASS":
        lines.append(
            "> **The tested relational identities remain exactly invariant "
            "under repeated binary scale doubling.**"
        )
        lines.append("")
        lines.append(
            "> **The representation changes while the ratios "
            "`1/2`, `3/4`, and `1/4` remain exact.**"
        )
    else:
        lines.append(
            "> **At least one tested relational identity failed "
            "during binary scale expansion.**"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## VALIDATION BOUNDARY")
    lines.append("")
    lines.append(
        "This validator establishes exact arithmetic invariance of the defined "
        "fraction families under binary scale doubling."
    )
    lines.append("")
    lines.append(
        "It does not independently establish that a particular numerical base "
        "is generated by these relations."
    )

    return "\n".join(lines) + "\n"


def main() -> int:

    timestamp = datetime.now().astimezone()

    root = base_dir()
    output_dir = root / OUTPUT_DIR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 86)
    print("P.B.F. BINARY-SCALE INVARIANCE VALIDATOR")
    print("=" * 86)

    levels = [build_level(i) for i in range(LEVEL_COUNT)]

    transitions = [
        validate_transition(levels[i - 1], levels[i])
        for i in range(1, len(levels))
    ]

    level_pass = all(row["status"] == "PASS" for row in levels)
    transition_pass = all(row["status"] == "PASS" for row in transitions)

    global_status = "PASS" if level_pass and transition_pass else "FAIL"

    for row in levels:
        print(
            f"LEVEL {row['level']:02d} | "
            f"HALF {row['half_expression']:>8} | "
            f"THREE-QUARTER {row['three_quarter_expression']:>8} | "
            f"ONE-QUARTER {row['one_quarter_expression']:>8} | "
            f"{row['status']}"
        )

    print("-" * 86)
    print(f"GLOBAL STATUS: {global_status}")
    print("=" * 86)

    payload = {
        "repository": "RP9. RH. Z0",
        "repository_branch": "RP9. RIEMANN SUBMISSION",
        "python_code_id": PYTHON_CODE_ID,
        "filesystem_name": FILE_NAME,
        "official_code_title": OFFICIAL_CODE_TITLE,
        "repository_position": "PRIMARY SUBMISSION — SUBJECT OF EXAMINATION AND REVIEW",
        "version": VERSION,
        "timestamp": timestamp.isoformat(),
        "execution_root": str(root),
        "output_directory": str(output_dir),
        "level_count": LEVEL_COUNT,
        "global_status": global_status,
        "levels": levels,
        "transitions": transitions,
    }

    write_json(output_dir / DATA_FILE, payload)

    report = build_report(levels, transitions, global_status)
    (output_dir / REPORT_FILE).write_text(
        report,
        encoding="utf-8",
    )

    control_log = [
        "P.B.F. BINARY-SCALE INVARIANCE — CONTROL LOG",
        "=" * 78,
        f"Python Code ID     : {PYTHON_CODE_ID}",
        f"Official Code Title: {OFFICIAL_CODE_TITLE}",
        f"File               : {FILE_NAME}",
        f"Version            : {VERSION}",
        f"Timestamp      : {timestamp.isoformat()}",
        f"Levels tested  : {len(levels)}",
        f"Transitions    : {len(transitions)}",
        f"Level PASS     : {sum(x['status'] == 'PASS' for x in levels)}",
        f"Transition PASS: {sum(x['status'] == 'PASS' for x in transitions)}",
        f"Global Status  : {global_status}",
        "",
        "PRIMARY IDENTITIES",
        "-" * 78,
        "1/2 family     : exact",
        "3/4 family     : exact",
        "1/4 family     : exact",
        "Complement     : three-quarter + one-quarter = 1",
        "Scale operator : x2",
        "",
    ]

    (output_dir / CONTROL_FILE).write_text(
        "\n".join(control_log) + "\n",
        encoding="utf-8",
    )

    print()
    print(f"OUTPUT DIRECTORY: {output_dir}")

    return 0 if global_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
