from __future__ import annotations

from pathlib import Path

from poc.run_poc import reset_store, run_scenario

SCENARIO_DIR = Path(__file__).parents[1] / "poc" / "scenarios"


def setup_function() -> None:
    reset_store()


def test_scenario_a_normal_continue() -> None:
    artifact = run_scenario(SCENARIO_DIR / "scenario_a_normal_continue.json")
    summary = artifact["summary"]
    assert summary["boundary_states"] == ["NORMAL"]
    assert summary["stability_status"] == "STABLE"
    assert summary["operator_response"] == "CONTINUE"
    assert summary["continuity_type"] == "DIRECT_CONNECTION"


def test_scenario_b_unknown_reslice_prepares_only_one_next_request() -> None:
    artifact = run_scenario(SCENARIO_DIR / "scenario_b_unknown_reslice.json")
    summary = artifact["summary"]
    assert summary["boundary_states"] == ["UNKNOWN"]
    assert summary["operator_response"] == "RESLICE"
    assert summary["continuity_type"] == "RESLICE_CONNECTION"
    assert summary["next_request"]["mode"] == "RESLICE"
    assert summary["next_request"]["source_type"] == "CONTEXT_EVIDENCE"
    assert artifact["seed_summary"] is not None


def test_scenario_c_void_evidence_and_defer_are_separate() -> None:
    artifact = run_scenario(SCENARIO_DIR / "scenario_c_void_defer.json")
    result = artifact["result"]
    summary = artifact["summary"]
    assert summary["boundary_states"] == ["VOID"]
    assert summary["stability_status"] == "VOID_RELATED"
    assert summary["operator_response"] == "DEFER"
    assert summary["continuity_type"] == "DEFERRED_PENDING_RELATION"
    assert summary["evidence_counts"]["void"] == 1
    void_record = result["slice_done"]["void_evidence"][0]
    assert "deferred" not in void_record
    assert "resolved" not in void_record
    assert result["continuity"]["pending"] is True


def test_scenario_d_adjust_preserves_continuity() -> None:
    artifact = run_scenario(SCENARIO_DIR / "scenario_d_adjust.json")
    summary = artifact["summary"]
    assert summary["stability_status"] == "ADAPTIVE"
    assert summary["operator_response"] == "ADJUST"
    assert summary["continuity_type"] == "ADJUSTED_CONNECTION"


def test_scenario_d_jump_is_noncontinuous_reconnection() -> None:
    artifact = run_scenario(SCENARIO_DIR / "scenario_d_jump.json")
    result = artifact["result"]
    summary = artifact["summary"]
    assert summary["stability_status"] == "UNSTABLE"
    assert summary["operator_response"] == "JUMP"
    assert summary["continuity_type"] == "JUMP_RECONNECTION"
    assert result["continuity"]["connected"] is False
