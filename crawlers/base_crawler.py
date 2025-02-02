import httpx
import json
import asyncio
import re

from httpx import Response

from crawlers.utils.logger import logger
from crawlers.utils.api_exceptions import (
    APIError,
    APIConnectionError,
    APIResponseError,
    APITimeoutError,
    APIUnavailableError,
    APIUnauthorizedError,
    APINotFoundError,
    APIRateLimitError,
    APIRetryExhaustedError,
)

class BaseCrawler:
    def __init__(
            self,
            proxies: dict = None,
            max_retries: int = 3,
            max_connections: int = 50,
            timeout: int = 10,
            max_tasks: int = 50,
            crawler_headers: dict = {},
    ):
        if isinstance(proxies, dict):
            self.proxies = proxies
            # [f"{k}://{v}" for k, v in proxies.items()]
        else:
            self.proxies = None

        # Crawler request header
        self.crawler_headers = crawler_headers or {}

        # Number of asynchronous tasks
        self._max_tasks = max_tasks
        self.semaphore = asyncio.Semaphore(max_tasks)

        # Limit the maximum number of connections
        self._max_connections = max_connections
        self.limits = httpx.Limits(max_connections=max_connections)

        # Business logic retry count
        self._max_retries = max_retries
        # Underlying connection retry count
        self.atransport = httpx.AsyncHTTPTransport(retries=max_retries)

        # Timeout waiting time
        self._timeout = timeout
        self.timeout = httpx.Timeout(timeout)
        # Asynchronous client
        self.aclient = httpx.AsyncClient(
            headers=self.crawler_headers,
            proxies=self.proxies,
            timeout=self.timeout,
            limits=self.limits,
            transport=self.atransport,
        )

    async def fetch_response(self, endpoint: str) -> Response:
        return await self.get_fetch_data(endpoint)

    async def fetch_get_json(self, endpoint: str) -> dict:
        response = await self.get_fetch_data(endpoint)
        return self.parse_json(response)

    def parse_json(self, response: Response) -> dict:
        if (
                response is not None
                and isinstance(response, Response)
                and response.status_code == 200
        ):
            try:
                return response.json()
            except json.JSONDecodeError as e:
                match = re.search(r"\{.*\}", response.text)
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError as e:
                    logger.error("Failed to parse {0} interface JSON: {1}".format(response.url, e))
                    raise APIResponseError("Failed to parse JSON data")

        else:
            if isinstance(response, Response):
                logger.error(
                    "Failed to obtain data. Status code: {0}".format(response.status_code)
                )
            else:
                logger.error("Invalid response type. Response Type: {0}".format(type(response)))

            raise APIResponseError("Failed to obtain data")

    async def get_fetch_data(self, url: str):
        for attempt in range(self._max_retries):
            try:
                response = await self.aclient.get(url, follow_redirects=True)
                if not response.text.strip() or not response.content:
                    error_message = "The {0}th response content is empty, status code: {1}, URL: {2}".format(attempt + 1, response.status_code, response.url)

                    logger.warning(error_message)

                    if attempt == self._max_retries - 1:
                        raise APIRetryExhaustedError("Failed to obtain endpoint data. The number of attempts reached the upper limit.")

                    await asyncio.sleep(self._timeout)
                    continue

                response.raise_for_status()
                return response

            except httpx.RequestError:
                raise APIConnectionError("Failed to connect to endpoint, check network environment or proxy: {0} Proxy: {1} Class name: {2}".format(url, self.proxies, self.__class__.__name__))

            except httpx.HTTPStatusError as http_error:
                self.handle_http_status_error(http_error, url, attempt + 1)

            except APIError as e:
                e.display_error()
                
    def handle_http_status_error(self, http_error, url: str, attempt):
        response = getattr(http_error, "response", None)
        status_code = getattr(response, "status_code", None)

        if response is None or status_code is None:
            logger.error("HTTP status error: {0}, URL: {1}, number of attempts: {2}".format(http_error, url, attempt))
            raise APIResponseError(f"An unexpected condition was encountered while handling an HTTP error: {http_error}")

        if status_code == 302:
            pass
        elif status_code == 404:
            raise APINotFoundError(f"HTTP Status Code {status_code}")
        elif status_code == 503:
            raise APIUnavailableError(f"HTTP Status Code {status_code}")
        elif status_code == 408:
            raise APITimeoutError(f"HTTP Status Code {status_code}")
        elif status_code == 401:
            raise APIUnauthorizedError(f"HTTP Status Code {status_code}")
        elif status_code == 429:
            raise APIRateLimitError(f"HTTP Status Code {status_code}")
        else:
            logger.error("HTTP status error: {0}, URL: {1}, number of attempts: {2}".format(status_code, url, attempt))
            raise APIResponseError(f"HTTP Status Error: {status_code}")

    async def close(self):
        await self.aclient.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclient.aclose()
