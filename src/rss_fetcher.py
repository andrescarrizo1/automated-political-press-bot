import asyncio
import re
import hashlib
import feedparser
from typing import List, Set

async def fetch_feed(url: str) -> List[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_parse_feed, url)

def _sync_parse_feed(url: str) -> List[dict]:
    parsed = feedparser.parse(url)
    entradas = []
    for entry in parsed.entries:
        titulo = entry.get("title", "").strip()
        resumen = entry.get("summary", entry.get("description", "")).strip()
        entradas.append({
            "titulo": titulo,
            "link": entry.get("link", "").strip(),
            "resumen": resumen,
            "fecha": entry.get("published", entry.get("updated", "")).strip(),
            "content_hash": _generate_content_hash(titulo, resumen)
        })
    return entradas

def _generate_content_hash(titulo: str, resumen: str) -> str:
    normalized_title = re.sub(r"\s+", " ", titulo).strip().lower()
    normalized_resumen = re.sub(r"<[^>]+>", " ", resumen)
    normalized_resumen = re.sub(r"\s+", " ", normalized_resumen).strip().lower()
    combined_text = f"{normalized_title}|{normalized_resumen}"
    return hashlib.md5(combined_text.encode("utf-8")).hexdigest()

async def recolectar_noticias(feeds: List[str], slugs_vistos: Set[str], content_hashes_vistos: Set[str]) -> List[dict]:
    results = await asyncio.gather(*[fetch_feed(url) for url in feeds], return_exceptions=True)
    noticias = []

    for result in results:
        if isinstance(result, Exception): continue
        for entry in result:
            if entry['content_hash'] not in content_hashes_vistos:
                noticias.append(entry)

    noticias.sort(key=lambda x: x['fecha'], reverse=True)
    return noticias[:8]
