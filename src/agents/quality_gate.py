from typing import List
from core.models import FramedNews, CheckResult

# Definición de palabras clave de emergencia
PALABRAS_EMERGENCIA = [
    "desaparecido", "desaparecida", "búsqueda", "alerta", "catástrofe",
    "terremoto", "incendio", "inundación", "evacuación", "peligro",
    "seguridad pública", "Defensa Civil", "bomberos"
]

class QualityGate:
    def __init__(self, cliente_config):
        self.config = cliente_config

    def run_all(self, articulo_dict: dict, framed: FramedNews) -> List[CheckResult]:
        checks = []
        texto_completo = f"{articulo_dict.get('titulo', '')} {articulo_dict.get('contenido_html', '')}"

        # 1. Emergency Override
        if framed.is_emergency:
            checks.append(CheckResult("emergency_override", True, "info", "Es emergencia, procediendo."))
            return checks

        # 2. Veto Check
        veto_match = [t for t in self.config.temas_vetar if t.lower() in texto_completo.lower()]
        checks.append(CheckResult("veto_check", len(veto_match) == 0, "critical", f"Temas vetados: {veto_match}"))

        # 3. Protected Persons Check
        # Buscamos nombre protegido cerca de palabras negativas
        for persona in self.config.personas_protegidas:
            if persona.lower() in texto_completo.lower():
                # Búsqueda simple de contexto negativo
                if any(bad in texto_completo.lower() for bad in ["denuncia", "acusado", "escándalo"]):
                    checks.append(CheckResult("proteccion_personas", False, "critical", f"Posible crítica a {persona}"))

        # 4. Length Check
        words = re.sub('<[^<]+?>', '', texto_completo).split()
        checks.append(CheckResult("longitud", len(words) >= 300, "warning", f"Palabras: {len(words)}"))

        # 5. Slug Check
        slug = articulo_dict.get("slug", "")
        checks.append(CheckResult("slug_check", len(slug) > 0 and len(slug) <= 40, "critical", "Slug inválido"))

        return checks

    def is_publishable(self, checks: List[CheckResult]) -> bool:
        return all(c.passed for c in checks if c.severity == "critical")
import re
