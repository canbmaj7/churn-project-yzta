# Proje Bulgular ve İlerleme Günlüğü

> Bu dosya proje boyunca yapılan çalışmaları ve elde edilen bulguları özetler.
> Her aşama tamamlandıkça güncellenir.

**Yerel proje yolu:** `C:\Users\Can\Desktop\data\churn-project-yzta 1` (yolda boşluk var; `cd` ile tırnak kullan).

---

## AŞAMA 1 — Proje Kurulumu ✅
**Tarih:** 14 Nisan 2026

### Yapılanlar:
- Proje klasör yapısı oluşturuldu (`data/`, `notebooks/`, `src/`, `models/`, `api/`)
- Python sanal ortamı (`venv`) kuruldu ve aktive edildi
- Gerekli kütüphaneler yüklendi ve `requirements.txt` dosyasına kaydedildi
- Git deposu başlatıldı, `.gitignore` oluşturuldu
- İlk commit atıldı: `initial project structure`

### Kullanılan Kütüphaneler:
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
**Dosyalar:** `notebooks/02_preprocessing.ipynb`, `data/processed/train_test_split.pkl`, `scripts/rebuild_eda_preprocessing.py`

### Yapılanlar:
- `customerID` kaldırıldı; `TotalCharges` sayısala çevrildi, eksikler 0 ile dolduruldu
- `Churn` → 0/1; ikili kategoriler ve `get_dummies(..., drop_first=True)` ile çok kategorili sütunlar kodlandı
- `tenure`, `MonthlyCharges`, `TotalCharges` için `StandardScaler` (fit yalnızca train)
- `train_test_split` %80/%20, `random_state=42`, `stratify=y` → **5634** eğitim, **1409** test satırı; **30** özellik
- Doğrulama assert’leri ve `joblib` paketi: `X_train`, `X_test`, `y_train`, `y_test`, `scaler`, `feature_columns`
- `notebooks/03_modeling.ipynb` ön işlemi tekrarlamadan bu paketi yükler

### Not — Kategorik kodlama:
Çok seviyeli sütunlarda her kategori için `k−1` dummy sütun üretilir; düşen seviye referans (tüm dummy’ler 0 iken) ile temsil edilir; bilgi kaybı yoktur.

---

## Sonraki Adımlar

### AŞAMA 4 — Model Geliştirme ⬜
- [ ] `03_modeling.ipynb`: en az 3 model (ör. Logistic Regression, Random Forest, XGBoost)
- [ ] Metrikler: recall, F1, ROC-AUC, confusion matrix (accuracy tek başına yeterli değil)
- [ ] En iyi modeli seç ve `models/best_model.pkl` kaydet

### AŞAMA 5 — API ⬜
- [ ] FastAPI `/predict`
- [ ] Test

---

*Son güncelleme: Aşama 3 tamamlandı — GitHub: [canbmaj7/churn-project-yzta](https://github.com/canbmaj7/churn-project-yzta)*
