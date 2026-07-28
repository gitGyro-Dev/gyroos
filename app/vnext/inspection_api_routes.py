from __future__ import annotations

from fastapi import APIRouter, status

from .experimental_error_response import experimental_error
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
from .inspection_comparison_collection_comparison_sequence import (
    ExperimentalComparisonCollectionComparisonSequenceRequest,
    ExperimentalComparisonCollectionComparisonSequenceResult,
)
from .inspection_comparison_collection_comparison_sequence_service import (
    ExperimentalComparisonCollectionComparisonSequenceError,
    ExperimentalComparisonCollectionComparisonSequenceService,
)
from .inspection_comparison_collection_comparison_service import (
    ExperimentalComparisonCollectionComparisonError,
    ExperimentalComparisonCollectionComparisonService,
)
from .inspection_comparison_ledger_comparison import (
    ExperimentalComparisonLedgerComparisonRequest,
    ExperimentalComparisonLedgerComparisonResult,
)
from .inspection_comparison_ledger_comparison_archive import (
    ExperimentalComparisonLedgerComparisonArchiveRequest,
    ExperimentalComparisonLedgerComparisonArchiveResult,
)
from .inspection_comparison_ledger_comparison_archive_service import (
    ExperimentalComparisonLedgerComparisonArchiveError,
    ExperimentalComparisonLedgerComparisonArchiveService,
)
from .inspection_comparison_ledger_comparison_service import (
    ExperimentalComparisonLedgerComparisonError,
    ExperimentalComparisonLedgerComparisonService,
)
from .inspection_comparison_register_comparison import (
    ExperimentalComparisonRegisterComparisonRequest,
    ExperimentalComparisonRegisterComparisonResult,
)
from .inspection_comparison_register_comparison_ledger import (
    ExperimentalComparisonRegisterComparisonLedgerRequest,
    ExperimentalComparisonRegisterComparisonLedgerResult,
)
from .inspection_comparison_register_comparison_ledger_service import (
    ExperimentalComparisonRegisterComparisonLedgerError,
    ExperimentalComparisonRegisterComparisonLedgerService,
)
from .inspection_comparison_register_comparison_service import (
    ExperimentalComparisonRegisterComparisonError,
    ExperimentalComparisonRegisterComparisonService,
)
from .inspection_comparison_review_bundle import (
    ExperimentalComparisonReviewBundleRequest,
    ExperimentalComparisonReviewBundleResult,
)
from .inspection_comparison_review_bundle_service import (
    ExperimentalComparisonReviewBundleError,
    ExperimentalComparisonReviewBundleService,
)
from .inspection_comparison_sequence_comparison import (
    ExperimentalComparisonSequenceComparisonRequest,
    ExperimentalComparisonSequenceComparisonResult,
)
from .inspection_comparison_sequence_comparison_register import (
    ExperimentalComparisonSequenceComparisonRegisterRequest,
    ExperimentalComparisonSequenceComparisonRegisterResult,
)
from .inspection_comparison_sequence_comparison_register_service import (
    ExperimentalComparisonSequenceComparisonRegisterError,
    ExperimentalComparisonSequenceComparisonRegisterService,
)
from .inspection_comparison_sequence_comparison_service import (
    ExperimentalComparisonSequenceComparisonError,
    ExperimentalComparisonSequenceComparisonService,
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

inspection_router = APIRouter(prefix="/vnext/experimental")

inspection_receipt_service = ExperimentalInspectionReceiptService()
inspection_batch_service = ExperimentalInspectionBatchService()
manifest_comparison_service = ExperimentalManifestComparisonService()
comparison_review_bundle_service = ExperimentalComparisonReviewBundleService()
review_bundle_comparison_service = ExperimentalReviewBundleComparisonService()
review_bundle_comparison_set_service = ExperimentalReviewBundleComparisonSetService()
comparison_set_comparison_service = ExperimentalComparisonSetComparisonService()
comparison_set_comparison_series_service = ExperimentalComparisonSetComparisonSeriesService()
comparison_series_comparison_service = ExperimentalComparisonSeriesComparisonService()
comparison_series_comparison_collection_service = ExperimentalComparisonSeriesComparisonCollectionService()
comparison_collection_comparison_service = ExperimentalComparisonCollectionComparisonService()
comparison_collection_comparison_sequence_service = ExperimentalComparisonCollectionComparisonSequenceService()
comparison_sequence_comparison_service = ExperimentalComparisonSequenceComparisonService()
comparison_sequence_comparison_register_service = ExperimentalComparisonSequenceComparisonRegisterService()
comparison_register_comparison_service = ExperimentalComparisonRegisterComparisonService()
comparison_register_comparison_ledger_service = ExperimentalComparisonRegisterComparisonLedgerService()
comparison_ledger_comparison_service = ExperimentalComparisonLedgerComparisonService()
comparison_ledger_comparison_archive_service = ExperimentalComparisonLedgerComparisonArchiveService()

@inspection_router.post("/inspection-receipts", response_model=ExperimentalInspectionReceiptResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_receipt(request: ExperimentalInspectionReceiptRequest):
    try:
        return inspection_receipt_service.create_receipt(request)
    except ExperimentalInspectionReceiptError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_INSPECTION_RECEIPT_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_INSPECTION_RECEIPT_CREATE")

@inspection_router.post("/inspection-batch-manifests", response_model=ExperimentalInspectionBatchResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_batch_manifest(request: ExperimentalInspectionBatchRequest):
    try:
        return inspection_batch_service.create_manifest(request)
    except ExperimentalInspectionBatchError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_INSPECTION_BATCH_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_INSPECTION_BATCH_CREATE")

@inspection_router.post("/inspection-manifest-comparisons", response_model=ExperimentalManifestComparisonResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_manifest_comparison(request: ExperimentalManifestComparisonRequest):
    try:
        return manifest_comparison_service.compare(request)
    except ExperimentalManifestComparisonError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_MANIFEST_COMPARISON_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_MANIFEST_COMPARISON_CREATE")

@inspection_router.post("/inspection-comparison-review-bundles", response_model=ExperimentalComparisonReviewBundleResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_review_bundle(request: ExperimentalComparisonReviewBundleRequest):
    try:
        return comparison_review_bundle_service.create_bundle(request)
    except ExperimentalComparisonReviewBundleError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_REVIEW_BUNDLE_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_REVIEW_BUNDLE_CREATE")

@inspection_router.post("/inspection-review-bundle-comparisons", response_model=ExperimentalReviewBundleComparisonResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_review_bundle_comparison(request: ExperimentalReviewBundleComparisonRequest):
    try:
        return review_bundle_comparison_service.compare(request)
    except ExperimentalReviewBundleComparisonError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_CREATE")

@inspection_router.post("/inspection-review-bundle-comparison-sets", response_model=ExperimentalReviewBundleComparisonSetResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_review_bundle_comparison_set(request: ExperimentalReviewBundleComparisonSetRequest):
    try:
        return review_bundle_comparison_set_service.create_set(request)
    except ExperimentalReviewBundleComparisonSetError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_SET_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_SET_CREATE")

@inspection_router.post("/inspection-review-bundle-comparison-set-comparisons", response_model=ExperimentalComparisonSetComparisonResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_review_bundle_comparison_set_comparison(request: ExperimentalComparisonSetComparisonRequest):
    try:
        return comparison_set_comparison_service.compare(request)
    except ExperimentalComparisonSetComparisonError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_SET_COMPARISON_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_SET_COMPARISON_CREATE")

@inspection_router.post("/inspection-comparison-set-comparison-series", response_model=ExperimentalComparisonSetComparisonSeriesResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_set_comparison_series(request: ExperimentalComparisonSetComparisonSeriesRequest):
    try:
        return comparison_set_comparison_series_service.create_series(request)
    except ExperimentalComparisonSetComparisonSeriesError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SET_COMPARISON_SERIES_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_SET_COMPARISON_SERIES_CREATE")

@inspection_router.post("/inspection-comparison-series-comparisons", response_model=ExperimentalComparisonSeriesComparisonResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_series_comparison(request: ExperimentalComparisonSeriesComparisonRequest):
    try:
        return comparison_series_comparison_service.compare(request)
    except ExperimentalComparisonSeriesComparisonError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SERIES_COMPARISON_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_SERIES_COMPARISON_CREATE")

@inspection_router.post("/inspection-comparison-series-comparison-collections", response_model=ExperimentalComparisonSeriesComparisonCollectionResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_series_comparison_collection(request: ExperimentalComparisonSeriesComparisonCollectionRequest):
    try:
        return comparison_series_comparison_collection_service.create_collection(request)
    except ExperimentalComparisonSeriesComparisonCollectionError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SERIES_COMPARISON_COLLECTION_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_SERIES_COMPARISON_COLLECTION_CREATE")

@inspection_router.post("/inspection-comparison-collection-comparisons", response_model=ExperimentalComparisonCollectionComparisonResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_collection_comparison(request: ExperimentalComparisonCollectionComparisonRequest):
    try:
        return comparison_collection_comparison_service.compare(request)
    except ExperimentalComparisonCollectionComparisonError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_COLLECTION_COMPARISON_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_COLLECTION_COMPARISON_CREATE")

@inspection_router.post("/inspection-comparison-collection-comparison-sequences", response_model=ExperimentalComparisonCollectionComparisonSequenceResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_collection_comparison_sequence(request: ExperimentalComparisonCollectionComparisonSequenceRequest):
    try:
        return comparison_collection_comparison_sequence_service.create_sequence(request)
    except ExperimentalComparisonCollectionComparisonSequenceError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_COLLECTION_COMPARISON_SEQUENCE_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_COLLECTION_COMPARISON_SEQUENCE_CREATE")

@inspection_router.post("/inspection-comparison-sequence-comparisons", response_model=ExperimentalComparisonSequenceComparisonResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_sequence_comparison(request: ExperimentalComparisonSequenceComparisonRequest):
    try:
        return comparison_sequence_comparison_service.compare(request)
    except ExperimentalComparisonSequenceComparisonError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SEQUENCE_COMPARISON_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_SEQUENCE_COMPARISON_CREATE")

@inspection_router.post("/inspection-comparison-sequence-comparison-registers", response_model=ExperimentalComparisonSequenceComparisonRegisterResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_sequence_comparison_register(request: ExperimentalComparisonSequenceComparisonRegisterRequest):
    try:
        return comparison_sequence_comparison_register_service.create_register(request)
    except ExperimentalComparisonSequenceComparisonRegisterError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SEQUENCE_COMPARISON_REGISTER_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_SEQUENCE_COMPARISON_REGISTER_CREATE")

@inspection_router.post("/inspection-comparison-register-comparisons", response_model=ExperimentalComparisonRegisterComparisonResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_register_comparison(request: ExperimentalComparisonRegisterComparisonRequest):
    try:
        return comparison_register_comparison_service.compare(request)
    except ExperimentalComparisonRegisterComparisonError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_REGISTER_COMPARISON_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_REGISTER_COMPARISON_CREATE")

@inspection_router.post("/inspection-comparison-register-comparison-ledgers", response_model=ExperimentalComparisonRegisterComparisonLedgerResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_register_comparison_ledger(request: ExperimentalComparisonRegisterComparisonLedgerRequest):
    try:
        return comparison_register_comparison_ledger_service.create_ledger(request)
    except ExperimentalComparisonRegisterComparisonLedgerError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_REGISTER_COMPARISON_LEDGER_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_REGISTER_COMPARISON_LEDGER_CREATE")

@inspection_router.post("/inspection-comparison-ledger-comparisons", response_model=ExperimentalComparisonLedgerComparisonResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_ledger_comparison(request: ExperimentalComparisonLedgerComparisonRequest):
    try:
        return comparison_ledger_comparison_service.compare(request)
    except ExperimentalComparisonLedgerComparisonError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_LEDGER_COMPARISON_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_LEDGER_COMPARISON_CREATE")

@inspection_router.post("/inspection-comparison-ledger-comparison-archives", response_model=ExperimentalComparisonLedgerComparisonArchiveResult, status_code=status.HTTP_201_CREATED)
def create_experimental_inspection_comparison_ledger_comparison_archive(request: ExperimentalComparisonLedgerComparisonArchiveRequest):
    try:
        return comparison_ledger_comparison_archive_service.create_archive(request)
    except ExperimentalComparisonLedgerComparisonArchiveError as exc:
        return experimental_error(422, code="GYRO_VNEXT_EXPERIMENTAL_COMPARISON_LEDGER_COMPARISON_ARCHIVE_INVALID", message=str(exc), category="VALIDATION", phase="EXPERIMENTAL_COMPARISON_LEDGER_COMPARISON_ARCHIVE_CREATE")
