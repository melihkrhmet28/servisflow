import logging
from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.database import create_service_request, get_all_service_requests, init_db

# Log yapılandırması
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("servisflow")

# Dizin yolları
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


# Hizmet türleri sabitleri
class ServiceTypeEnum(str, Enum):
    RANDEVU_YONETIMI = "randevu_yonetimi"
    MUSTERI_BILDIRIM = "musteri_bildirim"
    OZEL_ENTEGRASYON = "ozel_entegrasyon"


# Pydantic Talep Doğrulama Modeli
class ServiceRequestCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Ad Soyad bilgisi (en az 2, en fazla 100 karakter)",
        examples=["Ahmet Yılmaz"],
    )
    email: EmailStr = Field(
        ...,
        description="Geçerli bir e-posta adresi",
        examples=["ahmet.yilmaz@sirket.com"],
    )
    service_type: ServiceTypeEnum = Field(
        ...,
        description="Seçilen hizmet türü: randevu_yonetimi, musteri_bildirim, ozel_entegrasyon",
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Talep mesajı (en az 10, en fazla 1000 karakter)",
        examples=["İşletmemiz için otomatik randevu ve WhatsApp hatırlatma altyapısı kurmak istiyoruz."],
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name_content(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("Ad Soyad en az 2 karakter olmalıdır ve sadece boşluktan oluşamaz.")
        return trimmed

    @field_validator("message")
    @classmethod
    def validate_message_content(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 10:
            raise ValueError("Mesaj alanı en az 10 karakter olmalıdır ve sadece boşluktan oluşamaz.")
        return trimmed


# Yanıt Modelleri
class ServiceRequestResponseData(BaseModel):
    id: int
    full_name: str
    email: str
    service_type: str
    message: str
    created_at: Any


class ServiceRequestSuccessResponse(BaseModel):
    status: str = "success"
    message: str
    data: ServiceRequestResponseData


# Lifespan: Başlangıçta veritabanını başlat
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ServisFlow başlatılıyor... Veritabanı tabloları doğrulanıyor.")
    init_db()
    logger.info("ServisFlow veritabanı hazır.")
    yield
    logger.info("ServisFlow kapatılıyor...")


# FastAPI uygulaması
app = FastAPI(
    title="ServisFlow API",
    description="Hizmet işletmeleri ve KOBİ'ler için akıllı randevu ve talep yönetim otomasyonu API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS ayarları (gerekli durumlarda harici frontend entegrasyonu için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statik dosyalar ve Şablonlar
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# Özel doğrulama hatası yakalayıcı (Açıklayıcı Türkçe hata mesajları)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages: List[str] = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err["loc"] if loc != "body"])
        msg = err["msg"]
        
        # Pydantic field_validator kaynaklı "Value error, " önekini temizle
        if msg.startswith("Value error, "):
            clean_msg = msg.replace("Value error, ", "").strip()
            error_messages.append(clean_msg)
            continue

        # Kullanıcı dostu mesaj eşleştirmeleri
        if "value is not a valid email address" in msg:
            error_messages.append("Lütfen geçerli bir e-posta adresi giriniz.")
        elif "Input should be 'randevu_yonetimi', 'musteri_bildirim' or 'ozel_entegrasyon'" in msg:
            error_messages.append("Geçersiz hizmet türü seçildi. Lütfen listeden geçerli bir seçenek belirleyiniz.")
        elif "String should have at least 2 characters" in msg:
            error_messages.append("Ad Soyad en az 2 karakter olmalıdır.")
        elif "String should have at least 10 characters" in msg:
            error_messages.append("Mesaj en az 10 karakter içermelidir.")
        elif "String should have at most 100 characters" in msg:
            error_messages.append("Ad Soyad en fazla 100 karakter olabilir.")
        elif "String should have at most 1000 characters" in msg:
            error_messages.append("Mesaj en fazla 1000 karakter olabilir.")
        else:
            error_messages.append(f"{field}: {msg}" if field else msg)

    # exc.errors() içindeki ValueError vb. serileştirilemeyen nesneleri string'e dönüştür
    safe_raw_details = []
    for err in exc.errors():
        err_copy = dict(err)
        if "ctx" in err_copy and isinstance(err_copy["ctx"], dict):
            err_copy["ctx"] = {k: str(v) for k, v in err_copy["ctx"].items()}
        safe_raw_details.append(err_copy)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Girilen bilgilerde doğrulama hatası tespit edildi.",
            "errors": error_messages,
            "raw_details": safe_raw_details,
        },
    )


# --- ROUTE TANIMLARI ---

@app.get("/", response_class=HTMLResponse, summary="Landing Page")
async def get_index(request: Request):
    """
    Ana landing page sayfasını ve servis talep formunu Jinja2 ile render eder.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": "ServisFlow",
            "tagline": "Hizmet İşletmeleri ve KOBİ'ler İçin Akıllı Randevu & Talep Otomasyonu",
        },
    )


@app.get("/health", summary="Sağlık Kontrolü")
async def health_check():
    """
    Docker ve izleme araçları için servis sağlık durumu kontrolü.
    """
    return {
        "status": "ok",
        "service": "ServisFlow",
        "version": "1.0.0",
    }


@app.post(
    "/api/requests",
    response_model=ServiceRequestSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni Servis Talebi Oluştur",
)
async def post_service_request(payload: ServiceRequestCreate):
    """
    Kullanıcıdan gelen servis talebini doğrular ve SQLite veritabanına güvenle kaydeder.
    """
    try:
        saved_record = create_service_request(
            full_name=payload.full_name,
            email=payload.email,
            service_type=payload.service_type.value,
            message=payload.message,
        )

        if not saved_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Kayıt oluşturulurken beklenmeyen bir hata meydana geldi.",
            )

        logger.info(
            f"Yeni talep alındı: ID={saved_record.get('id')}, İsim={payload.full_name}, Hizmet={payload.service_type}"
        )

        return ServiceRequestSuccessResponse(
            status="success",
            message="Servis talebiniz başarıyla alındı. Uzman ekibimiz en kısa sürede sizinle iletişime geçecektir.",
            data=ServiceRequestResponseData(**saved_record),
        )
    except Exception as e:
        logger.error(f"Talep kaydedilirken hata oluştu: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sunucu tarafında veritabanı hatası oluştu. Lütfen daha sonra tekrar deneyiniz.",
        )


@app.get("/api/requests", summary="Mevcut Talepleri Listele (Denetim & Geliştirme)")
async def list_service_requests(limit: int = 50):
    """
    Geliştirme ve doğrulama süreçlerinde taleplerin doğrulanması için yardımcı listeleyici.
    """
    records = get_all_service_requests(limit=limit)
    return {
        "count": len(records),
        "requests": records,
    }
