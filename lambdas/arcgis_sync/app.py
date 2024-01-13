import logging
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests
from arcgis import ArcGISClient

# Sync all the Items modified in last X days
# - Match the Items to existing Deals
# - Sync the data for the newly matched Deals
# Sync the data for a specified Layer

LOGGER = logging.getLogger(__name__)


def handler(event, context):
    """Synchronize the ArcGIS data"""

    # If the event contains a layer_id, the request is to sync
    # the data for the particular layer
    if layer_id := event.get("layer_id"):
        return sync_layer(layer_id)

    # Otherwise, the request is to sync the ArcGIS items, match
    # them to deals, and sync any layers that have been modified
    # in the past N days
    days = int(event.get("days", 7))
    sync_items(days=days)

    return {"StatusCode": 200}


def sync_layer(layer_id):
    """Synchronize the ArcGIS data for a deal's layer"""
    raise NotImplementedError


def sync_items(days=1):
    """Synchronize the ArcGIS items within the past N days"""
    client = ArcGISClient()
    start = datetime.now(timezone.utc) - timedelta(days=days)

    for item_type in client.ItemType:
        for item in client.search(item_type=item_type, start=start):
            LOGGER.info(f"Upserting {item_type} '{item['title']}'")
            data = {
                "item_id": item["id"],
                "item_type": item_type.upper().replace(" ", "_"),
                "title": item["title"],
                "url": item.get("url"),
            }
            _post("/api/arcgis/items/", data=data)


def _request(method, path, query=None, data=None):
    """Perform an HTTP request to the main API"""
    token = os.environ.get("API_KEY")
    headers = {"Authorization": f"Token {token}"}

    base_url = os.environ.get("API_BASE_URL")
    url = f"{base_url}{path}"

    if query:
        params = urlencode(query)
        url += f"?{params}"

    resp = requests.request(method, url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()

    return resp.json()


def _get(path, query=None, data=None):
    """Perform a GET request to the main API"""
    return _request("GET", path, query=query, data=data)


def _post(path, query=None, data=None):
    """Perform a POST request to the main API"""
    return _request("POST", path, query=query, data=data)
