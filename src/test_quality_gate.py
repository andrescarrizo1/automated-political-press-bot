import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.models import NewsItem
from core.config import ClientConfig
from agents.framer import PoliticalFramer
from agents.writer import ArticleWriter
from agents.quality_gate import QualityGate

# Configuración con un tema vetado para probar el gate
config = ClientConfig(
    client_id="malargue_pro_gobierno",
    rol_municipal="pro_gobierno",
    personas_protegidas=["Celso Jaque"],
    personas_objetivo=[],
    temas_vetar=["corrupción"],
    temas_amplificar=[]
)

# Noticia que contiene un "tema vetado"
noticia = NewsItem(
    title="Anuncio importante",
    source="Diario",
    date="2026-06-10",
    content="El caso de corrupción en el municipio debe ser investigado.",
    url="http://diario.com",
    client_id="malargue_pro_gobierno"
)

# Pipeline
framer = PoliticalFramer(config)
framed = framer.frame(noticia)
writer = ArticleWriter()
articulo = writer.write(framed)

# Quality Gate
gate = QualityGate(config)
checks = gate.run_all(articulo, framed)

print("--- RESULTADO QUALITY GATE ---")
for c in checks:
    print(f"{c.name}: {'PASSED' if c.passed else 'FAILED'} ({c.severity}) - {c.message}")

if not gate.is_publishable(checks):
    print("\n¡ARTÍCULO BLOQUEADO! No pasa los estándares de calidad.")
else:
    print("\n¡ARTÍCULO APTO PARA PUBLICACIÓN!")
