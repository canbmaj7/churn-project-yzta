"""
Ham Telco müşteri satırını (02_preprocessing ile aynı mantık) model girdisine çevirir.
`data/processed/train_test_split.pkl` içindeki `scaler` ve `feature_columns` kullanılır.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
# Opsiyonel hafif paket (repoda tutulabilir; yoksa train_test_split.pkl kullanılır)
ARTIFACTS_PKL = ROOT / "data" / "processed" / "preprocess_artifacts.pkl"
# 02_preprocessing.ipynb çıktısı
PROCESSED_PKL = ROOT / "data" / "processed" / "train_test_split.pkl"

BINARY_COLS = ["gender", "Partner", "Dependents", "PhoneService", "PaperlessBilling"]
CAT_COLS = [
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaymentMethod",
]

# API gövdesinde beklenen ham alanlar (customerID / Churn yok)
RAW_API_FIELDS: tuple[str, ...] = (
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
)


@lru_cache(maxsize=1)
def _bundle() -> dict[str, Any]:
    if ARTIFACTS_PKL.is_file():
        return joblib.load(ARTIFACTS_PKL)
    if PROCESSED_PKL.is_file():
        return joblib.load(PROCESSED_PKL)
    raise FileNotFoundError(
        f"Ön işleme paketi yok. Şunlardan biri gerekli: {ARTIFACTS_PKL} veya {PROCESSED_PKL}. "
        "Önce notebooks/02_preprocessing.ipynb çalıştırın."
    )


def preprocess_bundle_available() -> bool:
    return ARTIFACTS_PKL.is_file() or PROCESSED_PKL.is_file()


def raw_customer_to_feature_dict(
    raw: dict[str, Any],
    feature_columns: list[str],
) -> dict[str, float]:
    """Tek ham müşteri sözlüğünü, modelin beklediği özellik sözlüğüne dönüştürür."""
    missing = [f for f in RAW_API_FIELDS if f not in raw]
    if missing:
        raise ValueError(f"Eksik alanlar: {missing}")

    bundle = _bundle()
    scaler = bundle["scaler"]
    num_cols: list[str] = list(bundle["num_cols"])

    row = {k: raw[k] for k in RAW_API_FIELDS}
    X = pd.DataFrame([row])

    X["TotalCharges"] = pd.to_numeric(X["TotalCharges"], errors="coerce").fillna(0.0)
    X["MonthlyCharges"] = pd.to_numeric(X["MonthlyCharges"], errors="coerce")
    X["tenure"] = pd.to_numeric(X["tenure"], errors="coerce")
    if X["MonthlyCharges"].isna().any() or X["tenure"].isna().any():
        raise ValueError("MonthlyCharges ve tenure sayısal olmalıdır.")

    X["SeniorCitizen"] = pd.to_numeric(X["SeniorCitizen"], errors="coerce").fillna(0).astype(int)

    for col in BINARY_COLS:
        X[col] = X[col].astype("string").str.strip()
    for col in BINARY_COLS:
        if col == "gender":
            X[col] = X[col].map({"Male": 1, "Female": 0})
        else:
            X[col] = X[col].map({"Yes": 1, "No": 0})
    if X[BINARY_COLS].isnull().any().any():
        raise ValueError(
            "İkili alanlarda geçersiz değer; gender: Male/Female, diğerleri: Yes/No olmalıdır."
        )

    for col in CAT_COLS:
        X[col] = X[col].astype("string").str.strip()

    X = pd.get_dummies(X, columns=list(CAT_COLS), drop_first=True)
    X = X.reindex(columns=feature_columns, fill_value=0)
    X[num_cols] = scaler.transform(X[num_cols])

    vec = X.iloc[0]
    return {c: float(vec[c]) for c in feature_columns}
