---
name: arquitectura-agentica-liberty-press
description: Documentación de la migración de n8n a arquitectura agentica en Python
metadata:
  type: project
---

**Proyecto:** Migración de sistema de contenidos de n8n a Python Agentic.

**Contexto:**
El sistema anterior basado en n8n y prompts gigantes (15k tokens) presentaba problemas de consistencia, limitaciones en SEO, estructura periodística débil y falta de estrategia política clara.

**Cambios realizados:**
1. **Estructura:** Migración a arquitectura modular Python.
2. **Modelos Core (`core/models.py`, `core/config.py`):** Unificación en `ClienteConfig` y modelos canónicos `NewsItem`, `FramedNews`.
3. **Motor de Framing (`agents/framer.py`):** Lógica programática para encuadre político y detección de emergencias.
4. **Escritor (`agents/writer.py`):** Integración async con LLM (Gemini) y plantillas Jinja2.
5. **Quality Gate (`agents/quality_gate.py`):** Filtros automáticos, control de temas vetados y excepción para emergencias.
6. **Persistencia (Database):** SQL Schema unificado con soporte para `content_hash` y metadatos SEO.
7. **Orquestador (main.py):** Pipeline completo unificado, reemplazando la dependencia de n8n.
8. **Publicación y Bot:** Integración mantenida con `blogger_publisher.py` y `telegram_bot.py` sobre arquitectura async.

**Estado actual:** Sistema unificado y funcional.
**Siguiente paso:** Despliegue y monitoreo de las primeras ingestas mediante la nueva arquitectura.
