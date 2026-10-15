#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# RP9_CODE_ID: C.0086

# =============================================================================
# RP9. CODE IDENTITY
#
# REPOSITORY: RP9. RH. Z0
#     RP9. RIEMANN SUBMISSION
#
# PYTHON CODE ID: K6. B
# OFFICIAL CODE TITLE: K6. EXACT BINARY PULSE INVARIANCE CHECK
#
# REPOSITORY POSITION:
# PRIMARY SUBMISSION — SUBJECT OF EXAMINATION AND REVIEW
# =============================================================================
#
"""K.6(B) exact binary pulse invariance check.

This self-contained program verifies one relation only:

    q_n = (3/4) / 2^n
    8 / q_n -> exact alternating remainders 2/3 and 1/3

All binding operations use fractions.Fraction. No floating-point value,
tolerance, geometric measurement, or external comparison is used.
"""

from datetime import datetime
from fractions import Fraction
from pathlib import Path
import json
import os
import sys
import traceback


PYTHON_CODE_ID = "K6. B"
FILE_NAME = "K6. B.py"
OFFICIAL_CODE_TITLE = "K6. EXACT BINARY PULSE INVARIANCE CHECK"
VERSION = "3.0.0"
FRAMEWORK = "RP9"
CONTROL_ID = "K6_BINARY_PULSE_T01"

# Standard local execution output directory.
OUTPUT_DIR_NAME = "2. OUTPUT"

# Standard short output filenames.
OUTPUT_DATA_FILE = "K6.B_DATA.json"
OUTPUT_REPORT_FILE = "K6.B_REPORT.md"
OUTPUT_CONTROL_FILE = "K6.B_CONTROL.log"

POSITION_COUNT = 100
PULSE_BASE = Fraction(3, 4)
CONTROL_VALUE = Fraction(8, 1)
EVEN_REMAINDER = Fraction(2, 3)
ODD_REMAINDER = Fraction(1, 3)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def fraction_record(value: Fraction) -> dict:
    return {
        "fraction": f"{value.numerator}/{value.denominator}",
        "numerator": value.numerator,
        "denominator": value.denominator,
    }


def expected_remainder(position: int) -> Fraction:
    return EVEN_REMAINDER if position % 2 == 0 else ODD_REMAINDER


def execute_control() -> dict:
    rows = []

    for position in range(POSITION_COUNT):
        q_n = PULSE_BASE / (2 ** position)
        quotient = CONTROL_VALUE / q_n
        whole_part = quotient.numerator // quotient.denominator
        remainder = quotient - whole_part
        expected = expected_remainder(position)
        position_status = "PASS" if remainder == expected else "FAIL"

        rows.append({
            "position": position,
            "q_n": fraction_record(q_n),
            "control_8_div_q_n": fraction_record(quotient),
            "whole_part": whole_part,
            "observed_remainder": fraction_record(remainder),
            "expected_remainder": fraction_record(expected),
            "status": position_status,
        })

    pass_count = sum(row["status"] == "PASS" for row in rows)
    fail_count = POSITION_COUNT - pass_count
    global_status = "PASS" if fail_count == 0 else "FAIL"
    first_deviation = next(
        (row["position"] for row in rows if row["status"] == "FAIL"),
        None,
    )

    return {
        "metadata": {
            "framework": FRAMEWORK,
            "repository": "RP9. RH. Z0",
            "repository_branch": "RP9. RIEMANN SUBMISSION",
            "python_code_id": PYTHON_CODE_ID,
            "filesystem_name": FILE_NAME,
            "official_code_title": OFFICIAL_CODE_TITLE,
            "repository_position": "PRIMARY SUBMISSION — SUBJECT OF EXAMINATION AND REVIEW",
            "version": VERSION,
            "control_id": CONTROL_ID,
            "timestamp": now_iso(),
            "arithmetic": "Exact rational arithmetic using fractions.Fraction",
        },
        "scope": {
            "first_position": 0,
            "last_position": POSITION_COUNT - 1,
            "position_count": POSITION_COUNT,
            "pulse_base": fraction_record(PULSE_BASE),
            "control_value": fraction_record(CONTROL_VALUE),
            "formula_q_n": "q_n = (3/4) / 2^n",
            "formula_control": "8 / q_n",
            "expected_even_remainder": fraction_record(EVEN_REMAINDER),
            "expected_odd_remainder": fraction_record(ODD_REMAINDER),
        },
        "positions": rows,
        "result": {
            "pass_count": pass_count,
            "fail_count": fail_count,
            "first_deviation": first_deviation,
            "global_status": global_status,
        },
    }


def build_markdown(payload: dict) -> str:
    scope = payload["scope"]
    result = payload["result"]
    lines = [
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
        f"# {OFFICIAL_CODE_TITLE}",
        "",
        f"- **Version:** {VERSION}",
        "",
        "## Function",
        "",
        "Verify, using exact rational arithmetic, that:",
        "",
        "$$",
        "q_n=\\frac{3/4}{2^n}",
        "$$",
        "",
        "followed by:",
        "",
        "$$",
        "\\frac{8}{q_n}",
        "$$",
        "",
        "produces the exact alternating remainder sequence:",
        "",
        "$$",
        "\\frac23,\\frac13,\\frac23,\\frac13,\\ldots",
        "$$",
        "",
        "## Validation boundary",
        "",
        f"- Positions: `{scope['first_position']}` through `{scope['last_position']}`",
        f"- Position count: `{scope['position_count']}`",
        "- Even positions require the exact remainder `2/3`.",
        "- Odd positions require the exact remainder `1/3`.",
        "- All binding operations use `fractions.Fraction`.",
        "- No floating-point value or tolerance participates in `PASS` or `FAIL`.",
        "- No additional K.6 function is tested or claimed.",
        "",
        "## Position results",
        "",
        "| Position | q_n | 8 / q_n | Whole part | Expected remainder | Observed remainder | Status |",
        "|---:|---:|---:|---:|---:|---:|:---:|",
    ]

    for row in payload["positions"]:
        lines.append(
            f"| {row['position']} "
            f"| {row['q_n']['fraction']} "
            f"| {row['control_8_div_q_n']['fraction']} "
            f"| {row['whole_part']} "
            f"| {row['expected_remainder']['fraction']} "
            f"| {row['observed_remainder']['fraction']} "
            f"| **{row['status']}** |"
        )

    first_deviation = (
        "NONE" if result["first_deviation"] is None
        else str(result["first_deviation"])
    )
    lines.extend([
        "",
        "## Final result",
        "",
        f"- PASS: **{result['pass_count']}**",
        f"- FAIL: **{result['fail_count']}**",
        f"- First deviation: **{first_deviation}**",
        f"- Global status: **{result['global_status']}**",
        "",
        "`GLOBAL_STATUS=PASS` means that every position within the declared domain produced its exact expected remainder.",
        "",
    ])
    return "\n".join(lines)


def write_outputs(payload: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / OUTPUT_DATA_FILE
    markdown_path = output_dir / OUTPUT_REPORT_FILE
    log_path = output_dir / OUTPUT_CONTROL_FILE

    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(build_markdown(payload), encoding="utf-8")

    result = payload["result"]
    first_deviation = (
        "NONE" if result["first_deviation"] is None
        else str(result["first_deviation"])
    )
    log_lines = [
        f"PYTHON_CODE_ID={PYTHON_CODE_ID}",
        f"OFFICIAL_CODE_TITLE={OFFICIAL_CODE_TITLE}",
        f"FILE={FILE_NAME}",
        f"VERSION={VERSION}",
        f"CONTROL_ID={CONTROL_ID}",
        f"TIMESTAMP={payload['metadata']['timestamp']}",
        f"POSITION_FIRST={payload['scope']['first_position']}",
        f"POSITION_LAST={payload['scope']['last_position']}",
        f"POSITION_COUNT={payload['scope']['position_count']}",
        f"PASS_COUNT={result['pass_count']}",
        f"FAIL_COUNT={result['fail_count']}",
        f"FIRST_DEVIATION={first_deviation}",
        f"GLOBAL_STATUS={result['global_status']}",
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")


def main() -> int:
    try:
        output_dir = Path(__file__).resolve().parent / OUTPUT_DIR_NAME
        payload = execute_control()
        write_outputs(payload, output_dir)

        result = payload["result"]
        first_deviation = (
            "NONE" if result["first_deviation"] is None
            else str(result["first_deviation"])
        )
        print(f"PYTHON CODE ID: {PYTHON_CODE_ID}")
        print(f"OFFICIAL CODE TITLE: {OFFICIAL_CODE_TITLE}")
        print(f"CONTROL: {CONTROL_ID}")
        print(f"POSITIONS: 0..{POSITION_COUNT - 1} ({POSITION_COUNT} total)")
        print(f"PASS: {result['pass_count']} | FAIL: {result['fail_count']}")
        print(f"FIRST DEVIATION: {first_deviation}")
        print(f"GLOBAL STATUS: {result['global_status']}")
        print(f"OUTPUT DIRECTORY: {output_dir}")
        return 0 if result["global_status"] == "PASS" else 1
    except Exception:
        print("EXECUTION ERROR", file=sys.stderr)
        traceback.print_exc()
        return 2
    finally:
        if os.name == "nt" and sys.stdin.isatty():
            try:
                input("Press Enter to close...")
            except EOFError:
                pass


if __name__ == "__main__":
    sys.exit(main())
