# 🚂 SmartRail — Intelligent Indian Railways Journey Planner

> **Next-Generation Multi-Train Routing, Delay Prediction & Risk-Scored Layover Engine**

SmartRail is an intelligent train journey planner built for Indian Railways (IRCTC). When direct trains are full or unavailable, SmartRail discovers smart connecting routes across 100+ major stations, evaluates layover transfer risks, clusters metropolitan terminals (e.g., CSMT ⇄ BCT in Mumbai, NDLS ⇄ NZM in Delhi), and predicts class-wise seat availability and waitlist confirmation chances.

---

## ✨ Features

- **🌐 Time-Dependent Graph Routing**: Custom Dijkstra algorithm navigating time-expanded directed graphs where edges model actual departure/arrival minutes and layovers.
- **🏙️ Multi-Terminal City Clustering**: Automatic transit discovery across sister stations in metro areas (e.g., Bangalore `SBC` & `YPR`, Mumbai `CSMT`, `BCT`, `LTT`, `BDTS`, Delhi `NDLS`, `NZM`, `DLI`) with realistic inter-terminal transit buffers (+45 mins).
- **⚠️ Layover Risk & Reliability Scoring**: Quantifies connection risk (`SAFE`, `MODERATE`, `RISKY`) using buffer thresholds, junction congestion modeling, and historical delay patterns.
- **🎟️ Class-Wise Seat Availability & Waitlist Probabilities**: Real-time mock availability engine across sleeper and AC tiers (`SL`, `3A`, `2A`, `1A`, `CC`, `2S`) with dynamic confirmation chance estimation for waitlisted tickets.
- **🔍 Instant Station Autocomplete & Live Timetables**: Rapid station search with fuzzy matching and full route stoppage views.
- **⚡ High-Performance Caching**: Redis-backed caching for station lookups (24h TTL) and route queries (30m TTL).
- **🎨 Premium Modern Dark UI**: Responsive Next.js interface with glassmorphism, route timelines, and availability chips.

---

## 🏗️ Architecture

```
                       ┌─────────────────────────┐
                       │   Next.js 14 Frontend   │ (Port 3000)
                       │  (App Router + CSS Var) │
                       └───────────┬─────────────┘
                                   │ /api/* rewrites
                                   ▼
                       ┌─────────────────────────┐
                       │     FastAPI Backend     │ (Port 8000)
                       │ (Async SQLAlchemy 2.0)  │
                       └─────┬──────────────┬────┘
                             │              │
              ┌──────────────┴───┐     ┌────┴─────────────┐
              ▼                  ▼     ▼                  ▼
     ┌─────────────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
     │  Time-Expanded  │ │  Layover  │ │PostgreSQL │ │  Redis 7  │
     │ Dijkstra Router │ │  Scorer   │ │    16     │ │  (Cache)  │
     └─────────────────┘ └───────────┘ └───────────┘ └───────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | [Next.js](https://nextjs.org/) (App Router), Vanilla CSS, React 19, Lucide Icons |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/), Python 3.12+, Pydantic v2 |
| **Database** | [PostgreSQL 16](https://www.postgresql.org/) / [Supabase](https://supabase.com/) (AsyncIO + `asyncpg`, see [Supabase Setup Guide](docs/SUPABASE_SETUP.md)) |
| **Caching** | [Redis 7](https://redis.io/) (`redis-py` with `hiredis`) |
| **Graph & Algorithms** | [NetworkX](https://networkx.org/), Custom Time-Dependent Multi-Criteria Dijkstra |
| **ML & Analytics** | [scikit-learn](https://scikit-learn.org/), [XGBoost](https://xgboost.readthedocs.io/), [PyTorch](https://pytorch.org/) (delay modeling) |
| **Orchestration** | [Docker](https://www.docker.com/) & Docker Compose |

---

## 📁 Repository Structure

```
Smart-Rail/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI route handlers (health, stations, trains, journeys)
│   │   ├── config.py        # Pydantic environment settings
│   │   ├── database/        # Async PostgreSQL & Redis connection pools
│   │   ├── models/          # SQLAlchemy ORM models (Station, Train, TrainStop, TrainRun, Delay)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── seed/            # 100+ stations, 85+ express trains, 50k+ delay records
│   │   ├── services/        # Dijkstra graph router, graph builder, scoring engine
│   │   └── main.py          # FastAPI application entry & lifespan
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── components/      # JourneyCard, SearchForm, StationAutocomplete, etc.
│   │   ├── search/          # Search results page with filter drawer
│   │   ├── train/[number]/  # Individual train timetable & stoppage view
│   │   ├── globals.css      # Design tokens, dark theme, and utility styles
│   │   └── layout.js        # Root layout with navigation & footer
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml       # Full stack container configuration
└── README.md
```

---

## 🚀 Getting Started

### Option A: Using Docker Compose (Recommended)

Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Priyanshu55183/Smart-Rail.git
   cd Smart-Rail
   ```

2. **Start all services**:
   ```bash
   docker compose up --build
   ```

3. **Access the application**:
   - **Frontend UI**: [http://localhost:3000](http://localhost:3000)
   - **Backend API**: [http://localhost:8000](http://localhost:8000)
   - **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option B: Local Manual Setup

#### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 16 running locally OR a cloud [Supabase](https://supabase.com/) project (see [Supabase Setup Guide](docs/SUPABASE_SETUP.md))
- Redis running locally (default: `localhost:6379`)

#### 2. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (.env in backend directory or root)
# Ensure DATABASE_URL and REDIS_URL point to your local instances

# Start FastAPI server (seeds DB automatically on first boot)
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup
```bash
cd frontend

# Install packages
npm install

# Start Next.js development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status (DB, Redis, Memory) |
| `GET` | `/api/stations/search?q={query}` | Autocomplete stations by code or name |
| `GET` | `/api/stations/popular` | Retrieve top destination stations |
| `GET` | `/api/trains/{number}` | Get train schedule and stop sequence |
| `POST` | `/api/journeys/search` | Search direct and 1-stop/2-stop connecting journeys |

### Example Journey Search Request

```json
POST /api/journeys/search
Content-Type: application/json

{
  "from_station": "SBC",
  "to_station": "NDLS",
  "date": "2026-09-10",
  "max_layover_hours": 8,
  "min_layover_hours": 0.75,
  "sort_by": "recommended"
}
```

---

## 🧪 Testing

Run backend tests using pytest:

```bash
cd backend
pytest -v
```

---

## 📄 License

This project is licensed under the MIT License.
