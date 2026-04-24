"""
Churn tahmin arayüzü — API'ye ham müşteri gönderir.

Yerel: API'yi ayrı terminalde başlatın (uvicorn api.app:app --reload).
Docker: docker-compose ile API_BASE=http://api:8000 ayarlanır.

Çalıştırma:
    streamlit run streamlit_app.py
"""
from __future__ import annotations

import os

import httpx
import streamlit as st

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="Telco Churn", layout="wide")
st.title("Müşteri kaybı tahmini")
st.caption(f"API: `{API_BASE}` — ham veri `POST /predict/raw` ile gönderilir.")

with st.sidebar:
    st.markdown("**Not:** Ön işleme için `data/processed/train_test_split.pkl` gerekir.")
    if st.button("Sağlık kontrolü (GET /)"):
        try:
            r = httpx.get(f"{API_BASE}/", timeout=10.0)
            st.json(r.json())
        except httpx.RequestError as e:
            st.error(f"API'ye ulaşılamıyor: {e}")

col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("gender", ["Female", "Male"])
    senior = st.selectbox("SeniorCitizen", ["No", "Yes"])
    partner = st.selectbox("Partner", ["Yes", "No"])
    dependents = st.selectbox("Dependents", ["Yes", "No"])
    tenure = st.number_input("tenure (ay)", min_value=0, max_value=100, value=12)
    phone = st.selectbox("PhoneService", ["Yes", "No"])
    multiple = st.selectbox(
        "MultipleLines",
        ["No phone service", "No", "Yes"],
    )
    internet = st.selectbox("InternetService", ["DSL", "Fiber optic", "No"])

with col2:
    osec = st.selectbox("OnlineSecurity", ["No", "Yes", "No internet service"])
    obak = st.selectbox("OnlineBackup", ["No", "Yes", "No internet service"])
    dprot = st.selectbox("DeviceProtection", ["No", "Yes", "No internet service"])
    tsupport = st.selectbox("TechSupport", ["No", "Yes", "No internet service"])
    stv = st.selectbox("StreamingTV", ["No", "Yes", "No internet service"])
    smov = st.selectbox("StreamingMovies", ["No", "Yes", "No internet service"])
    contract = st.selectbox(
        "Contract",
        ["Month-to-month", "One year", "Two year"],
    )
    paperless = st.selectbox("PaperlessBilling", ["Yes", "No"])
    payment = st.selectbox(
        "PaymentMethod",
        [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)",
        ],
    )
    monthly = st.number_input("MonthlyCharges", min_value=0.0, value=70.35)
    total = st.number_input("TotalCharges", min_value=0.0, value=843.15)

payload = {
    "gender": gender,
    "SeniorCitizen": int(senior == "Yes"),
    "Partner": partner,
    "Dependents": dependents,
    "tenure": int(tenure),
    "PhoneService": phone,
    "MultipleLines": multiple,
    "InternetService": internet,
    "OnlineSecurity": osec,
    "OnlineBackup": obak,
    "DeviceProtection": dprot,
    "TechSupport": tsupport,
    "StreamingTV": stv,
    "StreamingMovies": smov,
    "Contract": contract,
    "PaperlessBilling": paperless,
    "PaymentMethod": payment,
    "MonthlyCharges": float(monthly),
    "TotalCharges": float(total),
}

if st.button("Tahmin et", type="primary"):
    try:
        r = httpx.post(f"{API_BASE}/predict/raw", json=payload, timeout=30.0)
        if r.status_code != 200:
            st.error(f"{r.status_code}: {r.text}")
        else:
            st.success("Yanıt alındı")
            st.json(r.json())
    except httpx.RequestError as e:
        st.error(f"İstek hatası: {e}. API çalışıyor mu? (`uvicorn api.app:app --reload`)")
