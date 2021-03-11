"""Somfy Protect Api"""

import asyncio
import base64
import json
import logging
import os
import sys
import time
from enum import Enum
from typing import Dict

import requests
from requests.exceptions import HTTPError

from somfy_protect_api.log import setup_logger


BASE_URL = "https://api.myfox.io/v3"
SOMFY_PROTECT_OAUTH_TOKEN = "https://sso.myfox.io/oauth/oauth/v2/token"

LOGGER = logging.getLogger(__name__)


class Status(Enum):
    """List of Allowed Security Level

    Args:
        Enum (str): Security Level
    """

    DISARMED = 1
    ARMED = 2
    PARTIAL = 3


class SomfyProtectApi:
    """Somfy Protect Api
    """

    def __init__(
        self, username: str, password: str,
    ):
        setup_logger(debug=True)
        self.client_id = base64.b64decode('ODRlZGRmNDgtMmI4ZS0xMWU1LWIyYTUtMTI0Y2ZhYjI1NTk1XzQ3NWJ1cXJmOHY4a2d3b280Z293MDhna2tjMGNrODA0ODh3bzQ0czhvNDhzZzg0azQw').decode('utf-8')
        self.client_secret = base64.b64decode('NGRzcWZudGlldTB3Y2t3d280MGt3ODQ4Z3c0bzBjOGs0b3djODBrNGdvMGNzMGs4NDQ=').decode('utf-8')
        self.username = username
        self.password = password
        self.token = None

        headers = {"Content-type": "application/json"}
        self.headers = headers

    def get_new_token(self) -> Dict:
        """Generate New Token

        Returns:
            Dict: Token
        """
        LOGGER.info("Create new Token")
        data = {
            "username": self.username,
            "password": self.password,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "password",
        }
        try:
            response = requests.post(
                data=json.dumps(data),
                headers=self.headers,
                url=SOMFY_PROTECT_OAUTH_TOKEN,
            )
            self.token = response.json()
            self.token["expiration_date"] = int(time.time()) + self.token.get(
                "expires_in"
            )
            return self.token
        except Exception as exp:
            LOGGER.warning(f"Unable to get new token: {exp}")

    def refresh_token(self, refresh_token: str) -> Dict:
        """Refresh an existing Token

        Args:
            refresh_token (str): Token to refresh

        Returns:
            Dict: Token
        """
        LOGGER.info("Refresh current Token")
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        try:
            response = requests.post(
                data=json.dumps(data),
                headers=self.headers,
                url=SOMFY_PROTECT_OAUTH_TOKEN,
            )
            self.token = response.json()
            self.token["expiration_date"] = time.time() - self.token.get("expires_in")
            return self.token
        except Exception as exp:
            LOGGER.warning(f"Unable to refresh token: {exp}")

    def token_has_expired(self) -> bool:
        """Check if current token will expired.

        Returns:
            bool: True if expired, else False
        """
        LOGGER.info("Token Expired ? ")
        return bool(
            self.token.get("expiration_date", int(time.time()))
            <= (int(time.time()) - 1000)
        )

    def update_token(self) -> Dict:
        """ Look for a Token
            Can be created, refreshed or just returned.

        Returns:
            Dict: Token.
        """
        LOGGER.info("Update Token")
        if self.token and not self.token_has_expired():
            return self.token
        if self.token:
            try:
                self.token = self.refresh_token(self.token.get("refresh_token"))
                return self.token
            except Exception as exc:
                LOGGER.warning(f"Unable to refresh token: {exc}")
        else:
            try:
                self.token = self.get_new_token()
                return self.token
            except Exception as exc:
                LOGGER.warning(f"Unable to refresh token: {exc}")

    def get_all_sites(self) -> Dict:
        """Get All Sites

        Returns:
            Dict: Sites Object
        """
        LOGGER.info("Get All Sites")
        token = self.update_token()
        self.headers["Authorization"] = f"Bearer {token.get('access_token')}"
        try:
            response = requests.get(headers=self.headers, url=f"{BASE_URL}/site")
            return response.json()
        except Exception as exp:
            LOGGER.warning(f"Unable to get All Sites: {exp}")

    def get_site(self, site_id: str) -> Dict:
        """Get Site

        Args:
            site_id (str): Site ID

        Returns:
            Dict: Site Oject
        """
        LOGGER.info(f"Get Site ID: {site_id}")
        token = self.update_token()
        self.headers["Authorization"] = f"Bearer {token.get('access_token')}"
        try:
            response = requests.get(
                headers=self.headers, url=f"{BASE_URL}/site/{site_id}"
            )
            return response.json()
        except Exception as exp:
            LOGGER.warning(f"Unable to get Site {site_id}: {exp}")

    def get_devices_from_site_id(self, site_id: str) -> Dict:
        """List Devices from a Site ID

        Args:
            site_id (str): Site ID

        Returns:
            Dict: Device List Object
        """
        LOGGER.info(f"Get Site ID {site_id}")
        token = self.update_token()
        self.headers["Authorization"] = f"Bearer {token.get('access_token')}"
        try:
            response = requests.get(
                headers=self.headers, url=f"{BASE_URL}/site/{site_id}/device"
            )
            return response.json()
        except Exception as exp:
            LOGGER.warning(f"Unable to get Devices on Site {site_id}: {exp}")

    def get_device(self, site_id: str, device_id: str) -> Dict:
        """Get Device details

        Args:
            site_id (str): Site ID
            device_id (str): Device ID

        Returns:
            Dict: detailed Device object
        """
        LOGGER.info(f"Get Device ID {device_id} on Site ID {site_id}")
        token = self.update_token()
        self.headers["Authorization"] = f"Bearer {token.get('access_token')}"
        try:
            response = requests.get(
                headers=self.headers,
                url=f"{BASE_URL}/site/{site_id}/device/{device_id}",
            )
            return response.json()
        except Exception as exp:
            LOGGER.warning(f"Unable to get Device {device_id} on Site {site_id}: {exp}")

    def set_security_level(self, site_id: str, status: Status) -> Dict:
        """Set Alarm Security Level

        Args:
            site_id (str): Site ID
            status (Status): Security Level

        Returns:
            Dict: [description]
        """
        LOGGER.info(f"Set Security Level to {status.lower()} on Site ID {site_id}")
        token = self.update_token()
        self.headers["Authorization"] = f"Bearer {token.get('access_token')}"
        try:
            response = requests.put(
                headers=self.headers,
                data=json.dumps(status.lower()),
                url=f"{BASE_URL}/site/{site_id}/security",
            )
            return response.json()
        except Exception as exp:
            LOGGER.warning(
                f"Unable to set SecurityLevel to {status} on Site {site_id}: {exp}"
            )
