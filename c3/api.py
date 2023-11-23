from typing import Any

import requests
from requests.exceptions import HTTPError

from c3.utils.constants import MainnetConstants


class ApiClient:
    def __init__(
        self,
        base_url=MainnetConstants.API_URL,
    ) -> None:
        self.base_url = base_url

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
            }
        )

    def get(self, url_path: str, params: Any = None) -> Any:
        url = self.base_url + url_path

        try:
            response = self.session.get(
                url,
                params=params,
            )
            response.raise_for_status()

            try:
                return response.json()
            except ValueError:
                return {"error": f"Could not parse JSON: {response.text}"}
        except HTTPError as http_err:
            # Raise a new exception that includes the response text
            raise Exception(
                f"HTTP Error: {http_err} - Response Text: {response.text}"
            ) from http_err
        except requests.RequestException as req_err:
            # Handle any other requests-related exceptions
            print(f"A requests error occurred: {req_err}")
            raise
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
        raise

    def post(self, url_path: str, payload: Any = {}) -> Any:
        url = self.base_url + url_path

        try:
            response = self.session.post(url, json=payload)
            # This will raise an HTTPError if the response was unsuccessful
            response.raise_for_status()

            try:
                return response.json()
            except ValueError:
                return {"error": f"Could not parse JSON: {response.text}"}
        except HTTPError as http_err:
            # Raise a new exception that includes the response text
            raise Exception(
                f"HTTP Error: {http_err} - Response Text: {response.text}"
            ) from http_err
        except requests.RequestException as req_err:
            # Handle any other requests-related exceptions
            print(f"A requests error occurred: {req_err}")
            raise
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
        raise
