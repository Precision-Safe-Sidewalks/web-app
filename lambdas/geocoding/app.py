import json
import os

import psycopg2
from mapbox import Geocoder
from psycopg2.extras import execute_batch


def handler(event, context):
    """Measurement reverse geocoding Lambda function"""
    project_id = event["project_id"]
    stage = event["stage"]

    print(f"Processing project_id={project_id} stage={stage}")
    measurements = get_measurements(project_id, stage)
    print(f"Found {len(measurements)} measurements")
    addresses = get_geocoded_addresses(measurements)
    print(f"Geocoded {len(addresses)} addresses")
    update_measurements(addresses)
    print("Updated measurements")

    return {
        "StatusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({"count": len(addresses)}),
    }


def get_measurements(project_id, stage):
    """Return the measurement records for the project/stage"""
    query = """
        SELECT
            id,
            ST_X(coordinate) lon,
            ST_Y(coordinate) lat
        FROM repairs_measurement
        WHERE project_id = %(project_id)s
            AND stage = %(stage)s
    """

    with get_db().cursor() as cursor:
        params = {"project_id": project_id, "stage": stage}
        cursor.execute(query, params)

        columns = [c.name for c in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_geocoded_addresses(measurements):
    """Return the Mapbox geocoded addresses"""
    geocoder = Geocoder()
    addresses = []

    for measurement in measurements:
        pk = measurement["id"]
        lat = measurement["lat"]
        lon = measurement["lon"]

        address = None
        resp = geocoder.reverse(lat=lat, lon=lon, limit=1, types=["address"])
        print(resp)

        if resp.ok:
            features = resp.json()["features"]

            if features:
                feature = features[0]
                address = f"{feature['address']} {feature['text']}"
            else:
                print(f"No features found for measurement={pk}")

        else:
            error = resp.json()
            print(f"Error geocoding measurement={pk}: {error}")

        addresses.append({"id": pk, "address": address})

    return addresses


def update_measurements(addresses):
    """Update the measurement geocoded addresses"""
    query = """
        UPDATE repairs_measurement
            SET geocoded_address = %(address)s
        WHERE id = %(id)s
    """

    with get_db() as conn:
        with conn.cursor() as cursor:
            execute_batch(cursor, query, addresses)
            conn.commit()


def get_db():
    """Return the database connection"""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT", 5432),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        dbname=os.environ.get("DB_NAME"),
    )
