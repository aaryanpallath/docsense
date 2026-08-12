# Project: DocSense — AI Document Classifier & Extractor

## Goal
A full-stack, containerized, CI/CD-deployed app that classifies and extracts
structured data from uploaded documents (receipts/invoices to start). Built
to demonstrate: full-stack development, REST API design, Docker, CI/CD,
cloud deployment, and applied AI — matching the skill list in an IBM
Software Developer Intern posting.

Build in two phases. Phase 1 is a working weekend MVP. Phase 2 extends it.
Do not start Phase 2 work until Phase 1 is fully working end-to-end
(including deployed and reachable via a public URL).

---

## Tech Stack
- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL (SQLite is fine for
  local dev, but the deployed version should use a real Postgres instance —
  e.g. a free Postgres addon/instance compatible with the deploy target)
- **Frontend:** React (Vite), plain CSS or Tailwind — keep it simple and clean
- **AI:** Call an LLM API (e.g. Anthropic or OpenAI) for structured field
  extraction from document text. Do not train/fine-tune anything — prompt +
  structured JSON output is enough for this project.
- **Containerization:** Docker (separate Dockerfiles for backend and
  frontend), docker-compose for local orchestration
- **CI/CD:** GitHub Actions
- **Deployment:** IBM Cloud Code Engine (Phase 1). IBM Cloud Kubernetes
  Service is a Phase 2 stretch goal if time allows.

---

## Phase 1 — Weekend MVP

### Core user flow
1. User uploads a document (PDF or image of a receipt/invoice, or pastes raw text).
2. Backend sends the document text/content to an LLM with a prompt asking
   for structured JSON: `{ vendor, date, total_amount, category, line_items }`.
3. Backend stores the original document reference + extracted JSON in
   Postgres.
4. Frontend shows a list of uploaded documents and, on click, the extracted
   fields in a clean table/card view.
5. User can edit/correct any extracted field and save the correction (this
   "human-in-the-loop correction" detail is worth keeping — it's a realistic
   product touch, not just a toy demo).

### Backend — API endpoints
- `POST /documents` — upload a document, triggers extraction, returns the
  extracted record
- `GET /documents` — list all documents with summary fields
- `GET /documents/{id}` — full detail for one document
- `PATCH /documents/{id}` — update/correct extracted fields
- `GET /health` — health check endpoint

### Frontend — pages
- Upload page (drag-and-drop or file picker)
- Document list page (table: vendor, date, amount, category)
- Document detail page (extracted fields, editable, save button)

### Docker
- `backend/Dockerfile` — FastAPI app
- `frontend/Dockerfile` — build React app, serve via nginx or a lightweight
  static server
- `docker-compose.yml` — runs backend + frontend + Postgres locally with one
  command

### CI/CD (GitHub Actions)
On every push to `main`:
- Run backend tests (pytest — write a handful of real tests: at minimum,
  API endpoint tests and one test for the extraction-parsing logic)
- Build both Docker images
- Push images to a container registry (IBM Container Registry or Docker Hub)
- Deploy to IBM Cloud Code Engine

### Deployment
- Deploy both services to IBM Cloud Code Engine (free/lite tier)
- End state: a public URL where the app is actually live and usable

### Repo hygiene (do this from the start, not at the end)
- Use a GitHub Project board (Kanban: Backlog / In Progress / Done)
- Break the work into issues before writing code (roughly: scaffold repo →
  backend API → AI extraction → frontend → Docker → CI/CD → deploy)
- Use feature branches + PRs into `main`, even working solo
- `.env.example` file documenting required environment variables (LLM API
  key, database URL, etc.) — never commit real secrets

### README (write this last, but make it the priority deliverable)
- One-paragraph description + live demo link at the top
- Architecture diagram (can be a simple ASCII/text diagram: React → FastAPI
  → LLM API, with Postgres, all containerized, deployed via GitHub Actions
  to IBM Cloud)
- Tech stack list
- How to run locally (`docker-compose up`)
- Screenshot or GIF of the app in use

---

## Phase 2 — Stretch goals (only after Phase 1 is deployed and working)
- Redeploy the same Docker images to IBM Cloud Kubernetes Service instead
  of Code Engine, with a basic `deployment.yaml` / `service.yaml`, to show
  orchestration knowledge beyond serverless
- Add authentication (simple email/password or OAuth) so documents are
  scoped per user
- Add a confidence score or "needs review" flag when the LLM extraction is
  uncertain, surfaced in the UI
- Add CSV export of all extracted documents

---

## Explicit non-goals (keep scope tight)
- No fine-tuning or custom model training — prompting is sufficient
- No mobile app
- No multi-tenant billing/subscription logic
- Don't over-engineer the frontend design system — clean and functional
  beats polished but slow to ship
