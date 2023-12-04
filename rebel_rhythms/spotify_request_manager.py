import requests
from requests import Response
from requests.exceptions import Timeout
from typing import Union, Dict, Any, Callable

from rebel_rhythms.custom_exceptions import (
    ForbiddenException,
    RateLimitException,
    SpotifyClientException,
    ResourceNotFoundException,
    UnauthorizedException,
    BadRequestException,
)


class SpotifyRequestManager:
    def __init__(self, spotify_auth, market):
        self.base_url = "https://api.spotify.com"
        self.spotify_auth = spotify_auth
        self.market = market
        self._load_and_refresh_tokens()

    def _handle_params(self, params: Dict, include_market: bool) -> Dict:
        params = params or {}
        if include_market:
            params.setdefault("market", self.market)
        return params

    def _handle_response(self, response: Response) -> Union[Dict, bool]:
        if (
            response.status_code == 200
            or response.status_code == 201
            or response.status_code == 202
        ):
            if not response.content:
                return None
            try:
                return response.json()
            except ValueError as e:
                raise SpotifyClientException(f"Invalid JSON received: {str(e)}")

        elif response.status_code == 204:
            return True

        elif response.status_code == 401:
            raise UnauthorizedException(
                "Bad or expired token. Re-authenticate the user."
            )

        elif response.status_code == 403:
            raise ForbiddenException(
                "Bad OAuth request (wrong consumer key, bad nonce, expired timestamp, etc.)"
            )

        elif response.status_code == 429:
            raise RateLimitException("The app has exceeded its rate limits.")

        elif response.status_code == 404:
            raise ResourceNotFoundException("Resource not found.")

        elif response.status_code == 400:
            raise BadRequestException(response.json())

        else:
            raise SpotifyClientException(
                f"Request failed with status code {response.status_code}"
            )

    def _request(
        self, method: str, endpoint: str, include_market: bool = True, **kwargs
    ) -> Any:
        url = f"{self.base_url}{endpoint}"
        kwargs["params"] = self._handle_params(kwargs.get("params"), include_market)
        try:
            response = getattr(requests, method)(
                url, timeout=30, **kwargs
            )  # 30-second timeout
        except Timeout:
            raise SpotifyClientException("The request timed out after 30 seconds.")

        if response.status_code == 401 and self._refresh_token_if_required(response):
            try:
                response = getattr(requests, method)(
                    url, timeout=30, **kwargs
                )  # 30-second timeout
            except Timeout:
                raise SpotifyClientException("The request timed out after 30 seconds.")

        return self._handle_response(response)

    def _api_call(self, method: str, endpoint: str, **kwargs) -> Any:
        kwargs["headers"] = kwargs.get("headers") or self.headers
        return self._request(method, endpoint, **kwargs)

    def get(self, endpoint, **kwargs):
        return self._api_call("get", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self._api_call("post", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self._api_call("put", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._api_call("delete", endpoint, **kwargs)

    def _load_and_refresh_tokens(self):
        self.tokens = self.spotify_auth.load_tokens() or self._initiate_authorization()
        if not self.tokens:
            raise ValueError("Failed to obtain Spotify tokens.")
        self._refresh_tokens_if_needed()
        self.headers = {"Authorization": f'Bearer {self.tokens["access_token"]}'}

    def _initiate_authorization(self):
        self.spotify_auth.initiate_authorization()
        return self.spotify_auth.load_tokens()

    def _refresh_tokens_if_needed(self):
        refresh_token = self.tokens.get("refresh_token")
        if not refresh_token:
            raise ValueError("Refresh token not found.")
        new_tokens = self.spotify_auth.refresh_tokens()
        self.tokens.update(new_tokens)
        self.spotify_auth.store_tokens(self.tokens)

    def _refresh_token_if_required(self, response):
        if response.status_code == 401:
            new_tokens = self.spotify_auth.refresh_tokens()
            if "access_token" in new_tokens:
                self.tokens.update(new_tokens)
                self.spotify_auth.store_tokens(self.tokens)
                self.headers = {
                    "Authorization": f'Bearer {self.tokens["access_token"]}'
                }
                return True
            else:
                raise ValueError("Failed to refresh the token.")
        return False

    def _navigate_to_item_path(self, response, path: str):
        items = response
        for attr in path.split("."):
            items = items.get(attr, {})
        return items

    def _fetch_from_api(
        self,
        endpoint: str,
        params: dict,
        convert_func: Callable,
        item_path: str = "items",
        next_path: str = "next",
        include_market: bool = True,
    ):
        limit = params.get("limit", 50)
        offset = params.get("offset", 0)
        while True:
            params.update({"limit": limit, "offset": offset})
            response = self.get(endpoint, params=params, include_market=include_market)
            import pdb

            items = self._navigate_to_item_path(response, item_path)

            for item in items:
                yield convert_func(item)

            next_value = self._navigate_to_item_path(response, next_path)

            if next_value is None:
                break
            offset += limit

    def _fetch_limited_from_api(
        self,
        endpoint: str,
        params: dict,
        convert_func: Callable,
        max_items: int,
        item_path: str = "items",
        next_path: str = "next",
        include_market: bool = True,
    ):
        limit = params.get("limit", 50)
        offset = params.get("offset", 0)
        items_returned = 0

        while True:
            params.update({"limit": limit, "offset": offset})
            response = self.get(endpoint, params=params, include_market=include_market)
            items = self._navigate_to_item_path(response, item_path)

            for item in items:
                if items_returned >= max_items:
                    return
                yield convert_func(item)
                items_returned += 1

            next_value = self._navigate_to_item_path(response, next_path)

            if next_value is None:
                break
            offset += limit
