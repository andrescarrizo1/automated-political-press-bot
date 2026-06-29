# config.py - Archivo de configuración centralizado

from core.models import ClienteConfig
import json

def cargar_config(path: str) -> ClienteConfig:
    """Carga y valida la configuración del cliente desde un JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ClienteConfig(**data)

def construir_prompt_editorial(cliente: ClienteConfig, noticias_texto: str) -> str:
    """Genera el prompt central para LLM, ahora delegando la lógica al sistema agentico."""
    return f"""
    Eres un EDITOR SEO y PERIODISTA MUNICIPAL. Tu objetivo es aplicar las reglas políticas de {cliente.municipio} a la siguiente noticia y redactar un artículo SEO-optimizado.

    REGLAS DE SEGURIDAD:
    - Personas a proteger: {', '.join(cliente.personas_protegidas)}
    - Temas a vetar: {', '.join(cliente.temas_vetar)}

    Tono: {cliente.tono}

    Si detectas una EMERGENCIA (Desaparecido, catástrofe, incendio), ignora los vetos políticos y publica inmediatamente con tono urgente.

    NOTICIA PARA PROCESAR:
    {noticias_texto}

    Devuelve un JSON estrictamente válido:
    {{
        "titulo": "string",
        "slug": "string",
        "contenido_html": "string",
        "resumen_aprobacion": "string",
        "categoria": "string",
        "meta_description": "string",
        "palabras_clave_seo": "string"
    }}
    """
