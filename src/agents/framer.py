from core.models import ClienteConfig, NewsItem, FramedNews, FramingRule
import re

PALABRAS_EMERGENCIA = [
    "desaparecido", "desaparecida", "búsqueda", "alerta", "catástrofe",
    "terremoto", "incendio", "inundación", "evacuación", "peligro",
    "seguridad pública", "Defensa Civil", "bomberos"
]

class PoliticalFramer:
    def __init__(self, config: ClienteConfig):
        self.config = config

    def _es_emergencia(self, news: NewsItem) -> bool:
        texto_completo = f"{news.title} {news.content}".lower()
        return any(palabra.lower() in texto_completo for palabra in PALABRAS_EMERGENCIA)

    def frame(self, news: NewsItem) -> FramedNews:
        is_emergency = self._es_emergencia(news)

        # Lógica de tipo
        if is_emergency:
            news_type = "emergencia"
            rule = FramingRule("Informativo urgente", "informativo urgente", [], [])
        elif any(tema.lower() in news.content.lower() for tema in self.config.temas_amplificar):
            news_type = "amplificar"
            rule = FramingRule("Gestión positiva", self.config.tono, self.config.personas_protegidas, self.config.personas_objetivo)
        elif any(tema.lower() in news.content.lower() for tema in self.config.temas_vetar):
            news_type = "vetar"
            rule = FramingRule("Neutralización", self.config.tono, [], [])
        else:
            news_type = "neutral"
            rule = FramingRule("Neutral", self.config.tono, [], [])

        # Construcción prompt (simplificado para el pipeline)
        prompt = f"Redacta una noticia para {self.config.municipio}. Enfoque: {rule.angle}. Tono: {rule.tono}."

        return FramedNews(news, prompt, news_type, rule, is_emergency)
