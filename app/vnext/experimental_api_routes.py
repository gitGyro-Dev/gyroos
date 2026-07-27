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
from .inspection_comparison_collection_comparison import (
    ExperimentalComparisonCollectionComparisonRequest,
    ExperimentalComparisonCollectionComparisonResult,
)
from .inspection_comparison_collection_comparison_service import (
    ExperimentalComparisonCollectionComparisonError,
    ExperimentalComparisonCollectionComparisonService,
)
from .inspection_comparison_review_bundle import (
    ExperimentalComparisonReviewBundleRequest,
    ExperimentalComparisonReviewBundleResult,
)
from .inspection_comparison_review_bundle_service import (
    ExperimentalComparisonReviewBundleError,
    ExperimentalComparisonReviewBundleService,
)
from .inspection_comparison_series_comparison import (
    ExperimentalComparisonSeriesComparisonRequest,
    ExperimentalComparisonSeriesComparisonResult,
)
from .inspection_comparison_series_comparison_collection import (
    ExperimentalComparisonSeriesComparisonCollectionRequest,
    ExperimentalComparisonSeriesComparisonCollectionResult,
)
from .inspection_comparison_series_comparison_collection_service import (
    ExperimentalComparisonSeriesComparisonCollectionError,
    ExperimentalComparisonSeriesComparisonCollectionService,
)
from .inspection_comparison_series_comparison_service import (
    ExperimentalComparisonSeriesComparisonError,
    ExperimentalComparisonSeriesComparisonService,
)
from .inspection_comparison_set_comparison_series import (
    ExperimentalComparisonSetComparisonSeriesRequest,
    ExperimentalComparisonSetComparisonSeriesResult,
)
from .inspection_comparison_set_comparison_series_service import (
    ExperimentalComparisonSetComparisonSeriesError,
    ExperimentalComparisonSetComparisonSeriesService,
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
from .inspection_review_bundle_comparison import (
    ExperimentalReviewBundleComparisonRequest,
    ExperimentalReviewBundleComparisonResult,
)
from .inspection_review_bundle_comparison_service import (
    ExperimentalReviewBundleComparisonError,
    ExperimentalReviewBundleComparisonService,
)
from .inspection_review_bundle_comparison_set import (
    ExperimentalReviewBundleComparisonSetRequest,
    ExperimentalReviewBundleComparisonSetResult,
)
from .inspection_review_bundle_comparison_set_comparison import (
    ExperimentalComparisonSetComparisonRequest,
    ExperimentalComparisonSetComparisonResult,
)
from .inspection_review_bundle_comparison_set_comparison_service import (
    ExperimentalComparisonSetComparisonError,
    ExperimentalComparisonSetComparisonService,
)
from .inspection_review_bundle_comparison_set_service import (
    ExperimentalReviewBundleComparisonSetError,
    ExperimentalReviewBundleComparisonSetService,
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
review_bundle_comparison_service = ExperimentalReviewBundleComparisonService()
review_bundle_comparison_set_service = ExperimentalReviewBundleComparisonSetService()
comparison_set_comparison_service = ExperimentalComparisonSetComparisonService()
comparison_set_comparison_series_service = (
    ExperimentalComparisonSetComparisonSeriesService()
)
comparison_series_comparison_service = ExperimentalComparisonSeriesComparisonService()
comparison_series_comparison_collection_service = (
    ExperimentalComparisonSeriesComparisonCollectionService()
)
comparison_collection_comparison_service = ExperimentalComparisonCollectionComparisonService()


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


@router.post(
    "/inspection-review-bundle-comparisons",
    response_model=ExperimentalReviewBundleComparisonResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_review_bundle_comparison(
    request: ExperimentalReviewBundleComparisonRequest,
):
    try:
        return review_bundle_comparison_service.compare(request)
    except ExperimentalReviewBundleComparisonError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_INVALID",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_CREATE",
        )


@router.post(
    "/inspection-review-bundle-comparison-sets",
    response_model=ExperimentalReviewBundleComparisonSetResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_review_bundle_comparison_set(
    request: ExperimentalReviewBundleComparisonSetRequest,
):
    try:
        return review_bundle_comparison_set_service.create_set(request)
    except ExperimentalReviewBundleComparisonSetError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_SET_INVALID",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_SET_CREATE",
        )


@router.post(
    "/inspection-review-bundle-comparison-set-comparisons",
    response_model=ExperimentalComparisonSetComparisonResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_review_bundle_comparison_set_comparison(
    request: ExperimentalComparisonSetComparisonRequest,
):
    try:
        return comparison_set_comparison_service.compare(request)
    except ExperimentalComparisonSetComparisonError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SET_COMPARISON_INVALID",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_COMPARISON_SET_COMPARISON_CREATE",
        )


@router.post(
    "/inspection-comparison-set-comparison-series",
    response_model=ExperimentalComparisonSetComparisonSeriesResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_comparison_set_comparison_series(
    request: ExperimentalComparisonSetComparisonSeriesRequest,
):
    try:
        return comparison_set_comparison_series_service.create_series(request)
    except ExperimentalComparisonSetComparisonSeriesError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SET_COMPARISON_SERIES_INVALID",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_COMPARISON_SET_COMPARISON_SERIES_CREATE",
        )


@router.post(
    "/inspection-comparison-series-comparisons",
    response_model=ExperimentalComparisonSeriesComparisonResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_comparison_series_comparison(
    request: ExperimentalComparisonSeriesComparisonRequest,
):
    try:
        return comparison_series_comparison_service.compare(request)
    except ExperimentalComparisonSeriesComparisonError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SERIES_COMPARISON_INVALID",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_COMPARISON_SERIES_COMPARISON_CREATE",
        )


@router.post(
    "/inspection-comparison-series-comparison-collections",
    response_model=ExperimentalComparisonSeriesComparisonCollectionResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_comparison_series_comparison_collection(
    request: ExperimentalComparisonSeriesComparisonCollectionRequest,
):
    try:
        return comparison_series_comparison_collection_service.create_collection(request)
    except ExperimentalComparisonSeriesComparisonCollectionError as exc:
        return experimental_error(
            422,
            code=(
                "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SERIES_"
                "COMPARISON_COLLECTION_INVALID"
            ),
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_COMPARISON_SERIES_COMPARISON_COLLECTION_CREATE",
        )


@router.post(
    "/inspection-comparison-collection-comparisons",
    response_model=ExperimentalComparisonCollectionComparisonResult,
    status_code=status.HTTP_201_CREATED,
)
def create_experimental_inspection_comparison_collection_comparison(
    request: ExperimentalComparisonCollectionComparisonRequest,
):
    try:
        return comparison_collection_comparison_service.compare(request)
    except ExperimentalComparisonCollectionComparisonError as exc:
        return experimental_error(
            422,
            code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_COLLECTION_COMPARISON_INVALID",
            message=str(exc),
            category="VALIDATION",
            phase="EXPERIMENTAL_COMPARISON_COLLECTION_COMPARISON_CREATE",
        )
