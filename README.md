# DocSense — AI Document Classifier & Extractor

DocSense is a full-stack app that turns uploaded receipts and invoices (PDF,
image, or pasted text) into structured, editable data. A FastAPI backend
sends document content to the Claude API for structured JSON extraction
(vendor, date, total, category, line items), stores the result in Postgres,
and a React frontend lets users review, correct, and save the extracted
fields — a human-in-the-loop correction loop, not just a one-shot demo.

**Live demo:** https://docsense-frontend.2dguyh5px15c.us-east.codeengine.appdomain.cloud

---

## Architecture

```
                 ┌──────────────┐
    upload/edit  │              │
   ┌────────────▶│  React (SPA) │
   │              │  nginx       │
   │              └──────┬───────┘
   │                     │ REST (JSON)
   │                     ▼
   │              ┌──────────────┐        ┌──────────────┐
   │              │   FastAPI    │──────▶│  Claude API   │
   │              │   backend    │◀──────│ (extraction)  │
   │              └──────┬───────┘        └──────────────┘
   │                     │ SQLAlchemy
   │                     ▼
   │              ┌──────────────┐
   │              │  PostgreSQL  │
   │              └──────────────┘
   │
   └── user (browser)

  All services containerized (Docker) → built & tested by GitHub Actions
  → pushed to IBM Container Registry → deployed to IBM Cloud Code Engine
```

---

## Tech stack

| Layer          | Choice                                      |
| -------------- | -------------------------------------------- |
| Backend        | Python, FastAPI, SQLAlchemy                  |
| Database       | PostgreSQL (SQLite for quick local dev)      |
| Frontend       | React (Vite), plain CSS                      |
| AI extraction  | Anthropic Claude API (structured JSON output)|
| Containers     | Docker, docker-compose                       |
| CI/CD          | GitHub Actions                               |
| Deployment     | IBM Cloud Code Engine (Phase 1)              |

---

## Project layout

```
backend/    FastAPI app, SQLAlchemy models, Claude extraction logic, pytest tests
frontend/   React (Vite) app — upload, document list, document detail pages
.github/    CI/CD workflow (test → build → push → deploy)
docker-compose.yml   Runs backend + frontend + Postgres together
```

---

## Running locally

Requires Docker.

```bash
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY to a real key

docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000 (docs at http://localhost:8000/docs)
- Postgres: localhost:5432 (user/pass/db: `docsense`)

### Running the backend without Docker

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn app.main:app --reload
```

Without `DATABASE_URL` set, the backend falls back to a local SQLite file
(`backend/docsense.db`).

### Running the backend tests

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

### Running the frontend without Docker

```bash
cd frontend
npm install
npm run dev
```

---

## API

| Method | Path                | Description                              |
| ------ | -------------------- | ----------------------------------------- |
| POST   | `/documents`          | Upload a file or raw text; runs extraction, stores + returns the record |
| GET    | `/documents`          | List all documents (summary fields)       |
| GET    | `/documents/{id}`     | Full detail for one document              |
| PATCH  | `/documents/{id}`     | Correct/update extracted fields           |
| GET    | `/health`             | Health check                              |

---

## CI/CD

On every push to `main` (`.github/workflows/ci.yml`):

1. Run backend pytest suite
2. Build both Docker images
3. Push images to IBM Container Registry
4. Deploy to IBM Cloud Code Engine

### Required GitHub Actions secrets

| Secret                      | Purpose                                   |
| ---------------------------- | ------------------------------------------ |
| `IBM_CLOUD_API_KEY`          | IBM Cloud IAM API key                      |
| `IBM_CLOUD_REGION`           | e.g. `us-south`                            |
| `IBM_CLOUD_RESOURCE_GROUP`   | IBM Cloud resource group name              |
| `ICR_NAMESPACE`              | IBM Container Registry namespace           |
| `CE_PROJECT`                 | IBM Cloud Code Engine project name         |
| `ANTHROPIC_API_KEY`          | Passed through to the deployed backend     |
| `DATABASE_URL`               | Postgres connection string for the deployed backend |
| `CORS_ORIGINS`               | Allowed origin(s) for the deployed frontend URL |

### Deploying to IBM Cloud Code Engine (one-time bootstrap)

The CI workflow *updates* existing Code Engine applications, so they need to
exist once before the first automated deploy:

```bash
ibmcloud target -r <region> -g <resource-group>
ibmcloud ce project create --name docsense
ibmcloud ce project select --name docsense

ibmcloud ce application create --name docsense-backend \
  --image icr.io/<namespace>/docsense-backend:latest \
  --port 8000 \
  --env ANTHROPIC_API_KEY=<key> \
  --env DATABASE_URL=<postgres-url>

ibmcloud ce application create --name docsense-frontend \
  --image icr.io/<namespace>/docsense-frontend:latest \
  --port 80
```

IBM's own Databases for PostgreSQL has no free tier (paid "standard" plans
only), so this project uses [Neon](https://neon.tech) instead — free tier,
serverless Postgres, reachable from anywhere including Code Engine. Create a
project there, grab the **pooled** connection string, and use that as
`DATABASE_URL`.

---

## Screenshot

_Add a screenshot or GIF of the app here once deployed._

---

## Phase 2 (stretch goals, after Phase 1 is deployed)

- Redeploy to IBM Cloud Kubernetes Service with `deployment.yaml` / `service.yaml`
- Simple authentication so documents are scoped per user
- Confidence score / "needs review" flag on uncertain extractions
- CSV export of all extracted documents
