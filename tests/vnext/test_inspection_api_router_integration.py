from __future__ import annotations

from app.vnext.experimental_api_routes import router


def _route_methods() -> dict[str, set[str]]:
    return {
        route.path: set(route.methods or set())
        for route in router.routes
        if hasattr(route, "path")
    }


def test_all_inspection_routes_remain_registered_under_parent_router() -> None:
    routes = _route_methods()
    expected_paths = {
        "/vnext/experimental/inspection-receipts",
        "/vnext/experimental/inspection-batch-manifests",
        "/vnext/experimental/inspection-manifest-comparisons",
        "/vnext/experimental/inspection-comparison-review-bundles",
        "/vnext/experimental/inspection-review-bundle-comparisons",
        "/vnext/experimental/inspection-review-bundle-comparison-sets",
        "/vnext/experimental/inspection-review-bundle-comparison-set-comparisons",
        "/vnext/experimental/inspection-comparison-set-comparison-series",
        "/vnext/experimental/inspection-comparison-series-comparisons",
        "/vnext/experimental/inspection-comparison-series-comparison-collections",
        "/vnext/experimental/inspection-comparison-collection-comparisons",
        "/vnext/experimental/inspection-comparison-collection-comparison-sequences",
        "/vnext/experimental/inspection-comparison-sequence-comparisons",
        "/vnext/experimental/inspection-comparison-sequence-comparison-registers",
        "/vnext/experimental/inspection-comparison-register-comparisons",
        "/vnext/experimental/inspection-comparison-register-comparison-ledgers",
        "/vnext/experimental/inspection-comparison-ledger-comparisons",
        "/vnext/experimental/inspection-comparison-ledger-comparison-archives",
    }

    assert expected_paths <= routes.keys()
    for path in expected_paths:
        assert routes[path] == {"POST"}


def test_inspection_router_does_not_add_retrieval_or_mutation_routes() -> None:
    routes = _route_methods()
    inspection_routes = {
        path: methods
        for path, methods in routes.items()
        if path.startswith("/vnext/experimental/inspection-")
    }

    assert inspection_routes
    assert all(methods == {"POST"} for methods in inspection_routes.values())
