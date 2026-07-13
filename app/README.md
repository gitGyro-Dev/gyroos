# GyroOS Bounded Runtime API

This directory contains the first bounded implementation based on:

- `docs/52_api_boundary_and_execution_model.md`
- `docs/53_canonical_request_schema.md`
- `docs/54_canonical_slice_done_and_evidence_schemas.md`
- `docs/55_stability_response_and_continuity_schemas.md`
- `docs/56_validation_and_cross_reference_rules.md`
- `docs/57_loop_step_execution_contract.md`
- `docs/58_supporting_endpoint_contract.md`
- `docs/59_http_status_runtime_status_and_error_model.md`
- `docs/60_api_implementation_and_test_plan.md`

## Execution boundary

```text
one HTTP request
=
one bounded Gyro Process
```

The implementation does not recursively execute a prepared Re-Slice request.

## Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-api.txt
```

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Test

```powershell
python -m pytest tests/test_bounded_api.py -q
```

## Initial endpoints

```text
POST /loop/step
GET  /health
GET  /process/{process_id}
GET  /memory/record/{record_id}
```

## Responsibility boundary

```text
SliceEngine
→ produces SliceDone

StabilityEngine
→ produces StabilityResult

LoopController
→ sole OperatorResponse selector

ContinuityBuilder
→ produces RuntimeContinuityResult

InMemoryStore
→ atomically publishes a complete result group
```

The policy included in this first implementation is a bounded demonstration policy. Its configured mappings are implementation policy and are not Gyro Logic definitions.
