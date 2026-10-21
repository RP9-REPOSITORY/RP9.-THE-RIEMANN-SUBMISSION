#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# RP9_CODE_ID: C.0084

# =============================================================================
# RP9. CODE IDENTITY
#
# REPOSITORY: RP9. RH. Z0
#     RP9. RIEMANN SUBMISSION
#
# PYTHON CODE ID: K6. A
# OFFICIAL CODE TITLE: K6. SCALE INVARIANCE CROSSCHECK
#
# REPOSITORY POSITION:
# PRIMARY SUBMISSION — SUBJECT OF EXAMINATION AND REVIEW
# =============================================================================
#
"""Exact K.6 scale-invariance crosscheck for the submitted P.B.F. chain.

The code is self-contained and generates its own JSON, Markdown, control-log,
trace, and execution-log outputs.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List
import json
import os
import platform
import sys
import traceback

PYTHON_CODE_ID = "K6. A"
FILE_NAME = "K6. A.py"
OFFICIAL_CODE_TITLE = "K6. SCALE INVARIANCE CROSSCHECK"
SCRIPT_VERSION = "2.0.0"
OUTPUT_DIR_NAME = "2. OUTPUT"
OUTPUT_DATA_FILE = "K6.A_DATA.json"
OUTPUT_TRACE_FILE = "K6.A_TRACE.json"
OUTPUT_REPORT_FILE = "K6.A_REPORT.md"
OUTPUT_CONTROL_FILE = "K6.A_CONTROL.txt"
OUTPUT_EXECUTION_FILE = "K6.A_EXECUTION.log"

LINEAR_CONTAINED = Fraction(2, 3)
LINEAR_EXPANDED = Fraction(3, 2)
PLANAR_MAIN = Fraction(3, 4)
PLANAR_COMPLEMENT = Fraction(1, 4)
VOLUMETRIC_MAIN = Fraction(6, 8)
VOLUMETRIC_COMPLEMENT = Fraction(2, 8)


@dataclass(frozen=True)
class Crosscheck:
    test_id: str
    title: str
    source: str
    target: str
    operation: str
    expected: str
    observed: Dict[str, Any]
    status: str
    boundary: str


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def json_safe(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {
            "fraction": fraction_text(value),
            "numerator": value.numerator,
            "denominator": value.denominator,
        }
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def status(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def run_crosschecks() -> List[Crosscheck]:
    checks: List[Crosscheck] = []

    product = LINEAR_CONTAINED * LINEAR_EXPANDED
    checks.append(Crosscheck(
        "K6_SCALE_T01", "Reciprocal directional lock", "2/3", "3/2",
        "(2/3) × (3/2)", "1", {"product": product},
        status(product == 1), "Verifies exact reciprocal closure only."
    ))

    normalized = LINEAR_EXPANDED / 2
    checks.append(Crosscheck(
        "K6_SCALE_T02", "Linear-to-planar normalization", "3/2", "3/4",
        "(3/2) / 2", "3/4", {"result": normalized},
        status(normalized == PLANAR_MAIN),
        "Verifies the stated exact rational transformation only."
    ))

    planar_sum = PLANAR_MAIN + PLANAR_COMPLEMENT
    checks.append(Crosscheck(
        "K6_SCALE_T03", "Planar complementary closure", "3/4", "1/4",
        "3/4 + 1/4", "1", {"sum": planar_sum},
        status(planar_sum == 1), "Verifies complete planar closure only."
    ))

    main_equal = PLANAR_MAIN == VOLUMETRIC_MAIN
    checks.append(Crosscheck(
        "K6_SCALE_T04", "Main relation scale invariance", "3/4", "6/8",
        "3/4 = 6/8", "Exact quotient equality",
        {"planar": PLANAR_MAIN, "volumetric": VOLUMETRIC_MAIN, "equal": main_equal},
        status(main_equal),
        "Verifies quotient invariance across the two representations."
    ))

    complement_equal = PLANAR_COMPLEMENT == VOLUMETRIC_COMPLEMENT
    volumetric_sum = VOLUMETRIC_MAIN + VOLUMETRIC_COMPLEMENT
    complete = complement_equal and volumetric_sum == 1
    checks.append(Crosscheck(
        "K6_SCALE_T05", "Complementary relation scale invariance", "1/4", "2/8",
        "1/4 = 2/8; 6/8 + 2/8 = 1",
        "Exact complement equality and complete closure",
        {
            "planar_complement": PLANAR_COMPLEMENT,
            "volumetric_complement": VOLUMETRIC_COMPLEMENT,
            "equal": complement_equal,
            "volumetric_sum": volumetric_sum,
        },
        status(complete),
        "Verifies complementary invariance and complete volumetric closure."
    ))

    core_pass = all(check.status == "PASS" for check in checks)
    checks.append(Crosscheck(
        "K6_SCALE_T12", "Global submitted-chain control", "K6_SCALE_T01", "K6_SCALE_T05",
        "All five independent core controls must PASS", "5/5 core controls PASS",
        {
            "core_test_count": len(checks),
            "core_pass_count": sum(check.status == "PASS" for check in checks),
            "all_core_controls_pass": core_pass,
        },
        status(core_pass),
        "Summarizes the five preceding controls and introduces no new relation."
    ))
    return checks


def build_payload() -> Dict[str, Any]:
    checks = run_crosschecks()
    global_pass = all(check.status == "PASS" for check in checks)
    return {
        "metadata": {
            "repository": "RP9. RH. Z0",
            "repository_branch": "RP9. RIEMANN SUBMISSION",
            "python_code_id": PYTHON_CODE_ID,
            "filesystem_name": FILE_NAME,
            "official_code_title": OFFICIAL_CODE_TITLE,
            "repository_position": "PRIMARY SUBMISSION — SUBJECT OF EXAMINATION AND REVIEW",
            "script_version": SCRIPT_VERSION,
            "created_at": now_iso(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "arithmetic": "Exact rational arithmetic using fractions.Fraction",
        },
        "scope": {
            "tested_chain": ["2/3", "3/2", "3/4", "1/4", "6/8", "2/8"]
        },
        "crosschecks": [json_safe(asdict(check)) for check in checks],
        "result": {
            "test_count": len(checks),
            "pass_count": sum(check.status == "PASS" for check in checks),
            "fail_count": sum(check.status == "FAIL" for check in checks),
            "global_status": status(global_pass),
        },
    }


def build_trace(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {"step": index, "timestamp": payload["metadata"]["created_at"], **check}
        for index, check in enumerate(payload["crosschecks"], start=1)
    ]


def build_markdown(payload: Dict[str, Any]) -> str:
    summary = payload["result"]
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
        f"- **Version:** {SCRIPT_VERSION}",
        "",
        "## Function", "",
        "Verify exact relational continuity across the submitted K.6 chain:", "",
        "```text", "2/3 ↔ 3/2", "      ↓", "3/4 ↔ 1/4", "      ↓",
        "6/8 ↔ 2/8", "```", "",
        "All numerical operations use exact rational arithmetic.", "",
        "## Control Matrix", "",
        "| Test | Source | Target | Operation | Status |",
        "|---|---|---|---|:---:|",
    ]
    for check in payload["crosschecks"]:
        lines.append(
            f"| {check['test_id']} | `{check['source']}` | `{check['target']}` | "
            f"{check['operation']} | **{check['status']}** |"
        )
    lines.extend([
        "", "## Scope Boundary", "",
        "This code tests only the relations explicitly listed above.",
        "", "## Final Result", "",
        f"- Tests: **{summary['test_count']}**",
        f"- PASS: **{summary['pass_count']}**",
        f"- FAIL: **{summary['fail_count']}**",
        f"- Global status: **{summary['global_status']}**", "",
        "Global PASS means that every explicitly defined transformation, quotient",
        "equivalence, and complementary closure in this submitted chain passed.", "",
    ])
    return "\n".join(lines)


def write_outputs(output_dir: Path, payload: Dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "data": output_dir / OUTPUT_DATA_FILE,
        "trace": output_dir / OUTPUT_TRACE_FILE,
        "presentation": output_dir / OUTPUT_REPORT_FILE,
        "control": output_dir / OUTPUT_CONTROL_FILE,
        "execution": output_dir / OUTPUT_EXECUTION_FILE,
    }
    files["data"].write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    files["trace"].write_text(
        json.dumps(build_trace(payload), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    files["presentation"].write_text(build_markdown(payload), encoding="utf-8")

    control_lines = [
        f"PYTHON_CODE_ID={PYTHON_CODE_ID}", f"OFFICIAL_CODE_TITLE={OFFICIAL_CODE_TITLE}", f"FILE={FILE_NAME}", f"VERSION={SCRIPT_VERSION}",
        f"TIMESTAMP={payload['metadata']['created_at']}",
    ]
    control_lines.extend(
        f"{check['test_id']}={check['status']}" for check in payload["crosschecks"]
    )
    control_lines.append(f"GLOBAL_STATUS={payload['result']['global_status']}")
    files["control"].write_text("\n".join(control_lines) + "\n", encoding="utf-8")

    execution_lines = [
        f"PYTHON_CODE_ID={PYTHON_CODE_ID}", f"OFFICIAL_CODE_TITLE={OFFICIAL_CODE_TITLE}", f"FILE={FILE_NAME}", f"VERSION={SCRIPT_VERSION}",
        f"OUTPUT_DIRECTORY={output_dir}", "FILES_CREATED=5",
        f"GLOBAL_STATUS={payload['result']['global_status']}",
    ]
    files["execution"].write_text("\n".join(execution_lines) + "\n", encoding="utf-8")


def main() -> int:
    exit_code = 0
    try:
        print("Starting RP9 K.6 scale invariance crosscheck...", flush=True)
        output_dir = Path(__file__).resolve().parent / OUTPUT_DIR_NAME
        payload = build_payload()
        write_outputs(output_dir, payload)
        summary = payload["result"]
        print(f"GLOBAL STATUS: {summary['global_status']}")
        print(f"Tests: {summary['test_count']} | PASS: {summary['pass_count']} | FAIL: {summary['fail_count']}")
        for check in payload["crosschecks"]:
            print(f"{check['test_id']} | {check['status']} | {check['title']}")
        print(f"Output directory: {output_dir}")
        print("Execution complete. Output files were written successfully.", flush=True)
        if summary["global_status"] != "PASS":
            exit_code = 1
    except Exception:
        exit_code = 2
        print("EXECUTION ERROR", file=sys.stderr, flush=True)
        traceback.print_exc()
    finally:
        if os.name == "nt" and sys.stdin.isatty():
            try:
                input("Press Enter to close...")
            except EOFError:
                pass
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
