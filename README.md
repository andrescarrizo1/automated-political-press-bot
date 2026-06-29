# 🏛️ Automated Political Press Engine (AI-Driven PR)


![n8n](https://img.shields.io/badge/n8n-FF6D5W?style=for-the-badge&logo=n8n&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Telegram API](https://img.shields.io/badge/Telegram_API-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Google_Sheets-34A853?style=for-the-badge&logo=googlesheets&logoColor=white)
![Blogger API](https://img.shields.io/badge/Blogger_API-FF5722?style=for-the-badge&logo=blogger&logoColor=white)

Un pipeline de automatización end-to-end diseñado para el monitoreo, curaduría y generación de comunicados de prensa en el sector gubernamental y político. 

A diferencia de un bot de redacción tradicional, este sistema actúa como un **Secretario de Prensa Autónomo**. Combina extracción de datos en tiempo real (ETL), procesamiento avanzado con Modelos de Lenguaje Grande (LLMs) fuertemente condicionados por contexto político, y un sistema de validación estricta para garantizar la seguridad de la imagen institucional (Brand Safety).

---

## 🏗️ Arquitectura y Flujo de Datos

El sistema está orquestado visualmente a través de n8n, dividiendo la lógica en nodos especializados que actúan como micro-servicios interconectados:

1. **Ingesta Multi-Fuente (ETL):** Disparadores asíncronos consultan feeds RSS (Google News, medios locales, webs oficiales) en intervalos programados. El sistema aplica algoritmos de deduplicación para evitar el procesamiento redundante de noticias ya cubiertas.
2. **Procesamiento de Lenguaje Natural (Context-Aware LLM):** Los datos crudos ingresan a Google Gemini 2.5 Flash. Mediante una profunda *Ingeniería de Prompts*, la IA procesa la información aplicando un marco estricto de reglas editoriales locales (reconocimiento de aliados, estrategias frente a la oposición, temas sensibles).
3. **Gestión de Estados (State Machine):** El resultado se almacena temporalmente en Google Sheets (actuando como base de datos transaccional de baja latencia). Cada artículo nace con un estado inicial de `PENDING` (Borrador).
4. **Validación Human-in-the-Loop (HITL):** Para mitigar el riesgo de alucinaciones de la IA o crisis diplomáticas, el orquestador notifica a un administrador vía Telegram. Mediante Callbacks (botones interactivos en el chat), el humano aprueba (`APROBADO`) o rechaza (`DESCARTADO`) el contenido propuesto.
5. **Distribución Omnicanal:** Tras recibir la autorización criptográfica del webhook de Telegram, el flujo actualiza el estado en la base de datos y dispara peticiones HTTP POST hacia las APIs de destino (actualmente Blogger, preparado para escalar a Meta Graph API y X/Twitter).

---

## 🛡️ Brand Safety y Control de Riesgos Políticos

En un entorno gubernamental, un error de comunicación puede desencadenar una crisis institucional. Para asegurar la estabilidad en producción, implementamos capas de seguridad semántica:

### Ingeniería de Prompts Basada en Roles (RBAC Semántico)
El modelo no solo resume texto; opera bajo un conjunto de `[REGLAS_EDITORIALES_ABSOLUTAS]` inyectadas dinámicamente en el System Prompt. Esto obliga a la IA a comprender el ecosistema político local (ej. a quién defender frente a acusaciones, qué temas de infraestructura amplificar y qué conflictos sindicales neutralizar en la redacción).

### Manejo de Excepciones JSON (Graceful Degradation)
Los LLMs ocasionalmente fallan al estructurar las respuestas. El flujo cuenta con un nodo de ejecución en JavaScript (Limpieza JSON) que captura excepciones de parseo, utiliza expresiones regulares para remover "artefactos" (como backticks de markdown residuales) y recupera la estructura de datos sin romper el pipeline.

```javascript
// Ejemplo de recuperación de fallos en la estructura del LLM
try {
    parsed = JSON.parse(jsonString);
} catch (e) {
    const objectMatch = jsonString.match(/\{[\s\S]*\}/);
    if (!objectMatch) throw new Error("No JSON found in response");
    // Lógica de recuperación y limpieza con RegEx...
}
```

---

## 🧠 Justificación Técnica: Orquestación Visual con n8n

> **¿Por qué utilizar n8n para este caso de uso específico?**  
> Mientras que los pipelines de procesamiento masivo de datos se benefician de lenguajes puros como Python, los entornos de relaciones públicas requieren **agilidad táctica**. 

Utilizar una arquitectura basada en n8n nos otorgó tres ventajas críticas a nivel de ingeniería:
1. **Iteración Rápida de Prompts:** Permite a los analistas de comunicación ajustar el contexto del LLM y las reglas editoriales en caliente, sin necesidad de redesplegar el código fuente.
2. **Webhooks Nativos para HITL:** La integración bidireccional inmediata con los Webhooks de Telegram acelera el desarrollo del sistema de aprobación (Human-in-the-Loop) sin gestionar sockets o servidores web intermedios.
3. **Escalabilidad Agnóstica:** El diseño modular (Multi-Tenant) permite clonar el pipeline y adaptarlo a un municipio, campaña o candidato distinto en cuestión de minutos, cambiando únicamente las credenciales de salida y el contexto del prompt.
