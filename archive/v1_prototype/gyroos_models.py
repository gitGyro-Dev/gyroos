
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


# ============================================================
# GyroOS Mini Kernel - Python Data Model Definitions
# ============================================================


# ----------------------------
# Basic aliases
# ----------------------------
WorldID = str
ObserverID = str
ObjectID = str
QueryID = str
PerceptionID = str
ConflictID = str
ResolutionID = str
EventID = str
GoalID = str
PatternID = str
ModelID = str


# ----------------------------
# Enums
# ----------------------------
class ObserverType(str, Enum):
    HUMAN = "human"
    AI_AGENT = "ai_agent"
    PROCESS = "process"
    SENSOR = "sensor"
    KERNEL_AGENT = "kernel_agent"


class QueryType(str, Enum):
    SPATIAL = "spatial"
    STRUCTURAL = "structural"
    PATTERN = "pattern"
    COMPOSITE = "composite"


class TargetType(str, Enum):
    WORLD = "world"
    SUBSET = "subset"
    SELF = "self"
    OBJECT = "object"
    RELATION = "relation"


class RelationType(str, Enum):
    TRUST = "trust"
    AUTHORITY = "authority"
    DEPENDENCY = "dependency"
    CONTRADICTION = "contradiction"
    SYNCHRONIZATION = "synchronization"
    INHERITANCE = "inheritance"


class ConflictType(str, Enum):
    CONTRADICTION = "contradiction"
    MISMATCH = "mismatch"
    PRIORITY_COLLISION = "priority_collision"
    INTERPRETATION_GAP = "interpretation_gap"
    GOAL_CONFLICT = "goal_conflict"


class ResolveMode(str, Enum):
    COEXIST = "coexist"
    PRIORITY = "priority"
    MERGE = "merge"
    PENDING = "pending"


class GoalScope(str, Enum):
    LOCAL = "local"
    GLOBAL = "global"
    SHARED = "shared"


class EventType(str, Enum):
    OBSERVATION = "observation"
    QUERY_GENERATION = "query_generation"
    CONFLICT_DETECTION = "conflict_detection"
    CONFLICT_RESOLUTION = "conflict_resolution"
    GOAL_UPDATE = "goal_update"
    REBALANCE = "rebalance"
    REPLAY = "replay"


# ----------------------------
# Core helper structures
# ----------------------------
@dataclass
class Identity:
    name: str
    observer_type: ObserverType
    namespace: str = "default"
    authority_level: int = 0
    trust_score: float = 1.0


@dataclass
class CapabilityProfile:
    max_depth: float = 1.0
    allowed_query_types: Set[QueryType] = field(default_factory=set)
    allowed_targets: Set[TargetType] = field(default_factory=set)
    allowed_actions: Set[str] = field(default_factory=set)
    write_permission: bool = False
    self_observation_permission: bool = True

    def can_query(self, query_type: QueryType) -> bool:
        return not self.allowed_query_types or query_type in self.allowed_query_types


@dataclass
class Filter:
    filter_id: str
    target_features: Set[str] = field(default_factory=set)
    weight_map: Dict[str, float] = field(default_factory=dict)
    sensitivity: float = 1.0


@dataclass
class Hypothesis:
    hypothesis_id: str
    description: str
    condition: str = ""
    confidence: float = 0.5


@dataclass
class GoalBias:
    preferred_outcomes: Set[str] = field(default_factory=set)
    penalty_rules: Set[str] = field(default_factory=set)
    optimization_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class PriorityProfile:
    novelty_weight: float = 1.0
    risk_weight: float = 1.0
    goal_relevance_weight: float = 1.0
    recency_weight: float = 1.0


@dataclass
class UpdatePolicy:
    learning_rate: float = 0.1
    adaptation_mode: str = "incremental"
    forgetting_factor: float = 0.0


@dataclass
class Expectation:
    expectation_id: str
    filters: List[Filter] = field(default_factory=list)
    hypotheses: List[Hypothesis] = field(default_factory=list)
    goal_bias: GoalBias = field(default_factory=GoalBias)
    priority_profile: PriorityProfile = field(default_factory=PriorityProfile)
    update_policy: UpdatePolicy = field(default_factory=UpdatePolicy)


@dataclass
class OptimizationProfile:
    stability_weight: float = 1.0
    exploration_weight: float = 1.0
    adaptation_weight: float = 1.0
    efficiency_weight: float = 1.0
    safety_weight: float = 1.0


@dataclass
class Goal:
    goal_id: GoalID
    scope: GoalScope
    description: str
    target_patterns: Set[str] = field(default_factory=set)
    optimization_profile: OptimizationProfile = field(default_factory=OptimizationProfile)
    constraints: Set[str] = field(default_factory=set)
    priority: float = 1.0
    mutability: float = 0.5
    validity_window: Optional[str] = None


@dataclass
class PredictionProfile:
    strategy: str = "default"
    horizon: int = 1
    confidence: float = 0.5


@dataclass
class ObserverModel:
    model_id: ModelID
    hypothesis_set: List[Hypothesis] = field(default_factory=list)
    pattern_library: Set[str] = field(default_factory=set)
    prediction_profile: PredictionProfile = field(default_factory=PredictionProfile)
    confidence: float = 0.5


@dataclass
class MemoryState:
    recent_events: List[EventID] = field(default_factory=list)
    summarized_history: List[str] = field(default_factory=list)
    retained_perceptions: List[PerceptionID] = field(default_factory=list)
    learning_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ObserverRelation:
    source: ObserverID
    target: ObserverID
    relation_type: RelationType
    weight: float = 1.0


@dataclass
class ObserverStatus:
    active: bool = True
    load: float = 0.0
    stability: float = 1.0
    availability: float = 1.0


@dataclass
class Observer:
    observer_id: ObserverID
    identity: Identity
    capability: CapabilityProfile
    expectation: Expectation
    model: ObserverModel
    memory: MemoryState
    local_goal: Goal
    relations: List[ObserverRelation] = field(default_factory=list)
    local_time: int = 0
    status: ObserverStatus = field(default_factory=ObserverStatus)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def tick(self) -> None:
        self.local_time += 1

    def remember_event(self, event_id: EventID) -> None:
        self.memory.recent_events.append(event_id)


@dataclass
class ObjectRef:
    object_id: ObjectID
    object_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TargetSpec:
    target_type: TargetType
    target_ids: Set[ObjectID] = field(default_factory=set)
    target_labels: Set[str] = field(default_factory=set)


@dataclass
class PatternSpec:
    conditions: Set[str] = field(default_factory=set)
    thresholds: Dict[str, float] = field(default_factory=dict)
    anomaly_mode: bool = False


@dataclass
class StructureSpec:
    object_type: str = ""
    relation_constraints: Set[str] = field(default_factory=set)


@dataclass
class SpatialSpec:
    coordinates: Optional[tuple] = None
    region: Optional[str] = None
    scope: str = "local"


@dataclass
class TimeScope:
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    event_range: Optional[tuple] = None


@dataclass
class QueryStatus:
    active: bool = True
    resolved: bool = False
    expired: bool = False


@dataclass
class Query:
    query_id: QueryID
    issuer: ObserverID
    query_type: QueryType
    target_spec: TargetSpec
    pattern_spec: PatternSpec = field(default_factory=PatternSpec)
    structure_spec: StructureSpec = field(default_factory=StructureSpec)
    spatial_spec: SpatialSpec = field(default_factory=SpatialSpec)
    depth_hint: float = 0.1
    priority: float = 1.0
    time_scope: Optional[TimeScope] = None
    origin: str = "observer_generated"
    status: QueryStatus = field(default_factory=QueryStatus)

    def clamp_depth(self, max_depth: float) -> None:
        self.depth_hint = min(self.depth_hint, max_depth)


@dataclass
class SliceSignature:
    depth: float
    filter_profile: List[str] = field(default_factory=list)
    hypothesis_profile: List[str] = field(default_factory=list)
    semantic_context: str = ""


@dataclass
class PatternMatch:
    pattern_id: PatternID
    score: float
    matched_features: Set[str] = field(default_factory=set)


@dataclass
class RelationObservation:
    source: ObjectID
    target: ObjectID
    relation_type: str
    weight: float = 1.0


@dataclass
class EvaluationHint:
    local_fitness: float = 0.0
    global_alignment: float = 0.0
    conflict_risk: float = 0.0
    novelty_score: float = 0.0


@dataclass
class Perception:
    perception_id: PerceptionID
    observer_id: ObserverID
    source_query: QueryID
    world_ref: WorldID
    slice_signature: SliceSignature
    recognized_objects: List[ObjectRef] = field(default_factory=list)
    recognized_patterns: List[PatternMatch] = field(default_factory=list)
    recognized_relations: List[RelationObservation] = field(default_factory=list)
    confidence_map: Dict[str, float] = field(default_factory=dict)
    evaluation_hint: EvaluationHint = field(default_factory=EvaluationHint)
    timestamp: float = 0.0


@dataclass
class ConflictSet:
    conflict_id: ConflictID
    perceptions: List[PerceptionID]
    conflict_type: ConflictType
    severity: float = 0.0
    scope: str = "local"
    detected_at: float = 0.0
    status: str = "open"


@dataclass
class Resolution:
    resolution_id: ResolutionID
    conflict_id: ConflictID
    mode: ResolveMode
    selected_perceptions: List[PerceptionID] = field(default_factory=list)
    merged_perception: Optional[PerceptionID] = None
    pending_reason: Optional[str] = None
    applied_weights: Dict[PerceptionID, float] = field(default_factory=dict)
    resolved_at: float = 0.0


@dataclass
class WorldDelta:
    changed_objects: Set[ObjectID] = field(default_factory=set)
    disturbance_score: float = 0.0
    semantic_shift: float = 0.0
    balance_shift: float = 0.0


@dataclass
class BalanceState:
    balance_score: float = 1.0
    stability_score: float = 1.0
    exploration_score: float = 0.0
    adaptation_score: float = 0.0
    conflict_load: float = 0.0
    goal_alignment_score: float = 1.0
    observer_diversity_score: float = 0.0
    timestamp: float = 0.0


@dataclass
class HistoryRecord:
    event_id: EventID
    event_type: EventType
    physical_time: float
    event_time: int
    semantic_time: int
    observer_ids: List[ObserverID] = field(default_factory=list)
    query_ids: List[QueryID] = field(default_factory=list)
    perception_ids: List[PerceptionID] = field(default_factory=list)
    conflict_ids: List[ConflictID] = field(default_factory=list)
    resolution_ids: List[ResolutionID] = field(default_factory=list)
    local_goal_snapshot: Dict[ObserverID, Goal] = field(default_factory=dict)
    global_goal_snapshot: Optional[Goal] = None
    balance_snapshot: Optional[BalanceState] = None
    world_delta: WorldDelta = field(default_factory=WorldDelta)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryPriorityPatch:
    query_id: QueryID
    new_priority: float


@dataclass
class DepthPatch:
    observer_id: ObserverID
    new_max_depth: float


@dataclass
class GoalPatch:
    goal_id: GoalID
    new_priority: float


@dataclass
class RelationPatch:
    source: ObserverID
    target: ObserverID
    relation_type: RelationType
    new_weight: float


@dataclass
class ConflictPolicyPatch:
    conflict_type: ConflictType
    preferred_mode: ResolveMode


@dataclass
class RebalancePlan:
    plan_id: str
    target_scope: str
    query_priority_updates: List[QueryPriorityPatch] = field(default_factory=list)
    depth_limit_updates: List[DepthPatch] = field(default_factory=list)
    goal_weight_updates: List[GoalPatch] = field(default_factory=list)
    relation_updates: List[RelationPatch] = field(default_factory=list)
    conflict_policy_updates: List[ConflictPolicyPatch] = field(default_factory=list)
    expected_balance_gain: float = 0.0


@dataclass
class WorldState:
    world_id: WorldID
    tick: int = 0
    physical_time: float = 0.0
    event_time: int = 0
    semantic_time: int = 0
    observers: Dict[ObserverID, Observer] = field(default_factory=dict)
    objects: Dict[ObjectID, ObjectRef] = field(default_factory=dict)
    active_queries: Dict[QueryID, Query] = field(default_factory=dict)
    active_conflicts: Dict[ConflictID, ConflictSet] = field(default_factory=dict)
    global_goal: Optional[Goal] = None
    balance_state: BalanceState = field(default_factory=BalanceState)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def next_tick(self, dt: float = 1.0) -> None:
        self.tick += 1
        self.physical_time += dt
        self.event_time += 1

    def add_object(self, obj: ObjectRef) -> None:
        self.objects[obj.object_id] = obj

    def add_observer(self, observer: Observer) -> None:
        self.observers[observer.observer_id] = observer

    def add_query(self, query: Query) -> None:
        self.active_queries[query.query_id] = query

    def add_conflict(self, conflict: ConflictSet) -> None:
        self.active_conflicts[conflict.conflict_id] = conflict


# ----------------------------
# Minimal factory helpers
# ----------------------------
def make_simple_observer(
    observer_id: str,
    name: str,
    observer_type: ObserverType,
    goal_description: str,
    goal_scope: GoalScope = GoalScope.LOCAL,
) -> Observer:
    goal = Goal(
        goal_id=f"goal:{observer_id}",
        scope=goal_scope,
        description=goal_description,
    )
    identity = Identity(name=name, observer_type=observer_type)
    capability = CapabilityProfile(
        max_depth=0.5,
        allowed_query_types={QueryType.PATTERN, QueryType.STRUCTURAL, QueryType.COMPOSITE},
        allowed_targets={TargetType.WORLD, TargetType.SUBSET, TargetType.OBJECT},
        allowed_actions={"observe", "slice"},
        write_permission=False,
    )
    expectation = Expectation(expectation_id=f"exp:{observer_id}")
    model = ObserverModel(model_id=f"model:{observer_id}")
    memory = MemoryState()
    return Observer(
        observer_id=observer_id,
        identity=identity,
        capability=capability,
        expectation=expectation,
        model=model,
        memory=memory,
        local_goal=goal,
    )


def make_simple_query(
    query_id: str,
    issuer: str,
    condition: str,
    depth: float = 0.1,
    priority: float = 1.0,
) -> Query:
    return Query(
        query_id=query_id,
        issuer=issuer,
        query_type=QueryType.PATTERN,
        target_spec=TargetSpec(target_type=TargetType.SUBSET),
        pattern_spec=PatternSpec(conditions={condition}),
        depth_hint=depth,
        priority=priority,
    )


if __name__ == "__main__":
    # Example usage
    world = WorldState(world_id="world:demo")
    observer_a = make_simple_observer("obs:A", "Observer A", ObserverType.AI_AGENT, "anomaly_detection")
    observer_b = make_simple_observer("obs:B", "Observer B", ObserverType.PROCESS, "stability_check")

    world.add_observer(observer_a)
    world.add_observer(observer_b)
    world.add_object(ObjectRef(object_id="cpu", object_type="metric", attributes={"usage": 87, "temp": 72}))

    query_a = make_simple_query("q:A:1", "obs:A", "cpu_usage > 80", depth=0.3, priority=1.0)
    query_b = make_simple_query("q:B:1", "obs:B", "system_stable", depth=0.2, priority=0.8)

    world.add_query(query_a)
    world.add_query(query_b)

    print("GyroOS mini data model loaded.")
    print(f"Observers: {list(world.observers.keys())}")
    print(f"Objects: {list(world.objects.keys())}")
    print(f"Queries: {list(world.active_queries.keys())}")
