# telegram_bot.py — versión corregida completa

import asyncio
import logging
import threading
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

logger = logging.getLogger(__name__)


class LibertyPressBot:
    def __init__(self, token: str, chat_id: str, db, publisher_fn, message_queue: asyncio.Queue):
        self.token = token
        self.chat_id = chat_id
        self.db = db
        self.publisher_fn = publisher_fn
        # Queue creada en el thread principal — el bot lee de aquí
        self.message_queue = message_queue
        self.application = None
        self._ready = threading.Event()  # Para sincronizar el arranque

    # ------------------------------------------------------------------ #
    # DIAGNÓSTICO — llama esto UNA VEZ al arrancar para confirmar que
    # el bot ve el chat antes de intentar enviar nada.
    # ------------------------------------------------------------------ #
    async def _diagnostico(self):
        bot = self.application.bot

        me = await bot.get_me()
        logger.info(f"[DIAGNÓSTICO] Bot autenticado: @{me.username} (id={me.id})")

        try:
            chat = await bot.get_chat(self.chat_id)
            logger.info(f"[DIAGNÓSTICO] Chat encontrado: {chat.type} — {getattr(chat, 'title', None) or getattr(chat, 'first_name', None)}")
        except Exception as e:
            logger.error(f"[DIAGNÓSTICO] ❌ get_chat({self.chat_id}) falló: {e}")
            logger.error("Verificá que el chat_id tenga el signo correcto:")
            logger.error("  → Chat privado:  número positivo  (ej: 5378050103)")
            logger.error("  → Grupo/Canal:   número negativo  (ej: -1001234567890)")
            raise  # Falla rápido si el chat no existe — mejor que fallar al publicar

    # ------------------------------------------------------------------ #
    # JOB PERIÓDICO — corre dentro del event loop del bot cada 3 seg
    # Lee de la queue y envía mensajes de aprobación
    # ------------------------------------------------------------------ #
    async def _poll_queue(self, context: ContextTypes.DEFAULT_TYPE):
        try:
            noticia = self.message_queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        try:
            await send_aprobacion(context.bot, self.chat_id, noticia)
            self.message_queue.task_done()
            logger.info(f"[BOT] Noticia encolada a Telegram: {noticia['slug']}")
        except Exception as e:
            logger.error(f"[BOT] Error enviando aprobación: {e}")
            # Re-encolar para reintentar en el próximo ciclo
            await self.message_queue.put(noticia)

    # ------------------------------------------------------------------ #
    # HANDLERS de botones inline
    # ------------------------------------------------------------------ #
    async def handler_publicar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer("⏳ Publicando...")

        slug = query.data.replace("publish:", "")
        noticia = self.db.get_noticia_por_slug(slug)

        if not noticia:
            await query.edit_message_text(f"⚠️ Noticia `{slug}` no encontrada en DB.")
            return

        self.db.actualizar_status(slug, "PROCESANDO")

        try:
            url = await self.publisher_fn(noticia)
            self.db.actualizar_status(slug, "PUBLICADO")
            await query.edit_message_text(
                f"✅ *Publicado*\n\n📰 {noticia['titulo']}\n🔗 {url}",
                parse_mode="Markdown"
            )
            logger.info(f"[BOT] Publicado: {slug} → {url}")
        except Exception as e:
            self.db.actualizar_status(slug, "ERROR", str(e))
            await query.edit_message_text(f"❌ Error publicando `{slug}`:\n`{e}`", parse_mode="Markdown")
            logger.error(f"[BOT] Error publicando {slug}: {e}")

    async def handler_descartar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        slug = query.data.replace("discard:", "")

        self.db.actualizar_status(slug, "DESCARTADO")
        await query.answer("Descartado")
        await query.edit_message_text(f"❌ *Descartado:* `{slug}`", parse_mode="Markdown")
        logger.info(f"[BOT] Descartado: {slug}")

    # ------------------------------------------------------------------ #
    # ARRANQUE — corre en thread separado
    # ------------------------------------------------------------------ #
    def run_in_thread(self):
        thread = threading.Thread(target=self._run_blocking, daemon=True, name="TelegramBot")
        thread.start()
        # Esperar a que el bot esté listo antes de que el loop de ingesta empiece
        self._ready.wait(timeout=30)
        if not self._ready.is_set():
            raise RuntimeError("El bot de Telegram no arrancó en 30 segundos")
        return thread

    def _run_blocking(self):
        """Corre en el thread secundario. Crea su propio event loop limpio."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.application = (
            Application.builder()
            .token(self.token)
            .build()
        )

        self.application.add_handler(
            CallbackQueryHandler(self.handler_publicar, pattern=r"^publish:")
        )
        self.application.add_handler(
            CallbackQueryHandler(self.handler_descartar, pattern=r"^discard:")
        )

        # Job para leer de la queue — corre cada 3 segundos dentro del loop del bot
        self.application.job_queue.run_repeating(
            self._poll_queue, interval=3, first=5
        )

        # Correr diagnóstico post-initialize, pre-polling
        async def _post_init(app):
            await self._diagnostico()
            self._ready.set()  # Señal al thread principal de que estamos listos

        self.application.post_init = _post_init

        # run_polling bloquea este thread — su loop interno maneja todo
        self.application.run_polling(
            allowed_updates=["callback_query"],
            drop_pending_updates=True,  # Ignorar callbacks viejos al reiniciar
        )


# ------------------------------------------------------------------ #
# FUNCIÓN STANDALONE — envía el mensaje de aprobación
# Debe llamarse desde DENTRO del event loop del bot (vía job o handler)
# ------------------------------------------------------------------ #
async def send_aprobacion(bot: Bot, chat_id: str, noticia: dict):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Publicar", callback_data=f"publish:{noticia['slug']}"),
            InlineKeyboardButton("❌ Descartar", callback_data=f"discard:{noticia['slug']}"),
        ]
    ])

    texto = (
        f"🚨 *NUEVA NOTICIA — MALARGÜE*\n\n"
        f"📰 {noticia.get('titulo', 'Sin título')}\n\n"
        f"📝 {noticia.get('resumen_aprobacion', '_(sin resumen)_')}\n\n"
        f"📂 Categoría: {noticia.get('categoria', 'general')}\n"
        f"🔖 Slug: `{noticia['slug']}`\n\n"
        f"👇 *¿Publicamos en Blogger?*"
    )

    await bot.send_message(
        chat_id=chat_id,
        text=texto,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )