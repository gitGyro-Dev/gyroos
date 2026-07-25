from __future__ import annotations

from .builders import (
    TrajectoryEdgeBuilder,
    TrajectoryGraphBuilder,
    TrajectoryNodeBuilder,
)
from .models import (
    TrajectoryAssemblyRequest,
    TrajectoryAssemblyResult,
    TrajectoryNode,
)


class TrajectoryAssemblyService:
    """Assemble explicit Trajectory nodes, edges, and one graph in memory only.

    The service coordinates existing pure builders. It does not resolve referenced
    records, infer edges, calculate paths, select authority, derive branch/merge
    semantics, persist records, or modify Runtime behavior.
    """

    def __init__(self) -> None:
        self._node_builder = TrajectoryNodeBuilder()
        self._edge_builder = TrajectoryEdgeBuilder()
        self._graph_builder = TrajectoryGraphBuilder()

    def assemble(self, request: TrajectoryAssemblyRequest) -> TrajectoryAssemblyResult:
        nodes: list[TrajectoryNode] = []
        node_by_id: dict[str, TrajectoryNode] = {}

        for spec in request.nodes:
            node = self._node_builder.build(
                process_id=request.process_id,
                record_ref=spec.record_ref,
                record_type=spec.record_type,
                slice_ref=spec.slice_ref,
                node_role=spec.node_role,
                provisional=spec.provisional,
                metadata=spec.metadata,
                trajectory_node_id=spec.trajectory_node_id,
            )
            if node.trajectory_node_id in node_by_id:
                raise ValueError("TrajectoryNode IDs must be unique within one request")
            nodes.append(node)
            node_by_id[node.trajectory_node_id] = node

        edges = []
        edge_ids: set[str] = set()
        for spec in request.edges:
            source_node = self._require_node(
                node_by_id,
                spec.source_node_ref,
                "source_node_ref",
            )
            target_node = self._require_node(
                node_by_id,
                spec.target_node_ref,
                "target_node_ref",
            )
            edge = self._edge_builder.build(
                source_node=source_node,
                target_node=target_node,
                edge_type=spec.edge_type,
                relation_ref=spec.relation_ref,
                readable=spec.readable,
                provisional=spec.provisional,
                authoritative=spec.authoritative,
                evidence_refs=spec.evidence_refs,
                metadata=spec.metadata,
                trajectory_edge_id=spec.trajectory_edge_id,
                expected_source_node_ref=spec.source_node_ref,
                expected_target_node_ref=spec.target_node_ref,
            )
            if edge.trajectory_edge_id in edge_ids:
                raise ValueError("TrajectoryEdge IDs must be unique within one request")
            edges.append(edge)
            edge_ids.add(edge.trajectory_edge_id)

        graph = self._graph_builder.build(
            process_id=request.process_id,
            nodes=nodes,
            edges=edges,
            root_node_refs=request.root_node_refs,
            terminal_node_refs=request.terminal_node_refs,
            provisional=request.provisional,
            metadata=request.graph_metadata,
            trajectory_graph_id=request.trajectory_graph_id,
        )

        return TrajectoryAssemblyResult(
            nodes=nodes,
            edges=edges,
            graph=graph,
        )

    @staticmethod
    def _require_node(
        node_by_id: dict[str, TrajectoryNode],
        node_ref: str,
        field_name: str,
    ) -> TrajectoryNode:
        try:
            return node_by_id[node_ref]
        except KeyError as exc:
            raise ValueError(
                f"{field_name} must reference a TrajectoryNode in the same request"
            ) from exc
