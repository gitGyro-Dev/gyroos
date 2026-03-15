
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from gyroos_models import (
    Query,
    QueryID,
    QueryType,
    TargetSpec,
    TargetType,
    PatternSpec,
    WorldState,
    Observer,
    QueryStatus,
)


@dataclass
class QueryCore:
    """
    Minimal query engine for GyroOS Mini Kernel.

    Responsibilities:
    - generate observer-driven queries
    - generate simple world-driven queries
    - merge query signals
    - rank queries by lightweight priority rules
    """
    counter: int = 0

    def _next_id(self, prefix: str = "q") -> QueryID:
        self.counter += 1
        return f"{prefix}:{self.counter}"

    def generate_query(self, observer: Observer, world: WorldState) -> Query:
        """
        Generate an observer query from local goal + simple world hints.
        """
        goal_text = observer.local_goal.description.lower()

        # world-driven hint
        cpu_obj = world.objects.get("cpu")
        usage = None
        if cpu_obj is not None:
            usage = cpu_obj.attributes.get("usage")

        if "anomaly" in goal_text:
            condition = "cpu_usage > 80"
            priority = 1.0 if usage is not None and usage > 80 else 0.8
            qtype = QueryType.PATTERN
        elif "stability" in goal_text:
            condition = "system_stable"
            priority = 0.9 if usage is not None and usage < 85 else 0.7
            qtype = QueryType.COMPOSITE
        else:
            condition = "world_snapshot"
            priority = 0.5
            qtype = QueryType.STRUCTURAL

        query = Query(
            query_id=self._next_id(),
            issuer=observer.observer_id,
            query_type=qtype,
            target_spec=TargetSpec(target_type=TargetType.SUBSET),
            pattern_spec=PatternSpec(conditions={condition}),
            depth_hint=min(observer.capability.max_depth, 0.3),
            priority=priority,
            origin="merged",
            status=QueryStatus(active=True),
        )
        return query

    def generate_world_query(self, world: WorldState) -> List[Query]:
        """
        Generate world-side signals.
        For the mini kernel, emit a query when CPU usage is high.
        """
        queries: List[Query] = []
        cpu_obj = world.objects.get("cpu")
        if cpu_obj is not None:
            usage = cpu_obj.attributes.get("usage", 0)
            if isinstance(usage, (int, float)) and usage > 80:
                queries.append(
                    Query(
                        query_id=self._next_id(prefix="wq"),
                        issuer="world",
                        query_type=QueryType.PATTERN,
                        target_spec=TargetSpec(target_type=TargetType.OBJECT, target_ids={"cpu"}),
                        pattern_spec=PatternSpec(conditions={"cpu_usage > 80"}, anomaly_mode=True),
                        depth_hint=0.2,
                        priority=1.0,
                        origin="world_generated",
                    )
                )
        return queries

    def merge_queries(self, world_queries: List[Query], observer_query: Query) -> Query:
        """
        Merge simple world/observer signals.
        Current rule: if world emits a matching anomaly query,
        raise observer query priority.
        """
        merged = observer_query
        for wq in world_queries:
            if "cpu_usage > 80" in wq.pattern_spec.conditions and "cpu_usage > 80" in merged.pattern_spec.conditions:
                merged.priority = max(merged.priority, wq.priority)
                merged.origin = "merged"
        return merged

    def rank_query(self, query: Query) -> float:
        """
        Lightweight ranking score.
        """
        novelty_weight = query.priority
        depth_weight = 1.0 - min(query.depth_hint, 1.0) * 0.2
        return novelty_weight * depth_weight
