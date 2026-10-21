#!/usr/bin/env python3
# RP9_CODE_ID: C.0097
# =============================================================================
# RP9. CODE IDENTITY
#
# REPOSITORY: RP9. RH. Z0
#     RP9. RIEMANN SUBMISSION
#
# PYTHON CODE ID: K8. C
# OFFICIAL CODE TITLE: K8. P.B.F. BINARY STRUCTURE → BASE 10 PROJECTION LOCK VALIDATOR
#
# REPOSITORY POSITION:
# PRIMARY SUBMISSION — SUBJECT OF EXAMINATION AND REVIEW
# =============================================================================
"""
P.B.F. BINARY STRUCTURE -> BASE 10 PROJECTION LOCK VALIDATOR
============================================================

Version: 2.0.0

PURPOSE
-------
Test the final projection boundary:

    BINARY / RELATIONAL STRUCTURE
            ↓
       PROJECTION ONLY
            ↓
      BASE 10 REPRESENTATION

The validator does NOT use Base 10 to generate the relational state.

It first generates the exact relational families from binary scale expansion:

    1/2
    3/4 ↔ 1/4
    1/8

through repeated x2 scaling.

Only AFTER each exact Fraction state has been generated is it projected into
Base 10.

The Base 10 representation is then decoded back to an exact Fraction.

LOCK CONDITION
--------------
PASS requires all of the following:

1. Binary generation occurs before Base 10 projection.
2. The exact rational state is unchanged by projection.
3. Base 10 -> Fraction reconstruction returns the original state exactly.
4. Equivalent binary-scale representations map to the same Base 10 value.
5. The complement relation remains exact:
       active + lock = full frame
6. No new relational state is introduced by Base 10 encoding.
7. 1/4 and 1/8 are represented exactly as downstream decimal projections.

No floating-point arithmetic is used.
No tolerance is used.

OUTPUT
------
Creates:

    2. OUTPUT/

containing:

    K8.C_CONTROL.txt
    K8.C_DATA.json
    K8.C_REPORT.md
"""

from __future__ import annotations

import json
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple


PYTHON_CODE_ID = "K8. C"
FILE_NAME = "K8. C.py"
OFFICIAL_CODE_TITLE = "K8. P.B.F. BINARY STRUCTURE → BASE 10 PROJECTION LOCK VALIDATOR"
VERSION = "2.0.0"

OUTPUT_DIR_NAME = "2. OUTPUT"
DATA_FILE = "K8.C_DATA.json"
REPORT_FILE = "K8.C_REPORT.md"
CONTROL_FILE = "K8.C_CONTROL.txt"

LEVEL_COUNT = 8


def base_dir() -> Path:
    """Return the validator's own directory, independent of terminal CWD."""
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()


# ============================================================================
# EXACT BASE-10 ENCODING / DECODING
# ============================================================================

def fraction_to_decimal_exact(value: Fraction) -> str:
    """
    Convert a Fraction to an exact finite Base-10 decimal.

    This validator deliberately uses binary-generated denominators whose
    reduced form contains only factors 2 and/or 5, so the Base-10 expansion
    must terminate exactly.

    Raises ValueError if a non-terminating decimal would be required.
    """
    n = value.numerator
    d = value.denominator

    sign = "-" if n < 0 else ""
    n = abs(n)

    # Determine whether the reduced denominator terminates in Base 10.
    test_d = d
    while test_d % 2 == 0:
        test_d //= 2
    while test_d % 5 == 0:
        test_d //= 5

    if test_d != 1:
        raise ValueError(
            f"{value} does not have a finite exact Base-10 representation"
        )

    integer_part = n // d
    remainder = n % d

    if remainder == 0:
        return f"{sign}{integer_part}"

    digits: List[str] = []

    while remainder:
        remainder *= 10
        digit = remainder // d
        remainder %= d
        digits.append(str(digit))

    return f"{sign}{integer_part}." + "".join(digits)


def decimal_exact_to_fraction(text: str) -> Fraction:
    """
    Decode a finite decimal string into an exact Fraction.
    """
    text = text.strip()

    sign = -1 if text.startswith("-") else 1
    if text[0] in "+-":
        text = text[1:]

    if "." not in text:
        return Fraction(sign * int(text), 1)

    integer_part, fractional_part = text.split(".", 1)

    if not fractional_part:
        return Fraction(sign * int(integer_part), 1)

    scale = 10 ** len(fractional_part)
    numerator = int(integer_part) * scale + int(fractional_part)

    return Fraction(sign * numerator, scale)


# ============================================================================
# BINARY / RELATIONAL SOURCE GENERATION
# ============================================================================

def expanded_fraction(base_num: int, base_den: int, level: int) -> Tuple[int, int]:
    factor = 2 ** level
    return base_num * factor, base_den * factor


def build_level(level: int) -> Dict[str, object]:
    """
    Generate all source states BEFORE any Base-10 projection.
    """
    factor = 2 ** level

    # HALF FAMILY
    half_num, half_den = expanded_fraction(1, 2, level)
    half = Fraction(half_num, half_den)

    # ACTIVE / LOCK FAMILY
    active_num, active_den = expanded_fraction(3, 4, level)
    lock_num, lock_den = expanded_fraction(1, 4, level)

    active = Fraction(active_num, active_den)
    lock = Fraction(lock_num, lock_den)

    # ONE-EIGHTH FAMILY
    eighth_num, eighth_den = expanded_fraction(1, 8, level)
    eighth = Fraction(eighth_num, eighth_den)

    full_frame = active + lock

    return {
        "level": level,
        "binary_factor": factor,

        "half_expression": f"{half_num}/{half_den}",
        "half_fraction": half,

        "active_expression": f"{active_num}/{active_den}",
        "active_fraction": active,

        "lock_expression": f"{lock_num}/{lock_den}",
        "lock_fraction": lock,

        "eighth_expression": f"{eighth_num}/{eighth_den}",
        "eighth_fraction": eighth,

        "full_frame_fraction": full_frame,
    }


# ============================================================================
# PROJECTION TEST
# ============================================================================

def project_and_validate(level_data: Dict[str, object]) -> Dict[str, object]:
    """
    Project exact relational states into Base 10 only after source generation.
    """

    source_states = {
        "half": level_data["half_fraction"],
        "active": level_data["active_fraction"],
        "lock": level_data["lock_fraction"],
        "eighth": level_data["eighth_fraction"],
        "full_frame": level_data["full_frame_fraction"],
    }

    projections: Dict[str, Dict[str, object]] = {}

    for name, source_fraction in source_states.items():
        decimal_text = fraction_to_decimal_exact(source_fraction)
        reconstructed = decimal_exact_to_fraction(decimal_text)

        projections[name] = {
            "source_fraction": f"{source_fraction.numerator}/{source_fraction.denominator}",
            "base10": decimal_text,
            "reconstructed_fraction": f"{reconstructed.numerator}/{reconstructed.denominator}",
            "roundtrip_exact": reconstructed == source_fraction,
        }

    # Structural invariants.
    complement_exact = (
        source_states["active"] + source_states["lock"]
        == source_states["full_frame"]
        == Fraction(1, 1)
    )

    expected_values = {
        "half": Fraction(1, 2),
        "active": Fraction(3, 4),
        "lock": Fraction(1, 4),
        "eighth": Fraction(1, 8),
        "full_frame": Fraction(1, 1),
    }

    relational_identity_preserved = all(
        source_states[name] == expected
        for name, expected in expected_values.items()
    )

    all_roundtrips_exact = all(
        item["roundtrip_exact"]
        for item in projections.values()
    )

    no_new_state_introduced = all(
        decimal_exact_to_fraction(item["base10"])
        == source_states[name]
        for name, item in projections.items()
    )

    # Explicit expected Base-10 representations.
    decimal_identity = (
        projections["half"]["base10"] == "0.5"
        and projections["active"]["base10"] == "0.75"
        and projections["lock"]["base10"] == "0.25"
        and projections["eighth"]["base10"] == "0.125"
        and projections["full_frame"]["base10"] == "1"
    )

    status = all(
        [
            complement_exact,
            relational_identity_preserved,
            all_roundtrips_exact,
            no_new_state_introduced,
            decimal_identity,
        ]
    )

    return {
        "level": level_data["level"],
        "binary_factor": level_data["binary_factor"],

        "source": {
            "half_expression": level_data["half_expression"],
            "active_expression": level_data["active_expression"],
            "lock_expression": level_data["lock_expression"],
            "eighth_expression": level_data["eighth_expression"],
        },

        "projection": projections,

        "checks": {
            "complement_exact": complement_exact,
            "relational_identity_preserved": relational_identity_preserved,
            "all_roundtrips_exact": all_roundtrips_exact,
            "no_new_state_introduced": no_new_state_introduced,
            "base10_expected_values_exact": decimal_identity,
        },

        "status": "PASS" if status else "FAIL",
    }


def validate_cross_level_identity(results: List[Dict[str, object]]) -> Dict[str, object]:
    """
    Equivalent binary-scale source states must collapse to the same Base-10
    representation because Base 10 is downstream representation only.
    """

    fields = ["half", "active", "lock", "eighth", "full_frame"]

    reference = {
        field: results[0]["projection"][field]["base10"]
        for field in fields
    }

    checks = {}

    for field in fields:
        checks[field] = all(
            row["projection"][field]["base10"] == reference[field]
            for row in results
        )

    return {
        "reference_base10": reference,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


# ============================================================================
# OUTPUT
# ============================================================================

def write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_report(
    results: List[Dict[str, object]],
    cross_level: Dict[str, object],
    global_status: str,
) -> str:

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
        "# P.B.F. BINARY STRUCTURE → BASE 10 PROJECTION LOCK",
        "",
        f"**Version:** `{VERSION}`",
        "",
        f"**Global Status:** **{global_status}**",
        "",
    ])

    lines.append("---")
    lines.append("")
    lines.append("## TESTED DIRECTION")
    lines.append("")
    lines.append("```text")
    lines.append("BINARY / RELATIONAL SOURCE")
    lines.append("        ↓")
    lines.append("EXACT FRACTION STATE")
    lines.append("        ↓")
    lines.append("BASE 10 ENCODING")
    lines.append("        ↓")
    lines.append("EXACT FRACTION RECONSTRUCTION")
    lines.append("        ↓")
    lines.append("IDENTITY CHECK")
    lines.append("```")
    lines.append("")

    lines.append("> Base 10 is never used as a source generator in this test.")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## EXECUTED PROJECTION TABLE")
    lines.append("")
    lines.append(
        "| Level | Binary factor | Half | Base 10 | Active | Base 10 | Lock | Base 10 | 1/8 | Base 10 | Status |"
    )
    lines.append(
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|"
    )

    for row in results:
        lines.append(
            f"| {row['level']} "
            f"| {row['binary_factor']} "
            f"| `{row['source']['half_expression']}` "
            f"| `{row['projection']['half']['base10']}` "
            f"| `{row['source']['active_expression']}` "
            f"| `{row['projection']['active']['base10']}` "
            f"| `{row['source']['lock_expression']}` "
            f"| `{row['projection']['lock']['base10']}` "
            f"| `{row['source']['eighth_expression']}` "
            f"| `{row['projection']['eighth']['base10']}` "
            f"| **{row['status']}** |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## EXACT PROJECTION AND RECONSTRUCTION")
    lines.append("")
    lines.append("| State | Source fraction | Base 10 | Reconstructed fraction | Exact |")
    lines.append("|:---|---:|---:|---:|:---:|")

    first_projection = results[0]["projection"]
    state_labels = {
        "half": "Half",
        "active": "Active",
        "lock": "Lock",
        "eighth": "One eighth",
        "full_frame": "Full frame",
    }

    for key, label in state_labels.items():
        item = first_projection[key]
        lines.append(
            f"| {label} "
            f"| `{item['source_fraction']}` "
            f"| `{item['base10']}` "
            f"| `{item['reconstructed_fraction']}` "
            f"| **{'PASS' if item['roundtrip_exact'] else 'FAIL'}** |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## CROSS-LEVEL BASE-10 IDENTITY")
    lines.append("")

    refs = cross_level["reference_base10"]

    lines.append("```text")
    lines.append(f"1/2 family  → {refs['half']}")
    lines.append(f"3/4 family  → {refs['active']}")
    lines.append(f"1/4 family  → {refs['lock']}")
    lines.append(f"1/8 family  → {refs['eighth']}")
    lines.append(f"full frame  → {refs['full_frame']}")
    lines.append("```")
    lines.append("")

    lines.append(
        f"**Cross-level representation identity: {cross_level['status']}**"
    )
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## LOCK CONDITIONS")
    lines.append("")
    lines.append("```text")
    lines.append("SOURCE GENERATED BEFORE BASE 10      : REQUIRED")
    lines.append("EXACT ROUNDTRIP                      : REQUIRED")
    lines.append("RELATIONAL IDENTITY PRESERVED        : REQUIRED")
    lines.append("3/4 + 1/4 = 1                       : REQUIRED")
    lines.append("NO NEW STATE FROM BASE 10            : REQUIRED")
    lines.append("SAME VALUE ACROSS BINARY SCALE       : REQUIRED")
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## RESULT")
    lines.append("")

    if global_status == "PASS":
        lines.append(
            "> **BASE-10 PROJECTION LOCK: PASS**"
        )
        lines.append("")
        lines.append(
            "> The tested Base-10 layer is a lossless downstream representation "
            "of the already generated binary-divisible relational states."
        )
        lines.append("")
        lines.append(
            "> Binary scale changes the source representation, while the exact "
            "relational value and its Base-10 projection remain invariant."
        )
        lines.append("")
        lines.append(
            "> Base 10 introduces no new relational state in the executed test."
        )
    else:
        lines.append(
            "> **BASE-10 PROJECTION LOCK: FAIL**"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## VALIDATION BOUNDARY")
    lines.append("")
    lines.append(
        "This validator establishes the tested projection relation for the "
        "defined exact rational families."
    )
    lines.append("")
    lines.append(
        "It tests Base 10 as a downstream representation layer; it does not "
        "claim that every property of the decimal number system is generated "
        "by these fractions."
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    timestamp = datetime.now().astimezone()

    root = base_dir()
    output_dir = root / OUTPUT_DIR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)

    source_levels = [
        build_level(level)
        for level in range(LEVEL_COUNT)
    ]

    results = [
        project_and_validate(level)
        for level in source_levels
    ]

    cross_level = validate_cross_level_identity(results)

    levels_pass = all(row["status"] == "PASS" for row in results)
    cross_level_pass = cross_level["status"] == "PASS"

    global_status = (
        "PASS"
        if levels_pass and cross_level_pass
        else "FAIL"
    )

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
        "results": results,
        "cross_level": cross_level,
    }

    write_json(output_dir / DATA_FILE, payload)

    report = build_report(
        results,
        cross_level,
        global_status,
    )

    (output_dir / REPORT_FILE).write_text(
        report,
        encoding="utf-8",
    )

    control_log = [
        "P.B.F. BINARY STRUCTURE -> BASE 10 PROJECTION LOCK — CONTROL LOG",
        "=" * 82,
        f"Python Code ID       : {PYTHON_CODE_ID}",
        f"Official Code Title  : {OFFICIAL_CODE_TITLE}",
        f"File                 : {FILE_NAME}",
        f"Version              : {VERSION}",
        f"Timestamp            : {timestamp.isoformat()}",
        f"Levels tested        : {LEVEL_COUNT}",
        f"Level PASS           : {sum(r['status'] == 'PASS' for r in results)}/{LEVEL_COUNT}",
        f"Cross-level identity : {cross_level['status']}",
        "",
        "BASE-10 TARGET REPRESENTATIONS",
        "-" * 82,
        f"1/2                  : {cross_level['reference_base10']['half']}",
        f"3/4                  : {cross_level['reference_base10']['active']}",
        f"1/4                  : {cross_level['reference_base10']['lock']}",
        f"1/8                  : {cross_level['reference_base10']['eighth']}",
        f"Full frame           : {cross_level['reference_base10']['full_frame']}",
        "",
        "FINAL",
        "-" * 82,
        f"BASE-10 PROJECTION LOCK: {global_status}",
    ]

    (output_dir / CONTROL_FILE).write_text(
        "\n".join(control_log) + "\n",
        encoding="utf-8",
    )

    print("=" * 82)
    print("P.B.F. BINARY STRUCTURE -> BASE 10 PROJECTION LOCK VALIDATOR")
    print("=" * 82)

    for row in results:
        print(
            f"LEVEL {row['level']:02d} | "
            f"HALF {row['source']['half_expression']:>8} -> "
            f"{row['projection']['half']['base10']:<6} | "
            f"ACTIVE {row['source']['active_expression']:>8} -> "
            f"{row['projection']['active']['base10']:<6} | "
            f"LOCK {row['source']['lock_expression']:>8} -> "
            f"{row['projection']['lock']['base10']:<6} | "
            f"{row['status']}"
        )

    print("-" * 82)
    print(f"CROSS-LEVEL IDENTITY    : {cross_level['status']}")
    print(f"BASE-10 PROJECTION LOCK : {global_status}")
    print(f"OUTPUT DIRECTORY        : {output_dir}")
    print("=" * 82)

    return 0 if global_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
