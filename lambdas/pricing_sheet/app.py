import json
import os
import uuid
from datetime import datetime

import boto3
import openpyxl
import psycopg2

BUCKET = "precision-safe-sidewalks"


def handler(event, context):
    """Pricing sheet generator handler"""
    request_id = event["request_id"]

    generator = PricingSheetGenerator(request_id)
    generator.generate()
    url = generator.upload_to_s3()

    return {
        "StatusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({"url": url}),
    }


class PricingSheetGenerator:
    """Pricing sheet generator for a project"""

    def __init__(self, request_id):
        self.request_id = request_id
        self.project_id = self.get_project_id()
        self.pricing_model = self.get_pricing_model()
        self.filename = None

        if self.pricing_model is None:
            raise ValueError(f"Invalid pricing model for project: {self.project_id}")

    def generate(self):
        """Generate the pricing sheet"""
        template = self.get_template()
        data = self.get_data()
        self.insert_data(template, data)

    def get_project_id(self):
        """Return the project id from the request id"""

        sql = """
            SELECT
                p.id
            FROM repairs_project p
                JOIN repairs_pricingsheet ps ON p.id = ps.project_id
                JOIN repairs_pricingsheetrequest psr ON ps.id = psr.pricing_sheet_id
        """

        with self.get_db().cursor() as cursor:
            cursor.execute(sql, (self.request_id,))
            return cursor.fetchone()[0]

    def get_pricing_model(self):
        """Return the pricing model of the project"""

        sql = """
            SELECT 
                CASE
                    WHEN pricing_model = 1 THEN 'INCH_FOOT'
                    WHEN pricing_model = 2 THEN 'SQUARE_FOOT'
                    ELSE NULL
                END AS pricing_model
            FROM repairs_project 
            WHERE id = %s
        """

        with self.get_db().cursor() as cursor:
            cursor.execute(sql, (self.project_id,))
            return cursor.fetchone()[0]

    def get_template(self):
        """Return the template for the pricing model"""

        if self.pricing_model == "INCH_FOOT":
            return "templates/TEMP Pricing Inch Foot  - 8-29-2023- FINAL.xltx"

        if self.pricing_model == "SQUARE_FOOT":
            # TODO: add SQUARE_FOOT template
            return None

    def get_data(self):
        """Return the data for the pricing model/project"""

        if self.pricing_model == "INCH_FOOT":
            return self.get_data_inch_foot()

        if self.pricing_model == "SQUARE_FOOT":
            return self.get_data_square_foot()

    def get_data_inch_foot(self):
        """Return the data for the inch foot pricing model"""
        return {}

    def get_data_square_foot(self):
        """Return the data for the square foot pricing model"""
        return {}

    def insert_data(self, template, data):
        """Insert the data into the pricing sheet template"""
        workbook = openpyxl.load_workbook(template, keep_vba=True)

        _, ext = os.path.splitext(template)
        self.filename = f"/tmp/{uuid.uuid4()}{ext}"

        workbook.save(self.filename)
        workbook.close()

    def get_db(self):
        """Return the database connection"""
        return psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT", 5432),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            dbname=os.environ.get("DB_NAME"),
        )

    def upload_to_s3(self):
        """Upload the file to S3 and return the presigned URL"""
        generated_at = datetime.now().date()
        _, ext = os.path.splitext(self.filename)
        key = f"pricing_sheets/{generated_at}_{self.request_id}_pricing_sheet{ext}"

        s3 = boto3.client("s3")
        s3.upload_file(self.filename, BUCKET, key)

        self.update_request(key)

        return key

    def update_request(self, key):
        """Update the request's S3 bucket/key"""

        sql = """
            UPDATE repairs_pricingsheetrequest SET
                s3_bucket = %s,
                s3_key = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE request_id = %s
        """

        with self.get_db() as conn:
            with conn.cursor() as cursor:
                params = (BUCKET, key, self.request_id)
                cursor.execute(sql, params)
                conn.commit()
