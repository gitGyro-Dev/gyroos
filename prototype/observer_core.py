
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from gyroos_models import (
    Observer,
    ObserverID,
    ObserverRelation,
    ObserverStatus,
    RelationType,
    BalanceState,
)


@dataclass
class ObserverCore:
    """
    Minimal observer manager for GyroOS Mini Kernel.

    Responsibilities:
    - register observers
    - retrieve observers
    - update local goal / expectation / memory
    - maintain lightweight observer-to-observer relations
    """
    observers: Dict[ObserverID, Observer]

    def register_observer(self, observer: Observer) -> Observer:
        self.observers[observer.observer_id] = observer
        return observer

    def get_observer(self, observer_id: ObserverID) -> Optional[Observer]:
        return self.observers.get(observer_id)

    def list_observers(self) -> List[Observer]:
        return list(self.observers.values())

    def update_observer(
        self,
        observer_id: ObserverID,
        observation_result: Optional[dict] = None,
        balance_state: Optional[BalanceState] = None,
    ) -> Optional[Observer]:
        """
        Minimal observer update policy:
        - increments local time
        - remembers event ids when present
        - updates simple load / stability hints
        """
        observer = self.observers.get(observer_id)
        if observer is None:
            return None

        observer.tick()

        if observation_result:
            event_id = observation_result.get("event_id")
            if event_id:
                observer.remember_event(event_id)

            # lightweight learning hint
            perception_ids = observation_result.get("perception_ids", [])
            observer.metadata["last_perception_ids"] = perception_ids

        if balance_state:
            observer.status.load = max(0.0, balance_state.conflict_load)
            observer.status.stability = max(0.0, min(1.0, balance_state.stability_score))

        return observer

    def relate_observer(
        self,
        source_id: ObserverID,
        target_id: ObserverID,
        relation_type: RelationType,
        weight: float = 1.0,
    ) -> Optional[ObserverRelation]:
        source = self.observers.get(source_id)
        target = self.observers.get(target_id)
        if source is None or target is None:
            return None

        relation = ObserverRelation(
            source=source_id,
            target=target_id,
            relation_type=relation_type,
            weight=weight,
        )
        source.relations.append(relation)
        return relation

    def set_status(
        self,
        observer_id: ObserverID,
        active: Optional[bool] = None,
        load: Optional[float] = None,
        stability: Optional[float] = None,
        availability: Optional[float] = None,
    ) -> Optional[ObserverStatus]:
        observer = self.observers.get(observer_id)
        if observer is None:
            return None

        if active is not None:
            observer.status.active = active
        if load is not None:
            observer.status.load = load
        if stability is not None:
            observer.status.stability = stability
        if availability is not None:
            observer.status.availability = availability

        return observer.status
