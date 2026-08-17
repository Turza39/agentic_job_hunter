# Phase 4 Setup and Validation Script (Windows PowerShell)

Write-Host "========================================"
Write-Host "Agentic Job Hunter - Phase 4 Setup"
Write-Host "========================================"

# Check if docker and docker-compose are installed
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow
$dockerCheck = docker --version 2>$null
if (!$dockerCheck) {
    Write-Host "Error: Docker is not installed" -ForegroundColor Red
    exit 1
}

$composeCheck = docker-compose --version 2>$null
if (!$composeCheck) {
    Write-Host "Error: Docker Compose is not installed" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker and Docker Compose installed" -ForegroundColor Green

# Check if .env file exists
Write-Host "`nChecking environment configuration..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Write-Host "Error: .env file not found" -ForegroundColor Red
    Write-Host "Please create a .env file in the project root"
    exit 1
}

Write-Host "✓ .env file found" -ForegroundColor Green

# Create required directories
Write-Host "`nCreating required directories..." -ForegroundColor Yellow
$directories = @(
    "cv-storage/uploads",
    "database",
    "n8n/workflows",
    "browser-worker",
    "dashboard"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}

Write-Host "✓ Directories created" -ForegroundColor Green

# Build and start containers
Write-Host "`nBuilding Docker images..." -ForegroundColor Yellow
docker-compose build

Write-Host "`nStarting PostgreSQL..." -ForegroundColor Yellow
docker-compose up -d postgres

# Wait for PostgreSQL to be healthy
Write-Host "`nWaiting for PostgreSQL to be healthy..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        docker-compose exec -T postgres pg_isready -U jobagent -d job_agent 2>$null | Out-Null
        Write-Host "✓ PostgreSQL is healthy" -ForegroundColor Green
        break
    }
    catch {
        $attempt++
        Start-Sleep -Seconds 1
    }
}

if ($attempt -eq $maxAttempts) {
    Write-Host "Error: PostgreSQL failed to start" -ForegroundColor Red
    exit 1
}

# Start n8n
Write-Host "`nStarting n8n..." -ForegroundColor Yellow
docker-compose up -d n8n

# Start API
Write-Host "`nStarting API service..." -ForegroundColor Yellow
docker-compose up -d api

# Wait for API to be healthy
Write-Host "`nWaiting for API to be healthy..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ API is healthy" -ForegroundColor Green
            break
        }
    }
    catch {
        $attempt++
        Start-Sleep -Seconds 1
    }
}

if ($attempt -eq $maxAttempts) {
    Write-Host "Warning: API startup is taking longer than expected" -ForegroundColor Yellow
}

# Display service status
Write-Host "`nService Status:" -ForegroundColor Yellow
docker-compose ps

# Display endpoints
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Phase 4 Setup Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Services are now running:`n" -ForegroundColor White

Write-Host "  PostgreSQL:" -ForegroundColor Yellow
Write-Host "    Host: localhost"
Write-Host "    Port: 5433"
Write-Host "    Database: job_agent"
Write-Host "    Username: jobagent"
Write-Host "    Password: turza039`n"

Write-Host "  n8n Orchestration:" -ForegroundColor Yellow
Write-Host "    URL: http://localhost:5678`n"

Write-Host "  API Service:" -ForegroundColor Yellow
Write-Host "    URL: http://localhost:8000"
Write-Host "    Docs: http://localhost:8000/docs"
Write-Host "    Health: http://localhost:8000/health`n"

Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Test the API: python api/test_api.py"
Write-Host "  2. Create your first profile via the interactive docs"
Write-Host "  3. Proceed to Phase 5 (Job Source System)`n"

Write-Host "To stop all services:" -ForegroundColor Yellow
Write-Host "  docker-compose down`n"

Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f api"
Write-Host "  docker-compose logs -f postgres"
Write-Host "  docker-compose logs -f n8n`n"
