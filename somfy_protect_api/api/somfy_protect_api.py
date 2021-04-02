"""Somfy Protect Api"""
import base64
from json import JSONDecodeError
from typing import Any, Callable, Dict, List, Optional, Union

from oauthlib.oauth2 import LegacyApplicationClient, TokenExpiredError
from requests import Response
from requests_oauthlib import OAuth2Session

from somfy_protect_api.api.devices.category import Category
from somfy_protect_api.api.model import (
    AvailableStatus,
    Device,
    Site,
)

BASE_URL = "https://api.myfox.io/v3"

SOMFY_PROTECT_TOKEN = "https://sso.myfox.io/oauth/oauth/v2/token"


class SomfyProtectApi:
    """Somfy Protect Api Class
    """

    def __init__(
        self,
        username: str,
        password: str,
        token: Optional[Dict[str, str]] = None,
        token_updater: Optional[Callable[[str], None]] = None,
        user_agent: Optional[str] = "Somfy Protect",
    ):

        self.username = username
        self.password = password
        self.client_id = base64.b64decode(
            "ODRlZGRmNDgtMmI4ZS0xMWU1LWIyYTUtMTI0Y2ZhYjI1NTk1XzQ3NWJ1cXJmOHY4a2d3b280Z293MDhna2tjMGNrODA0ODh3bzQ0czhvNDhzZzg0azQw"
        ).decode("utf-8")
        self.client_secret = base64.b64decode(
            "NGRzcWZudGlldTB3Y2t3d280MGt3ODQ4Z3c0bzBjOGs0b3djODBrNGdvMGNzMGs4NDQ="
        ).decode("utf-8")
        self.token_updater = token_updater

        extra = {"client_id": self.client_id, "client_secret": self.client_secret}

        self._oauth = OAuth2Session(
            client=LegacyApplicationClient(client_id=self.client_id),
            token=token,
            auto_refresh_kwargs=extra,
            token_updater=token_updater,
        )
        self._oauth.headers["User-Agent"] = user_agent

    def get_sites(self) -> List[Site]:
        """Get All Sites

        Returns:
            List[Site]: List of Site object
        """
        response = self.get("/site")
        response.raise_for_status()
        return [Site(**s) for s in response.json().get("items")]

    def get_site(self, site_id: str) -> Site:
        """Get Site

        Args:
            site_id (str): Site ID


        Returns:
            Site: Site object
        """
        response = self.get(f"/site/{site_id}")
        response.raise_for_status()
        return Site(**response.json())

    def update_site(self, site_id: str, security_level: AvailableStatus) -> Dict:
        """Set Alarm Security Level

        Args:
            site_id (str): Site ID
            security_level (AvailableStatus): Security Level
        Returns:
            Dict: requests Response object
        """
        security_level = {"status": security_level.lower()}
        response = self.put(f"/site/{site_id}/security", json=security_level)
        response.raise_for_status()
        return response.json()

    def update_device(self, site_id: str, device_id: str, device_label: str, settings: Dict,) -> Dict:
        """Update Device Settings

        Args:
            site_id (str): Site ID
            device_id (str): Device ID
            device_label (str): Device Label
            settings (Dict): Settings (as return by get_device)

        Returns:
            str: Task ID
        """
        if settings is None or device_label is None:
            raise ValueError(f"Missing settings and/or device_label")

        # Clean Settings Dict
        settings.pop("object")
        # settings.pop('disarmed')
        # settings.pop('partial')
        # settings.pop('armed')

        payload = {"settings": settings, "label": device_label}
        response = self.put(f"/site/{site_id}/device/{device_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def get_devices(self, site_id: str, category: Optional[Category] = None) -> List[Device]:
        """List Devices from a Site ID

        Args:
            site_id (Optional[str], optional): Site ID. Defaults to None.
            category (Optional[Category], optional): [description]. Defaults to None.

        Returns:
            List[Device]: List of Device object
        """
        devices = []  # type: List[Device]
        response = self.get(f"/site/{site_id}/device")
        try:
            content = response.json()
        except JSONDecodeError:
            response.raise_for_status()

        devices += [
            Device(**d)
            for d in content.get("items")
            if category is None or category.value in Device(**d).device_definition.get("label")
        ]

        return devices

    def get_device(self, site_id: str, device_id: str) -> Device:
        """Get Device details

        Args:
            site_id (str): Site ID
            device_id (str): Site ID

        Returns:
            Device: Device object
        """
        response = self.get(f"/site/{site_id}/device/{device_id}")
        response.raise_for_status()
        return Device(**response.json())

    def get(self, path: str) -> Response:
        """Fetch an URL from the Somfy Protect API.

        Args:
            path (str): Path to request

        Returns:
            Response: requests Response object
        """
        return self._request("get", path)

    def post(self, path: str, *, json: Dict[str, Any]) -> Response:
        """Post data to the Somfy Protect API.

        Args:
            path (str): Path to request
            json (Dict[str, Any]): Data in json format

        Returns:
            Response: requests Response object
        """
        return self._request("post", path, json=json)

    def put(self, path: str, *, json: Dict[str, Any]) -> Response:
        """Put data to the Somfy Protect API.

        Args:
            path (str): Path to request
            json (Dict[str, Any]): Data in json format

        Returns:
            Response: requests Response object
        """
        print(json)
        return self._request("put", path, json=json)

    def request_token(self,) -> Dict[str, str]:
        """Generic method for fetching a Somfy Protect access token.

        Returns:
            Dict[str, str]: Token
        """

        return self._oauth.fetch_token(
            SOMFY_PROTECT_TOKEN,
            username=self.username,
            password=self.password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

    def refresh_tokens(self) -> Dict[str, Union[str, int]]:
        """Refresh and return new Somfy tokens.

        Returns:
            Dict[str, Union[str, int]]: Token
        """
        token = self._oauth.refresh_token(SOMFY_PROTECT_TOKEN)

        if self.token_updater is not None:
            self.token_updater(token)

        return token

    def _request(self, method: str, path: str, **kwargs: Any) -> Response:
        """Make a request.

        We don't use the built-in token refresh mechanism of OAuth2 session because
        we want to allow overriding the token refresh logic.

        Args:
            method (str): HTTP Methid
            path (str): Path to request

        Returns:
            Response: requests Response object
        """

        url = f"{BASE_URL}{path}"
        try:
            return getattr(self._oauth, method)(url, **kwargs)
        except TokenExpiredError:
            self._oauth.token = self.refresh_tokens()

            return getattr(self._oauth, method)(url, **kwargs)
