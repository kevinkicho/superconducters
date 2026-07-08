from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Superconductivity Pipeline API", version="0.1.0")

# In-memory storage for candidates and submissions
candidates_db: List[Dict[str, Any]] = []
submissions_db: List[Dict[str, Any]] = []

class CandidateRequest(BaseModel):
    formula: str
    pressure: Optional[float] = None
    temperature: Optional[float] = None

class CandidateResponse(BaseModel):
    id: int
    formula: str
    pressure: Optional[float]
    temperature: Optional[float]

class SubmitRequest(BaseModel):
    candidate_id: int
    synthesis_params: Optional[Dict[str, Any]] = None

class BatchPredictRequest(BaseModel):
    formulas: List[str]

class BatchPredictResponse(BaseModel):
    predictions: List[Dict[str, Any]]

@app.get("/candidates", response_model=List[CandidateResponse])
def get_candidates(api_key: str = Header(None)):
    """Return list of all candidates."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    return candidates_db

@app.post("/candidates", response_model=CandidateResponse)
def create_candidate(req: CandidateRequest, api_key: str = Header(None)):
    """Add a new candidate superconductor to the database."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    candidate = {
        "id": len(candidates_db) + 1,
        "formula": req.formula,
        "pressure": req.pressure,
        "temperature": req.temperature,
    }
    candidates_db.append(candidate)
    logger.info(f"Created candidate {candidate['id']}: {req.formula}")
    return candidate

@app.post("/submit", response_model=Dict[str, Any])
def submit_prediction(req: SubmitRequest, api_key: str = Header(None)):
    """Submit a candidate for detailed prediction/synthesis."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    candidate = next((c for c in candidates_db if c["id"] == req.candidate_id), None)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    submission = {
        "id": len(submissions_db) + 1,
        "candidate_id": req.candidate_id,
        "formula": candidate["formula"],
        "synthesis_params": req.synthesis_params,
        "status": "submitted",
    }
    submissions_db.append(submission)
    logger.info(f"Submitted prediction for candidate {req.candidate_id}")
    return submission

@app.post("/batch_predict", response_model=BatchPredictResponse)
def batch_predict(req: BatchPredictRequest, api_key: str = Header(None)):
    """Batch predict Tc for a list of formulas using a simple empirical model."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    predictions = []
    for formula in req.formulas:
        # Simple heuristic: higher hydrogen fraction -> higher predicted Tc (placeholder)
        h_count = formula.count('H') + formula.count('h')
        predicted_tc = min(300, 20 + 10 * h_count)  # Dummy model
        predictions.append({
            "formula": formula,
            "predicted_tc": predicted_tc,
            "confidence": 0.5,
        })
    return {"predictions": predictions}

@app.get("/health")
def health():
    return {"status": "ok"}
