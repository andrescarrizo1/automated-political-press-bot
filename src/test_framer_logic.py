import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.models import NewsItem
from core.config import ClientConfig
from agents.framer import PoliticalFramer

# Creamos una configuración de prueba
config = ClientConfig(
    client_id="malargue_pro_gobierno",
    rol_municipal="pro_gobierno",
    personas_protegidas=["Celso Jaque"],
    personas_objetivo=["Oposición"],
    temas_vetar=["corrupción", "interna"],
    temas_amplificar=["gestión", "obra"]
)

# Creamos una noticia de prueba
noticia = NewsItem(
    title="Inician las obras de pavimento en Malargüe",
    source="Diario local",
    date="2026-06-10",
    content="El intendente anunció el inicio de las obras de pavimento en los barrios del sector norte con una inversión de 500 millones.",
    url="http://diario.com",
    client_id="malargue_pro_gobierno"
)

# Ejecutamos el framer
framer = PoliticalFramer(config)
framed = framer.frame(noticia)

print("--- PROMPT GENERADO ---")
print(framed.prompt)
print("--- PREVIEW FRAMING ---")
print(f"Tipo: {framed.news_type}")
print(f"Regla aplicada: {framed.rule.angle}")
