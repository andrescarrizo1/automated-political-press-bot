# 🏛️ Motor Automatizado de Prensa Política (RRPP con IA)


![n8n](https://img.shields.io/badge/n8n-FF6D5W?style=for-the-badge&logo=n8n&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Telegram API](https://img.shields.io/badge/Telegram_API-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Google_Sheets-34A853?style=for-the-badge&logo=googlesheets&logoColor=white)
![Blogger API](https://img.shields.io/badge/Blogger_API-FF5722?style=for-the-badge&logo=blogger&logoColor=white)

Un pipeline de automatización end-to-end diseñado para el monitoreo, curaduría y generación de comunicados de prensa en el sector gubernamental y político. 

A diferencia de un bot de redacción tradicional, este sistema actúa como un **Secretario de Prensa Autónomo**. Combina extracción de datos en tiempo real (ETL), procesamiento avanzado con Modelos de Lenguaje Grande (LLMs) fuertemente condicionados por contexto político, y un sistema de validación estricta para garantizar la seguridad de la imagen institucional (Brand Safety).

---

## 🏗️ Evolución de la Arquitectura: De n8n a Python Puro (Agentic Workflow)

Originalmente prototipado en n8n para iteración rápida (Low-Code), el sistema migró a un **Backend en Python Puro** para superar las limitaciones de la orquestación visual y lograr un control absoluto sobre el flujo de ejecución, el asincronismo y la persistencia de datos.

La arquitectura actual implementa un **Flujo Agéntico de 3 Etapas** utilizando procesamiento concurrente:

1. **Ingesta Asíncrona (ETL):** Un motor basado en `asyncio` que consume feeds RSS. Implementa algoritmos de deduplicación utilizando hashes criptográficos y una base de datos local SQLite para evitar procesar noticias repetidas.
2. **Sistema Agéntico Multicapa:** En lugar de un solo prompt masivo, la información fluye por tres agentes especializados:
   - **`PoliticalFramer`:** Analiza la noticia cruda y le aplica el "encuadre" político correcto según las directrices del cliente.
   - **`ArticleWriter`:** Toma el contexto del Framer y redacta el comunicado con formato periodístico.
   - **`QualityGate`:** Un agente evaluador estricto que veta la publicación si detecta desviaciones del manual de estilo o riesgos de *Brand Safety*.
3. **Gestión de Estados (SQLite):** Se abandonó Google Sheets en favor de una base de datos transaccional SQLite local, garantizando integridad referencial y baja latencia. Cada artículo nace como `PENDING`.
4. **Sistema de Aprobación (HITL con Telegram):** Un bot de Telegram integrado asíncronamente recibe los artículos aprobados por el *QualityGate*. El administrador humano tiene la decisión final mediante botones interactivos (Callbacks).
5. **Distribución Omnicanal:** Al recibir el `APROBADO`, el sistema despacha el contenido automáticamente a través de la API de Blogger (con capacidad de escalado a otras redes).

---

## 🛡️ Brand Safety y Quality Gate

En un entorno gubernamental, un error de comunicación desencadena crisis institucionales. Para asegurar la estabilidad en producción, el sistema cuenta con:

### Ingeniería de Prompts Modular
El ecosistema político local (ej. a quién defender, qué conflictos neutralizar) se inyecta dinámicamente en el `PoliticalFramer`. 

### Tolerancia a Fallos y Verificación Cruzada
Si los LLMs (usualmente Gemini vía LangChain/API directa) alucinan o entregan formatos incorrectos, el `QualityGate` actúa como cortafuegos. El sistema no hace *crash*; simplemente veta la noticia y la marca como bloqueada en la base de datos local, alertando sobre el motivo.


---

## 🚀 Framework Liberty Press (Arquitectura SaaS / Multi-Cliente)

Para escalar la solución de un orquestador individual a un producto comercial, el repositorio implementa el **Liberty Press Framework**. Esta estructura de directorios demuestra capacidad para pensar en despliegues a nivel empresarial (B2B/B2G) y arquitecturas multi-cliente.

```text
liberty-press-framework/
├── _template/          # Boilerplate y base estructural para instanciar nuevos clientes
├── clientes/           # Entornos aislados por entidad (Ej: malargue_oficial, malargue_oposicion)
│   ├── config.json     # Variables de entorno y endpoints (Blogger, Telegram) por tenant
│   └── fuentes/        # Feeds RSS y orígenes de datos hiper-locales
├── docs/               # Documentación de onboarding, despliegue de n8n y propuestas
└── MASTER_PROMPT       # El core lógico (Brand Safety & Contexto Político) inyectado al LLM
```

### Por qué esto es relevante a nivel Ingeniería:
- **Separación de Intereses (SoC):** La lógica de orquestación (flujos de n8n) está completamente desacoplada de la configuración del cliente (fuentes, endpoints) y la lógica de negocio (Prompts).
- **Despliegue Replicable (Onboarding Ágil):** El directorio `_template` permite inicializar un nuevo "Secretario de Prensa" en minutos, reduciendo el Time-to-Market para nuevos clientes gubernamentales.
- **Aislamiento de Contexto:** Cada tenant en `clientes/` mantiene sus propias directrices políticas, garantizando que el LLM no mezcle directivas entre diferentes municipalidades o perfiles políticos.
