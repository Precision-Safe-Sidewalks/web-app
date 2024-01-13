import os
import time
from enum import Enum
from urllib.parse import urlencode

import requests


class ArcGISClient:
    """ArcGIS REST API client"""

    class ItemType(str, Enum):
        WEB_MAP = "Web Map"
        FEATURE_SERVICE = "Feature Service"

    def __init__(self):
        self._auth_url = "https://www.arcgis.com/sharing/rest/generateToken"
        self._base_url = "https://psspims.maps.arcgis.com"
        self._token = None
        self._token_expires = -1

    def _request(self, method, path, query=None, json=None, base_url=None):
        """Perform an API request"""
        if self.is_token_expired():
            self.refresh_token()

        query = query or {}
        query["token"] = self._token

        if "f" not in query:
            query["f"] = "json"

        if not base_url:
            base_url = self._base_url

        params = urlencode(query)
        url = f"{base_url}{path}?{params}"

        resp = requests.request(method, url, json=json, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        if data.get("error"):
            raise ValueError(resp.json())

        return data

    def _get(self, path, query=None, base_url=None):
        """Perform a GET request"""
        return self._request("GET", path, query=query, base_url=base_url)

    def refresh_token(self):
        """Refersh the ArcGIS API token"""
        self._token = None
        self._token_expires = None

        data = {
            "username": os.environ.get("ARCGIS_USERNAME"),
            "password": os.environ.get("ARCGIS_PASSWORD"),
            "referer": "https://www.arcgis.com",
            "client": "referer",
            "f": "json",
        }

        resp = requests.post(self._auth_url, data, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        self._token = data.get("token")
        self._token_expires = data.get("expires", -1)

    def is_token_expired(self):
        """Return True if the token is expired"""
        return self._token is None or (time.time() - 15) * 1000 > self._token_expires

    def search(self, item_type=None, start=None, end=None):
        """Search using the content API"""
        query = {
            "q": 'owner:"a.hester@precisionsafesidewalks.com"',
            "sortField": "modified",
            "sortOrder": "asc",
            "num": 100,
            "start": 0,
        }

        if item_type:
            query["q"] += f' AND type: "{item_type}"'

        if start or end:
            t0 = 0 if not start else 1000 * start.timestamp()
            t1 = time.time() * 1000 if not end else 1000 * end.timestamp()
            query["filter"] = f"modified: [{t0} TO {t1}]"

        url = "/sharing/search"
        results = []

        while query["start"] != -1:
            data = self._get(url, query=query)
            results += data.get("results", [])
            query["start"] = data.get("nextStart", -1)

        return results

    def get_item(self, item_id):
        """Fetch an Item definition"""
        url = f"/sharing/rest/content/items/{item_id}"
        return self._get(url)

    def get_item_layers(self, item_id):
        """Fetch an Item's layer definitions"""
        url = f"/sharing/rest/content/items/{item_id}/data"
        return self._get(url).get("operationalLayers", [])

    def get_features(self, item_id, layer_title):
        """Fetch a Layer's features by its item and title"""
        item = self.get_item(item_id)
        url = None

        for layer in item["data"]["operationalLayers"]:
            if layer["title"] == layer_title:
                url = layer["url"]
                break

        if not url:
            raise ValueError(f"Layer {layer_title} not found")

        query = {
            "where": "1=1",
            "returnGeometry": True,
            "orderByFields": "OBJECTID ASC",
            "outFields": "*",
            "outSR": 4326,
            "f": "geojson",
        }

        return self._get("/query", query=query, base_url=url)
