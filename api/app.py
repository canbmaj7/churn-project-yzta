"""
Churn tahmin API — en iyi modeli `models/model_registry.json` üzerinden yükler.

- ``POST /predict`` — ön işlenmiş 30 özellik (``feature_columns`` ile aynı anahtarlar).
- ``POST /predict/raw`` — ham Telco alanları; ``data/processed/train_test_split.pkl``
  içindeki ``scaler`` ile aynı ön işleme uygulanır.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import joblib
import numpy as np
from fastapi import Body, FastAPI, HTTPException

from .preprocess import RAW_API_FIELDS, preprocess_bundle_available, raw_customer_to_feature_dict

app = FastAPI(title="Churn API", version="1.1.0")


def _models_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "models"


def _load_model_and_registry():
    """Önce registry; yoksa best_model.pkl."""
    mdir = _models_dir()
    reg_path = mdir / "model_registry.json"
    if reg_path.is_file():
        registry = json.loads(reg_path.read_text(encoding="utf-8"))
        rel = registry["best_model_file"]
        model_path = mdir / rel
        if not model_path.is_file():
            raise FileNotFoundError(f"Model dosyası yok: {model_path}")
        model = joblib.load(model_path)
        return model, registry
    pkl = mdir / "best_model.pkl"
    if not pkl.is_file():
        raise FileNotFoundError("model_registry.json veya best_model.pkl bulunamadı.")
    bundle = joblib.load(pkl)
    registry = {
        "best_model_key": bundle.get("model_name", "unknown"),
        "feature_columns": bundle["feature_columns"],
    }
    return bundle["model"], registry


_model, _registry = _load_model_and_registry()
FEATURE_COLUMNS: list[str] = list(_registry["feature_columns"])


def _predict_body_openapi_example() -> dict[str, float | int]:
    """Swagger / OpenAPI için tam 30 alanlı örnek gövde (README ile uyumlu)."""
    base = {name: 0 for name in FEATURE_COLUMNS}
    overrides: dict[str, float | int] = {
        "gender": 0,
        "SeniorCitizen": 0,
        "Partner": 1,
        "Dependents": 0,
        "tenure": 12,
        "PhoneService": 1,
        "PaperlessBilling": 1,
        "MonthlyCharges": 70.35,
        "TotalCharges": 843.15,
        "MultipleLines_No phone service": 0,
        "MultipleLines_Yes": 0,
        "InternetService_Fiber optic": 1,
        "InternetService_No": 0,
        "OnlineSecurity_No internet service": 0,
        "OnlineSecurity_Yes": 0,
        "OnlineBackup_No internet service": 0,
        "OnlineBackup_Yes": 0,
        "DeviceProtection_No internet service": 0,
        "DeviceProtection_Yes": 0,
        "TechSupport_No internet service": 0,
        "TechSupport_Yes": 0,
        "StreamingTV_No internet service": 0,
        "StreamingTV_Yes": 1,
        "StreamingMovies_No internet service": 0,
        "StreamingMovies_Yes": 1,
        "Contract_One year": 0,
        "Contract_Two year": 0,
        "PaymentMethod_Credit card (automatic)": 0,
        "PaymentMethod_Electronic check": 1,
        "PaymentMethod_Mailed check": 0,
    }
    for k, v in overrides.items():
        if k in base:
            base[k] = v
    return base


_PREDICT_EXAMPLE = _predict_body_openapi_example()

_RAW_BODY_EXAMPLE: dict[str, Any] = {
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 12,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "Yes",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 70.35,
    "TotalCharges": 843.15,
}


def _predict_from_feature_dict(features: dict[str, float | int | bool]) -> dict:
    missing = [c for c in FEATURE_COLUMNS if c not in features]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Eksik sütunlar ({len(missing)} adet), örnek: {missing[:5]}",
        )
    x = np.array([[float(features[c]) for c in FEATURE_COLUMNS]], dtype=np.float64)
    if not hasattr(_model, "predict_proba"):
        raise HTTPException(status_code=500, detail="Model predict_proba desteklemiyor.")
    proba = float(_model.predict_proba(x)[0, 1])
    pred = int(_model.predict(x)[0])
    return {
        "churn_prediction": pred,
        "churn_probability": round(proba, 4),
        "message": (
            "Bu müşteri churn riski taşımaktadır."
            if pred == 1
            else "Düşük churn riski tahmin edildi."
        ),
        "model_used": _registry.get("best_model_key"),
    }


@app.get("/")
def health():
    return {
        "status": "ok",
        "best_model": _registry.get("best_model_key"),
        "n_features": len(FEATURE_COLUMNS),
        "preprocess_bundle_available": preprocess_bundle_available(),
    }


@app.post("/predict")
def predict(
    features: Annotated[
        dict[str, float | int | bool],
        Body(
            openapi_examples={
                "on_islenmis": {
                    "summary": "Ön işlenmiş tek müşteri (30 alan)",
                    "description": "Anahtarlar `model_registry.json` → `feature_columns` ile birebir aynı olmalıdır.",
                    "value": _PREDICT_EXAMPLE,
                },
            },
        ),
    ],
):
    """Girdi: ön işlenmiş tek satır — anahtarlar `feature_columns` ile aynı (30 alan)."""
    return _predict_from_feature_dict(features)


@app.post("/predict/raw")
def predict_raw(
    customer: Annotated[
        dict[str, Any],
        Body(
            openapi_examples={
                "telco_ornek": {
                    "summary": "Ham Telco müşteri satırı",
                    "description": f"Zorunlu alanlar: {', '.join(RAW_API_FIELDS)}",
                    "value": _RAW_BODY_EXAMPLE,
                },
            },
        ),
    ],
):
    """
    Ham kategorik/sayısal Telco alanları (notebook 02 ile aynı sözleşme).
    `train_test_split.pkl` yoksa 503 döner.
    """
    if not preprocess_bundle_available():
        raise HTTPException(
            status_code=503,
            detail=(
                "Ön işleme paketi yok. `data/processed/` altında `preprocess_artifacts.pkl` veya "
                "`train_test_split.pkl` olmalı (02_preprocessing.ipynb çıktısı)."
            ),
        )
    try:
        features = raw_customer_to_feature_dict(customer, FEATURE_COLUMNS)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    out = _predict_from_feature_dict(features)
    out["input_mode"] = "raw"
    return out
