import os
from urllib.parse import urlencode, urljoin

import requests


def get_item(item_id):
    """Retrieve an ArcGIS Item by id"""
    return _request("GET", f"/api/arcgis/items/{item_id}/", raise_exception=False)


def upsert_item(data):
    """Upsert an ArcGIS Item"""
    return _request("POST", "/api/arcgis/items/", data=data)


def set_item_parent(item_id, parent_id):
    """Set the parent for an ArcGIS Item"""
    data = {"parent": parent_id}
    return _request("PATCH", f"/api/arcgis/items/{item_id}/", data=data)


def match_items():
    """Match the ArcGIS Items to their Web Maps"""
    return _request("POST", "/api/arcgis/items/match/")


def get_project_by_item(item_id):
    """Retrieve a Project by its parent"""
    query = {"arcgis_item": item_id}
    results = _request("GET", "/api/projects/", query=query)

    if results.get("count"):
        return results["results"][0]

    return None


def get_project_layer(layer_id):
    """Retrieve a ProjectLayer"""
    return _request("GET", f"/api/projects/layers/{layer_id}/")


def create_project_layer(data):
    """Create a ProjectLayer"""
    return _request("POST", "/api/projects/layers/", data=data)


def set_project_layer_features(layer_id, data):
    """Set the ProjectLayer's features"""
    return _request("POST", f"/api/projects/layers/{layer_id}/features/", data=data)


def _request(method, path, query=None, data=None, raise_exception=True):
    """Perform an HTTP request to the API"""
    token = os.environ.get("API_KEY")
    base_url = os.environ.get("API_BASE_URL")

    url = urljoin(base_url, path)
    headers = {"Authorization": f"Token {token}"}

    if query:
        url += f"?{urlencode(query)}"

    resp = requests.request(method, url, json=data, headers=headers, timeout=60)

    if not resp.ok:
        if raise_exception:
            resp.raise_for_status()
        return None

    return resp.json()
