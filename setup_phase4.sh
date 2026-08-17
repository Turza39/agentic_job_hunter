#!/bin/bash
# Phase 4 Setup and Validation Script

set -e

echo "========================================"
echo "Agentic Job Hunter - Phase 4 Setup"
echo "========================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker and docker-compose are installed
echo -e "\n${YELLOW}Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose installed${NC}"

# Check if .env file exists
echo -e "\n${YELLOW}Checking environment configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create a .env file in the project root with the following content:"
    echo ""
    cat << 'EOF'
POSTGRES_USER=jobagent
POSTGRES_PASSWORD=turza039
POSTGRES_DB=job_agent
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

N8N_HOST=localhost
N8N_PORT=5678
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin
N8N_PROTOCOL=http
N8N_SECURE_COOKIE=false

API_HOST=0.0.0.0
API_PORT=8000

DEBUG=false

CV_UPLOAD_DIR=cv-storage/uploads
MAX_CV_SIZE_MB=10

GEMINI_API_KEY=your_api_key_here
TELEGRAM_API_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EOF
    exit 1
fi

echo -e "${GREEN}✓ .env file found${NC}"

# Create required directories
echo -e "\n${YELLOW}Creating required directories...${NC}"
mkdir -p cv-storage/uploads
mkdir -p database
mkdir -p n8n/workflows
mkdir -p browser-worker
mkdir -p dashboard
echo -e "${GREEN}✓ Directories created${NC}"

# Build and start containers
echo -e "\n${YELLOW}Building Docker images...${NC}"
docker-compose build

echo -e "\n${YELLOW}Starting PostgreSQL...${NC}"
docker-compose up -d postgres

# Wait for PostgreSQL to be healthy
echo -e "\n${YELLOW}Waiting for PostgreSQL to be healthy...${NC}"
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T postgres pg_isready -U jobagent -d job_agent > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is healthy${NC}"
        break
    fi
    sleep 1
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}Error: PostgreSQL failed to start${NC}"
    exit 1
fi

# Start n8n
echo -e "\n${YELLOW}Starting n8n...${NC}"
docker-compose up -d n8n

# Start API
echo -e "\n${YELLOW}Starting API service...${NC}"
docker-compose up -d api

# Wait for API to be healthy
echo -e "\n${YELLOW}Waiting for API to be healthy...${NC}"
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T api curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is healthy${NC}"
        break
    fi
    sleep 1
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${YELLOW}Warning: API startup is taking longer than expected${NC}"
fi

# Display service status
echo -e "\n${YELLOW}Service Status:${NC}"
docker-compose ps

# Display endpoints
echo -e "\n${GREEN}========================================"
echo "Phase 4 Setup Complete!"
echo "========================================${NC}"
echo ""
echo "Services are now running:"
echo ""
echo -e "  ${YELLOW}PostgreSQL:${NC}"
echo "    Host: localhost"
echo "    Port: 5433"
echo "    Database: job_agent"
echo "    Username: jobagent"
echo "    Password: turza039"
echo ""
echo -e "  ${YELLOW}n8n Orchestration:${NC}"
echo "    URL: http://localhost:5678"
echo ""
echo -e "  ${YELLOW}API Service:${NC}"
echo "    URL: http://localhost:8000"
echo "    Docs: http://localhost:8000/docs"
echo "    Health: http://localhost:8000/health"
echo ""
echo "Next steps:"
echo "  1. Test the API: python api/test_api.py"
echo "  2. Create your first profile via the interactive docs"
echo "  3. Proceed to Phase 5 (Job Source System)"
echo ""
echo -e "${YELLOW}To stop all services:${NC}"
echo "  docker-compose down"
echo ""
echo -e "${YELLOW}To view logs:${NC}"
echo "  docker-compose logs -f api"
echo "  docker-compose logs -f postgres"
echo "  docker-compose logs -f n8n"
