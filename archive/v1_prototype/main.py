
from __future__ import annotations

"""
GyroOS Mini Kernel - minimal runnable demo

How to run:
    python main.py

Expected behavior:
- Creates a simple world with CPU / temperature / load metrics
- Registers two observers:
    * Observer A: anomaly_detection
    * Observer B: stability_check
- Generates queries from each observer
- Produces perceptions
- Detects conflict if perceptions differ
- Resolves conflict
- Records history
- Evaluates balance
- Applies rebalance and disturbance
"""

from dataclasses import asdict
from typing import Dict, List, Optional
import itertools
import time

from gyroos_models import (
    WorldState,
    Observer,
    ObserverType,
    GoalScope,
    ObjectRef,
    Perception,
    PerceptionID,
    SliceSignature,
    EvaluationHint,
    PatternMatch,
    ConflictSet,
    ConflictType,
    Resolution,
    ResolveMode,
    HistoryRecord,
    EventType,
    WorldDelta,
    BalanceState,
    RebalancePlan,
    make_simple_observer,
)
from world_core import WorldCore
from observer_core import ObserverCore
from query_core import QueryCore


# ============================================================
# Minimal local cores used only for the demo
# ============================================================

class ObservationCore:
    def __init__(self) -> None:
        self._perception_counter = itertools.count(1)
        self._conflict_counter = itertools.count(1)
        self._resolution_counter = itertools.count(1)
        self._event_counter = itertools.count(1)

    def observe(self, observer: Observer, query, world: WorldState) -> Perception:
        cpu = world.objects.get("cpu")
        attrs = cpu.attributes if cpu else {}

        usage = float(attrs.get("usage", 0))
        temp = float(attrs.get("temp", 0))
        load = float(attrs.get("load", 0))

        conditions = query.pattern_spec.conditions
        recognized_patterns = []
        confidence_map = {}
        semantic_context = ""

        # Minimal interpretation rules
        if "cpu_usage > 80" in conditions:
            is_anomaly = usage > 80 or temp > 75
            semantic_context = "anomaly_detection"
            score = 0.92 if is_anomaly else 0.28
            recognized_patterns.append(
                PatternMatch(
                    pattern_id="pattern:cpu_anomaly" if is_anomaly else "pattern:cpu_normal",
                    score=score,
                    matched_features={"usage", "temp"},
                )
            )
            confidence_map["anomaly"] = score

        elif "system_stable" in conditions:
            stable = usage < 85 and load < 4.0 and temp < 78
            semantic_context = "stability_check"
            score = 0.88 if stable else 0.35
            recognized_patterns.append(
                PatternMatch(
                    pattern_id="pattern:system_stable" if stable else "pattern:system_unstable",
                    score=score,
                    matched_features={"usage", "load", "temp"},
                )
            )
            confidence_map["stability"] = score

        else:
            semantic_context = "world_snapshot"
            recognized_patterns.append(
                PatternMatch(
                    pattern_id="pattern:world_snapshot",
                    score=0.5,
                    matched_features={"usage", "load", "temp"},
                )
            )
            confidence_map["snapshot"] = 0.5

        pid = f"p:{next(self._perception_counter)}"
        perception = Perception(
            perception_id=pid,
            observer_id=observer.observer_id,
            source_query=query.query_id,
            world_ref=world.world_id,
            slice_signature=SliceSignature(
                depth=query.depth_hint,
                semantic_context=semantic_context,
            ),
            recognized_objects=[
                ObjectRef(
                    object_id="cpu",
                    object_type="metric",
                    attributes={"usage": usage, "temp": temp, "load": load},
                )
            ],
            recognized_patterns=recognized_patterns,
            confidence_map=confidence_map,
            evaluation_hint=EvaluationHint(
                local_fitness=max(confidence_map.values()) if confidence_map else 0.0,
                global_alignment=0.6,
                conflict_risk=0.2,
                novelty_score=0.3,
            ),
            timestamp=world.physical_time,
        )
        return perception

    def batch_observe(self, observers: List[Observer], queries: List, world: WorldState) -> Dict:
        perceptions = []
        for observer, query in zip(observers, queries):
            perceptions.append(self.observe(observer, query, world))

        conflicts = self.detect_conflict(perceptions)
        resolution = self.resolve_conflict(conflicts, ResolveMode.MERGE if conflicts else ResolveMode.COEXIST)

        # Disturbance: if there is conflict, slightly larger disturbance
        changed_objects = {"cpu"} if world.objects.get("cpu") else set()
        disturbance_score = 0.3 if conflicts else 0.1
        delta = WorldDelta(
            changed_objects=changed_objects,
            disturbance_score=disturbance_score,
            semantic_shift=0.2 if conflicts else 0.05,
            balance_shift=0.15 if conflicts else 0.03,
        )

        event_id = f"evt:{next(self._event_counter)}"
        return {
            "event_id": event_id,
            "perceptions": perceptions,
            "perception_ids": [p.perception_id for p in perceptions],
            "conflicts": conflicts,
            "resolution": resolution,
            "disturbance": delta,
        }

    def detect_conflict(self, perceptions: List[Perception]) -> List[ConflictSet]:
        if len(perceptions) < 2:
            return []

        labels = []
        for p in perceptions:
            if not p.recognized_patterns:
                labels.append("unknown")
            else:
                labels.append(p.recognized_patterns[0].pattern_id)

        if len(set(labels)) == 1:
            return []

        cid = f"c:{next(self._conflict_counter)}"
        conflict = ConflictSet(
            conflict_id=cid,
            perceptions=[p.perception_id for p in perceptions],
            conflict_type=ConflictType.INTERPRETATION_GAP,
            severity=0.7,
            scope="local",
            detected_at=perceptions[0].timestamp if perceptions else 0.0,
            status="open",
        )
        return [conflict]

    def resolve_conflict(self, conflicts: List[ConflictSet], mode: ResolveMode) -> Optional[Resolution]:
        if not conflicts:
            return None

        conflict = conflicts[0]
        rid = f"r:{next(self._resolution_counter)}"
        resolution = Resolution(
            resolution_id=rid,
            conflict_id=conflict.conflict_id,
            mode=mode,
            selected_perceptions=conflict.perceptions[:],
            merged_perception=None,
            pending_reason=None if mode != ResolveMode.PENDING else "awaiting_more_observation",
            applied_weights={pid: 0.5 for pid in conflict.perceptions},
            resolved_at=time.time(),
        )
        conflict.status = "resolved"
        return resolution


class HistoryCore:
    def __init__(self) -> None:
        self.records: List[HistoryRecord] = []

    def append_event(
        self,
        world: WorldState,
        result: Dict,
    ) -> HistoryRecord:
        record = HistoryRecord(
            event_id=result["event_id"],
            event_type=EventType.OBSERVATION,
            physical_time=world.physical_time,
            event_time=world.event_time,
            semantic_time=world.semantic_time,
            observer_ids=[p.observer_id for p in result["perceptions"]],
            query_ids=[p.source_query for p in result["perceptions"]],
            perception_ids=[p.perception_id for p in result["perceptions"]],
            conflict_ids=[c.conflict_id for c in result["conflicts"]],
            resolution_ids=[result["resolution"].resolution_id] if result["resolution"] else [],
            local_goal_snapshot={},
            global_goal_snapshot=world.global_goal,
            balance_snapshot=world.balance_state,
            world_delta=result["disturbance"],
        )
        self.records.append(record)
        return record

    def get_recent_events(self, limit: int = 5) -> List[HistoryRecord]:
        return self.records[-limit:]

    def replay_history(self) -> List[HistoryRecord]:
        return self.records[:]


class BalanceCore:
    def evaluate_balance(self, world: WorldState, observers: List[Observer], recent_events: List[HistoryRecord]) -> BalanceState:
        conflict_load = 0.0
        if recent_events:
            conflict_events = sum(1 for e in recent_events if e.conflict_ids)
            conflict_load = conflict_events / max(len(recent_events), 1)

        # very simple demo metrics
        stability = max(0.0, 1.0 - conflict_load * 0.5)
        exploration = min(1.0, 0.2 + len(observers) * 0.1)
        balance = max(0.0, (stability + exploration) / 2.0)

        state = BalanceState(
            balance_score=balance,
            stability_score=stability,
            exploration_score=exploration,
            adaptation_score=0.4,
            conflict_load=conflict_load,
            goal_alignment_score=0.7,
            observer_diversity_score=min(1.0, len(observers) * 0.25),
            timestamp=world.physical_time,
        )
        return state

    def make_rebalance_plan(self, balance_state: BalanceState) -> RebalancePlan:
        gain = 0.05 if balance_state.conflict_load > 0 else 0.02
        return RebalancePlan(
            plan_id=f"rb:{int(time.time()*1000)}",
            target_scope="mini_kernel",
            expected_balance_gain=gain,
        )


# ============================================================
# Demo scenario
# ============================================================

def print_world(world: WorldState) -> None:
    cpu = world.objects.get("cpu")
    if not cpu:
        print("World has no CPU object.")
        return
    attrs = cpu.attributes
    print(
        f"[WORLD] tick={world.tick} "
        f"usage={attrs.get('usage'):.2f} "
        f"temp={attrs.get('temp'):.2f} "
        f"load={attrs.get('load'):.2f}"
    )


def print_perception(p: Perception) -> None:
    pattern = p.recognized_patterns[0].pattern_id if p.recognized_patterns else "none"
    score = p.recognized_patterns[0].score if p.recognized_patterns else 0.0
    print(
        f"  [PERCEPTION] observer={p.observer_id} "
        f"query={p.source_query} "
        f"pattern={pattern} "
        f"score={score:.2f}"
    )


def main() -> None:
    # 1. Create world and cores
    world = WorldState(world_id="world:gyro-mini")
    world_core = WorldCore(world=world)
    observer_core = ObserverCore(observers=world.observers)
    query_core = QueryCore()
    observation_core = ObservationCore()
    history_core = HistoryCore()
    balance_core = BalanceCore()

    # 2. Populate world
    world_core.add_object(
        object_id="cpu",
        object_type="metric",
        attributes={"usage": 87.0, "temp": 72.0, "load": 3.2},
    )

    # 3. Register observers
    observer_a = make_simple_observer(
        observer_id="obs:A",
        name="Observer A",
        observer_type=ObserverType.AI_AGENT,
        goal_description="anomaly_detection",
        goal_scope=GoalScope.LOCAL,
    )
    observer_b = make_simple_observer(
        observer_id="obs:B",
        name="Observer B",
        observer_type=ObserverType.PROCESS,
        goal_description="stability_check",
        goal_scope=GoalScope.LOCAL,
    )

    observer_core.register_observer(observer_a)
    observer_core.register_observer(observer_b)

    # 4. Mini loop
    for _ in range(3):
        world_core.step_world(dt=1.0)
        print_world(world)

        observers = observer_core.list_observers()
        world_queries = query_core.generate_world_query(world)

        queries = []
        for obs in observers:
            q = query_core.generate_query(obs, world)
            q = query_core.merge_queries(world_queries, q)
            q.clamp_depth(obs.capability.max_depth)
            world.add_query(q)
            queries.append(q)
            print(
                f"  [QUERY] observer={obs.observer_id} "
                f"id={q.query_id} "
                f"conditions={sorted(list(q.pattern_spec.conditions))} "
                f"depth={q.depth_hint:.2f} priority={q.priority:.2f}"
            )

        result = observation_core.batch_observe(observers, queries, world)

        for p in result["perceptions"]:
            print_perception(p)

        if result["conflicts"]:
            for c in result["conflicts"]:
                print(
                    f"  [CONFLICT] id={c.conflict_id} "
                    f"type={c.conflict_type.value} severity={c.severity:.2f}"
                )
        else:
            print("  [CONFLICT] none")

        if result["resolution"]:
            r = result["resolution"]
            print(
                f"  [RESOLUTION] id={r.resolution_id} "
                f"mode={r.mode.value}"
            )

        record = history_core.append_event(world, result)
        balance = balance_core.evaluate_balance(world, observers, history_core.get_recent_events())
        plan = balance_core.make_rebalance_plan(balance)

        world.balance_state = balance
        world_core.apply_disturbance(result["disturbance"])
        world_core.apply_rebalance(plan)

        for obs in observers:
            observer_core.update_observer(
                observer_id=obs.observer_id,
                observation_result={
                    "event_id": record.event_id,
                    "perception_ids": result["perception_ids"],
                },
                balance_state=balance,
            )

        print(
            f"  [BALANCE] balance={balance.balance_score:.2f} "
            f"stability={balance.stability_score:.2f} "
            f"exploration={balance.exploration_score:.2f} "
            f"conflict_load={balance.conflict_load:.2f}"
        )
        print("-" * 72)

    # 5. Summary
    print("\n=== HISTORY SUMMARY ===")
    for rec in history_core.replay_history():
        print(
            f"event={rec.event_id} "
            f"tick={rec.event_time} "
            f"perceptions={rec.perception_ids} "
            f"conflicts={rec.conflict_ids} "
            f"resolutions={rec.resolution_ids}"
        )


if __name__ == "__main__":
    main()
