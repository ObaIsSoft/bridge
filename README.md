# 🌉 Bridge.dev
**Transform any website into a clean, structured REST API in seconds.**

Bridge.dev is a powerful orchestration platform designed to "API-ify" the un-API'd web. It combines high-fidelity browser automation with real-time telemetry and advanced security to provide a reliable bridge between static data and your applications.

---

## ✨ Key Features

- **🚀 Website-to-API Bridging**: Define schemas and extract structured JSON from dynamic SPAs and static sites using our Playwright-powered engine.
- **📊 Real-Time Telemetry**: Monitor extraction success rates, data volume, and average latency via a live Command Center.
- **🛡️ Security First**: Integrated secret detection (deep scan) for Git history and active file system monitoring to prevent token leakage.
- **🤖 MCP Integration**: Native support for the Model Context Protocol. Export your bridge configurations directly to AI agents.
- **⚡ Async Orchesration**: Powered by Celery and Redis for handling complex, long-running extraction tasks with robust error recovery.
- **🪝 Delivery Webhooks**: Push extraction payloads directly to your external services with configurable event triggers.

## 🛠️ Tech Stack

### Frontend
- **Framework**: [Next.js 14](https://nextjs.org/) (App Router)
- **Styling**: Tailwind CSS with Premium Glassmorphism Design
- **Icons**: Lucide React
- **Notifications**: Sonner

### Backend
- **API**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **Database**: PostgreSQL with SQLAlchemy (Async)
- **Queue**: Celery + Redis
- **Engine**: Playwright

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (nvm recommended)
- Python 3.12+

### Quick Setup

1. **Clone and Initialize**:
   ```bash
   ./setup.sh
   ```

2. **Run Infrastructure**:
   ```bash
   docker-compose up -d
   ```

3. **Start Development Servers**:
   - **API**: `cd apps/api && python3 main.py`
   - **Web**: `cd apps/web && npm run dev`

Access the platform at `http://localhost:3000`.

---

## 📂 Project Structure

- `apps/api`: FastAPI backend with extraction logic and management routers.
- `apps/web`: Next.js frontend with real-time dashboards and bridge builders.
- `apps/mcp-server`: Dedicated MCP service for AI agent integration.
- `infrastructure`: Docker configurations and database initialization scripts.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
