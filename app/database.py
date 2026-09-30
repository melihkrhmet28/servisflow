import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Optional, Dict, Any

# Veritabanı dosya yolu ayarı (Çevre değişkeni veya varsayılan yerel dosya)
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "servisflow.db"
DB_PATH = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH)))

# Veritabanı dizininin var olduğundan emin ol
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    SQLite bağlantısı oluşturan ve işlem bitiminde commit/rollback
    ile kapatmayı garanti eden context manager.
    """
    conn = sqlite3.connect(
        str(DB_PATH),
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        timeout=10.0,
    )
    # Sonuçların sözlük (dict-like) olarak dönmesi için row_factory ayarı
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """
    Gerekli tabloları ve dizinleri oluşturur.
    Uygulama ayağa kalktığında çağrılır.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS service_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        service_type TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    create_index_query = """
    CREATE INDEX IF NOT EXISTS idx_service_requests_created_at 
    ON service_requests(created_at DESC);
    """

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        cursor.execute(create_index_query)


def create_service_request(
    full_name: str, email: str, service_type: str, message: str
) -> Dict[str, Any]:
    """
    Yeni bir servis talebini veritabanına parametreli sorgu (SQL Injection korumalı) ile kaydeder.
    Kaydedilen kaydın bilgilerini döndürür.
    """
    insert_query = """
    INSERT INTO service_requests (full_name, email, service_type, message, created_at)
    VALUES (?, ?, ?, ?, ?);
    """
    now = datetime.utcnow()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Parametreli sorgu ile SQL Injection riski tamamen engellenir
        cursor.execute(
            insert_query,
            (full_name.strip(), email.strip().lower(), service_type.strip(), message.strip(), now),
        )
        record_id = cursor.lastrowid

        # Kaydedilen kaydı geri al
        cursor.execute(
            "SELECT id, full_name, email, service_type, message, created_at FROM service_requests WHERE id = ?",
            (record_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else {}


def get_all_service_requests(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Mevcut servis taleplerini listelemek için yardımcı fonksiyon (idempotent / denetim amaçlı).
    """
    query = """
    SELECT id, full_name, email, service_type, message, created_at 
    FROM service_requests 
    ORDER BY created_at DESC 
    LIMIT ?;
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
