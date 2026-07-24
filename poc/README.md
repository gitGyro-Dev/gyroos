# GyroOS Priority F — Bounded PoC

This directory contains repeatable Proof-of-Concept scenarios for the canonical bounded Runtime API.

## Runtime boundary

```text
one request
=
one bounded Gyro Process
```

The runner invokes `ProcessExecutor` with the same canonical `LoopStepRequest` used by `POST /loop/step`.
It does not provide a second Runtime implementation.

## Scenarios

```text
scenario_a_normal_continue.json
= readable Boundary / NORMAL / CONTINUE

scenario_b_unknown_reslice.json
= UNKNOWN / ContextEvidence / RESLICE preparation

scenario_c_void_defer.json
= identifiable Boundary / VOID / VoidEvidence / DEFER

scenario_d_adjust.json
= conflicting reading / bounded ADJUST

scenario_d_jump.json
= conflicting reading / JUMP reconnection
```

The response choices are explicit bounded PoC policy inputs.
They are not universal mappings from Boundary State or Stability.

## Run

From the repository root:

```powershell
python -m pip install -r requirements-api.txt
python poc/run_poc.py
```

Write complete artifacts:

```powershell
python poc/run_poc.py --output-dir poc/results
```

Run selected scenarios:

```powershell
python poc/run_poc.py `
  --scenario scenario_a_normal_continue.json `
  --scenario scenario_c_void_defer.json
```

## Tests

```powershell
python -m pytest tests/test_bounded_api.py tests/test_priority_f_poc.py -q
```

## Result structure

Each generated artifact contains:

```text
scenario_id
expected
summary
seed_summary when applicable
complete LoopStepResult
```

The summary is an observation view.
The complete canonical Runtime result remains the source artifact.

## Important distinctions

```text
VOID
≠ DEFER

ContextEvidence
≠ RESLICE

StabilityResult
≠ OperatorResponse

OperatorResponse
≠ RuntimeContinuityResult
```

The controlled PoC policy selects the response through `LoopController`.
