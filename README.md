# 🏛️ Bot Automatizado de Prensa Política (n8n + IA)

> **Pipeline de Generación de Contenido y Relaciones Públicas impulsado por IA (SaaS B2G Listo para Producción)**

Este repositorio contiene el archivo `workflow.json` de una **automatización en n8n** altamente especializada, diseñada como un **Motor de Prensa y Relaciones Públicas** para instituciones gubernamentales, campañas políticas y municipalidades. 

Actúa como un secretario de prensa autónomo: monitorea fuentes de noticias en tiempo real, redacta artículos estratégicamente alineados usando Modelos de Lenguaje Grande (LLMs) y los envía a través de un proceso de aprobación con validación humana antes de su publicación final.

---

## 🚀 Visión de Negocio y Potencial SaaS

Esta arquitectura fue diseñada pensando en un modelo de negocio **B2B / B2G (Business-to-Government) Software as a Service (SaaS)**. 

Es un sistema completamente **Multi-Tenant (Multi-inquilino) y Agnóstico**, lo que significa que puede adaptarse instantáneamente a cualquier partido político (oficialismo u oposición) o municipio con tan solo ajustar las variables de contexto de la Inteligencia Artificial. 

### 💰 Monetización / Modelo de Suscripción por Niveles (Tiers)
El motor está estructurado para soportar diferentes niveles comerciales (tiers) según las necesidades del cliente:
- **Nivel Básico (Basic Tier):** Publicación automatizada en blog + 1 resumen diario + 1 fuente de noticias.
- **Nivel Profesional (Pro Tier):** Múltiples fuentes RSS + Aprobaciones en tiempo real por Telegram + Publicación en múltiples redes (Blogger, Facebook).
- **Nivel Enterprise / Campaña:** Prompts granulares para manejo de crisis + Distribución Omnicanal (Twitter/X, Instagram, LinkedIn) + Publicaciones diarias ilimitadas.

---

## ⚙️ Arquitectura Técnica y Características

1. **Ingesta Multi-Fuente (ETL):** 
   - Extrae (hace scraping) múltiples feeds RSS (Google News, diarios locales, sitios oficiales del municipio) en un horario personalizable (ej. cada 20 minutos).
   - Incluye una lógica robusta de deduplicación para evitar procesar la misma noticia dos veces.

2. **Ingeniería de Prompts Avanzada y Seguridad de Marca (Brand Safety):**
   - Utiliza LLMs avanzados (como Gemini 2.5 Flash) con prompts de sistema (System Prompts) desarrollados a medida.
   - Aplica **Reglas Editoriales Estrictas**: Las instrucciones están programadas (hardcoded) para especificar a quién defender, a quién criticar, qué conflictos locales amplificar y qué escándalos evitar, garantizando la seguridad de la imagen política.
   
3. **Gestión de Estados y Base de Datos:**
   - Utiliza Google Sheets como una base de datos intermedia de baja fricción y fácil acceso.
   - Rastrea el estado de cada artículo generado (`PENDING`, `APROBADO`, `DESCARTADO`, `ERROR`).

4. **Validación Humana (Human-in-the-Loop - HITL):**
   - Para garantizar la seguridad en entornos políticos altamente sensibles, la IA **no publica de forma autónoma**.
   - Los borradores son enviados a un administrador a través de un Bot de Telegram con botones interactivos (`✅ Publicar` / `❌ Descartar`).
   - Esto asegura que un humano tenga la última palabra antes de que el contenido se haga público.

5. **Publicación Omnicanal Automatizada:**
   - Tras la aprobación, el sistema actualiza la base de datos y dispara peticiones HTTP POST hacia las plataformas de contenido (actualmente integrado con la API de Google Blogger).
   - Su diseño modular permite una fácil expansión hacia otras APIs como la Meta Graph API (Facebook/Instagram) o Twitter/X.

## 🛠️ Cómo usarlo
Importa el archivo `workflow.json` directamente en una instancia activa de n8n. Las credenciales de Google Sheets, la API del Bot de Telegram y la API de Blogger deben configurarse dentro del entorno de n8n para activar el pipeline.
