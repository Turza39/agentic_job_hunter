# Quick Start Guide

Get the project running locally in 5 minutes.

## Prerequisites

- Docker & Docker Compose installed
- Git installed
- Text editor or IDE (VS Code recommended)

## Step 1: Clone and Setup (1 minute)

```bash
# Clone the repository
git clone <repo-url>
cd agentic-job-hunter

# Copy environment template
cp .env.example .env
```

## Step 2: Update Configuration (2 minutes)

Edit `.env` file and update:

```bash
# CRITICAL - Change these in production:
POSTGRES_PASSWORD=your_secure_password
N8N_BASIC_AUTH_PASSWORD=your_n8n_password

# ADD YOUR API KEYS:
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Get your API keys:
- **Gemini**: https://ai.google.dev
- **Telegram**: @BotFather on Telegram

## Step 3: Start Services (1 minute)

```bash
# Start Docker services
docker compose up -d

# Verify services started
docker compose ps

# Should show:
# - job-agent-db (PostgreSQL) - healthy
# - job-agent-n8n (n8n)       - running
```

## Step 4: Verify Installation (1 minute)

### Check Database

```bash
# Access PostgreSQL
docker exec -it job-agent-db psql -U jobagent -d job_agent

# List tables (you should see ~10 tables)
\dt

# Exit
\q
```

### Check n8n

Open http://localhost:5678 in browser:
- Username: `admin` (or your configured user)
- Password: Check `.env` N8N_BASIC_AUTH_PASSWORD

## Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **n8n** | http://localhost:5678 | admin / (see .env) |
| **PostgreSQL** | localhost:5432 / 5433 | jobagent / (see .env) |
| **API** | http://localhost:8000 | (not yet deployed) |
| **Dashboard** | http://localhost:3000 | (not yet deployed) |

## Common Issues

### PostgreSQL won't start

```bash
# Check logs
docker compose logs postgres

# Common cause: Port 5432 already in use
# Solution: Change POSTGRES_PORT in .env to 5433 (or another free port)

# Restart
docker compose restart postgres
```

### n8n won't start

```bash
# Check logs
docker compose logs n8n

# Wait for PostgreSQL to be healthy
docker compose logs postgres

# Restart after PostgreSQL is ready
docker compose restart n8n
```

### Can't connect to PostgreSQL

```bash
# Verify it's running
docker compose ps postgres

# Check credentials
docker exec job-agent-db psql -U jobagent -d job_agent -c "SELECT 1"

# If connection fails, check .env variables
cat .env | grep POSTGRES
```

## Next Steps

1. **Explore the Database Schema**
   ```bash
   docker exec -it job-agent-db psql -U jobagent -d job_agent
   \d          # List all tables
   SELECT * FROM companies LIMIT 5;  # Query a table
   ```

2. **Access n8n Dashboard**
   - Visit http://localhost:5678
   - Login with credentials from .env
   - Explore the interface (no workflows yet)

3. **Plan Phase 4**
   - Start building the API service
   - Set up FastAPI project
   - Create endpoints for profiles and CVs

4. **Set up IDE**
   - Recommended: VS Code with Docker extension
   - Install Python extension (for API development)
   - Install TypeScript extension (for browser worker)

## Useful Commands

### Docker

```bash
# View service logs
docker compose logs -f n8n          # Follow n8n logs
docker compose logs postgres        # Show PostgreSQL logs

# Stop services
docker compose down                 # Stop and remove containers
docker compose down -v              # Also remove volumes (WARNING: deletes data)

# Rebuild services
docker compose build

# Execute commands in container
docker exec -it job-agent-db bash  # Shell into database container
```

### Database Backup

```bash
# Create backup
docker exec job-agent-db pg_dump -U jobagent job_agent > backup.sql

# Restore backup
docker exec -i job-agent-db psql -U jobagent job_agent < backup.sql
```

### Check Health

```bash
# All services
docker compose ps

# Specific service health
docker exec job-agent-db pg_isready -U jobagent
```

## File Structure Check

Verify you have these key files:

```bash
ls -la                              # Should show:
# .env                             ✓
# .env.example                      ✓
# .gitignore                        ✓
# docker-compose.yml                ✓
# README.md                         ✓
# ARCHITECTURE.md                   ✓
# SETUP.md                          ✓
# database/init.sql                 ✓
# n8n/, api/, browser-worker/, dashboard/, cv-storage/  ✓
```

## Environment Variables Reference

```bash
# Database
POSTGRES_USER=jobagent              # PostgreSQL username
POSTGRES_PASSWORD=...              # CHANGE THIS!
POSTGRES_DB=job_agent              # Database name
POSTGRES_HOST=postgres              # Container hostname
POSTGRES_PORT=5432                  # Database port

# n8n
N8N_BASIC_AUTH_ACTIVE=true         # Enable basic auth
N8N_BASIC_AUTH_USER=admin          # n8n username
N8N_BASIC_AUTH_PASSWORD=...        # CHANGE THIS!
N8N_HOST=0.0.0.0                   # Listen on all interfaces
N8N_PORT=5678                       # n8n port

# API (for future phases)
API_HOST=0.0.0.0
API_PORT=8000

# Integrations
GEMINI_API_KEY=...                  # Get from https://ai.google.dev
TELEGRAM_BOT_TOKEN=...              # From @BotFather
TELEGRAM_CHAT_ID=...                # Your Telegram user ID
```

## Troubleshooting Checklist

- [ ] Docker Compose is installed: `docker compose --version`
- [ ] Docker daemon is running: `docker ps`
- [ ] Port 5432 is available: `lsof -i :5432` (should be empty)
- [ ] Port 5678 is available: `lsof -i :5678` (should be empty)
- [ ] .env file exists and has values
- [ ] PostgreSQL service healthy: `docker compose ps postgres`
- [ ] n8n service running: `docker compose logs n8n | tail -20`

## Getting Help

If something doesn't work:

1. Check Docker Compose logs: `docker compose logs`
2. Verify services are running: `docker compose ps`
3. Check if ports are in use: `netstat -an | grep 5432` (macOS/Linux)
4. Restart services: `docker compose restart`
5. Clean slate: `docker compose down -v && docker compose up -d`

## Success Indicators

✅ You're ready when:

- [ ] `docker compose ps` shows all services "healthy" or "running"
- [ ] PostgreSQL accepts connections: `psql -h localhost -U jobagent -d job_agent -c "SELECT 1"`
- [ ] Can access n8n at http://localhost:5678
- [ ] Database has ~15 tables visible in `\dt`
- [ ] No error messages in `docker compose logs`

🎉 **Congratulations! Your infrastructure is ready.**

Next: Start Phase 4 - Build the API service
