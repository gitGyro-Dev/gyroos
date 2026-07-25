from __future__ import annotations

import pytest

from app.vnext.builders import (
    TrajectoryEdgeBuilder,
    TrajectoryGraphBuilder,
    TrajectoryNodeBuilder,
)
from app.vnext.models import TrajectoryGraph


def make_node(node_id: str, *, process_id: str = "process-1", record_ref: str | None = None):
    return TrajectoryNodeBuilder().build(
        process_id=process_id,
        record_ref=record_ref or f"record-{node_id}",
        record_type="StabilityScene",
        slice_ref=f"slice-{node_id}",
        trajectory_node_id=node_id,
    )


def test_builds_reference_only_trajectory_graph() -> None:
    source = make_node("node-source")
    target = make_node("node-target")
    edge = TrajectoryEdgeBuilder().build(
        source_node=source,
        target_node=target,
        edge_type="EXPLICIT_RELATION",
        relation_ref="continuity-relation-1",
        trajectory_edge_id="edge-1",
    )

    graph = TrajectoryGraphBuilder().build(
        process_id="process-1",
        nodes=[source, target],
        edges=[edge],
        root_node_refs=["node-source"],
        terminal_node_refs=["node-target"],
        trajectory_graph_id="graph-1",
    )

    assert graph.trajectory_node_refs == ["node-source", "node-target"]
    assert graph.trajectory_edge_refs == ["edge-1"]
    assert graph.root_node_refs == ["node-source"]
    assert graph.terminal_node_refs == ["node-target"]
    assert "nodes" not in TrajectoryGraph.model_fields
    assert "edges" not in TrajectoryGraph.model_fields
    assert "current_node_ref" not in TrajectoryGraph.model_fields


def test_node_preserves_explicit_record_reference_without_resolution() -> None:
    node = TrajectoryNodeBuilder().build(
        process_id="process-1",
        record_ref="external-record-1",
        record_type="DomainRecord",
        node_role="CANDIDATE",
    )

    assert node.record_ref == "external-record-1"
    assert node.record_type == "DomainRecord"
    assert node.node_role == "CANDIDATE"


def test_edge_rejects_process_mismatch() -> None:
    source = make_node("node-source", process_id="process-1")
    target = make_node("node-target", process_id="process-2")

    with pytest.raises(ValueError, match="process_id"):
        TrajectoryEdgeBuilder().build(
            source_node=source,
            target_node=target,
            edge_type="EXPLICIT_RELATION",
        )


def test_edge_rejects_self_reference() -> None:
    node = make_node("node-1")

    with pytest.raises(ValueError, match="distinct"):
        TrajectoryEdgeBuilder().build(
            source_node=node,
            target_node=node,
            edge_type="EXPLICIT_RELATION",
        )


def test_edge_expected_references_are_checked() -> None:
    source = make_node("node-source")
    target = make_node("node-target")

    with pytest.raises(ValueError, match="expected_source_node_ref"):
        TrajectoryEdgeBuilder().build(
            source_node=source,
            target_node=target,
            edge_type="EXPLICIT_RELATION",
            expected_source_node_ref="other-node",
        )


def test_graph_requires_edge_endpoints_inside_graph() -> None:
    source = make_node("node-source")
    external = make_node("node-external")
    edge = TrajectoryEdgeBuilder().build(
        source_node=source,
        target_node=external,
        edge_type="EXPLICIT_RELATION",
    )

    with pytest.raises(ValueError, match="target_node_ref"):
        TrajectoryGraphBuilder().build(
            process_id="process-1",
            nodes=[source],
            edges=[edge],
        )


def test_graph_rejects_duplicate_node_ids() -> None:
    first = make_node("node-1", record_ref="record-1")
    second = make_node("node-1", record_ref="record-2")

    with pytest.raises(ValueError, match="TrajectoryNode IDs"):
        TrajectoryGraphBuilder().build(
            process_id="process-1",
            nodes=[first, second],
        )


def test_graph_rejects_duplicate_edge_ids() -> None:
    first = make_node("node-1")
    second = make_node("node-2")
    third = make_node("node-3")
    edge_1 = TrajectoryEdgeBuilder().build(
        source_node=first,
        target_node=second,
        edge_type="EXPLICIT_RELATION",
        trajectory_edge_id="edge-1",
    )
    edge_2 = TrajectoryEdgeBuilder().build(
        source_node=second,
        target_node=third,
        edge_type="EXPLICIT_RELATION",
        trajectory_edge_id="edge-1",
    )

    with pytest.raises(ValueError, match="TrajectoryEdge IDs"):
        TrajectoryGraphBuilder().build(
            process_id="process-1",
            nodes=[first, second, third],
            edges=[edge_1, edge_2],
        )


def test_root_and_terminal_refs_must_be_bundled() -> None:
    node = make_node("node-1")

    with pytest.raises(ValueError, match="root_node_refs"):
        TrajectoryGraphBuilder().build(
            process_id="process-1",
            nodes=[node],
            root_node_refs=["external-node"],
        )


def test_trajectory_does_not_infer_authority_or_path_semantics() -> None:
    source = make_node("node-source")
    target = make_node("node-target")
    edge = TrajectoryEdgeBuilder().build(
        source_node=source,
        target_node=target,
        edge_type="BRANCH_CANDIDATE",
        readable=False,
        authoritative=False,
    )
    graph = TrajectoryGraphBuilder().build(
        process_id="process-1",
        nodes=[source, target],
        edges=[edge],
    )

    assert edge.edge_type == "BRANCH_CANDIDATE"
    assert edge.readable is False
    assert edge.authoritative is False
    assert graph.root_node_refs == []
    assert graph.terminal_node_refs == []
    assert "selected_path_refs" not in TrajectoryGraph.model_fields
    assert "authoritative_edge_ref" not in TrajectoryGraph.model_fields


def test_nested_metadata_is_copied() -> None:
    node_metadata = {"review": {"tags": ["node"]}}
    edge_metadata = {"review": {"tags": ["edge"]}}
    graph_metadata = {"review": {"tags": ["graph"]}}

    source = TrajectoryNodeBuilder().build(
        process_id="process-1",
        record_ref="record-source",
        record_type="StabilityScene",
        metadata=node_metadata,
        trajectory_node_id="node-source",
    )
    target = make_node("node-target")
    edge = TrajectoryEdgeBuilder().build(
        source_node=source,
        target_node=target,
        edge_type="EXPLICIT_RELATION",
        metadata=edge_metadata,
        trajectory_edge_id="edge-1",
    )
    graph = TrajectoryGraphBuilder().build(
        process_id="process-1",
        nodes=[source, target],
        edges=[edge],
        metadata=graph_metadata,
    )

    node_metadata["review"]["tags"].append("mutated")
    edge_metadata["review"]["tags"].append("mutated")
    graph_metadata["review"]["tags"].append("mutated")

    assert source.metadata == {"review": {"tags": ["node"]}}
    assert edge.metadata == {"review": {"tags": ["edge"]}}
    assert graph.metadata == {"review": {"tags": ["graph"]}}
