# Proje Bulgular ve İlerleme Günlüğü

> Bu dosya proje boyunca yapılan çalışmaları ve elde edilen bulguları özetler.
> Her aşama tamamlandıkça güncellenir.

### Güncel proje ağacı (özet)

Ayrıntılı açıklama için `ROADMAP.md` içinde "Aşama 1 — Klasör Yapısı" bölümüne bakılabilir.

```
churn-project-yzta/     (kök adı sürüme göre değişebilir)
├── data/
│   ├── WA_Fn-UseC_-Telco-Customer-Churn.xls
│   └── processed/
│       ├── train_test_split.pkl      (02 çıktısı; /predict/raw ve scaler için)
│       └── preprocess_artifacts.pkl   (isteğe bağlı; varsa öncelikli)
├── notebooks/          (01_eda, 02_preprocessing, 03_modeling)
├── models/
│   ├── best_model.pkl
│   ├── model_registry.json
│   └── saved/          (*.joblib — tüm eğitilmiş modeller)
├── api/
│   ├── app.py          (FastAPI v1.1.0)
│   └── preprocess.py   (ham Telco → feature_columns)
├── streamlit_app.py
├── Dockerfile, Dockerfile.streamlit, docker-compose.yml
├── requirements.txt
├── README.md
├── CHALLENGE.md
├── FINDINGS.md
├── ROADMAP.md
└── .gitignore
```

---

## AŞAMA 1 — Proje Kurulumu ✅
**Tarih:** 14 Nisan 2026

### Yapılanlar:
- Proje klasör yapısı oluşturuldu (`data/`, `notebooks/`, `models/`; API `api/` altında)
- Python sanal ortamı kuruldu ve aktive edildi
- Gerekli kütüphaneler yüklendi ve `requirements.txt` dosyasına kaydedildi
- `.gitignore` oluşturuldu

### Kullanılan Kütüphaneler (özet):
| Kütüphane | Versiyon | Amaç |
|-----------|----------|------|
| pandas | 3.0.2 | Veri işleme |
| numpy | 2.4.4 | Sayısal işlemler |
| matplotlib | 3.10.8 | Görselleştirme |
| seaborn | 0.13.2 | Görselleştirme |
| scikit-learn | 1.8.0 | ML modelleri ve ön işleme |
| xgboost | 3.2.0 | Gradient boosting modeli |
| lightgbm | 4.6.0 | Gradient boosting modeli |
| fastapi | 0.135.3 | API servisi |
| uvicorn | 0.44.0 | API sunucusu |
| joblib | 1.5.3 | Model kaydetme/yükleme |
| openpyxl | 3.1.5 | Excel dosyası okuma |
| jupyter | 1.1.1 | Notebook ortamı |
| streamlit | 1.52.2 | Arayüz |
| httpx | 0.28.1 | Arayüzden API çağrısı |

---

## AŞAMA 2 — Keşifsel Veri Analizi (EDA) ✅
**Tarih:** 14 Nisan 2026
**Dosya:** `notebooks/01_eda.ipynb`

### Veri Seti Hakkında Genel Bilgiler:
- **Kaynak:** Kaggle — Telco Customer Churn
- **Boyut:** 7043 satır × 21 sütun
- **Her satır:** Bir müşteriyi temsil ediyor
- **Hedef değişken:** `Churn` (Yes / No)

### Sütunlar ve Anlamları:
| Sütun | Tür | Açıklama |
|-------|-----|----------|
| customerID | str | Müşteri kimlik numarası (modele dahil edilmeyecek) |
| gender | str | Cinsiyet (Male / Female) |
| SeniorCitizen | int | Yaşlı vatandaş mı? (0 / 1) |
| Partner | str | Eşi var mı? (Yes / No) |
| Dependents | str | Bakmakla yükümlü olduğu kişi var mı? |
| tenure | int | Kaç aydır müşteri |
| PhoneService | str | Telefon hizmeti var mı? |
| MultipleLines | str | Birden fazla hat var mı? |
| InternetService | str | İnternet hizmet tipi (DSL / Fiber optic / No) |
| OnlineSecurity | str | Online güvenlik hizmeti var mı? |
| OnlineBackup | str | Online yedekleme var mı? |
| DeviceProtection | str | Cihaz koruması var mı? |
| TechSupport | str | Teknik destek var mı? |
| StreamingTV | str | TV yayını var mı? |
| StreamingMovies | str | Film yayını var mı? |
| Contract | str | Sözleşme tipi (Month-to-month / One year / Two year) |
| PaperlessBilling | str | Kağıtsız fatura kullanıyor mu? |
| PaymentMethod | str | Ödeme yöntemi |
| MonthlyCharges | float | Aylık ücret (dolar) |
| TotalCharges | **str** ⚠️ | Toplam ücret — sayısal olmalı, düzeltilecek |
| Churn | str | Müşteri ayrıldı mı? (Yes / No) — hedef değişken |

---

### Bulgular:

#### 1. Hedef Değişken — Churn Dağılımı
```
Churn = No  (Kalan)   : 5174 müşteri → %73.5
Churn = Yes (Ayrılan) : 1869 müşteri → %26.5
```
**Yorum:** Veri dengesizdir. Her 4 müşteriden 1'i ayrılıyor.
Model geliştirirken bu dengesizliği göz önünde bulundurmak gerekiyor.
Sadece "accuracy" metriği yanıltıcı olabilir — recall ve F1 skoruna odaklanılmalı.

#### 2. Sayısal Değişken İstatistikleri
| Değişken | Ortalama | Min | Max | Yorum |
|----------|----------|-----|-----|-------|
| tenure | 32.4 ay | 0 | 72 | Geniş dağılım, yeni ve köklü müşteriler bir arada |
| MonthlyCharges | $64.76 | $18.25 | $118.75 | Oldukça geniş bir aralık |
| SeniorCitizen | 0.16 (oran) | 0 | 1 | Müşterilerin sadece %16'sı yaşlı vatandaş |

#### 3. Veri Kalitesi Sorunları
- `TotalCharges` sütunu `str` (metin) tipinde — sayısala çevrilmeli
- Boş değerler `NaN` olarak gözükmüyor ama bazı satırlarda `" "` (boşluk) var
- `isnull().sum()` hepsi 0 gösterse de bu yanıltıcı — dönüştürme sonrası gerçek NaN'lar ortaya çıkacak

#### 4. Kategorik Değişken Gözlemleri (Grafik Bulgular)
- **Contract:** Month-to-month sözleşmeli müşterilerin churn oranı çok daha yüksek
- **InternetService:** Fiber optic kullananların churn oranı DSL'e göre belirgin şekilde yüksek
- **TechSupport:** Teknik destek almayan müşteriler daha çok ayrılıyor
- **OnlineSecurity:** Online güvenlik hizmeti olmayan müşterilerin churn oranı yüksek

#### 5. Sayısal Değişkenler ile Churn İlişkisi
- **tenure:** Düşük tenure (yeni müşteriler) churn etmeye daha yatkın
- **MonthlyCharges:** Yüksek aylık ücret ödeyen müşteriler daha çok churn ediyor

---

### EDA Sonuç Özeti:
Modelin en çok yararlanacağı değişkenler şunlar olabilir:
1. `Contract` — en güçlü ayrıştırıcı
2. `tenure` — ne kadar süredir müşteri
3. `MonthlyCharges` — ücret seviyesi
4. `InternetService` — hizmet tipi
5. `TechSupport` ve `OnlineSecurity` — ek hizmet kullanımı

---

## AŞAMA 3 — Veri Ön İşleme ✅
**Tarih:** 15 Nisan 2026  
**Dosyalar:** `notebooks/02_preprocessing.ipynb`, `data/processed/train_test_split.pkl`

### Yapılanlar:
- `customerID` kaldırıldı; `TotalCharges` sayısala çevrildi, eksikler 0 ile dolduruldu
- `Churn` → 0/1; ikili kategoriler ve `get_dummies(..., drop_first=True)` ile çok kategorili sütunlar kodlandı
- `tenure`, `MonthlyCharges`, `TotalCharges` için `StandardScaler` (fit yalnızca train)
- `train_test_split` %80/%20, `random_state=42`, `stratify=y` → **5634** eğitim, **1409** test satırı; **30** özellik
- Paket: `X_train`, `X_test`, `y_train`, `y_test`, `scaler`, `feature_columns`, `num_cols` (API `preprocess.py` ile uyumlu)
- `notebooks/03_modeling.ipynb` ön işlemi tekrarlamadan bu paketi yükler

### Not — Kategorik kodlama:
Çok seviyeli sütunlarda her kategori için `k−1` dummy sütun üretilir; düşen seviye referans (tüm dummy’ler 0 iken) ile temsil edilir; bilgi kaybı yoktur.

---

## AŞAMA 4 — Model Geliştirme ve Karşılaştırma ✅
**Dosya:** `notebooks/03_modeling.ipynb`

**Karşılaştırılan modeller** (tümü eğitildi; ayrıntılar `models/model_registry.json`):

| Model | Test Accuracy | Precision | Recall | F1 | ROC-AUC |
|-------|--------------|-----------|--------|-----|---------|
| LogisticRegression | 0.7381 | 0.5043 | 0.7834 | 0.6136 | 0.8417 |
| RandomForest | 0.7743 | 0.5636 | 0.6631 | 0.6093 | 0.8390 |
| GradientBoosting | 0.7984 | 0.6471 | 0.5294 | 0.5824 | 0.8419 |
| **XGBoost** | 0.7608 | 0.5345 | 0.7674 | **0.6301** | 0.8367 |
| LightGBM | 0.7502 | 0.5199 | 0.7674 | 0.6199 | 0.8344 |

**Seçim kriteri:** F1 skoru en yüksek olan model → **XGBoost** (`best_model_key`, `models/saved/XGBoost.joblib`, `best_model.pkl`).

---

## AŞAMA 5 — En İyi Modeli Kaydetme ✅

- `models/saved/*.joblib` — her modelin ayrı dosyası
- `models/best_model.pkl` — dağıtım için seçilen (XGBoost) model
- `model_registry.json` — özellik sütunları, `random_state`, metrikler ve en iyi model yolu

---

## AŞAMA 6 — API Servisi ✅
**Dosyalar:** `api/app.py`, `api/preprocess.py`

### Yapılanlar:
- **FastAPI** (v1.1.0): `GET /` (sağlık, en iyi model, özellik sayısı, `preprocess_bundle_available`)
- `POST /predict` — ön işlenmiş 30 alanlı JSON; yanıtta `churn_prediction`, `churn_probability`, `message`, `model_used`
- `POST /predict/raw` — ham Telco alanları; `preprocess.py` ile 02 ile aynı ön işleme (paket yoksa 503)
- Model yükleme: öncelik `models/model_registry.json` → `best_model_file`; yoksa `models/best_model.pkl`
- Çalıştırma: `uvicorn api.app:app --reload` (proje kökünden)
- OpenAPI: `http://localhost:8000/docs`

---

## AŞAMA 7 — Dokümantasyon ✅
- Kökte `README.md` (kurulum, notebook sırası, `/predict` ve `/predict/raw`, Docker, Streamlit)
- `ROADMAP.md`, `FINDINGS.md`, `CHALLENGE.md` ile birlikte teslim paketi

---

## AŞAMA 8 — Docker ✅
- `Dockerfile` — API imajı (`uvicorn api.app:app`)
- `docker-compose.yml` — `api` + `streamlit`; `./models` ve `./data/processed` salt okunur volume
- `Dockerfile.streamlit` — arayüz imajı (`API_BASE=http://api:8000`)

---

## AŞAMA 9 — Basit arayüz ✅
- `streamlit_app.py` — form ile ham müşteri verisi; `POST /predict/raw`
- Yerelde API ayrı süreçde çalışmalı; Compose ile birlikte kullanılabilir

---

## İsteğe bağlı iyileştirmeler

- CI/CD, gözlemlenebilirlik, hiperparametre aramasının genişletilmesi
- `Bank transfer (automatic)` ödeme yöntemi: eğitimde `drop_first` ile referans kategoriye düşer; API ham gövdede kabul edilir, dummy üretiminde notebook ile tutarlılık için 02 şemasına uyulmalıdır

---

*Son güncelleme: 22 Nisan 2026 — Çekirdek ML + FastAPI (`/predict`, `/predict/raw`) + Streamlit + Docker Compose tamam. GitHub: [canbmaj7/churn-project-yzta](https://github.com/canbmaj7/churn-project-yzta)*
