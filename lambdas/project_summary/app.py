import json
import os
from datetime import datetime

import boto3
import openpyxl
import psycopg2

BUCKET = "precision-safe-sidewalks"
TEMPLATE = "templates/PS Template - MACRO RB 8-29-23.xlsm"


def handler(event, context):
    """Project summary generator handler"""
    request_id = event["request_id"]

    generator = ProjectSummaryGenerator(request_id)
    generator.generate()
    url = generator.upload_to_s3()

    return {
        "StatusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({"url": url}),
    }


class ProjectSummaryGenerator:
    """Project summary generator for a project"""

    def __init__(self, request_id):
        self.request_id = request_id
        self.project = {}
        self.pricing_sheet = {}
        self.survey_instructions = {}
        self.project_instructions = {}
        self.filename = None

    def generate(self):
        """Generate the project summary"""
        self.project = self.get_project()
        self.pricing_sheet = self.get_pricing_sheet()
        self.survey_instructions = self.get_survey_instructions()
        self.project_instructions = self.get_project_instructions()

        data = self.get_data()
        self.insert_data(TEMPLATE, data)

    def get_project(self):
        """Return the project data"""

        sql = """
            SELECT
                project.id,
                project.name,
                project.po_number,
                account.initials AS bdm,
                territory.name AS territory,
                customer.name AS organization_name
            FROM repairs_project project
                JOIN repairs_projectsummaryrequest request ON project.id = request.project_id
                JOIN core_territory territory ON project.territory_id = territory.id
                JOIN customers_customer customer ON project.customer_id = customer.id
                JOIN accounts_user account ON project.business_development_manager_id = account.id
            WHERE request.request_id = %s
        """

        with self.get_db().cursor() as cursor:
            cursor.execute(sql, (self.request_id,))
            columns = [column.name for column in cursor.description]
            results = cursor.fetchone()
            return dict(zip(columns, results))

    def get_pricing_sheet(self):
        """Return the pricing sheet data"""

        sql = """
            SELECT
                pricing.id,
                pricing.estimated_sidewalk_miles,
                contact.address AS contact_address,
                contact.name AS contact_name,
                contact.title AS contact_title,
                contact.phone_number AS contact_phone_number,
                contact.email AS contact_email
            FROM repairs_pricingsheet pricing
                JOIN repairs_pricingsheetcontact contact ON pricing.id = contact.pricing_sheet_id
            WHERE pricing.project_id = %s
        """

        with self.get_db().cursor() as cursor:
            cursor.execute(sql, (self.project["id"],))
            columns = [column.name for column in cursor.description]
            results = cursor.fetchone()
            return dict(zip(columns, results))

    def get_survey_instructions(self):
        """Return the survey instructions data"""

        sql = """
            SELECT
                survey.id,
                account.initials AS surveyor
            FROM repairs_instruction survey
                JOIN accounts_user account ON survey.surveyed_by_id = account.id
            WHERE survey.stage = 'SURVEY'
                AND survey.project_id = %s
        """

        with self.get_db().cursor() as cursor:
            cursor.execute(sql, (self.project["id"],))
            columns = [column.name for column in cursor.description]
            results = cursor.fetchone()
            return dict(zip(columns, results))

    def get_project_instructions(self):
        """Return the project instructions data"""
        return {}

    def get_data(self):
        """Return the map of data to insert"""
        return {
            "SUMMARY": {
                "E1": datetime.today().strftime("%-m/%-d/%Y"),
                "D3": self.project["name"],
                "C8": self.project["po_number"],
                "P2": self.project["bdm"],
                "P4": self.survey_instructions["surveyor"],
                "Q2": self.project["territory"],
                "Q4": None,  # TODO: replace with survey date (check where this comes from)
                "R6": None,  # TODO: replace with PI hazards count
                "R10": None,  # TODO: replace with PI hazards inch feet
                "R17": None,  # TODO: replace with PI hazards linear feet (curbs)
                "AO39": self.project["organization_name"],
                "AQ39": self.pricing_sheet["contact_address"],
                "AS39": self.pricing_sheet["contact_name"],
                "AY39": self.pricing_sheet["contact_title"],
                "BC39": self.pricing_sheet["contact_phone_number"],
                "BG39": self.pricing_sheet["contact_email"],
                "BN39": self.pricing_sheet["estimated_sidewalk_miles"],
            },
        }

    def insert_data(self, template, data):
        """Insert the data into the Excel document"""
        workbook = workbook = openpyxl.load_workbook(template, keep_vba=True)

        for sheet_name, sheet_data in data.items():
            worksheet = workbook[sheet_name]

            for cell, value in sheet_data.items():
                worksheet[cell].value = value

        _, ext = os.path.splitext(template)
        self.filename = f"/tmp/{self.request_id}{ext}"

        workbook.save(self.filename)
        workbook.close()

    def upload_to_s3(self):
        """Upload the file to S3 and return the presigned URL"""
        project_name = self.project["name"]

        _, ext = os.path.splitext(self.filename)
        key = (
            f"project_summaries/{self.request_id}/{project_name} - Project Summary{ext}"
        )

        s3 = boto3.client("s3")
        s3.upload_file(self.filename, BUCKET, key)

        self.update_request(key)

        return key

    def update_request(self, key):
        """Update the request's S3 bucket/key"""

        sql = """ 
            UPDATE repairs_projectsummaryrequest SET
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

    def get_db(self):
        """Return the database connection"""
        return psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT", 5432),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            dbname=os.environ.get("DB_NAME"),
        )
