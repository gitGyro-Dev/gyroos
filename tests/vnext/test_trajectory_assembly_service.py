from __future__ import annotations

import pytest

from app.vnext.models import (
    TrajectoryAssemblyRequest,
    TrajectoryEdgeSpec,
    TrajectoryGraph,
    TrajectoryNodeSpec,
)
from app.vnext.trajectory_assembly import TrajectoryAssemblyService


def test_assembles_explicit_nodes_edges_and_graph() -> None:
    request = TrajectoryAssemblyRequest(
        process_id="process-1",
        nodes=[
            TrajectoryNodeSpec(
                trajectory_node_id="node-a",
                record_ref="scene-1",
                record_type="StabilityScene",
                slice_ref="slice-1",
                node_role="SOURCE",
            ),
            TrajectoryNodeSpec(
                trajectory_node_id="node-b",
                record_ref="context-2",
                record_type="ReadabilityContext",
                slice_ref="slice-2",
                node_role="TARGET",
            ),
        ],
        edges=[
            TrajectoryEdgeSpec(
                trajectory_edge_id="edge-a-b",
                source_node_ref="node-a",
                target_node_ref="node-b",
                edge_type="EXPLICIT_RELATION",
                relation_ref="continuity-relation-1",
                readable=True,
            )
        ],
        root_node_refs=["node-a"],
        terminal_node_refs=["node-b"],
        trajectory_graph_id="graph-1",
    )

    result = TrajectoryAssemblyService().assemble(request)

    assert [node.trajectory_node_id for node in result.nodes] == ["node-a", "node-b"]
    assert [edge.trajectory_edge_id for edge in result.edges] == ["edge-a-b"]
    assert result.graph.trajectory_node_refs == ["node-a", "node-b"]
    assert result.graph.trajectory_edge_refs == ["edge-a-b"]
    assert result.graph.root_node_refs == ["node-a"]
    assert result.graph.terminal_node_refs == ["node-b"]
    assert result.edges[0].relation_ref == "continuity-relation-1"


def test_empty_graph_is_allowed() -> None:
    result = TrajectoryAssemblyService().assemble(
        TrajectoryAssemblyRequest(process_id="process-1")
    )

    assert result.nodes == []
    assert result.edges == []
    assert result.graph.trajectory_node_refs == []
    assert result.graph.trajectory_edge_refs == []


def test_edge_requires_nodes_in_same_request() -> None:
    request = TrajectoryAssemblyRequest(
        process_id="process-1",
        nodes=[
            TrajectoryNodeSpec(
                trajectory_node_id="node-a",
                record_ref="record-a",
                record_type="EXPLICIT",
            )
        ],
        edges=[
            TrajectoryEdgeSpec(
                source_node_ref="node-a",
                target_node_ref="external-node",
                edge_type="EXPLICIT_RELATION",
            )
        ],
    )

    with pytest.raises(ValueError, match="target_node_ref"):
        TrajectoryAssemblyService().assemble(request)


def test_duplicate_node_ids_are_rejected() -> None:
    request = TrajectoryAssemblyRequest(
        process_id="process-1",
        nodes=[
            TrajectoryNodeSpec(
                trajectory_node_id="node-1",
                record_ref="record-a",
                record_type="A",
            ),
            TrajectoryNodeSpec(
                trajectory_node_id="node-1",
                record_ref="record-b",
                record_type="B",
            ),
        ],
    )

    with pytest.raises(ValueError, match="TrajectoryNode IDs"):
        TrajectoryAssemblyService().assemble(request)


def test_duplicate_edge_ids_are_rejected() -> None:
    request = TrajectoryAssemblyRequest(
        process_id="process-1",
        nodes=[
            TrajectoryNodeSpec(
                trajectory_node_id="node-a",
                record_ref="record-a",
                record_type="A",
            ),
            TrajectoryNodeSpec(
                trajectory_node_id="node-b",
                record_ref="record-b",
                record_type="B",
            ),
        ],
        edges=[
            TrajectoryEdgeSpec(
                trajectory_edge_id="edge-1",
                source_node_ref="node-a",
                target_node_ref="node-b",
                edge_type="RELATION_A",
            ),
            TrajectoryEdgeSpec(
                trajectory_edge_id="edge-1",
                source_node_ref="node-b",
                target_node_ref="node-a",
                edge_type="RELATION_B",
            ),
        ],
    )

    with pytest.raises(ValueError, match="TrajectoryEdge IDs"):
        TrajectoryAssemblyService().assemble(request)


def test_does_not_infer_edges_roots_terminals_or_authority() -> None:
    request = TrajectoryAssemblyRequest(
        process_id="process-1",
        nodes=[
            TrajectoryNodeSpec(
                trajectory_node_id="node-a",
                record_ref="record-a",
                record_type="A",
            ),
            TrajectoryNodeSpec(
                trajectory_node_id="node-b",
                record_ref="record-b",
                record_type="B",
            ),
        ],
    )

    result = TrajectoryAssemblyService().assemble(request)

    assert result.edges == []
    assert result.graph.root_node_refs == []
    assert result.graph.terminal_node_refs == []
    assert "current_node_ref" not in TrajectoryGraph.model_fields
    assert "preferred_path_ref" not in TrajectoryGraph.model_fields
    assert "authoritative_edge_ref" not in TrajectoryGraph.model_fields


def test_copies_nested_request_inputs() -> None:
    node_metadata = {"source": {"tags": ["explicit"]}}
    edge_metadata = {"relation": {"tags": ["explicit"]}}
    graph_metadata = {"graph": {"tags": ["explicit"]}}

    request = TrajectoryAssemblyRequest(
        process_id="process-1",
        nodes=[
            TrajectoryNodeSpec(
                trajectory_node_id="node-a",
                record_ref="record-a",
                record_type="A",
                metadata=node_metadata,
            ),
            TrajectoryNodeSpec(
                trajectory_node_id="node-b",
                record_ref="record-b",
                record_type="B",
            ),
        ],
        edges=[
            TrajectoryEdgeSpec(
                trajectory_edge_id="edge-a-b",
                source_node_ref="node-a",
                target_node_ref="node-b",
                edge_type="EXPLICIT_RELATION",
                metadata=edge_metadata,
            )
        ],
        graph_metadata=graph_metadata,
    )

    result = TrajectoryAssemblyService().assemble(request)
    node_metadata["source"]["tags"].append("mutated")
    edge_metadata["relation"]["tags"].append("mutated")
    graph_metadata["graph"]["tags"].append("mutated")

    assert result.nodes[0].metadata == {"source": {"tags": ["explicit"]}}
    assert result.edges[0].metadata == {"relation": {"tags": ["explicit"]}}
    assert result.graph.metadata == {"graph": {"tags": ["explicit"]}}
