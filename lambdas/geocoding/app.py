import json
import os

import psycopg2
from mapbox import Geocoder
from psycopg2.extras import execute_batch


def handler(event, context):
    """Measurement reverse geocoding Lambda function"""
    for record in event["Records"]:
        body = json.loads(record["body"])
        project_id = int(body["project_id"])
        stage = body["stage"]

        measurements = get_measurements(project_id, stage)
        addresses = get_geocoded_addresses(measurements)
        update_measurements(addresses)


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

        if resp.ok:
            features = resp.json()["features"]

            if features:
                feature = features[0]
                address = f"{feature['address']} {feature['text']}"

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
