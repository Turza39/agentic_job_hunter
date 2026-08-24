from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from playwright.async_api import async_playwright, Browser

from .scraper import discover_jobs, fetch_job


class DiscoverRequest(BaseModel):
    company_id: str | None = None
    source_url: HttpUrl


class FetchJobRequest(BaseModel):
    company_id: str | None = None
    source_url: HttpUrl | None = None
    job_url: HttpUrl
    title: str | None = None


browser: Browser | None = None
playwright_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    global browser
    global playwright_instance

    print("[Browser Worker] Starting Playwright...")

    playwright_instance = await async_playwright().start()

    browser = await playwright_instance.chromium.launch(
        headless=True
    )

    print("[Browser Worker] Chromium started.")

    yield

    print("[Browser Worker] Shutting down Chromium...")

    if browser:
        await browser.close()

    if playwright_instance:
        await playwright_instance.stop()


app = FastAPI(
    title="Agentic Job Hunter Browser Worker",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "browser_started": browser is not None,
    }


@app.post("/discover")
async def discover(request: DiscoverRequest):

    if browser is None:
        raise HTTPException(
            status_code=503,
            detail="Browser is not ready",
        )

    result = await discover_jobs(
        browser=browser,
        source_url=str(request.source_url),
    )

    return {
        "company_id": request.company_id,
        **result,
    }


@app.post("/fetch-job")
async def fetch_job_endpoint(request: FetchJobRequest):

    if browser is None:
        raise HTTPException(
            status_code=503,
            detail="Browser is not ready",
        )

    result = await fetch_job(
        browser=browser,
        job_url=str(request.job_url),
    )

    return {
        "company_id": request.company_id,
        "source_url": str(request.source_url) if request.source_url else None,
        "title": request.title,
        **result,
    }