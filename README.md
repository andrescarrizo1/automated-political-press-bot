# 🏛️ Automated Political Press Bot (n8n + AI)

> **AI-Driven PR & Content Generation Pipeline (B2G SaaS Ready)**

This repository contains the `workflow.json` of a highly specialized **n8n automation** designed as a **Press and Public Relations Engine** for government institutions, political campaigns, and municipalities. 

It acts as an autonomous press secretary: monitoring news sources in real-time, drafting strategically aligned articles using LLMs, and routing them through a human-in-the-loop approval process before final publication.

---

## 🚀 Business Vision & SaaS Potential

This architecture was designed with a **B2B / B2G (Business-to-Government) Software as a Service (SaaS)** model in mind. 

It is completely **Multi-Tenant and Agnostic**, meaning it can be instantly adapted to any political party (officialism or opposition) or municipality by simply tweaking the LLM's context variables. 

### 💰 Monetization / Tiered Subscription Model
The engine is structured to support different commercial tiers based on client needs:
- **Basic Tier:** Automated blogging + 1 daily digest + 1 news source.
- **Professional Tier:** Multiple RSS feeds + Real-time Telegram approvals + Multi-network posting (Blogger, Facebook).
- **Enterprise / Campaign Tier:** Granular crisis-management prompts + Omni-channel distribution (Twitter/X, Instagram, LinkedIn) + Unlimited daily publications.

---

## ⚙️ Technical Architecture & Features

1. **Multi-Source Ingestion (ETL):** 
   - Scrapes multiple RSS feeds (Google News, local newspapers, official municipality sites) on a customizable schedule (e.g., every 20 minutes).
   - Includes robust deduplication logic to prevent redundant processing.

2. **Advanced Prompt Engineering & Brand Safety:**
   - Utilizes advanced LLMs (e.g., Gemini 2.5 Flash) with heavily engineered system prompts.
   - Enforces **Strict Editorial Rules**: Instructions are hardcoded to specify who to defend, who to critique, which local conflicts to amplify, and which scandals to avoid (Brand Safety).
   
3. **State Management & Database:**
   - Uses Google Sheets as a low-friction, easily accessible intermediate database.
   - Tracks the state of every generated article (`PENDING`, `APROBADO`, `DESCARTADO`, `ERROR`).

4. **Human-in-the-Loop (HITL) Validation:**
   - To guarantee safety in highly sensitive political environments, the AI **does not publish autonomously**.
   - Drafts are sent to an administrator via a Telegram Bot featuring interactive Inline Keyboard buttons (`✅ Publicar` / `❌ Descartar`).
   - Ensures humans have the final say before any content goes public.

5. **Automated Omni-Channel Publishing:**
   - Upon approval, the system updates the database and triggers HTTP POST requests to content platforms (currently integrated with Google Blogger API).
   - The modular design allows easy extension to other APIs like Meta Graph API (Facebook/Instagram) or Twitter/X.

## 🛠️ How to use
Import the `workflow.json` file directly into an active n8n instance. Credentials for Google Sheets, Telegram Bot API, and Blogger API must be configured within the n8n environment to activate the pipeline.
