# Project Setup Guide

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- PostgreSQL CLI (optional, for direct database access)
- Python 3.9+ (for API and workers)
- Node.js 18+ (for frontend/dashboard)

### Initial Setup

1. **Clone and initialize**
   ```bash
   git clone <repo>
   cd job-agent
   cp .env.example .env
   ```

2. **Update environment variables** (`.env`)
   - Change PostgreSQL password
   - Add Gemini API key
   - Add Telegram bot token and chat ID

3. **Start services**
   ```bash
   docker compose up -d
   ```

4. **Verify services are running**
   ```bash
   docker compose ps
   ```

### Accessing Services

- **PostgreSQL**: `localhost:5432` (username: jobagent)
- **n8n Dashboard**: http://localhost:5678 (username: admin)

## Project Structure

```
job-agent/
├── README.md                    # Main project documentation
├── .env                        # Environment variables (DO NOT commit)
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore rules
├── docker-compose.yml          # Docker Compose configuration
│
├── database/                   # Database schemas and migrations
│   ├── README.md
│   ├── init.sql               # Initial PostgreSQL schema
│   └── migrations/            # Future database migrations
│
├── n8n/                        # n8n orchestration workflows
│   ├── README.md
│   ├── workflows/             # n8n workflow definitions
│   └── .env                    # n8n specific config
│
├── api/                        # REST API (Python/FastAPI)
│   ├── README.md
│   ├── requirements.txt
│   ├── main.py
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── schemas/
│   └── tests/
│
├── browser-worker/            # Playwright automation service
│   ├── README.md
│   ├── package.json
│   ├── src/
│   │   ├── index.ts
│   │   ├── services/
│   │   └── utils/
│   └── tests/
│
├── dashboard/                 # Web dashboard
│   ├── README.md
│   ├── package.json
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── services/
│   └── public/
│
└── cv-storage/               # CV storage and management
    ├── README.md
    └── uploads/              # User-uploaded CVs
```

## Development Workflow

### Phase-by-Phase Implementation

1. **Phase 1** ✅ - Repository structure
2. **Phase 2** ✅ - Docker environment
3. **Phase 3** ✅ - Database schema
4. **Phase 4** - Profile & CV management (API endpoints)
5. **Phase 5** - Job source abstraction
6. **Phase 6** - Career page collector (n8n workflow)
7. **Phase 7** - Bdjobs integration
8. **Phase 8** - Job deduplication
9. **Phase 9** - Preference filtering
10. **Phase 10** - Gemini job matching
11. **Phase 11** - CV selection
12. **Phase 12** - Telegram notifications
13. **Phase 13** - Application state machine
14. **Phase 14** - Browser worker (Playwright)
15. **Phase 15** - Automatic form filling
16. **Phase 16** - Unknown field handling with LLM
17. **Phase 17** - Conversational modification
18. **Phase 18** - Final submission safety
19. **Phase 19** - Application tracking
20. **Phase 20** - Dashboard UI
21. **Phase 21** - Reliability & error handling
22. **Phase 22** - Optional improvements

## Important Design Principles

> **LLM interprets and reasons; n8n orchestrates; PostgreSQL stores state; Playwright interacts with websites; the user controls irreversible actions.**

### Key Rules

1. **No automatic submissions** - User must explicitly approve before any application is submitted
2. **State machine** - Applications follow a strict state progression
3. **Approval invalidation** - Any change after approval revokes it (user must re-approve)
4. **Deduplication** - Same job from multiple sources is tracked as one
5. **Cheap filtering first** - Use deterministic filters before expensive AI calls
6. **LLM as advisor** - LLM provides recommendations, not commands
7. **PostgreSQL as source of truth** - All state lives in the database

## Common Commands

### Docker

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Access PostgreSQL
docker exec -it job-agent-db psql -U jobagent -d job_agent

# Access n8n
# Visit http://localhost:5678
```

### Database

```bash
# Create a backup
docker exec job-agent-db pg_dump -U jobagent job_agent > backup.sql

# Restore from backup
docker exec -i job-agent-db psql -U jobagent job_agent < backup.sql

# Run a query
docker exec job-agent-db psql -U jobagent -d job_agent -c "SELECT COUNT(*) FROM jobs;"
```

## Troubleshooting

### PostgreSQL connection failed

```bash
# Check if service is running
docker compose ps postgres

# Check logs
docker compose logs postgres

# Verify connection
docker exec job-agent-db pg_isready -U jobagent
```

### n8n not accessible

```bash
# Check if running
docker compose ps n8n

# Check logs
docker compose logs n8n

# Restart service
docker compose restart n8n
```

### Port already in use

```bash
# Find what's using the port (e.g., 5678)
lsof -i :5678

# Or change ports in docker-compose.yml
```

## Next Steps

1. Set up the API service (Phase 4+)
2. Create n8n workflows for job collection
3. Implement Gemini integration
4. Set up Telegram bot
5. Build the web dashboard

See [README.md](../README.md) for the full roadmap and design details.
