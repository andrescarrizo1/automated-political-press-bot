from editorial_agent import llamar_openrouter
from core.models import FramedNews

class ArticleWriter:
    async def write(self, framed: FramedNews) -> dict:
        # Llamada asíncrona al motor editorial (OpenRouter + Gemini)
        resultado = await llamar_openrouter(framed.prompt)
        return resultado
