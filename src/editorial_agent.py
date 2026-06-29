import os
import re
import json
import asyncio
import unicodedata
import logging
from typing import Optional
import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELO = "google/gemini-2.5-flash"
REINTENTOS = 2

logger = logging.getLogger(__name__)


def _limpiar_y_generar_slug(titulo: str, max_length: int = 40) -> str:
    """
    Genera un slug idempotente desde el título: minúsculas, sin tildes,
    espacios -> guiones, alfanumérico + guiones, máximo 40 chars.
    """
    if not titulo:
        return "noticia"
    base = titulo.lower().strip()
    # Normalizar y eliminar tildes
    base = unicodedata.normalize("NFD", base)
    base = "".join(c for c in base if unicodedata.category(c) != "Mn")
    # Reemplazar cualquier cosa que no sea alfanumérico o espacio por guión
    base = re.sub(r"[^a-z0-9\s]+", " ", base)
    base = re.sub(r"\s+", "-", base).strip("-")
    # Acortar
    if len(base) > max_length:
        base = base[:max_length].rsplit("-", 1)[0]
    if not base:
        base = "noticia"
    return base


def _extraer_json(texto: str) -> Optional[dict]:
    """
    Parser robusto: intenta json.loads directo; si falla, busca el bloque
    JSON más externo con regex.
    """
    texto = texto.strip()
    # Intento 1: carga directa
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass
    # Intento 2: buscar bloque { ... } más grande
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


async def llamar_openrouter(prompt: str) -> dict:
    """
    Llama a OpenRouter con el modelo Gemini 2.5 Flash.
    Parsea la respuesta como JSON robusto.
    Retorna dict con: titulo, slug, contenido_html, resumen_aprobacion, categoria.
    En caso de error, lanza excepción.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY no está configurada")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://example.com",
        "X-Title": "LibertyPress",
    }
    payload = {
        "model": MODELO,
        "messages": [
            {"role": "system", "content": "Eres un agente editorial político municipal argentino. Responde SIEMPRE en JSON estricto sin markdown ni texto extra."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
    }

    last_error = None
    for intento in range(REINTENTOS + 1):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                raw_content = data["choices"][0]["message"]["content"]
                parsed = _extraer_json(raw_content)
                if not parsed:
                    raise ValueError(f"No se pudo parsear JSON de la respuesta: {raw_content[:200]}")

                # Validar campos requeridos
                campos_requeridos = ["titulo", "slug", "contenido_html", "resumen_aprobacion", "categoria", "meta_description", "palabras_clave_seo"]
                for campo in campos_requeridos:
                    if campo not in parsed:
                        raise ValueError(f"Campo requerido faltante en respuesta JSON: {campo}")

                # Generar / limpiar slug
                cleaned_slug = _limpiar_y_generar_slug(str(parsed.get("titulo", "")))
                if not cleaned_slug:
                    cleaned_slug = "noticia"

                # Si el agente devolvió slug vacío (veto), respetarlo
                if str(parsed.get("slug", "")).strip() == "":
                    cleaned_slug = ""

                parsed["slug"] = cleaned_slug
                return parsed
        except Exception as exc:
            last_error = exc
            logger.warning(f"Intento {intento + 1} falló en OpenRouter: {exc}")
            await asyncio.sleep(2 ** intento)

    raise last_error if last_error else RuntimeError("Fallo desconocido en OpenRouter")
