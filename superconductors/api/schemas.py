"""Validated HTTP request and response contracts."""

from __future__ import annotations

import math
import uuid
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class CandidateRequest(BaseModel):
    formula: str = Field(min_length=1, max_length=100)
    tc: float | None = Field(
        default=None,
        ge=0,
        le=1000,
        validation_alias=AliasChoices("tc", "temperature"),
    )
    pressure: float | None = Field(default=None, ge=0, le=1000)
    structure: str | None = Field(default=None, max_length=200)

    @field_validator("formula")
    @classmethod
    def validate_formula(cls, value: str) -> str:
        from superconductors.prediction import parse_formula

        normalized = value.strip()
        parse_formula(normalized)
        return normalized

    @field_validator("tc", "pressure")
    @classmethod
    def finite_numbers(cls, value: float | None) -> float | None:
        if value is not None and not math.isfinite(value):
            raise ValueError("must be finite")
        return value


class CandidateResponse(BaseModel):
    id: str
    formula: str
    tc: float | None
    temperature: float | None = Field(
        description="Deprecated alias for tc; use tc for critical temperature"
    )
    pressure: float | None
    structure: str | None = None
    source: str
    evidence_type: str
    verification_status: str


class SynthesisParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pressure_gpa: float | None = Field(default=None, ge=0, le=1000)
    temperature_k: float | None = Field(default=None, ge=0, le=10000)
    precursor_ratio: float | None = Field(default=None, gt=0)
    annealing_time_hours: float | None = Field(default=None, ge=0)


class SubmitRequest(BaseModel):
    candidate_id: str | int
    synthesis_params: SynthesisParams | None = None

    @field_validator("candidate_id")
    @classmethod
    def validate_candidate_id(cls, value: str | int) -> str | int:
        if isinstance(value, int):
            if value <= 0:
                raise ValueError("legacy numeric candidate IDs must be positive")
            return value
        try:
            return str(uuid.UUID(value))
        except ValueError as exc:
            raise ValueError("candidate_id must be a UUID or positive legacy integer") from exc


class FormulaRequest(BaseModel):
    formula: str = Field(min_length=1, max_length=100)

    @field_validator("formula")
    @classmethod
    def normalize_formula(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("formula must not be blank")
        return normalized


class BatchPredictRequest(BaseModel):
    formulas: list[str] = Field(max_length=100)

    @field_validator("formulas")
    @classmethod
    def normalize_formulas(cls, values: list[str]) -> list[str]:
        normalized = [value.strip() for value in values]
        if any(not value or len(value) > 100 for value in normalized):
            raise ValueError("formulas must contain 1 to 100 characters")
        return normalized


class PredictionResponse(BaseModel):
    formula: str
    predicted_tc: float
    uncertainty: float
    confidence: float
    method: str
    applicability: str
    reference_pressure: float | None
    citation: str | None
    unit: str = "K"


class BatchPredictResponse(BaseModel):
    predictions: list[PredictionResponse]


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=1, max_length=500)


class SubmissionResponse(BaseModel):
    id: int
    candidate_id: str
    formula: str
    synthesis_params: dict[str, Any] | None
    status: str
    created_at: str
