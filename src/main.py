import os
import asyncio
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv

import database
import config
import rss_fetcher
import telegram_bot
import blogger_publisher
from agents.framer import PoliticalFramer
from agents.writer import ArticleWriter
from agents.quality_gate import QualityGate
from core.models import NewsItem

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Feeds RSS definidos para el Municipio de Malargüe
FEEDS = [
    "https://www.malargueadiario.com/feed/",
    "https://malalweb.com.ar/feed/",
    "https://www.malargue.gov.ar/feed/",
    "https://news.google.com/rss/search?q=Malarg%C3%BCe+Mendoza&hl=es-419&gl=AR&ceid=AR:es-419",
]


def _slug_con_sufijo(slug: str, slugs_existentes: set) -> str:
    """Garantiza unicidad de slug agregando -2, -3, etc."""
    if slug not in slugs_existentes:
        return slug
    contador = 2
    while True:
        nuevo = f"{slug}-{contador}"
        if nuevo not in slugs_existentes:
            return nuevo
        contador += 1


async def _publisher_wrapper(noticia: dict) -> str:
    """Callable async que ejecuta la publicación Blogger en un executor para no bloquear."""
    loop = asyncio.get_event_loop()
    url = await loop.run_in_executor(
        None,
        blogger_publisher.publicar_en_blogger,
        noticia["titulo"],
        noticia["contenido_html"],
        noticia.get("categoria", "politica"),
        [noticia.get("categoria", "politica")],
    )
    return url


async def procesar_con_sistema_agentico(cliente_config, noticia_rss):
    # 1. Framing
    framer = PoliticalFramer(cliente_config)
    framed = framer.frame(noticia_rss)

    # 2. Escritura
    writer = ArticleWriter()
    articulo_md = writer.write(framed)

    # 3. Quality Gate
    gate = QualityGate(cliente_config)
    checks = gate.run_all(articulo_md, framed)

    return {
        "slug": framed.original.title.lower().replace(" ", "-"), # Simplificado
        "titulo": framed.original.title,
        "contenido_html": articulo_md, # Se podría convertir de MD a HTML aquí
        "resumen_aprobacion": "Artículo procesado por nuevo sistema agentico.",
        "es_publicable": gate.is_publishable(checks),
        "checks": checks
    }


async def ingesta_loop(cliente_config: config.ClienteConfig, message_queue: asyncio.Queue):
    """Loop principal de ingesta."""
    while True:
        try:
            logger.info("Iniciando ciclo de ingesta...")
            slugs_vistos = set(database.get_slugs_recientes(dias=30))
            content_hashes_vistos = set(database.get_content_hashes_recientes(dias=30))

            noticias_rss_filtradas = await rss_fetcher.recolectar_noticias(FEEDS, slugs_vistos, content_hashes_vistos)
            if not noticias_rss_filtradas:
                await asyncio.sleep(900)
                continue

            for notici_original_rss in noticias_rss_filtradas:
                logger.info(f"Procesando noticia RSS: {notici_original_rss['titulo']}")

                # Inyección del sistema agentico
                noticia_obj = NewsItem(
                    title=notici_original_rss['titulo'],
                    source=notici_original_rss['link'],
                    date=notici_original_rss['fecha'],
                    content=notici_original_rss['resumen'],
                    url=notici_original_rss['link'],
                    client_id=cliente_config.municipio
                )

                resultado = await procesar_con_sistema_agentico(cliente_config, noticia_obj)

                # Si el sistema lo bloquea, saltamos
                if not resultado["es_publicable"]:
                    logger.info(f"Sistema vetó la noticia: {resultado['titulo']}. Motivo: {resultado['checks']}")
                    continue

                slug = resultado.get("slug", "").strip()
                titulo = resultado.get("titulo", "")
                contenido_html = resultado.get("contenido_html", "")
                resumen_aprobacion = resultado.get("resumen_aprobacion", "")

                # Asegurar unicidad de slug
                slugs_existentes_global = set(database.get_slugs_recientes(dias=90))
                slug_unico = _slug_con_sufijo(slug, slugs_existentes_global)

                # 4. Guardar en SQLite
                database.insertar_noticia(
                    slug=slug_unico,
                    titulo=titulo,
                    contenido_html=contenido_html,
                    resumen_aprobacion=resumen_aprobacion,
                    status="PENDING",
                    pub_date=datetime.now().isoformat(),
                    content_hash=notici_original_rss['content_hash'],
                )

                # 5. Notificar vía Telegram
                noticia_db = database.get_noticia_por_slug(slug_unico)
                if noticia_db:
                    await message_queue.put(noticia_db)
                    logger.info(f"Noticia encolada para Telegram: {slug_unico}")

        except Exception as exc:
            logger.exception(f"Error en el ciclo de ingesta: {exc}")

        await asyncio.sleep(900)


if __name__ == "__main__":
    load_dotenv()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    database.init_db()
    cliente_config = config.cargar_config("clientes/malargue_pro_gobierno.json")
    message_queue = asyncio.Queue()
    bot = telegram_bot.LibertyPressBot(token, chat_id, database, _publisher_wrapper, message_queue)
    bot.run_in_thread()
    asyncio.run(ingesta_loop(cliente_config, message_queue))
