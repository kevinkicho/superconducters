import requests
import time
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class PipelineClient:
    """Client for interacting with the FastAPI pipeline endpoints.

    Wraps /candidates, /submit, /batch_predict with authentication,
    error handling, and retry logic.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        timeout: int = 30,
    ):
        """
        Args:
            base_url: Base URL of the FastAPI server.
            api_key: API key for authentication (sent as X-API-Key header).
            max_retries: Maximum number of retry attempts for failed requests.
            backoff_factor: Multiplier for exponential backoff (seconds).
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if extra:
            headers.update(extra)
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    **kwargs,
                )
                if response.status_code in (429, 500, 502, 503, 504):
                    # Retry on rate limit or server errors
                    raise requests.exceptions.HTTPError(
                        f"HTTP {response.status_code}: {response.text}",
                        response=response,
                    )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries:
                    sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                    logger.warning(
                        f"Request failed (attempt {attempt}/{self.max_retries}): {e}. "
                        f"Retrying in {sleep_time:.1f}s..."
                    )
                    time.sleep(sleep_time)
                else:
                    logger.error(f"All retries exhausted for {method} {url}: {e}")
                    raise
        # Should not reach here
        raise RuntimeError("Unexpected retry loop exit")

    def get_candidates(self) -> List[Dict[str, Any]]:
        """Retrieve all candidates from /candidates.

        Returns:
            List of candidate dictionaries.
        """
        response = self._request("GET", "/candidates")
        return response.json()

    def submit_candidate(
        self,
        composition: str,
        pressure: Optional[float] = None,
        temperature: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit a new candidate to /submit.

        Args:
            composition: Chemical formula (e.g., "YBa2Cu3O7").
            pressure: Pressure in GPa (optional).
            temperature: Temperature in K (optional).
            notes: Additional notes (optional).

        Returns:
            Response JSON with candidate ID and status.
        """
        payload = {"composition": composition}
        if pressure is not None:
            payload["pressure"] = pressure
        if temperature is not None:
            payload["temperature"] = temperature
        if notes is not None:
            payload["notes"] = notes
        response = self._request("POST", "/submit", json=payload)
        return response.json()

    def batch_predict(
        self,
        candidates: List[Dict[str, Any]],
        format: str = "json",
    ) -> Dict[str, Any]:
        """Submit a batch of candidates for prediction via /batch_predict.

        Args:
            candidates: List of candidate dicts (each must have at least 'composition').
            format: Response format ("json" or "csv").

        Returns:
            Response JSON with predictions.
        """
        payload = {"candidates": candidates, "format": format}
        response = self._request("POST", "/batch_predict", json=payload)
        return response.json()

    def download_data(
        self,
        endpoint: str = "/candidates",
        output_path: Optional[str] = None,
    ) -> Optional[bytes]:
        """Download data from an endpoint (e.g., CSV export).

        Args:
            endpoint: API endpoint to download from.
            output_path: If provided, save content to this file.

        Returns:
            Raw bytes if output_path is None, else None.
        """
        response = self._request("GET", endpoint, stream=True)
        if output_path:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Downloaded data to {output_path}")
            return None
        return response.content


# ---------------------------------------------------------------------------
# External API fetch utilities (for materials discovery and literature)
# ---------------------------------------------------------------------------

def fetch_materials_project(api_key: str, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Fetch materials from the Materials Project API.

    Args:
        api_key: Materials Project API key.
        query: Query string (e.g., chemical formula, elements, or properties).
        max_results: Maximum number of results to return.

    Returns:
        List of material dictionaries with fields like 'material_id', 'formula',
        'band_gap', 'energy_per_atom', etc.
    """
    url = "https://api.materialsproject.org/rest/v2/materials/" + query + "/vasp"
    headers = {"X-API-KEY": api_key}
    params = {"max_results": max_results}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Fetched {len(data.get('response', []))} materials from Materials Project")
        return data.get("response", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Materials Project fetch failed: {e}")
        return []


def fetch_icsd(api_key: str, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Fetch structures from the Inorganic Crystal Structure Database (ICSD).

    Uses the ICSD REST API (requires a subscription).

    Args:
        api_key: ICSD API key.
        query: Search query (e.g., formula, elements, or collection code).
        max_results: Maximum number of results.

    Returns:
        List of structure dictionaries with fields like 'coll_code', 'formula',
        'cell_parameters', 'space_group', etc.
    """
    url = "https://icsd.ill.fr/icsd/rest/1.0/search"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    params = {"q": query, "limit": max_results}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Fetched {len(data)} structures from ICSD")
        return data if isinstance(data, list) else []
    except requests.exceptions.RequestException as e:
        logger.error(f"ICSD fetch failed: {e}")
        return []


def fetch_arxiv(query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Fetch papers from the arXiv API.

    Args:
        query: arXiv search query (e.g., "superconductivity room temperature").
        max_results: Maximum number of results.

    Returns:
        List of paper dictionaries with keys 'id', 'title', 'summary', 'authors',
        'published', 'link', etc.
    """
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        # arXiv returns Atom XML; parse with feedparser-like approach or just return raw text
        # For simplicity, we parse using xml.etree.ElementTree
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom",
              "arxiv": "http://arxiv.org/schemas/atom"}
        papers = []
        for entry in root.findall("atom:entry", ns):
            paper = {
                "id": entry.find("atom:id", ns).text if entry.find("atom:id", ns) is not None else "",
                "title": entry.find("atom:title", ns).text if entry.find("atom:title", ns) is not None else "",
                "summary": entry.find("atom:summary", ns).text if entry.find("atom:summary", ns) is not None else "",
                "published": entry.find("atom:published", ns).text if entry.find("atom:published", ns) is not None else "",
                "link": entry.find("atom:link", ns).attrib.get("href", "") if entry.find("atom:link", ns) is not None else "",
                "authors": [
                    author.find("atom:name", ns).text
                    for author in entry.findall("atom:author", ns)
                    if author.find("atom:name", ns) is not None
                ],
            }
            papers.append(paper)
        logger.info(f"Fetched {len(papers)} papers from arXiv")
        return papers
    except requests.exceptions.RequestException as e:
        logger.error(f"arXiv fetch failed: {e}")
        return []
