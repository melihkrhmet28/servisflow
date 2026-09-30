# AI_LOG.md — ServisFlow Yapay Zeka Tasarım ve Doğrulama Kayıtları

Bu doküman, **ServisFlow** projesinin geliştirilmesi sırasında yapay zeka asistanı tarafından alınan mimari kararları, doğrulama adımlarını ve güvenlik/erişilebilirlik tercihlerini belgeler.

---

## 1. Proje Özeti ve Hedefler

- **Proje Adı:** ServisFlow
- **Amaç:** Hizmet işletmeleri ve KOBİ'ler için akıllı randevu ve talep yönetim otomasyonu sunan modern bir landing page ve çalışan talep toplama altyapısı.
- **Hedef Kitle:** Oto servisler, güzellik ve bakım merkezleri, klinikler, özel ders/danışmanlık işletmeleri.

## 1.1 Kullanılan Araçlar ve İş Bölümü

- **Kullanılan AI Ortamı ve Modeli:** Antigravity IDE & Gemini Flash 3.8 (Medium model).
- **Görev Dağılımı:**
  - **AI (Gemini Flash 3.8):** İskelet mimarinin kurulması, FastAPI Pydantic v2 validasyon kurallarının yazılması, Tailwind CSS responsive landing page bileşenlerinin ve Dockerfile yapısının üretilmesi.
  - **Mühendis (Geliştirici):** ServisFlow B2B konseptinin ve veri modellerinin belirlenmesi, istemci ve sunucu doğrulama sınırlarının (en az/en fazla karakter, regex kuralları) tanımlanması, Docker Scout ile konteyner katman güvenlik taraması ve curl ile sınır-değer (edge-case) testlerinin yapılması.
  - **Önemli Not:** Bu projenin geliştirilmesi sırasında, AI asistanı ile mühendis (geliştirici) arasındaki iletişimde **"kullanılan araçlar"** (Antigravity, Gemini, Docker Scout) ve **"görev dağılımı"** (konsept, veri modelleri, güvenlik taraması) bilgileri, projenin teknik kapsamını ve gelişim sürecini eksiksiz belgelemek amacıyla bu AI_LOG.md dosyasına manuel olarak eklenmiştir. Bu meta veriler, projenin sadece kod içeriğini değil, aynı zamanda geliştirme metodolojisini ve kullanılan araç setini de kapsayıcı bir şekilde kaydetmektedir.
  
---

## 2. Mimari Kararlar ve Tasarım Tercihleri

### A. Backend & API (FastAPI)
- **Tercih Nedeni:** FastAPI, yüksek performanslı async desteği, yerel Pydantic tip doğrulaması ve OpenAPI (Swagger) otomatik dokümantasyonu sunduğu için seçildi.
- **Doğrulama (Pydantic v2):**
  - `full_name`: En az 2, en fazla 100 karakter (`@field_validator` ile boşluk temizleme ve sadece boşluk girişlerini engelleme).
  - `email`: `EmailStr` formatı ile RFC uyumlu e-posta adresi doğrulaması.
  - `service_type`: `ServiceTypeEnum` ile sadece tanımlı 3 değer kabul edildi (`randevu_yonetimi`, `musteri_bildirim`, `ozel_entegrasyon`).
  - `message`: En az 10, en fazla 1000 karakter (`@field_validator` ile anlamlı içerik kontrolü).
- **Hata Yönetimi ve Edge-Case Düzeltmesi (Pydantic v2 JSON Serileştirme):** Standart Pydantic 422 hataları kullanıcı dostu ve Türkçe mesajlar içeren JSON nesnelerine dönüştürüldü. Pydantic validasyon sınır testleri sırasında boş isim girişinde sunucunun 500 fırlattığı tespit edildi. RequestValidationError handler'ı incelenerek Pydantic v2 uyumlu hale getirildi ve beklenen 422 Unprocessable Entity yanıtı başarıyla sağlandı. Bu kapsamda, `@field_validator` kaynaklı `ValueError` nesnelerinin `exc.errors()` içindeki `ctx['error']` alanında doğrudan Python Exception örneği olarak kalması ve standart `json.dumps()` sırasında `TypeError: Object of type ValueError is not JSON serializable` (HTTP 500) hatası oluşturması engellendi; güvenli sözlük serileştirmesi sağlandı ve `Value error, ` önekleri temizlenerek kullanıcıya doğrudan 422 Unprocessable Entity döndürüldü.

### B. Veritabanı Katmanı (SQLite)
- **Tercih Nedeni:** Kurgusal SaaS prototipi ve MVP aşaması için sıfır yapılandırmalı, bağımsız ve taşınabilir çözüm.
- **Güvenlik (SQL Injection Koruması):**
  - Tüm INSERT ve SELECT işlemlerinde parametreli sorgular (`?` placeholders) kullanıldı.
  - Ham metin birleştirme (`f-string` veya string concatenation) kesinlikle engellendi.
  - `contextmanager` ile bağlantıların açık kalması engellendi, işlem başarısızlıklarında otomatik `rollback()` sağlandı.

### C. Arayüz ve Erişilebilirlik (Frontend & a11y)
- **Tailwind CSS & Google Fonts:** Modern ve yüksek dönüşüm oranına sahip SaaS estetiği (Plus Jakarta Sans, yumuşak gölgeler, mikro geçişler).
- **Erişilebilirlik (WCAG 2.1 AA Uyumluluğu):**
  - Her form elemanı için açık `<label for="...">` ve `<input id="...">` eşleşmesi yapıldı.
  - Klavyeyle gezinmeyi kolaylaştıran görünür `focus-visible` halkaları eklendi.
  - Hata bildirimleri için `aria-invalid`, `aria-describedby` ve dinamik durumlar için `aria-live="polite"` tanımlandı.
- **İstemci Tarafı Doğrulama ve Durumlar:**
  - Form gönderilmeden önce istemci doğrulaması çalışır ve gereksiz ağ isteklerini önler.
  - Gönderim anında buton `disabled` durumuna geçer ve spinner animasyonu gösterilir.
  - Başarılı gönderimde form gizlenir ve tebrik/onay kartı render edilir. "Yeni Talep Gönder" butonuyla kullanıcı formu tekrar doldurabilir.

### D. Konteynerleştirme (Docker)
- **Güvenlik Standartları:**
  - `python:3.11-slim` taban imajı seçilerek güvenlik açığı yüzeyi küçültüldü.
  - Konteyner içinde `root` yerine `appuser` (UID 1000) kullanıldı.
  - `HEALTHCHECK` direktifi ile uygulamanın sağlık durumu izlenebilir kılındı.
- **Geliştirme Kolaylığı:**
  - `docker-compose.yml` içinde SQLite verilerinin kalıcılığı için `servisflow_data` volume yapısı kuruldu.

---

## 3. Doğrulama ve Test Matrisi

| Test Senaryosu | Beklenen Sonuç | Doğrulama Durumu |
|---|---|---|
| **Ana Sayfa Erişimi (`GET /`)** | 200 OK ve Landing page HTML render | Başarılı |
| **Sağlık Kontrolü (`GET /health`)** | 200 OK ve `{"status": "ok", ...}` JSON | Başarılı |
| **Geçerli Talep Kaydı (`POST /api/requests`)** | 201 Created, DB'ye ekleme ve onay JSON | Başarılı |
| **Geçersiz E-posta Testi** | 422 Unprocessable Entity ve Türkçe hata mesajı | Başarılı |
| **Kısa Mesaj Testi (< 10 karakter)** | 422 Unprocessable Entity ("Mesaj en az 10 karakter...") | Başarılı |
| **Geçersiz Servis Türü** | 422 Unprocessable Entity ("Geçersiz hizmet türü...") | Başarılı |
| **SQL Injection Denemesi** | Parametreli sorgu ile metin olarak güvenle kaydedilir | Başarılı |
| **İstemci UI Durumları** | Spinner gösterimi, hata banner'ı, başarı onay kartı | Başarılı |

---

## 4. Gelecek Geliştirme Önerileri

1. **E-posta & Webhook Entegrasyonu:** Talep geldiğinde Slack/Discord veya SendGrid üzerinden bildirim gönderimi.
2. **Yönetici Paneli (Admin Dashboard):** Gelen taleplerin durumunu (Beklemede, İncelendi, Onaylandı) değiştiren basit bir admin arayüzü.
3. **PostgreSQL Geçişi:** Çoklu sunucu ve yüksek trafik senkronizasyonu için SQLite'tan PostgreSQL / SQLAlchemy ORM yapısına geçiş.
