"""HTTP routes for the supported application workflows."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from superconductors.models import Candidate

from .auth import issue_access_token, require_api_key
from .schemas import (
    BatchPredictRequest,
    BatchPredictResponse,
    CandidateRequest,
    CandidateResponse,
    LoginRequest,
    SubmissionResponse,
    SubmitRequest,
)

router = APIRouter()


def _service(request: Request):
    return request.app.state.service


def _prediction_payload(result) -> dict[str, object]:
    return {
        "formula": result.formula,
        "predicted_tc": round(result.tc, 2),
        "uncertainty": round(result.uncertainty, 2),
        "confidence": result.confidence,
        "method": result.method,
        "applicability": result.applicability,
        "reference_pressure": result.reference_pressure,
        "citation": result.citation,
        "unit": "K",
    }


def _candidate_payload(candidate) -> dict[str, object]:
    payload = candidate.to_dict()
    payload["temperature"] = payload["tc"]
    return payload


@router.get("/candidates", response_model=list[CandidateResponse])
def get_candidates(
    request: Request,
    min_tc: float | None = Query(default=None),
    max_tc: float | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=500),
    include_quarantined: bool = Query(default=False),
    _: str = Depends(require_api_key),
):
    if min_tc is not None and max_tc is not None and min_tc > max_tc:
        raise HTTPException(status_code=422, detail="min_tc must not exceed max_tc")
    candidates = [
        _candidate_payload(candidate)
        for candidate in _service(request).candidates()
        if (
            include_quarantined
            or candidate.candidate.verification_status not in {"disputed", "retracted"}
        )
        and (
            min_tc is None
            or (candidate.candidate.tc is not None and candidate.candidate.tc >= min_tc)
        )
        and (
            max_tc is None
            or (candidate.candidate.tc is not None and candidate.candidate.tc <= max_tc)
        )
    ]
    return candidates[offset : offset + limit]


@router.post("/candidates", response_model=CandidateResponse, status_code=201)
def create_candidate(
    request: Request,
    body: CandidateRequest,
    _: str = Depends(require_api_key),
):
    created = _service(request).create_candidate(
        Candidate(
            formula=body.formula,
            tc=body.tc,
            pressure=body.pressure,
            structure=body.structure,
            source="api",
        )
    )
    return _candidate_payload(created)


@router.post("/submit", response_model=SubmissionResponse)
def submit_prediction(
    request: Request,
    body: SubmitRequest,
    _: str = Depends(require_api_key),
):
    params = body.synthesis_params.model_dump(exclude_none=True) if body.synthesis_params else None
    submission = _service(request).submit(body.candidate_id, params)
    if submission is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return submission


@router.get("/submissions", response_model=list[SubmissionResponse])
def get_submissions(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    _: str = Depends(require_api_key),
):
    return _service(request).submissions(offset=offset, limit=limit)


@router.post("/batch_predict", response_model=BatchPredictResponse)
def batch_predict(
    request: Request,
    body: BatchPredictRequest,
    _: str = Depends(require_api_key),
):
    predictions = []
    for formula in body.formulas:
        try:
            predictions.append(_prediction_payload(_service(request).predict(formula)))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"predictions": predictions}


@router.get("/predict-tc")
def predict_tc_endpoint(
    request: Request,
    compound: str = Query(min_length=1, max_length=100),
    _: str = Depends(require_api_key),
):
    try:
        result = _service(request).predict(compound.strip())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    payload = _prediction_payload(result)
    return {"compound": payload.pop("formula"), **payload, "predicted_Tc": payload["predicted_tc"]}


@router.post("/login")
def login(request: Request, body: LoginRequest) -> dict[str, object]:
    settings = request.app.state.settings
    if not all((settings.admin_username, settings.admin_password, settings.api_key)):
        raise HTTPException(status_code=503, detail="Login is not configured")
    identity = request.client.host if request.client else "unknown"
    limiter = request.app.state.login_limiter
    if limiter.is_blocked(identity):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts",
            headers={"Retry-After": "60"},
        )
    valid = secrets.compare_digest(
        body.username, settings.admin_username
    ) and secrets.compare_digest(body.password, settings.admin_password)
    if not valid:
        limiter.record_failure(identity)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    limiter.reset(identity)
    return {
        "access_token": issue_access_token(settings.api_key),
        "token_type": "api-key",
        "expires_in": 3600,
        "role": "admin",
    }


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request) -> dict[str, str]:
    if not _service(request).ready():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Not ready")
    return {"status": "ready"}
