import json
import os
from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Superconductivity Pipeline API", version="0.1.0")

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "superconductor_database.json")

def _load_candidates() -> List[Dict[str, Any]]:
    if not os.path.exists(DATABASE_PATH):
        return []
    with open(DATABASE_PATH, "r") as f:
        data = json.load(f)
    return [
        {
            "id": i + 1,
            "formula": entry.get("name", entry.get("composition", "")),
            "pressure": entry.get("pressure"),
            "temperature": entry.get("Tc"),
        }
        for i, entry in enumerate(data)
    ]

def _append_candidate(candidate: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    try:
        with open(DATABASE_PATH, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    data.append({
        "name": candidate["formula"],
        "Tc": candidate.get("temperature"),
        "pressure": candidate.get("pressure"),
    })
    with open(DATABASE_PATH, "w") as f:
        json.dump(data, f, indent=2)

# Persistent JSON-file-backed storage for candidates
candidates_db: List[Dict[str, Any]] = _load_candidates()
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
    _append_candidate(candidate)
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
    """Batch predict Tc for a list of formulas using the Eliashberg (Allen-Dynes) model."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    from scripts.predict_tc import eliashberg_tc
    predictions = []
    for formula in req.formulas:
        try:
            predicted_tc = eliashberg_tc(formula)
            confidence = 0.7
        except Exception:
            predicted_tc = 0.0
            confidence = 0.0
        predictions.append({
            "formula": formula,
            "predicted_tc": round(predicted_tc, 2),
            "confidence": confidence,
        })
    return {"predictions": predictions}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Consolidated endpoints from run_pipeline.py ---

@app.post("/login")
def login(username: str = None, password: str = None):
    """Simple login endpoint returning an API key (demo purposes)."""
    if username == "admin" and password == "admin123":
        return {"api_key": "admin-demo-key", "role": "admin"}
    elif username == "researcher" and password == "researcher123":
        return {"api_key": "researcher-demo-key", "role": "researcher"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/feedback")
def submit_feedback(formula: str, rating: int, comment: str = ""):
    """Submit feedback/rating for a candidate formula."""
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    logger.info(f"Feedback: formula={formula}, rating={rating}, comment={comment}")
    return {"status": "ok", "formula": formula, "rating": rating}

@app.get("/predict-tc")
def predict_tc_endpoint(compound: str, api_key: str = Header(None)):
    """Predict Tc for a given compound using the trained model."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    from scripts.predict_tc import eliashberg_tc
    try:
        predicted_tc = eliashberg_tc(compound)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    return {"compound": compound, "predicted_Tc": round(predicted_tc, 2), "unit": "K"}

@app.post("/simulate-manufacturing")
def simulate_manufacturing(compound: str, api_key: str = Header(None)):
    """Simulate manufacturing process for a given compound."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    from scripts.predict_tc import eliashberg_tc
    try:
        predicted_tc = eliashberg_tc(compound)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    if predicted_tc > 200:
        success_prob = round(max(0.1, min(0.9, 0.5 - 0.001 * (predicted_tc - 200))), 2)
        estimated_cost = round(5000 + 200 * predicted_tc, 2)
    elif predicted_tc > 100:
        success_prob = round(max(0.2, min(0.95, 0.6 - 0.002 * (predicted_tc - 100))), 2)
        estimated_cost = round(2000 + 100 * predicted_tc, 2)
    else:
        success_prob = round(max(0.3, min(0.95, 0.8 - 0.001 * predicted_tc)), 2)
        estimated_cost = round(1000 + 50 * predicted_tc, 2)
    return {"compound": compound, "success_probability": success_prob, "estimated_cost": estimated_cost, "currency": "USD"}
