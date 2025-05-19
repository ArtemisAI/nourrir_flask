# NourrIR Flask Project

This is the NourrIR Flask application for educational, nutritional, and creative well-being.

## Architecture Overview

1. **Flask web-app** (Python 3): public pages (`/`, `/politique`, `/valeurs`, etc.) and a JSON endpoint `/nurih-ami` for chatbot messages.
2. **n8n** (low-code automation): hosts a *RAG* workflow (`n8n/workflows/web_chatbot_rag.json`).  
   – Fetches live HTML from the web-app, embeds it (Gemini), stores it in an in-memory vector-store and lets a LangChain **Agent** answer each question.  
   – Uses OpenAI GPT-4o (configurable) as the language-model.  
3. **Docker Compose** orchestrates the two containers (`web` + `n8n`) and mounts `./n8n` into the n8n data folder to persist the workflow database **and** auto-import the JSON file present in Git.

```
                            ┌────────┐  (HTTP POST /nurih-ami)
Frontend JS  ──────────────▶│ Flask  │──────────────────┐
                            └────────┘                  │
                                ▲                       │ REST
                                │ /chat (webhook)       ▼
                            ┌────────┐              ┌───────────┐
                            │  n8n   │──Vector/RAG──▶  Agent/LLM │
                            └────────┘              └───────────┘
```

## Local Development (without Docker)

```bash
# 1. Python deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Export env vars (adapt as needed)
export OLLAMA_URL=http://localhost:11434/api/chat
export OPENAI_API_KEY=sk-xxx
export GEMINI_API_KEY=ya29.XXXXX

# 3. Run Flask only (debug mode)
python app.py  # -> http://localhost:8080
```

**n8n** can also be started locally:

```bash
npx n8n start --tunnel  # or `docker run n8nio/n8n`
```

Import `n8n/workflows/web_chatbot_rag.json` manually the first time, then create the required credentials inside the UI (OpenAI, Google Gemini).  The workflow is designed to work even if Ollama or Gemini is down – it will fall back to the next provider.

## Running with Docker Compose (recommended)

```bash
# build & start
docker-compose up -d --build

# services
#  • Web app  : http://localhost:8282
#  • n8n UI   : http://localhost:5678  (user: n8n  /  pass: n8n)

# stop
docker-compose down
```

### What happens on first start?

1. `./n8n` is mounted into `/home/node/.n8n` (see docker-compose.yml).  
2. If *database.sqlite* is missing, the container executes `n8n import:workflow --input=/home/node/.n8n/workflows/*.json --all` so the JSON workflow shipped in Git is loaded automatically.  
3. Subsequent edits from the UI write to the same volume and survive restarts.  Remember to occasionally run `n8n export:workflow --all` and commit the file if you want Git to stay the source-of-truth.

## Password-protected Policy PDF

The page `/politique` links to *« Consulter la politique d’intégration complète »*.

1. On click, a French prompt asks: “Quel est votre prénom ?”  
2. The input name is checked against `static/assets/names.json` (`Daniel`, `Annie`, `Cynthia`, `Karine`, `Jason`, `Christiana`).  
3. If valid, the user is redirected to `/politique-pdf` which embeds the PDF and offers a download-button. Otherwise an *Accès refusé* alert is shown.

No server-side data is stored; the list can be edited directly in the JSON file.

## Extending the Knowledge Base

The RAG workflow currently indexes the home page and the policy page at every chat request for real-time freshness.  For very large volumes you might:

• Move the “Fetch Pages” node to a daily scheduled workflow.  
• Replace the in-memory vector-store with Supabase or another pgvector DB.

## FAQ

**Q : Comment changer le modèle ?**  
Ouvrez le node “OpenAI Chat Model” dans n8n et modifiez le champ *model*.

**Q : Puis-je tester une version sans OpenAI ?**  
Oui : déconnectez l’API OpenAI, le back-end passera automatiquement par Ollama puis Gemini selon disponibilité.

**Q : Comment ajouter un nouveau nom autorisé pour la politique ?**  
Ajoutez simplement le prénom dans `static/assets/names.json` et poussez sur Git ; aucun redéploiement n’est nécessaire.


## Setup

1. Copy `.env.example` to `.env` and set your environment variable values.
2. Install dependencies: `pip install -r requirements.txt`
3. For development: `python app.py` (no auto-reload).

## Production

- Build and start with Docker Compose:
  ```
  docker-compose build
  docker-compose up -d
  ```
- The application is served via Gunicorn; configuration in `gunicorn_config.py`.
- Health check endpoint: `GET /health` returns `{ "status": "ok" }`.
## n8n Integration

This project now includes an n8n service for chatbot processing. Follow these steps:

1. Create a `.env` file in the project root with:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Access the Flask app at `http://localhost:8282`.
4. Access n8n at `http://localhost:5678`, login with user `n8n` and password `n8n`.
5. A default workflow (`Chatbot Flow`) will be auto-imported on first start from `./n8n/workflows/chatbot_flow.json`.
6. The Flask endpoint `/nurih-ami` will forward messages to n8n at `/webhook/chat` and return the AI response.

n8n data (workflows, credentials) is persisted under `./n8n` and committed to Git.
