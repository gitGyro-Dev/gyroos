# 220. vNext Inspection Comparison Collection Comparison Minimal PoC

## Scope

P adds a bounded request-local comparison between two explicit O comparison collection references.

## Added

- `app/vnext/inspection_comparison_collection_comparison.py`
- `app/vnext/inspection_comparison_collection_comparison_service.py`
- model, service, and API tests under `tests/vnext/`
- one POST route under `/vnext/experimental`

## Behavior

The implementation validates explicit identifiers and bounded reference lists, then reports added, removed, and retained series-comparison IDs plus declared digest equality.

It does not retrieve collections, infer semantic trends, classify risk, aggregate authentication outcomes, update Runtime, or persist canonically.

## Verification

The Priority F workflow includes the P1-P3 tests.

```text
GitHub Actions verification = PENDING
```
