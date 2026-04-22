# Müşteri Kaybı Tahmini Projesi — Adım Adım Yol Haritası

> Bu dosya projen ilerledikçe güncellenecektir. Tamamlanan adımlar ✅, devam edenler 🔄, yapılmayanlar ⬜ ile işaretlenecektir.

---

## Genel Bakış

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

## AŞAMA 1 — Proje Yapısını Kurma

### 1.1 Klasör Yapısı

Projeyi başlatmadan önce temiz ve anlaşılır bir klasör yapısı oluştur:

```
churn-project-yzta/            ← proje kökü (klasör adı kopyaya göre değişebilir)
│
├── data/
│   ├── WA_Fn-UseC_-Telco-Customer-Churn.xls   ← ham veri
│   └── processed/
│       ├── train_test_split.pkl               ← 02_preprocessing sonrası (/predict/raw)
│       └── preprocess_artifacts.pkl           ← isteğe bağlı (varsa öncelikli)
│
├── notebooks/
│   ├── 01_eda.ipynb          ← Keşifsel Veri Analizi
│   ├── 02_preprocessing.ipynb ← Veri Ön İşleme
│   └── 03_modeling.ipynb     ← Model Geliştirme
│
├── models/
│   ├── .gitkeep
│   ├── best_model.pkl        ← seçilen en iyi model (XGBoost)
│   ├── model_registry.json   ← tüm modellerin test metrikleri ve dosya yolları
│   └── saved/                ← her modelin .joblib kopyası
│       ├── LogisticRegression.joblib
│       ├── RandomForest.joblib
│       ├── GradientBoosting.joblib
│       ├── XGBoost.joblib
│       └── LightGBM.joblib
│
├── api/
│   ├── app.py                ← FastAPI: GET `/`, POST `/predict`, POST `/predict/raw`
│   └── preprocess.py         ← ham Telco → feature_columns (02 ile uyumlu)
│
├── streamlit_app.py          ← Streamlit UI → `/predict/raw`
├── Dockerfile
├── Dockerfile.streamlit
├── docker-compose.yml        ← api + streamlit (models + data/processed volume)
│
├── requirements.txt
├── README.md
├── CHALLENGE.md
├── FINDINGS.md
├── .gitignore
└── ROADMAP.md
```

Ön işleme ve model adımları `notebooks/` altında. `api/app.py` ve `api/preprocess.py` ile ham/ön işlenmiş iki tahmin yolu desteklenir. Bu depoda ayrı bir `src/` veya `scripts/` klasörü yok. Sanal ortam (örn. `venv/`, `.venv/`) yerelde bulunur; `.gitignore` ile dışlanır, ağaçta gösterilmez.

### 1.2 Sanal Ortam ve Bağımlılıklar

1. Terminali aç, proje klasörüne gir
2. Sanal ortam oluştur (bu kopyada `.venv` kullanılıyor):
   ```
   python -m venv .venv
   ```
3. Sanal ortamı aktive et:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Temel kütüphaneleri yükle:
   ```
   pip install pandas numpy matplotlib seaborn scikit-learn xgboost lightgbm fastapi uvicorn joblib openpyxl jupyter
   ```
5. Yüklenen kütüphaneleri kaydet:
   ```
   pip freeze > requirements.txt
   ```

### 1.3 Git Deposu

1. `git init` ile git başlat
2. `.gitignore` dosyası oluştur — içine şunları ekle:
   - `venv/`, `.venv/`
   - `__pycache__/`
   - `*.pyc`
   - `.ipynb_checkpoints/`
3. İlk commit'i at: `git add . && git commit -m "initial project structure"`

---

## AŞAMA 2 — Keşifsel Veri Analizi (EDA)

`notebooks/01_eda.ipynb` dosyasını aç ve aşağıdaki soruları sırayla cevapla.

### 2.1 Veriyi Tanı

- Veriyi yükle (`pandas` ile)
- Kaç satır, kaç sütun var?
- Sütun isimleri ve veri tipleri neler?
- `.head()`, `.info()`, `.describe()` çıktılarını incele

### 2.2 Hedef Değişkeni Anla

- `Churn` sütununu incele: kaç `Yes`, kaç `No` var?
- Yüzde olarak churn oranı nedir?
- Bar grafik veya pasta grafik ile görselleştir
- **Soru:** Veri dengeli mi, dengesiz mi?

### 2.3 Eksik Değerleri Bul

- Her sütunda eksik değer var mı? (`.isnull().sum()`)
- `TotalCharges` sütununa dikkat et — bu sütun sayısal görünmesine rağmen bazı değerleri boşluk (`" "`) içerebilir, veri tipi `object` olabilir

### 2.4 Sayısal Değişkenleri Analiz Et

Sayısal sütunlar: `tenure`, `MonthlyCharges`, `TotalCharges`

- Histogram ile dağılımlarını gör
- Churn = Yes ve Churn = No gruplarını karşılaştır (örneğin kutu grafiği / boxplot)
- **Soru:** Uzun süreli müşteriler daha mı az churn ediyor?

### 2.5 Kategorik Değişkenleri Analiz Et

Kategorik sütunlar: `gender`, `Partner`, `Dependents`, `PhoneService`, `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`, `Contract`, `PaperlessBilling`, `PaymentMethod`

- Her kategorik değişken için churn oranlarını hesapla
- Gruplandırılmış bar grafikleri çiz
- **Önemli soruları sor:**
  - Hangi sözleşme tipi en çok churn üretiyor?
  - İnternet servis tipi churn ile ilişkili mi?
  - Ek hizmetler (TechSupport, OnlineSecurity) churn'ü azaltıyor mu?

### 2.6 Korelasyon Analizi

- Sayısal değişkenler arasındaki korelasyonu ısı haritası (heatmap) ile göster
- `tenure` ve `TotalCharges` arasındaki ilişkiyi yorumla

### 2.7 EDA Özet Notları

Analizin sonunda şu soruları cevapla ve bir not hücresi ekle:
- En önemli 3-5 bulgu nedir?
- Hangi değişkenlerin modele katkı sağlayacağını düşünüyorsun?
- Veri ile ilgili hangi problemleri (eksik değer, yanlış tip, vb.) tespit ettin?

---

## AŞAMA 3 — Veri Ön İşleme

`notebooks/02_preprocessing.ipynb` dosyasını aç.

### 3.1 Gereksiz Sütunları Kaldır

- `customerID` sütunu model için anlamsız — kaldır

### 3.2 Veri Tipi Düzeltmeleri

- `TotalCharges` sütununu sayısala çevir (`pd.to_numeric(..., errors='coerce')`)
- Boş değerlere dönüşen satırları incele — ne yapacağına karar ver (silmek veya doldurmak)

### 3.3 Eksik Değer Stratejisi

- Eksik değerler varsa nasıl dolduracağına karar ver:
  - Sayısal sütunlar için: ortalama, medyan veya 0
  - Kategorik sütunlar için: mod veya "Unknown" gibi yeni bir kategori
- Kararını not et ve uygula

### 3.4 Hedef Değişkeni Kodla

- `Churn` sütununu `Yes → 1`, `No → 0` olarak dönüştür

### 3.5 Kategorik Değişkenleri Kodla

İki yaygın yöntem var — birini seç veya ikisini karşılaştır:

**Yöntem A: Label Encoding**
- İkili (evet/hayır) sütunlar için uygundur: `gender`, `Partner`, `Dependents`, `PhoneService`, `PaperlessBilling`

**Yöntem B: One-Hot Encoding**
- Birden fazla kategorisi olan sütunlar için: `MultipleLines`, `InternetService`, `Contract`, `PaymentMethod` vb.
- `pd.get_dummies()` veya `sklearn.preprocessing.OneHotEncoder` kullanılabilir

### 3.6 Sayısal Değişkenleri Ölçekle

- `tenure`, `MonthlyCharges`, `TotalCharges` sütunlarını ölçekle
- `StandardScaler` veya `MinMaxScaler` kullan
- **Not:** Ölçeklemeyi sadece sayısal kolonlara uygula

### 3.7 Train / Test Ayrımı

- Veriyi eğitim (%80) ve test (%20) olarak ayır
- `train_test_split` kullan, `random_state` parametresini sabitle (örn: 42)
- `stratify=y` parametresini ekle — churn oranının her iki kümede de korunmasını sağlar

### 3.8 Ön İşleme Pipeline'ı (İleri Seviye)

Hazır hissedersen, tüm ön işleme adımlarını `sklearn.pipeline.Pipeline` ile bir araya getir. Bu sayede aynı adımları API'de de kolayca kullanabilirsin.

---

## AŞAMA 4 — Model Geliştirme ve Karşılaştırma

`notebooks/03_modeling.ipynb` dosyasını aç.

### 4.1 Denenecek Modeller

En az şu modelleri dene ve karşılaştır:

| Model | Kütüphane |
|-------|-----------|
| Logistic Regression | scikit-learn |
| Random Forest | scikit-learn |
| Gradient Boosting | scikit-learn |
| XGBoost | xgboost |
| LightGBM | lightgbm |

### 4.2 Değerlendirme Metrikleri

Churn problemi dengesiz bir sınıflandırma problemidir. Sadece `accuracy` yeterli değildir. Şu metriklere bak:

- **Accuracy** — genel doğruluk
- **Precision** — "churn" dediğinde ne kadar haklısın?
- **Recall** — gerçek churn'lerin kaçını yakaladın?
- **F1-Score** — precision ve recall dengesi
- **ROC-AUC** — modelin ayırt edici gücü
- **Confusion Matrix** — hangi hataları yapıyor?

> **Önemli Not:** Bu projede Recall değeri kritiktir. Kaçırılan bir churn müşterisi, yanlış alarm veren bir tahminten daha maliyetlidir.

### 4.3 Model Karşılaştırma Tablosu

Her model için metrikleri bir tabloda topla:

```
Model              | Accuracy | Precision | Recall | F1   | AUC
-------------------|----------|-----------|--------|------|-----
Logistic Reg.      |          |           |        |      |
Random Forest      |          |           |        |      |
Gradient Boosting  |          |           |        |      |
XGBoost            |          |           |        |      |
LightGBM           |          |           |        |      |
```

### 4.4 Hiperparametre Optimizasyonu (En İyi Model İçin)

En iyi performans veren modeli seç ve iyileştir:

- `GridSearchCV` veya `RandomizedSearchCV` kullan
- Cross-validation ile daha güvenilir sonuç al
- Optimize ettiğin parametreleri ve sonuçları not et

### 4.5 Dengesiz Veri Stratejileri (Opsiyonel ama Değerli)

Eğer churn oranı çok düşükse (örn. %15-20 gibi) şunları dene:
- `class_weight='balanced'` parametresi
- `SMOTE` ile sentetik veri üretimi (`imbalanced-learn` kütüphanesi)

### 4.6 Özellik Önemi (Feature Importance)

- Seçtiğin modelin hangi değişkenleri önemli bulduğunu görselleştir
- Bu sonucu EDA bulguları ile karşılaştır

---

## AŞAMA 5 — En İyi Modeli Kaydetme

### 5.1 Modeli Diske Kaydet

- `joblib` kütüphanesi ile modeli kaydet:
  ```
  joblib.dump(model, "models/best_model.pkl")
  ```
- Eğer ön işleme pipeline'ı ayrı bir nesne ise onu da kaydet:
  ```
  joblib.dump(preprocessor, "models/preprocessor.pkl")
  ```

### 5.2 Model Yükleme Testi

- Kaydedilen modeli tekrar yükle ve birkaç tahmin yaparak çalıştığını doğrula

---

## AŞAMA 6 — API Servisi Geliştirme

`api/app.py` ve `api/preprocess.py` dosyaları.

### 6.1 Framework Seçimi

**FastAPI** (otomatik dokümantasyon + modern): `fastapi`, `uvicorn`

### 6.2 API Yapısı (bu depo)

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | GET | Sağlık; `best_model`, `n_features`, `preprocess_bundle_available` |
| `/predict` | POST | 30 alan — `feature_columns` ile birebir (ön işlenmiş, scaler uygulanmış) |
| `/predict/raw` | POST | Ham Telco alanları; sunucu `preprocess.py` ile 02 ile aynı dönüşümü yapar (paket yoksa 503) |

### 6.3 `/predict` ve `/predict/raw`

- **`/predict`:** İstemci ön işlemiş olmalı; gövde `model_registry.json` → `feature_columns` ile uyumlu.
- **`/predict/raw`:** Ham müşteri JSON’u; örnek ve zorunlu alanlar `README.md` ve OpenAPI `/docs` içinde. Ön işleme için `data/processed/train_test_split.pkl` veya `preprocess_artifacts.pkl` gerekir.

**Örnek yanıt alanları:** `churn_prediction`, `churn_probability`, `message`, `model_used`; `/predict/raw` için ek: `input_mode: "raw"`.

### 6.4 API'yi Test Et

- API: `uvicorn api.app:app --reload`
- Swagger: `http://localhost:8000/docs`
- Streamlit: `streamlit run streamlit_app.py` (API ayrı terminalde)
- Compose: proje kökünde `docker compose up --build`

---

## AŞAMA 7 — Dokümantasyon

### 7.1 README.md Hazırla

`README.md` dosyası şu bölümleri içermelidir:

1. **Proje Açıklaması** — ne yapıyor, ne için?
2. **Kurulum** — sanal ortam ve bağımlılık kurulumu
3. **Kullanım** — API nasıl çalıştırılır?
4. **API Endpoint'leri** — hangi endpoint'ler var, nasıl kullanılır?
5. **Model Performansı** — hangi model seçildi, metrikleri neler?
6. **Klasör Yapısı** — proje dosya organizasyonu

---

## AŞAMA 8 — Docker

Bu depoda:

- **`Dockerfile`** — Python 3.12 slim; `api/` ile API (`uvicorn api.app:app`, port 8000).
- **`docker-compose.yml`** — `api` servisi `./models` ve `./data/processed` klasörlerini salt okunur bağlar; **`Dockerfile.streamlit`** ile `streamlit` servisi (port 8501, `API_BASE=http://api:8000`).

Proje kökünde: `docker compose up --build` — API [localhost:8000](http://localhost:8000), arayüz [localhost:8501](http://localhost:8501).

---

## AŞAMA 9 — Basit Arayüz

- **`streamlit_app.py`** — Form alanları, `httpx` ile `POST /predict/raw`, isteğe bağlı `API_BASE` ortam değişkeni.
- Yerel: `streamlit run streamlit_app.py` (önce API’yi başlat).
- Docker: `docker-compose.yml` içindeki `streamlit` servisi.

---

## Kontrol Listesi (Teslim Öncesi)

- [x] Klasör yapısı düzenli mi?
- [x] `requirements.txt` güncel mi?
- [x] EDA notebook'u çalışıyor mu?
- [x] Ön işleme adımları doğru uygulandı mı?
- [x] En az 3 model karşılaştırıldı mı?
- [x] Model `models/` klasörüne kaydedildi mi?
- [x] API çalışıyor ve `/predict` endpoint'i doğru cevap veriyor mu?
- [x] `README.md` hazır mı?
- [x] Git commit'leri düzenli mi? (yerel akışa bağlı)

---

## Önemli Notlar

- **Her aşama için ayrı bir git commit at.** Örn: `git commit -m "feat: EDA tamamlandı"`
- **Notebook'larını temiz tut.** Çıktılarını kaydet ama gereksiz hücreleri sil.
- **Modeli test verisiyle değerlendir**, eğitim verisiyle değil.
- **API'yi başlatmadan önce modelin yüklendiğinden emin ol.**

---

*Son güncelleme: 22 Nisan 2026 — Aşamalar 1–9 tamam (FastAPI `/predict` + `/predict/raw`, Streamlit, Docker Compose). Repo: [canbmaj7/churn-project-yzta](https://github.com/canbmaj7/churn-project-yzta)*
