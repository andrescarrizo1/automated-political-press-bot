import sqlite3
from datetime import datetime
from typing import List, Optional
from datetime import timedelta

DB_PATH = "liberty_press.db"


def init_db() -> None:
    """Crea la tabla de noticias si no existe."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS noticias (
                slug TEXT PRIMARY KEY,
                titulo TEXT NOT NULL,
                contenido_html TEXT,
                resumen_aprobacion TEXT,
                categoria TEXT DEFAULT 'politica',
                status TEXT DEFAULT 'PENDING',
                pub_date TEXT,
                error_msg TEXT,
                content_hash TEXT UNIQUE,
                meta_description TEXT,
                palabras_clave_seo TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()


def insertar_noticia(
    slug: str,
    titulo: str,
    contenido_html: str = "",
    resumen_aprobacion: str = "",
    categoria: str = "politica",
    status: str = "PENDING",
    pub_date: str = "",
    error_msg: str = "",
    content_hash: str = "",
    meta_description: str = "",     # Nuevo parámetro
    palabras_clave_seo: str = ""    # Nuevo parámetro
) -> bool:
    """Inserta una noticia. Retorna True si se insertó, False si el slug o el content_hash ya existen."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO noticias (slug, titulo, contenido_html, resumen_aprobacion, categoria, status, pub_date, error_msg, content_hash, meta_description, palabras_clave_seo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (slug, titulo, contenido_html, resumen_aprobacion, categoria, status, pub_date, error_msg, content_hash, meta_description, palabras_clave_seo)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


def get_noticias_por_status(status: str) -> List[dict]:
    """Devuelve todas las noticias con el status indicado."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM noticias WHERE status = ? ORDER BY created_at DESC",
            (status,)
        )
        return [dict(row) for row in cursor.fetchall()]


def actualizar_status(slug: str, nuevo_status: str, error_msg: str = "") -> bool:
    """Actualiza el status de una noticia. Opcionalmente guarda un mensaje de error."""
    with sqlite3.connect(DB_PATH) as conn:
        if error_msg:
            cursor = conn.execute(
                "UPDATE noticias SET status = ?, error_msg = ? WHERE slug = ?",
                (nuevo_status, error_msg, slug)
            )
        else:
            cursor = conn.execute(
                "UPDATE noticias SET status = ? WHERE slug = ?",
                (nuevo_status, slug)
            )
        conn.commit()
        return cursor.rowcount > 0


def get_noticia_por_slug(slug: str) -> Optional[dict]:
    """Devuelve una noticia por su slug, o None si no existe."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM noticias WHERE slug = ?",
            (slug,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_slugs_recientes(dias: int = 30) -> List[str]:
    """Devuelve los slugs procesados en los últimos 'dias' para deduplicación."""
    fecha_limite = (datetime.now() - timedelta(days=dias)).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT slug FROM noticias WHERE created_at >= ? ORDER BY created_at DESC",
            (fecha_limite,)
        )
        return [row[0] for row in cursor.fetchall()]


def get_content_hashes_recientes(dias: int = 30) -> List[str]:
    """Devuelve los content_hashes procesados en los últimos 'dias' para deduplicación."""
    fecha_limite = (datetime.now() - timedelta(days=dias)).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT content_hash FROM noticias WHERE created_at >= ? AND content_hash IS NOT NULL ORDER BY created_at DESC",
            (fecha_limite,)
        )
        return [row[0] for row in cursor.fetchall()]
