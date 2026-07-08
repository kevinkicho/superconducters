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
