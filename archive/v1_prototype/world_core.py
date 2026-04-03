
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from gyroos_models import WorldState, ObjectRef, WorldDelta, RebalancePlan


@dataclass
class WorldCore:
    """
    Minimal world manager for GyroOS Mini Kernel.

    Responsibilities:
    - keep current WorldState
    - advance world time
    - apply small natural drift to numeric attributes
    - apply observation disturbances
    - apply rebalance effects
    """
    world: WorldState
    natural_drift: Dict[str, float] = field(default_factory=lambda: {
        "usage": 0.5,
        "temp": 0.2,
        "load": 0.1,
    })

    def get_world(self) -> WorldState:
        return self.world

    def step_world(self, dt: float = 1.0) -> WorldState:
        """
        Advance world time and apply a very small deterministic drift
        to numeric object attributes.
        """
        self.world.next_tick(dt=dt)

        for obj in self.world.objects.values():
            self._apply_natural_drift(obj)

        return self.world

    def _apply_natural_drift(self, obj: ObjectRef) -> None:
        for key, drift in self.natural_drift.items():
            if key in obj.attributes and isinstance(obj.attributes[key], (int, float)):
                obj.attributes[key] = obj.attributes[key] + drift

    def apply_disturbance(self, delta: WorldDelta) -> WorldState:
        """
        Apply observation-side effects to the world.
        For the mini kernel, we update metadata and slightly nudge changed objects.
        """
        self.world.metadata["last_disturbance_score"] = delta.disturbance_score
        self.world.metadata["last_semantic_shift"] = delta.semantic_shift
        self.world.metadata["last_balance_shift"] = delta.balance_shift

        for object_id in delta.changed_objects:
            obj = self.world.objects.get(object_id)
            if obj is None:
                continue

            # Minimal side-effect rule:
            # if the object has numeric metrics, nudge them slightly.
            for key, value in list(obj.attributes.items()):
                if isinstance(value, (int, float)):
                    obj.attributes[key] = value + (0.05 * delta.disturbance_score)

        return self.world

    def apply_rebalance(self, plan: RebalancePlan) -> WorldState:
        """
        Apply rebalance effects to world metadata.
        In a larger kernel, this would also affect query priorities,
        observer constraints, and deeper policy state.
        """
        self.world.metadata["last_rebalance_plan"] = plan.plan_id
        self.world.metadata["expected_balance_gain"] = plan.expected_balance_gain
        self.world.balance_state.balance_score += plan.expected_balance_gain
        return self.world

    def add_object(self, object_id: str, object_type: str, attributes: Optional[Dict[str, Any]] = None) -> ObjectRef:
        obj = ObjectRef(
            object_id=object_id,
            object_type=object_type,
            attributes=attributes or {},
        )
        self.world.add_object(obj)
        return obj
