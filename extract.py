import os
import logging
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)
GITHUB_API = "https://api.github.com"


def _headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _get(url, params=None):
    response = requests.get(url, headers=_headers(), params=params, timeout=10)
    response.raise_for_status()
    return response

def fetch_issues(repo: str, max_pages: int = 5):
    page = 1
    while page <= max_pages:
        logger.info("Fetching %s issues page %d", repo, page)
        resp = _get(
            f"{GITHUB_API}/repos/{repo}/issues",
            params={"state": "all", "per_page": 100, "page": page},
        )
        batch = resp.json()
        if not batch:
            break
        for item in batch:
            yield item
            page += 1