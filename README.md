# ServisFlow - Akıllı Randevu ve Talep Yönetim Otomasyonu

ServisFlow, hizmet sektöründeki KOBİ'ler (oto servisler, klinikler, güzellik merkezleri, danışmanlar vb.) için randevu çakışmalarını engelleyen, müşteri bildirimlerini otomatikleştiren ve 7/24 talep toplayan modern bir SaaS landing page ve arka plan altyapısıdır.

---

## 🚀 Teknoloji Yığını

- **Backend:** Python 3.11+, FastAPI, Pydantic v2
- **Veritabanı:** SQLite3 (Parametreli SQL injection korumalı mimari)
- **Şablonlama & UI:** Jinja2 Templates, Tailwind CSS (CDN), Google Fonts (Plus Jakarta Sans)
- **Frontend Mantığı:** Vanilla JavaScript (ES6+, Fetch API, dinamik durum ve erişilebilirlik yönetimi)
- **Konteynerleştirme:** Docker (Python 3.11-slim, non-root güvenlik) & Docker Compose

---

## 📁 Proje Dizin Yapısı

```text
servisflow/
├── app/
│   ├── __init__.py          # Paket başlatıcı ve sürüm bilgisi
│   ├── main.py              # FastAPI uygulaması, endpoint'ler, CORS ve Pydantic modelleri
│   ├── database.py          # SQLite veritabanı bağlantısı, şema ve güvenli CRUD fonksiyonları
│   ├── static/
│   │   └── js/
│   │       └── app.js       # İstemci doğrulama, Fetch API ve dinamik UI durumları
│   └── templates/
│       └── index.html       # Modern, responsive ve a11y standartlarına uygun landing page
├── Dockerfile               # Üretime hazır, non-root kullanıcı ve sağlık kontrollü Dockerfile
├── docker-compose.yml       # Tek komutla yerel geliştirme ve çalıştırma yapılandırması
├── requirements.txt         # Gerekli tüm Python kütüphaneleri
├── README.md                # Kurulum, çalıştırma ve test dokümantasyonu
└── AI_LOG.md                # Yapay zeka tasarım ve doğrulama kayıtları
```

---

## ⚡ Hızlı Başlangıç

### Yöntem 1: Docker Compose ile Çalıştırma (Önerilen)

En hızlı ve izole yöntemdir:

```bash
# 1. Proje dizinine geçin
cd servisflow

# 2. Konteyneri derleyin ve arka planda ayağa kaldırın
docker-compose up --build -d

# 3. Logları takip etmek için (isteğe bağlı)
docker-compose logs -f
```

Uygulama hazır olduğunda tarayıcınızdan **`http://localhost:8000`** adresine gidebilirsiniz.

Kapatmak için:
```bash
docker-compose down
```

---

### Yöntem 2: Yerel Python Ortamında Çalıştırma

Sisteminizde Python 3.11 veya üzeri yüklü ise:

```bash
# 1. Proje dizinine geçin
cd servisflow

# 2. Sanal ortam (venv) oluşturun ve aktif edin
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS:
python3 -m venv venv
source venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. FastAPI sunucusunu uvicorn ile başlatın
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔌 API Dokümantasyonu ve Endpoint'ler

FastAPI tarafından otomatik üretilen etkileşimli Swagger dokümantasyonuna **`http://localhost:8000/docs`** adresinden erişebilirsiniz.

### 1. `GET /`
- **Açıklama:** Jinja2 üzerinden modern landing page ve talep formunu döner.
- **Yanıt:** `200 OK` (HTML)

### 2. `GET /health`
- **Açıklama:** Docker sağlık kontrolü ve uptime izleme servisleri için endpoint.
- **Yanıt:**
```json
{
  "status": "ok",
  "service": "ServisFlow",
  "version": "1.0.0"
}
```

### 3. `POST /api/requests`
- **Açıklama:** Yeni bir servis talebi oluşturur. Pydantic şeması ile sıkı doğrulama yapılır.
- **Header:** `Content-Type: application/json`
- **İstek Gövdesi (Payload):**
```json
{
  "full_name": "Canan Dağdeviren",
  "email": "canan@ornekisletme.com",
  "service_type": "randevu_yonetimi",
  "message": "Kliniğimiz için otomatik randevu ve takvim entegrasyonu talep ediyoruz."
}
```

- **Geçerli `service_type` Seçenekleri:**
  - `randevu_yonetimi`
  - `musteri_bildirim`
  - `ozel_entegrasyon`

- **Başarılı Yanıt (HTTP 201 Created):**
```json
{
  "status": "success",
  "message": "Servis talebiniz başarıyla alındı. Uzman ekibimiz en kısa sürede sizinle iletişime geçecektir.",
  "data": {
    "id": 1,
    "full_name": "Canan Dağdeviren",
    "email": "canan@ornekisletme.com",
    "service_type": "randevu_yonetimi",
    "message": "Kliniğimiz için otomatik randevu ve takvim entegrasyonu talep ediyoruz.",
    "created_at": "2026-09-30 16:15:00"
  }
}
```

- **Hatalı Doğrulama Yanıtı (HTTP 422 Unprocessable Entity):**
```json
{
  "status": "error",
  "message": "Girilen bilgilerde doğrulama hatası tespit edildi.",
  "errors": [
    "Lütfen geçerli bir e-posta adresi giriniz.",
    "Mesaj en az 10 karakter içermelidir."
  ]
}
```

### 4. `GET /api/requests`
- **Açıklama:** Geliştirme ve denetim amaçlı kaydedilen talepleri döner.

---

## 🧪 Test ve Doğrulama Adımları

### cURL ile Başarılı Talep Testi
```bash
curl -X POST "http://localhost:8000/api/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Mehmet Kaya",
    "email": "mehmet@oto-servis.com",
    "service_type": "musteri_bildirim",
    "message": "Oto servisimiz için WhatsApp randevu hatırlatma modülü kurmak istiyoruz."
  }'
```

### cURL ile Geçersiz E-posta / Doğrulama Hatası Testi
```bash
curl -X POST "http://localhost:8000/api/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "A",
    "email": "gecersiz-eposta",
    "service_type": "hatali_tur",
    "message": "Kısa"
  }'
```

---

## 🛡️ Güvenlik ve Erişilebilirlik (a11y) Özellikleri

1. **SQL Injection Koruması:** Veritabanına yazılan tüm girdiler SQLite `?` parametreli sorguları ile güvenli şekilde izole edilir.
2. **XSS Koruması:** İstemci tarafında `escapeHtml` fonksiyonu ile dinamik içerikler sterilize edilir.
3. **Form Erişilebilirliği (a11y):** Tüm giriş alanlarında `for` ve `id` birebir eşleştirilmiş, hata durumlarında `aria-invalid` ve `aria-describedby` öznitelikleri dinamik yönetilmiştir. Odaklanan elemanlarda yüksek kontrastlı `focus-visible` halkası mevcuttur.
4. **Konteyner Güvenliği:** Dockerfile içerisinde `root` yerine `appuser` (UID: 1000) kullanılarak en az yetki prensibi uygulanmıştır.
