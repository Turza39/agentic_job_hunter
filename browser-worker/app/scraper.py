from typing import Any
from urllib.parse import urlparse

from playwright.async_api import Browser, Page


JOB_PATH_PATTERNS = [
    "/job/",
    "/jobs/",
    "/career/",
    "/careers/",
    "/position/",
    "/positions/",
    "/vacancy/",
    "/vacancies/",
    "/requisition/",
    "/requisitions/",
]


def looks_like_job_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()

        return any(pattern in path for pattern in JOB_PATH_PATTERNS)

    except Exception:
        return False


def clean_title(text: str) -> str:
    if not text:
        return ""

    return " ".join(text.split()).strip()


async def extract_links_from_page(page: Page) -> list[dict[str, str]]:
    links = await page.locator("a").evaluate_all(
        """
        anchors => anchors.map(a => ({
            text: (a.innerText || a.textContent || '').trim(),
            href: a.href || ''
        }))
        """
    )

    results = []

    for link in links:
        href = link.get("href", "")
        text = clean_title(link.get("text", ""))

        if not href:
            continue

        if not looks_like_job_url(href):
            continue

        if not text:
            continue

        if len(text) < 2 or len(text) > 300:
            continue

        results.append(
            {
                "title": text,
                "job_url": href,
            }
        )

    return results


async def create_context(browser: Browser):
    return await browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        viewport={
            "width": 1440,
            "height": 900,
        },
    )


async def prepare_page(page: Page):
    """
    Wait for client-side rendering and lazy-loaded content.
    """

    await page.wait_for_timeout(5000)

    # Scroll progressively to trigger lazy loading.
    for _ in range(5):
        await page.evaluate(
            """
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'instant'
            });
            """
        )

        await page.wait_for_timeout(1000)

    await page.evaluate(
        """
        window.scrollTo({
            top: 0,
            behavior: 'instant'
        });
        """
    )

    await page.wait_for_timeout(500)


async def discover_jobs(
    browser: Browser,
    source_url: str,
) -> dict[str, Any]:

    context = await create_context(browser)
    page = await context.new_page()

    network_requests: list[str] = []

    def capture_request(request):
        url = request.url

        if any(
            keyword in url.lower()
            for keyword in [
                "job",
                "career",
                "search",
                "api",
                "requisition",
            ]
        ):
            network_requests.append(url)

    page.on("request", capture_request)

    try:
        print(f"[Playwright] Discovering jobs from: {source_url}")

        response = await page.goto(
            source_url,
            wait_until="domcontentloaded",
            timeout=30_000,
        )

        status_code = response.status if response else None

        await prepare_page(page)

        page_title = await page.title()

        body_text = await page.locator("body").inner_text()

        jobs = await extract_links_from_page(page)

        # Deduplicate by URL.
        unique_jobs = {}

        for job in jobs:
            unique_jobs[job["job_url"]] = job

        jobs = list(unique_jobs.values())

        print(
            f"[Playwright] Discovery finished: "
            f"status={status_code}, "
            f"jobs={len(jobs)}, "
            f"body_length={len(body_text)}"
        )

        return {
            "success": True,
            "source_url": source_url,
            "page_title": page_title,
            "status_code": status_code,
            "body_text_length": len(body_text),
            "jobs": jobs,
            "job_count": len(jobs),
            "network_requests": network_requests[:100],
        }

    except Exception as exc:

        print(f"[Playwright] Discovery error: {exc}")

        return {
            "success": False,
            "source_url": source_url,
            "error": str(exc),
            "jobs": [],
            "job_count": 0,
            "network_requests": network_requests[:100],
        }

    finally:
        await context.close()


async def fetch_job(
    browser: Browser,
    job_url: str,
) -> dict[str, Any]:

    context = await create_context(browser)
    page = await context.new_page()

    network_requests: list[str] = []

    def capture_request(request):
        url = request.url

        if any(
            keyword in url.lower()
            for keyword in [
                "job",
                "career",
                "api",
                "application",
                "requisition",
            ]
        ):
            network_requests.append(url)

    page.on("request", capture_request)

    try:
        print(f"[Playwright] Fetching job: {job_url}")

        response = await page.goto(
            job_url,
            wait_until="domcontentloaded",
            timeout=30_000,
        )

        status_code = response.status if response else None

        await prepare_page(page)

        page_title = await page.title()

        body_text = await page.locator("body").inner_text()

        # This is the important part:
        # page.content() gives us the CURRENT rendered DOM,
        # after JavaScript has executed.
        html = await page.content()

        print(
            f"[Playwright] Job fetch finished: "
            f"status={status_code}, "
            f"html_length={len(html)}, "
            f"text_length={len(body_text)}"
        )

        if not html or len(html) < 100:
            return {
                "success": False,
                "is_valid": False,
                "job_url": job_url,
                "status": "empty_job_page",
                "error": "Rendered page returned empty HTML",
            }

        return {
            "success": True,
            "is_valid": True,
            "status": "job_detail_fetched",
            "job_url": job_url,
            "status_code": status_code,
            "page_title": page_title,
            "html": html,
            "body_text": body_text,
            "html_length": len(html),
            "body_text_length": len(body_text),
            "network_requests": network_requests[:100],
        }

    except Exception as exc:

        print(f"[Playwright] Job fetch error: {exc}")

        return {
            "success": False,
            "is_valid": False,
            "job_url": job_url,
            "status": "job_detail_fetch_failed",
            "error": str(exc),
            "network_requests": network_requests[:100],
        }

    finally:
        await context.close()