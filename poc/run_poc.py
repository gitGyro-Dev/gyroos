from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.models import LoopStepRequest
from app.repositories import store
from app.runtime import ProcessExecutor

SCENARIO_DIR = Path(__file__).parent / "scenarios"
DEFAULT_FILES = [
    "scenario_a_normal_continue.json",
    "scenario_b_unknown_reslice.json",
    "scenario_c_void_defer.json",
    "scenario_d_adjust.json",
    "scenario_d_jump.json",
]


def reset_store() -> None:
    store.processes.clear()
    store.records.clear()
    store.idempotency.clear()
    store.current_scope.clear()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def execute_request(payload: dict[str, Any]) -> dict[str, Any]:
    request = LoopStepRequest.model_validate(payload)
    return ProcessExecutor(store).execute(request).model_dump(mode="json")


def summarize(scenario_id: str, result: dict[str, Any]) -> dict[str, Any]:
    slice_done = result["slice_done"]
    next_request = result["operator_response"].get("next_request")
    return {
        "scenario_id": scenario_id,
        "process_id": result["process_id"],
        "slice_id": slice_done["slice_id"],
        "boundary_states": [
            record["state_type"] for record in slice_done["boundary_state_records"]
        ],
        "stability_status": result["stability"]["status"],
        "stability_value": result["stability"]["value"],
        "operator_response": result["operator_response"]["response_type"],
        "continuity_type": result["continuity"]["continuity_type"],
        "evidence_counts": {
            "boundary": len(slice_done["boundary_evidence"]),
            "boundary_state": len(slice_done["boundary_state_records"]),
            "context": len(slice_done["context_evidence"]),
            "void": len(slice_done["void_evidence"]),
        },
        "next_request": None
        if next_request is None
        else {
            "mode": next_request["mode"],
            "source_type": next_request["source_type"],
            "source_ref": next_request["source_ref"],
            "parent_process_ref": next_request["parent_process_ref"],
            "parent_slice_ref": next_request["parent_slice_ref"],
            "requested_by_response_ref": next_request["requested_by_response_ref"],
        },
        "created_record_refs": result["created_record_refs"],
    }


def assert_expected(result: dict[str, Any], expected: dict[str, Any]) -> None:
    states = [
        record["state_type"]
        for record in result["slice_done"]["boundary_state_records"]
    ]
    if expected.get("boundary_state") not in states:
        raise AssertionError(
            f"expected boundary state {expected.get('boundary_state')}, got {states}"
        )
    checks = {
        "stability_status": result["stability"]["status"],
        "operator_response": result["operator_response"]["response_type"],
        "continuity_type": result["continuity"]["continuity_type"],
        "pending": result["continuity"]["pending"],
    }
    for key, expected_value in expected.items():
        if key in checks and checks[key] != expected_value:
            raise AssertionError(f"expected {key}={expected_value}, got {checks[key]}")
    if "next_request_mode" in expected:
        next_request = result["operator_response"].get("next_request")
        if not next_request or next_request["mode"] != expected["next_request_mode"]:
            raise AssertionError("expected bounded RESLICE next_request preparation")


def run_scenario(path: Path) -> dict[str, Any]:
    spec = load_json(path)
    scenario_id = spec["scenario_id"]
    before_count = len(store.processes)

    if "seed_request" in spec:
        seed_result = execute_request(spec["seed_request"])
        context_id = seed_result["slice_done"]["context_evidence"][0][
            "context_evidence_id"
        ]
        request = deepcopy(spec["prepare_request"])
        parameters = request["slice_request"]["slice_policy"]["parameters"]
        parameters["reslice_source_ref"] = context_id
        result = execute_request(request)
        scenario_process_delta = len(store.processes) - before_count - 1
        if scenario_process_delta != spec["expected"]["process_count_delta"]:
            raise AssertionError(
                "RESLICE preparation created an unexpected number of Processes"
            )
        if result["operator_response"]["next_request"]["source_ref"] != context_id:
            raise AssertionError("next_request did not preserve explicit Context identity")
        seed_summary = summarize(f"{scenario_id}_seed", seed_result)
    else:
        result = execute_request(spec["request"])
        seed_summary = None

    assert_expected(result, spec["expected"])
    return {
        "scenario_id": scenario_id,
        "expected": spec["expected"],
        "summary": summarize(scenario_id, result),
        "seed_summary": seed_summary,
        "result": result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run GyroOS bounded PoC scenarios.")
    parser.add_argument(
        "--scenario",
        action="append",
        help="Scenario file name. Repeat to run multiple files.",
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--reset-between", action="store_true")
    args = parser.parse_args()

    files = args.scenario or DEFAULT_FILES
    reset_store()
    outputs: list[dict[str, Any]] = []

    for filename in files:
        if args.reset_between:
            reset_store()
        artifact = run_scenario(SCENARIO_DIR / filename)
        outputs.append(artifact)
        print(json.dumps(artifact["summary"], ensure_ascii=False, indent=2))

        if args.output_dir is not None:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            target = args.output_dir / f"{artifact['scenario_id']}_result.json"
            target.write_text(
                json.dumps(artifact, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    print(f"Completed {len(outputs)} bounded PoC scenario(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
