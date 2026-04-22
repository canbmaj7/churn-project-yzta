# Müşteri Kaybı (Churn) Tahmini & API Servisi

Telekom sektörüne ait gerçek dünya verisi üzerinde makine öğrenmesi modeli geliştiren ve **FastAPI** ile churn tahmini sunan uçtan uca bir veri bilimi projesi.

---

## Proje Hakkında

Bu proje, [Kaggle — Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) veri setini kullanarak bir müşterinin hizmeti bırakıp bırakmayacağını tahmin eder. Keşifsel analiz, ön işleme, çoklu model karşılaştırması, model kaydı ve **REST API** ile tahmin uçları birlikte sunulur.

### Özellikler

- Kapsamlı Keşifsel Veri Analizi (EDA)
- Birden fazla ML modeli karşılaştırması (Logistic Regression, Random Forest, Gradient Boosting, XGBoost, LightGBM)
- **FastAPI** (sürüm 1.1.0): `GET /` (sağlık + ön işleme paketi bilgisi), `POST /predict` (30 alan, ön işlenmiş), `POST /predict/raw` (ham Telco alanları; sunucu tarafında 02 ile uyumlu ön işleme), otomatik OpenAPI (`/docs`)
- **Streamlit** arayüzü: `streamlit_app.py` — `POST /predict/raw` ile entegre
- **Docker:** `Dockerfile`, `Dockerfile.streamlit`, `docker-compose.yml` (API + arayüz)
- Adım adım yol haritası ve ilerleme günlüğü

---

## Klasör Yapısı

```
churn-project-yzta/   (kök klasör adı sürüme göre değişebilir)
│
├── data/
│   ├── WA_Fn-UseC_-Telco-Customer-Churn.xls   ← ham veri
│   └── processed/
│       ├── train_test_split.pkl               ← 02 çıktısı (scaler, feature_columns; /predict/raw için gerekli)
│       └── preprocess_artifacts.pkl           ← isteğe bağlı hafif paket (varsa öncelikli)
│
├── notebooks/
│   ├── 01_eda.ipynb           ← Keşifsel Veri Analizi
│   ├── 02_preprocessing.ipynb ← Veri Ön İşleme
│   └── 03_modeling.ipynb      ← Model Geliştirme
│
├── models/
│   ├── model_registry.json    ← en iyi model anahtarı, metrikler, feature listesi
│   ├── best_model.pkl         ← geriye dönük tek paket (registry yoksa API bunu yükler)
│   └── saved/                 ← her model ayrı dosya: LogisticRegression.joblib, …, LightGBM.joblib
│
├── api/
│   ├── app.py                 ← FastAPI uygulaması
│   └── preprocess.py          ← ham müşteri → feature_columns (02 ile aynı mantık)
│
├── streamlit_app.py           ← Streamlit UI (API_BASE ile yapılandırılır)
├── Dockerfile                 ← API imajı
├── Dockerfile.streamlit       ← arayüz imajı
├── docker-compose.yml         ← api + streamlit
│
├── requirements.txt          ← Streamlit Cloud / hafif kurulum (streamlit + httpx)
├── requirements-dev.txt      ← Jupyter + notebook + tam ML yığını
├── requirements-api.txt      ← Docker / Render API imajı
├── requirements-streamlit.txt
├── README.md
├── ROADMAP.md
├── FINDINGS.md
└── CHALLENGE.md
```

---

## Kurulum

### 1. Repoyu Klonla

```bash
git clone https://github.com/canbmaj7/churn-project-yzta.git
cd churn-project-yzta
```

### 2. Sanal Ortam Oluştur ve Aktifleştir

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**Mac / Linux:**

```bash
source venv/bin/activate
```

### 3. Bağımlılıkları Yükle

**Notebook, EDA ve model eğitimi** (tam liste):

```bash
pip install -r requirements-dev.txt
```

**Yalnızca Streamlit arayüzü** (Streamlit Cloud ile aynı minimal set):

```bash
pip install -r requirements.txt
```

### 4. Veriyi İndir

[Kaggle — Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) sayfasından veri setini indirip `data/` klasörüne koy.

---

## Kullanım

### Notebook'ları Çalıştır

```bash
jupyter lab
```

Sırayla şu notebook'ları çalıştır:

| Notebook | İçerik |
|----------|--------|
| `notebooks/01_eda.ipynb` | Keşifsel Veri Analizi |
| `notebooks/02_preprocessing.ipynb` | Veri Ön İşleme → `data/processed/train_test_split.pkl` üretir |
| `notebooks/03_modeling.ipynb` | Model Geliştirme (paketi yükler; ön işlemi tekrarlamaz) |

Repoda `train_test_split.pkl` varsa doğrudan `03` ile başlayabilirsin; veri veya kod değiştirdiysen `02`'yi yeniden çalıştır.

### API'yi başlat

Önce: `pip install -r requirements-api.txt` (veya notebook ortamı için `requirements-dev.txt`).

Proje kökünden (sanal ortam açıkken):

```bash
uvicorn api.app:app --reload
```

**Ön koşul:** `models/model_registry.json` ve `models/saved/` altındaki joblib dosyaları (veya yalnızca `models/best_model.pkl`) bulunmalıdır. Bunlar için `03_modeling.ipynb` çalıştırılır.

**`/predict/raw` için ek ön koşul:** `data/processed/train_test_split.pkl` veya `preprocess_artifacts.pkl` (02 çıktısı).

- **Swagger / OpenAPI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Sağlık:** `GET http://localhost:8000/`
- **Tahmin (ön işlenmiş):** `POST http://localhost:8000/predict`
- **Tahmin (ham Telco JSON):** `POST http://localhost:8000/predict/raw`

### Streamlit arayüzü

Ayrı bir terminalde API çalışırken:

```bash
streamlit run streamlit_app.py
```

Varsayılan API adresi `http://127.0.0.1:8000`. Değiştirmek için ortam değişkeni: `API_BASE=http://...`

### Docker Compose

Proje kökünde (modeller ve `data/processed` yerelde hazır olmalı; compose bunları volume ile bağlar):

```bash
docker compose up --build
```

- API: [http://localhost:8000](http://localhost:8000)
- Arayüz: [http://localhost:8501](http://localhost:8501)

---

## API kullanımı

### `GET /`

Yanıt örneği: `status`, `best_model`, `n_features` (30), `preprocess_bundle_available` (`train_test_split.pkl` veya `preprocess_artifacts.pkl` var mı).

### `POST /predict`

İstek gövdesi **düz bir JSON nesnesi** olmalıdır (sarmalayıcı `features` alanı yok). Anahtarlar, `02_preprocessing` çıktısı ve `models/model_registry.json` içindeki `feature_columns` listesi ile **birebir aynı** olmalıdır (30 sütun; ikili/kukla kodlamadan sonra sayısal değerler; sayısal sütunlar scaler sonrası).

**Örnek istek (eksiksiz gövde için tüm `feature_columns` gerekir):**

```json
{
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
  "PaymentMethod_Mailed check": 0
}
```

**Yanıt (JSON):**

```json
{
  "churn_prediction": 1,
  "churn_probability": 0.82,
  "message": "Bu müşteri churn riski taşımaktadır.",
  "model_used": "XGBoost"
}
```

Sunucu **import** anında `models/model_registry.json` dosyasını okur ve `best_model_file` ile en iyi modeli yükler (ör. `saved/XGBoost.joblib`). Registry yoksa `best_model.pkl` kullanılır.

### `POST /predict/raw`

Ham kategorik/sayısal Telco alanları (notebook 02 ile aynı sözleşme; `api/preprocess.py` içindeki `RAW_API_FIELDS`). Ön işleme paketi yoksa **503** döner.

Örnek gövde özeti: `gender`, `SeniorCitizen`, `Partner`, `Dependents`, `tenure`, `PhoneService`, `MultipleLines`, `InternetService`, ilgili ek hizmet alanları, `Contract`, `PaperlessBilling`, `PaymentMethod`, `MonthlyCharges`, `TotalCharges` (Swagger `/docs` içinde tam örnek var).

Başarılı yanıtta `/predict` ile aynı alanlara ek olarak `input_mode: "raw"` eklenir.

---

## Model Performansı

Test kümesi metrikleri (`notebooks/03_modeling.ipynb` çalıştırıldıktan sonra `models/model_registry.json` ile uyumlu).

| Model | Accuracy | Precision | Recall | F1 | AUC |
|-------|----------|-----------|--------|----|-----|
| Logistic Regression | 0.7381 | 0.5043 | 0.7834 | 0.6136 | 0.8417 |
| Random Forest | 0.7743 | 0.5636 | 0.6631 | 0.6093 | 0.8390 |
| Gradient Boosting | 0.7984 | 0.6471 | 0.5294 | 0.5824 | 0.8419 |
| XGBoost | 0.7608 | 0.5345 | 0.7674 | 0.6301 | 0.8367 |
| LightGBM | 0.7502 | 0.5199 | 0.7674 | 0.6199 | 0.8344 |

**Seçilen model (test F1):** XGBoost (`saved/XGBoost.joblib`) — API varsayılan olarak registry üzerinden bu modeli yükler.

> **Not:** Bu problemde Recall değeri kritiktir. Kaçırılan bir churn müşterisi, yanlış alarm veren bir tahminten daha maliyetlidir.

---

## Proje Durumu

| Aşama | Konu | Durum |
|-------|------|-------|
| 1 | Proje Yapısını Kurma | ✅ |
| 2 | Keşifsel Veri Analizi (EDA) | ✅ |
| 3 | Veri Ön İşleme | ✅ |
| 4 | Model Geliştirme ve Karşılaştırma | ✅ |
| 5 | En İyi Modeli Kaydetme | ✅ |
| 6 | API Servisi Geliştirme | ✅ |
| 7 | Dokümantasyon | ✅ |
| 8 | Docker | ✅ |
| 9 | Basit Arayüz (Streamlit) | ✅ |

---

## Kullanılan Teknolojiler

| Kategori | Kütüphane / Araç |
|----------|------------------|
| Veri İşleme | pandas, numpy |
| Görselleştirme | matplotlib, seaborn |
| Makine Öğrenmesi | scikit-learn, xgboost, lightgbm |
| API | FastAPI, uvicorn, httpx (istemci) |
| Arayüz | Streamlit |
| Konteyner | Docker, Docker Compose |
| Model Kaydetme | joblib |
| Notebook | JupyterLab |

---

## Dokümantasyon paketi

Teslim ve bakım için aşağıdaki dosyalar birlikte kullanılır:

| Dosya | İçerik |
|-------|--------|
| [README.md](README.md) | Kurulum, kullanım, API, Docker, Streamlit, model tablosu |
| [ROADMAP.md](ROADMAP.md) | Aşamalı yol haritası ve kontrol listesi |
| [FINDINGS.md](FINDINGS.md) | EDA / ön işleme / model / API özeti ve ilerleme günlüğü |
| [CHALLENGE.md](CHALLENGE.md) | Orijinal proje beklentileri |

---

## Katkı

Bu proje bir veri bilimi challenge'ı kapsamında geliştirilmektedir. Geri bildirim ve öneriler için issue açabilirsiniz.

---

*Detaylı yol haritası için [ROADMAP.md](ROADMAP.md) dosyasına, bulgular için [FINDINGS.md](FINDINGS.md) dosyasına bakınız.*

---

## Geliştirici

- **GitHub:** [@canbmaj7](https://github.com/canbmaj7) — [churn-project-yzta](https://github.com/canbmaj7/churn-project-yzta)
- **İletişim:** ahmetcanotlu@gmail.com
