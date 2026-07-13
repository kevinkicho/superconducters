"""FastAPI surface for candidate discovery and prediction."""

from __future__ import annotations

import logging
import os
import secrets
from threading import RLock
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from superconductors.config import Settings
from superconductors.models import Candidate
from superconductors.repository import CandidateRepository

logger = logging.getLogger(__name__)
settings = Settings.from_env()
repository = CandidateRepository(settings.database_path)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
app = FastAPI(title="Superconductivity Pipeline API", version="1.0.0")

_submissions: list[dict[str, Any]] = []
_submission_lock = RLock()


def require_api_key(provided: str | None = Depends(api_key_header)) -> str:
    expected = os.getenv("SUPERCONDUCTOR_API_KEY")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured",
        )
    if provided is None or not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return provided


class CandidateRequest(BaseModel):
    formula: str = Field(min_length=1)
    pressure: float | None = None
    temperature: float | None = None
    structure: str | None = None


class CandidateResponse(BaseModel):
    id: int
    formula: str
    pressure: float | None
    temperature: float | None
    structure: str | None = None


class SubmitRequest(BaseModel):
    candidate_id: int = Field(gt=0)
    synthesis_params: dict[str, Any] | None = None


class BatchPredictRequest(BaseModel):
    formulas: list[str]


class BatchPredictResponse(BaseModel):
    predictions: list[dict[str, Any]]


def _candidate_responses() -> list[dict[str, Any]]:
    return [
        {
            "id": index,
            "formula": candidate.formula,
            "pressure": candidate.pressure,
            "temperature": candidate.tc,
            "structure": candidate.structure,
        }
        for index, candidate in enumerate(repository.list(), start=1)
    ]


@app.get("/candidates", response_model=list[CandidateResponse])
def get_candidates(
    min_tc: float | None = Query(default=None),
    max_tc: float | None = Query(default=None),
    _: str = Depends(require_api_key),
) -> list[dict[str, Any]]:
    candidates = _candidate_responses()
    return [
        candidate
        for candidate in candidates
        if (
            min_tc is None
            or (candidate["temperature"] is not None and candidate["temperature"] >= min_tc)
        )
        and (
            max_tc is None
            or (candidate["temperature"] is not None and candidate["temperature"] <= max_tc)
        )
    ]


@app.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(req: CandidateRequest, _: str = Depends(require_api_key)) -> dict[str, Any]:
    repository.append(
        Candidate(
            formula=req.formula,
            tc=req.temperature,
            pressure=req.pressure,
            structure=req.structure,
            source="api",
        )
    )
    created = _candidate_responses()[-1]
    logger.info("Created candidate %s", created["id"])
    return created


@app.post("/submit")
def submit_prediction(req: SubmitRequest, _: str = Depends(require_api_key)) -> dict[str, Any]:
    candidate = next(
        (value for value in _candidate_responses() if value["id"] == req.candidate_id),
        None,
    )
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    with _submission_lock:
        submission = {
            "id": len(_submissions) + 1,
            "candidate_id": req.candidate_id,
            "formula": candidate["formula"],
            "synthesis_params": req.synthesis_params,
            "status": "submitted",
        }
        _submissions.append(submission)
    return submission


def _predict_formula(formula: str) -> tuple[float, float]:
    try:
        from superconductors.prediction import predict

        result = predict(formula)
        return result.tc, result.confidence
    except Exception:
        logger.exception("Tc prediction failed for %s", formula)
        return 0.0, 0.0


@app.post("/batch_predict", response_model=BatchPredictResponse)
def batch_predict(req: BatchPredictRequest, _: str = Depends(require_api_key)) -> dict[str, Any]:
    return {
        "predictions": [
            {
                "formula": formula,
                "predicted_tc": round(prediction, 2),
                "confidence": confidence,
            }
            for formula in req.formulas
            for prediction, confidence in [_predict_formula(formula)]
        ]
    }


@app.get("/predict-tc")
def predict_tc_endpoint(compound: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    prediction, confidence = _predict_formula(compound)
    return {
        "compound": compound,
        "predicted_Tc": round(prediction, 2),
        "confidence": confidence,
        "unit": "K",
    }


@app.post("/login")
def login(username: str, password: str) -> dict[str, str]:
    expected_username = os.getenv("SUPERCONDUCTOR_ADMIN_USERNAME")
    expected_password = os.getenv("SUPERCONDUCTOR_ADMIN_PASSWORD")
    api_key = os.getenv("SUPERCONDUCTOR_API_KEY")
    if not all((expected_username, expected_password, api_key)):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login is not configured",
        )
    valid = secrets.compare_digest(username, expected_username) and secrets.compare_digest(
        password, expected_password
    )
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"api_key": api_key, "role": "admin"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
