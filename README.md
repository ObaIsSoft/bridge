# Bridge.dev: The Web Interoperability Layer

**Mission**: To transform the chaotic, unstructured web into a reliable, structured API for AI Agents and Developers, while maintaining strict ethical compliance and "Good Citizen" standards.

---

## 🏗 System Architecture

Bridge.dev is a modular platform built to serve as a middleware between raw web content and structured data consumption.

### 1. The Core (Backend)
- **Framework**: Python 3.11 + FastAPI (Async).
- **ORM**: SQLAlchemy 2.0 (Async) with Pydantic v2 schemas.
- **Database**: SQLite (Development) / PostgreSQL (Production).
- **Task Queue**: Celery + Redis (for long-running extractions).
- **Browser Automation**: Playwright (Async) for rendering and interaction.

### 2. The Interface (Frontend)
- **Framework**: Next.js 14 (App Router).
- **Styling**: Tailwind CSS + Shadcn UI (Glassmorphism design).
- **State**: React Server Components + Client Hooks for real-time updates.

### 3. The Agent Interface (MCP)
- **Protocol**: Model Context Protocol (MCP).
- **Server**: `apps/mcp-server` running `FastMCP`.
- **Capabilities**: Exposes Bridge tools (`extract_data`, `get_schema`) directly to AI agents (Claude, cursor, etc.).

---

## 🚀 Key Features (Phases 1-3 Complete)

### Phase 1: The Magic (Schema Discovery)
We don't just scrape HTML; we understand it.
- **`SchemaDiscoveryService`**: Uses LLMs (OpenAI) to analyze a target URL and propose a strictly typed JSON schema.
- **Auto-Fill**: The frontend allows users to paste a URL and get a ready-to-use extraction schema in seconds.

### Phase 2: The Ethical Moat (Security & Compliance)
We prioritize consent and transparency.
- **`PermissionService`**: Automatically parses `robots.txt` and `security.txt`.
- **Smart Discovery**: Scans homepages for `mailto`, Twitter, and GitHub links to identify contact methods.
- **Handshake Protocol**: A structured workflow to reach out to site owners and request official permission or partnership.
- **The Surveyor**: Before scraping, the system checks for official APIs (`api.*`, `developer.*`) and warns the user if a sanctioned alternative exists.

### Phase 3: Agent-Native Evolution
Bridge.dev is designed for Agents first.
- **Action Layer (User Simulation)**:
  - **Interaction Scripts**: Define sequences of actions (Click, Scroll, Wait, Type) to navigate complex UIs.
  - **Authentication**: Supports Cookie injection and Login flows to access gated content.
  - **Implementation**: Powered by `InteractionService` wrapping Playwright.
- **Universal Lookup**:
  - Agents can reference bridges by **UUID** (Legacy), **Slug** (Human-readable, e.g., `amazon-products`), or **Domain** (Natural, e.g., `amazon.com`).
  - **MCP Integration**: `extract_data(bridge_identifier="example.com")` works out of the box.

---

## 🧪 Testing & Verification

We employ a rigorous testing strategy to ensure reliability.

### 1. Unit & Service Tests
- **Interaction Logic**: Verified in `tests/test_interaction.py`.
  - *Scenario*: Navigated to `example.com`, verified content rendering, clicked links, and ensured page transitions.
- **Surveyor**: Batch tested against 50+ URLs to tune API detection heuristics.

### 2. Manual Verification (cURL Protocols)
- **Named Lookups**: Verified endpoints (`GET /bridges/{id}`) accept Slugs and Domains.
  ```bash
  curl http://localhost:8000/api/v1/bridges/example.com
  # Returns 200 OK with correct Bridge JSON
  ```
- **Update Logic**: Verified `PUT` endpoints correctly merge complex JSON fields (`auth_config`, `interaction_script`) without data loss.

### 3. Frontend End-to-End
- **Settings Page**: Manually verified the "User Simulation" settings, ensuring valid JSON is saved and persisted.
- **Dashboard**: Verified real-time stats (Active Bridges, Success Rates) update dynamically.

---

## 🛠 Project Structure

```
bridge/
├── apps/
│   ├── api/                 # FastAPI Backend
│   │   ├── app/
│   │   │   ├── services/    # Core Business Logic (Crawler, Outreach, etc.)
│   │   │   ├── routers/     # API Endpoints
│   │   │   ├── models/      # SQL Tables
│   │   │   └── schemas/     # Pydantic Models
│   │   └── tests/           # Pytest Suite
│   ├── web/                 # Next.js Frontend
│   │   ├── src/app/         # App Router Pages
│   │   └── src/lib/         # API Clients
│   └── mcp-server/          # Agent Protocol Server
├── infrastructure/          # Docker & Deployment Configs
├── package.json             # Monorepo Orchestration
└── docker-compose.yml       # Redis & Services
```

---

## ⚡️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (Docker container recommended)

### 1. Backend Setup
```bash
cd apps/api
poetry install
# Start Redis
docker-compose up -d redis
# Run Server
poetry run python main.py
```

### 2. Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```

### 3. MCP Server (Optional)
```bash
cd apps/mcp-server
poetry install
python main.py
```

---

## 🔮 Next Steps: Phase 4 (Reliability)
With the foundation laid, we are moving to:
- **State Engine**: Redis-based deduplication to prevent re-crawling unchanged data.
- **Auth Managers**: Persistent session management for logged-in scraping contexts.
