import requests
from typing import Dict, Any

class Group1ApiClientError(Exception):
    """Base exception for Group 1 API Client errors."""
    pass

class ObservationNotFoundError(Group1ApiClientError):
    """Raised when the requested observation_id is not found."""
    pass

class MalformedResponseError(Group1ApiClientError):
    """Raised when the response is not valid JSON or lacks expected structure."""
    pass

class Group1ApiClient:
    """
    Deterministic client for interacting with the VANA MasterDB Observation API (Group 1).
    """
    def __init__(self, base_url: str = "http://163.128.209.18:8013", timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_health(self) -> Dict[str, Any]:
        """
        Check health status of the Group 1 API.
        """
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Group1ApiClientError(f"Health check failed: {e}")
        except ValueError as e:
            raise MalformedResponseError(f"Health check response malformed: {e}")

    def get_observation(self, observation_id: str) -> Dict[str, Any]:
        """
        Fetch the raw canonical observation JSON from the Group 1 API.
        """
        if not observation_id:
            raise Group1ApiClientError("observation_id must be provided")

        url = f"{self.base_url}/observations/{observation_id}"
        try:
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 404:
                raise ObservationNotFoundError(f"Observation '{observation_id}' not found on Group 1 API.")
            
            response.raise_for_status()
            payload = response.json()
            
            # Basic structural validation on raw response
            if not isinstance(payload, dict):
                raise MalformedResponseError("API response is not a JSON object")
            if "observation" not in payload:
                raise MalformedResponseError("API response is missing required 'observation' object")
                
            return payload

        except requests.exceptions.Timeout as e:
            raise Group1ApiClientError(f"Timeout connecting to Group 1 API: {e}")
        except requests.exceptions.ConnectionError as e:
            raise Group1ApiClientError(f"Connection failure to Group 1 API: {e}")
        except requests.exceptions.HTTPError as e:
            raise Group1ApiClientError(f"HTTP error response from Group 1 API: {e}")
        except ValueError as e:
            raise MalformedResponseError(f"Failed to parse JSON response from Group 1 API: {e}")
