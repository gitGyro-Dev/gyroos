from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.security import require_runtime_bearer
from .consumer_compatibility import (
    ExperimentalConsumerCompatibilityRequest,
    ExperimentalConsumerCompatibilityResult,
)
from .consumer_compatibility_service import (
    ExperimentalCompatibilityError,
    ExperimentalConsumerCompatibilityService,
)
from .experimental_api import (
    ExperimentalApiError,
    ExperimentalRecordCreateRequest,
    ExperimentalRecordListResponse,
    ExperimentalRecordResponse,
    experimental_api_settings,
)
from .experimental_api_provider import get_experimental_repository
from .experimental_repository import ExperimentalRecordRepository
from .inspection_batch_manifest import (
    ExperimentalInspectionBatchRequest,
    ExperimentalInspectionBatchResult,
)
from .inspection_batch_manifest_service import (
    ExperimentalInspectionBatchError,
    ExperimentalInspectionBatchService,
)
from .inspection_comparison_review_bundle import (
    ExperimentalComparisonReviewBundleRequest,
    ExperimentalComparisonReviewBundleResult,
)
from .inspection_comparison_review_bundle_service import (
    ExperimentalComparisonReviewBundleError,
    ExperimentalComparisonReviewBundleService,
)
from .inspection_manifest_comparison import (
    ExperimentalManifestComparisonRequest,
    ExperimentalManifestComparisonResult,
)
from .inspection_manifest_comparison_service import (
    ExperimentalManifestComparisonError,
    ExperimentalManifestComparisonService,
)
from .inspection_receipt import (
    ExperimentalInspectionReceiptRequest,
    ExperimentalInspectionReceiptResult,
)
from .inspection_receipt_service import (
    ExperimentalInspectionReceiptError,
    ExperimentalInspectionReceiptService,
)


router = APIRouter(
    prefix="/vnext/experimental",
    tags=["vNext Experimental"],
    dependencies=[Depends(require_runtime_bearer)],
)
compatibility_service = ExperimentalConsumerCompatibilityService()
inspection_receipt_service = ExperimentalInspectionReceiptService()
inspection_batch_service = ExperimentalInspectionBatchService()
manifest_comparison_service = ExperimentalManifestComparisonService()
comparison_review_bundle_service = ExperimentalComparisonReviewBundleService()


def experimental_error(
    status_code: int,
    *,
    code: str,
    message: str,
    category: str,
    phase: str,
    retryable: bool = False,
) -> JSONResponse:
    payload = ExperimentalApiError(
        error_code=code,
        message=message,
        category=category,
        phase=phase,
        retryable=retryable,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


@router.post(
    "/records",
    response_model=ExperimentalRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_record(
    request: ExperimentalRecordCreateRequest,
    repository: ExperimentalRecordRepository = Depends(get_experimental_repository),
):
    stored = repository.save(request.to_envelope())
    return ExperimentalRecordResponse(record=stored)


@router.get("/records/{record_id}", response_model=ExperimentalRecordResponse)
def get_experimental_record(
    record_id: str,
    repository: ExperimentalRecordRepository = Depends(get_experimental_repository),
):
    record = repository.get(record_id)
    if record is None:
        return experimental_error(
            404,
            code="GYRO_VNEXT_EXPERIMENTAL_RECORD_NOT_FOUND",
            message=f"Experimental record not found: {record_id}",
            category="NOT_FOUND",
            phase="EXPERIMENTAL_RECORD_RETRIEVAL",
        )
    return ExperimentalRecordResponse(record=record)


@router.get("/records", response_model=ExperimentalRecordListResponse)
def list_experimental_records(
    process_id: str | None = Query(default=None),
    record_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1),
    repository: ExperimentalRecordRepository = Depends(get_experimental_repository),
):
    bounded_limit = min(limit, experimental_api_settings.max_list_results)
    records = repository.list(process_id=process_id, record_type=record_type)[:bounded_limit]
    return ExperimentalRecordListResponse(records=records, count=len(records))


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experimental_record(
    record_id: str,
    repository: ExperimentalRecordRepository = Depends(get_experimental_repository),
):
    deleted = repository.delete(record_id)
    if not deleted:
        return experimental_error(
            404,
            code="GYRO_VNEXT_EXPERIMENTAL_RECORD_NOT_FOUND",
            message=f"Experimental record not found: {record_id}",
            category="NOT_FOUND",
            phase="EXPERIMENTAL_RECORD_DELETE",
        )
    return None


@router.post(
    "/compatibility/check",
    response_model=ExperimentalConsumerCompatibilityResult,
)
def check_experimental_consumer_compatibility(
    request: ExperimentalConsumerCompatibilityRequest,
):
    try:
        return compatibility_service.check(request)
    except ExperimentalCompatibilityError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_COMPATIBILITY_INVALID_VERSION",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_COMPATIBILITY_CHECK",
        )


@router.post(
    "/inspection-receipts",
    response_model=ExperimentalInspectionReceiptResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_receipt(
    request: ExperimentalInspectionReceiptRequest,
):
    try:
        return inspection_receipt_service.create_receipt(request)
    except ExperimentalInspectionReceiptError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_INSPECTION_RECEIPT_INVALID",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_INSPECTION_RECEIPT_CREATE",
        )


@router.post(
    "/inspection-batch-manifests",
    response_model=ExperimentalInspectionBatchResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_batch_manifest(
    request: ExperimentalInspectionBatchRequest,
):
    try:
        return inspection_batch_service.create_manifest(request)
    except ExperimentalInspectionBatchError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_INSPECTION_BATCH_INVALID",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_INSPECTION_BATCH_CREATE",
        )


@router.post(
    "/inspection-manifest-comparisons",
    response_model=ExperimentalManifestComparisonResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_manifest_comparison(
    request: ExperimentalManifestComparisonRequest,
):
    try:
        return manifest_comparison_service.compare(request)
    except ExperimentalManifestComparisonError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_MANIFEST_COMPARISON_INVALID",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_MANIFEST_COMPARISON_CREATE",
        )


@router.post(
    "/inspection-comparison-review-bundles",
    response_model=ExperimentalComparisonReviewBundleResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_comparison_review_bundle(
    request: ExperimentalComparisonReviewBundleRequest,
):
    try:
        return comparison_review_bundle_service.create_bundle(request)
    except ExperimentalComparisonReviewBundleError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_REVIEW_BUNDLE_INVALID",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_COMPARISON_REVIEW_BUNDLE_CREATE",
        )
