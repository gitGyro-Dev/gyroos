from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VNextModel(BaseModel):
    """Closed experimental model boundary for the vNext semantic PoC."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class DifferenceRepresentationType(str, Enum):
    SCALAR = "SCALAR"
    VECTOR = "VECTOR"
    TUPLE = "TUPLE"
    RELATION = "RELATION"
    CATEGORY = "CATEGORY"
    PARTIAL_ORDER = "PARTIAL_ORDER"
    SYMBOLIC = "SYMBOLIC"
    DISTRIBUTION = "DISTRIBUTION"
    FIELD = "FIELD"
    DOMAIN_DEFINED = "DOMAIN_DEFINED"


class BoundaryReadabilityState(str, Enum):
    UNREADABLE = "UNREADABLE"
    CANDIDATE = "CANDIDATE"
    READABLE_DISTINCTION = "READABLE_DISTINCTION"
    USABLE_BOUNDARY = "USABLE_BOUNDARY"


class LocalArticulation(VNextModel):
    articulation_id: str
    process_id: str
    slice_ref: str
    representation: dict[str, Any]
    readable: bool = True
    source_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReadableRelation(VNextModel):
    relation_id: str
    source_ref: str
    target_ref: str | None = None
    relation_type: str
    readable: bool = True
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UnresolvedLocalItem(VNextModel):
    unresolved_item_id: str
    description: str
    reason: str | None = None
    related_refs: list[str] = Field(default_factory=list)
    provisional: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContinuationCondition(VNextModel):
    condition_id: str
    description: str
    satisfied: bool | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    policy_ref: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StabilityScene(VNextModel):
    """Runtime representation of K_n; not a scalar Stability score."""

    stability_scene_id: str
    process_id: str
    slice_ref: str
    articulation: LocalArticulation
    readable_relations: list[ReadableRelation] = Field(default_factory=list)
    unresolved_local_items: list[UnresolvedLocalItem] = Field(default_factory=list)
    continuation_conditions: list[ContinuationCondition] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class StabilityObservation(VNextModel):
    """Optional observation of a StabilityScene; it does not replace the scene."""

    stability_observation_id: str
    stability_scene_ref: str
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    classification: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    policy_ref: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    observed_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DifferenceObject(VNextModel):
    """Slice-relative Difference without assuming distance, error, or scalar form."""

    difference_id: str
    process_id: str
    slice_ref: str
    orientation_ref: str | None = None
    context_refs: list[str] = Field(default_factory=list)
    representation_type: DifferenceRepresentationType
    representation: Any
    defined: bool = True
    comparable: bool | None = None
    evaluative: bool = False
    slice_relative: bool = True
    source_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_defined_representation(self) -> "DifferenceObject":
        if self.defined and self.representation is None:
            raise ValueError("defined DifferenceObject requires representation")
        return self


class BoundaryEvaluation(VNextModel):
    """Evaluation of whether Difference is readable and usable as a Boundary."""

    boundary_evaluation_id: str
    process_id: str
    slice_ref: str
    difference_ref: str
    orientation_ref: str | None = None
    context_refs: list[str] = Field(default_factory=list)
    readability_state: BoundaryReadabilityState
    readable_as_distinction: bool
    usable_distinction: bool
    provisional: bool = True
    policy_ref: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_readability_consistency(self) -> "BoundaryEvaluation":
        if self.usable_distinction and not self.readable_as_distinction:
            raise ValueError(
                "usable Boundary distinction requires readable_as_distinction=true"
            )
        if (
            self.readability_state == BoundaryReadabilityState.USABLE_BOUNDARY
            and not self.usable_distinction
        ):
            raise ValueError(
                "USABLE_BOUNDARY state requires usable_distinction=true"
            )
        return self


class SemanticRealizationBundle(VNextModel):
    """Reference-only grouping of isolated vNext semantic records.

    The bundle is not a canonical Process result, persistence transaction, or
    evaluation engine. It only records that the referenced objects belong to
    one explicit process and slice scope.
    """

    semantic_bundle_id: str
    process_id: str
    slice_ref: str
    stability_scene_ref: str
    stability_observation_refs: list[str] = Field(default_factory=list)
    difference_refs: list[str] = Field(default_factory=list)
    boundary_evaluation_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class StabilityObservationSpec(VNextModel):
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    classification: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    policy_ref: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    stability_observation_id: str | None = None


class DifferenceSpec(VNextModel):
    representation_type: DifferenceRepresentationType
    representation: Any
    orientation_ref: str | None = None
    context_refs: list[str] = Field(default_factory=list)
    defined: bool = True
    comparable: bool | None = None
    evaluative: bool = False
    slice_relative: bool = True
    source_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    difference_id: str | None = None


class BoundaryEvaluationSpec(VNextModel):
    difference_ref: str
    readability_state: BoundaryReadabilityState
    readable_as_distinction: bool
    usable_distinction: bool
    provisional: bool = True
    orientation_ref: str | None = None
    context_refs: list[str] | None = None
    policy_ref: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    boundary_evaluation_id: str | None = None


class SemanticAssemblyRequest(VNextModel):
    """Explicit input specification for isolated semantic assembly only."""

    process_id: str
    slice_ref: str
    articulation: LocalArticulation
    readable_relations: list[ReadableRelation] = Field(default_factory=list)
    unresolved_local_items: list[UnresolvedLocalItem] = Field(default_factory=list)
    continuation_conditions: list[ContinuationCondition] = Field(default_factory=list)
    scene_evidence_refs: list[str] = Field(default_factory=list)
    scene_metadata: dict[str, Any] = Field(default_factory=dict)
    stability_scene_id: str | None = None
    observations: list[StabilityObservationSpec] = Field(default_factory=list)
    differences: list[DifferenceSpec] = Field(default_factory=list)
    boundary_evaluations: list[BoundaryEvaluationSpec] = Field(default_factory=list)
    bundle_metadata: dict[str, Any] = Field(default_factory=dict)
    semantic_bundle_id: str | None = None


class SemanticAssemblyResult(VNextModel):
    """Complete in-memory output of one isolated semantic assembly operation."""

    scene: StabilityScene
    observations: list[StabilityObservation] = Field(default_factory=list)
    differences: list[DifferenceObject] = Field(default_factory=list)
    boundary_evaluations: list[BoundaryEvaluation] = Field(default_factory=list)
    bundle: SemanticRealizationBundle


class ReadabilityContext(VNextModel):
    """Explicit readability state available at one runtime point.

    This is not raw history storage, model training state, or a complete Context
    object. It records which items are currently available as readable inputs.
    """

    readability_context_id: str
    process_id: str
    slice_ref: str
    readable_item_refs: list[str] = Field(default_factory=list)
    unresolved_item_refs: list[str] = Field(default_factory=list)
    excluded_item_refs: list[str] = Field(default_factory=list)
    source_context_refs: list[str] = Field(default_factory=list)
    provisional: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IncorporationRecord(VNextModel):
    """Explicit record of a readability-context update.

    The record states what was incorporated or rejected. It does not perform
    learning, conflict resolution, rollback, or context replacement itself.
    """

    incorporation_record_id: str
    process_id: str
    slice_ref: str
    before_context_ref: str
    after_context_ref: str
    incorporated_item_refs: list[str] = Field(default_factory=list)
    rejected_item_refs: list[str] = Field(default_factory=list)
    update_reason: str
    provisional: bool = True
    reversible: bool = True
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_incorporation_content(self) -> "IncorporationRecord":
        overlap = set(self.incorporated_item_refs) & set(self.rejected_item_refs)
        if overlap:
            raise ValueError(
                "the same item cannot be both incorporated and rejected"
            )
        return self
