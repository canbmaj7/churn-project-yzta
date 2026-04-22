# VERİ BİLİMİ CHALLENGE RAPORU

## PROJE ADI: Müşteri Kaybı Tahmini ve Basit API Servisi

---

## PROJE AMACI

Bu çalışma kapsamında katılımcılardan, verilen veri seti üzerinde bir makine öğrenmesi modeli geliştirmeleri ve bu modeli çalışır bir API servisi haline getirmeleri beklenmektedir. Amaç yalnızca model eğitmek değil, veriyi anlayan ve sonuç üretebilen bir sistem geliştirmektir.

---

## VERİ SETİ

Kullanılacak veri seti Kaggle üzerinde bulunan **Telco Customer Churn** veri setidir. Bu veri seti telekom sektöründe müşteri kaybını tahmin etmeye yönelik gerçek dünya verilerinden oluşmaktadır.

---

## BEKLENEN ÇALIŞMA

Katılımcıların veri seti üzerinde keşifsel veri analizi yapması, veriyi modele uygun hale getirmesi ve bir makine öğrenmesi modeli geliştirmesi beklenmektedir. Modelin amacı, bir müşterinin hizmeti bırakıp bırakmayacağını tahmin etmektir.

Katılımcıların en az bir makine öğrenmesi modeli geliştirmesi, mümkünse birden fazla model deneyerek karşılaştırma yapması beklenir. En uygun performansı veren model seçilmelidir.

Model geliştirme sürecinden sonra, bu modelin bir servis haline getirilmesi gerekmektedir. Bu servis, HTTP üzerinden çalışan basit bir API olmalıdır.

---

## TEKNİK BEKLENTİLER

- Uygulama **Python** ile geliştirilmelidir.
- Makine öğrenmesi için uygun herhangi bir kütüphane kullanılabilir.
- Model bir web servisi üzerinden erişilebilir olmalıdır.
- API içinde en az bir adet **`predict`** endpoint'i bulunmalıdır.
- Bu endpoint, müşteri bilgilerini input olarak almalı ve modelin tahmin sonucunu output olarak döndürmelidir.

---

## BAŞARI KRİTERLERİ

- Veri setinin doğru anlaşılması ve işlenmesi
- Modelin doğru şekilde eğitilmesi ve çalışması
- Tahmin üretme yeteneği
- API servisinin düzgün çalışması
- Kod yapısının anlaşılır ve düzenli olması

---

## EK DEĞERLENDİRME KRİTERLERİ

- Birden fazla model denenmesi ve karşılaştırma yapılması
- Veri ön işleme sürecinin doğru kurgulanması
- Model performansının artırılmasına yönelik çalışmalar
- Basit dokümantasyon hazırlanması
- Opsiyonel olarak **Docker** kullanımı
- Opsiyonel olarak basit bir **arayüz** geliştirilmesi

---

## TESLİM BEKLENTİSİ

- Çalışan bir proje
- Git tabanlı bir kod deposu
- Projenin nasıl çalıştığını açıklayan kısa bir dokümantasyon

---

## SONUÇ

Bu çalışma, katılımcıların yalnızca model geliştirme becerisini değil, aynı zamanda bir makine öğrenmesi çözümünü uçtan uca bir sisteme dönüştürme yeteneğini ölçmeyi amaçlamaktadır.
