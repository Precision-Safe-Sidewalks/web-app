import logging
import re
from datetime import datetime, timedelta, timezone

from arcgis import ArcGISClient

from api import (
    create_project_layer,
    get_item,
    get_project_by_item,
    get_project_layer,
    match_items,
    set_item_parent,
    set_project_layer_features,
    upsert_item,
)

LOGGER = logging.getLogger(__name__)
RE_LAYER_TYPE = re.compile(r"^PSS\s+(?P<layer_type>Survey|Repair)")


def handler(event, context):
    """Synchronize the ArcGIS data"""

    # If the event contains a layer_id, the request is to sync
    # the data for the particular layer
    if layer_id := event.get("layer_id"):
        sync_layer(layer_id)

    # Otherwise, the request is to sync the ArcGIS items, match
    # them to deals, and sync any layers that have been modified
    # in the past N days
    else:
        days = int(event.get("days", 1))
        sync_items(days=days)

    return {"StatusCode": 200}


def sync_layer(layer_id):
    """Synchronize the ArcGIS data for a project layer"""
    project_layer = get_project_layer(layer_id)
    arcgis_layer = get_item(project_layer["arcgis_item"])

    client = ArcGISClient()
    features = client.get_features_by_url(arcgis_layer["url"])
    set_project_layer_features(layer_id, features)


def sync_items(days=1):
    """Synchronize the ArcGIS items within the past N days"""
    client = ArcGISClient()
    start = datetime.now(timezone.utc) - timedelta(days=days)
    layers = {}

    for item_type in (client.ItemType.FEATURE_SERVICE, client.ItemType.WEB_MAP):
        for item in client.search(item_type=item_type, start=start):
            LOGGER.info(f"Upserting {item_type} '{item['title']}'")

            data = {
                "item_id": item["id"],
                "item_type": item_type.upper().replace(" ", "_"),
                "title": item["title"],
                "parent": None,
            }

            if item_type == client.ItemType.FEATURE_SERVICE:
                data["url"] = item["url"] + "/0"

            item = upsert_item(data)

            # If the item is a Web Map, associate the children feature layers
            # with the web map.
            if item_type == client.ItemType.WEB_MAP:
                for layer in client.get_item_layers(item["item_id"]):
                    layer_item = get_item(layer["itemId"])

                    if layer_item:
                        layer_item = set_item_parent(layer_item["id"], item["id"])
                        layers[layer_item["id"]] = layer_item
            else:
                layers[item["id"]] = item

    # Match any Projects without an associated Web Map to the matching
    # Web Map based on the title.
    match_items()

    # For any layers that have changed in the last N days, sync the data
    # from ArcGIS if there is a matching Project.
    for layer_id, layer in layers.items():
        parent = layer["parent"]
        title = layer["title"]
        match = RE_LAYER_TYPE.match(title)

        if not (parent and match):
            continue

        layer_type = match.group("layer_type")
        project = get_project_by_item(parent)
        project_layer = None

        if not project:
            continue

        for candidate in project["layers"]:
            if candidate["arcgis_item"] == layer_id:
                project_layer = candidate
                break

        if not project_layer:
            data = {
                "project": project["id"],
                "stage": layer_type.upper().replace("REPAIR", "PRODUCTION"),
                "arcgis_item": layer_id,
            }
            project_layer = create_project_layer(data)

        sync_layer(project_layer["id"])
