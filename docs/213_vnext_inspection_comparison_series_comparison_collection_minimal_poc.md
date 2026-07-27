# 213. vNext Inspection Comparison Series Comparison Collection Minimal PoC

## 1. Purpose

This PoC demonstrates bounded request-local grouping of explicit N comparison-series comparison references.

```text
comparison references supplied explicitly
↓
validation and ordered digest
↓
immutable request-local collection manifest
```

## 2. Endpoint

```text
POST /vnext/experimental/inspection-comparison-series-comparison-collections
```

## 3. Example Request

```json
{
  "comparison_collection_id": "collection-001",
  "comparison_references": [
    {
      "series_comparison_id": "series-comparison-001",
      "left_comparison_series_id": "series-left-001",
      "right_comparison_series_id": "series-right-001",
      "added_count": 1,
      "removed_count": 2,
      "retained_count": 3,
      "digest_changed": true
    }
  ],
  "warnings": [],
  "source_refs": ["source-001"],
  "collection_metadata": {
    "purpose": "inspection"
  }
}
```

## 4. Example Result Meaning

```text
comparison_collection_created = true
```

This means only that a bounded collection manifest was assembled from supplied references.

It does not mean:

```text
semantic trend established
risk level established
authentication state aggregated
Runtime continuation approved
canonical history created
```

## 5. Digest Policy

```text
algorithm = SHA-256
canonicalization = JSON_SORTED_KEYS_UTF8_COMPACT_V1
input = ordered N comparison-reference list
```

The digest is an integrity label for the supplied reference list only.

## 6. Isolation

The PoC does not:

```text
retrieve N comparison reports
retrieve M series manifests
recompute comparison results
infer semantic trends
classify or aggregate risk
aggregate authentication outcomes
select OperatorResponse
change Runtime state
persist canonically
expose retrieval routes
```

## 7. Boundary

```text
comparison grouping
≠ semantic trend analysis
≠ risk aggregation
```
