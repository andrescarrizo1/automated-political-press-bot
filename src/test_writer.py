import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.models import NewsItem
from core.config import ClientConfig
from agents.framer import PoliticalFramer
from agents.writer import ArticleWriter

# Datos de prueba
config = ClientConfig(client_id="malargue_pro_gobierno", rol_municipal="pro_gobierno", personas_protegidas=["Celso Jaque"], personas_objetivo=[], temas_vetar=[], temas_amplificar=[])
noticia = NewsItem(title="Inician las obras de pavimento en Malargüe", source="Diario local", date="2026-06-10", content="El intendente anunció el inicio de las obras de pavimento en los barrios del sector norte con una inversión de 500 millones.", url="http://diario.com", client_id="malargue_pro_gobierno")

# Pipeline
framer = PoliticalFramer(config)
framed = framer.frame(noticia)
writer = ArticleWriter()
articulo = writer.write(framed)

print("--- ARTÍCULO FINAL GENERADO ---")
print(articulo)
