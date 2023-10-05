import json
import os
import platform
import subprocess

import boto3
import pandas
import psycopg2
from excel import Workbook

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
        self.project = self.get_project()
        self.filename = None
        self.raw_data = {}

        if self.project["pricing_model"] is None:
            raise ValueError(f"Invalid pricing model for project: {self.project_id}")

    def generate(self):
        """Generate the pricing sheet"""
        template = self.get_template()
        data = self.get_data()
        self.insert_data(template, data)
        self.convert_to()

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

    def get_project(self):
        """Return the project data"""

        sql = """
            SELECT 
                project.name AS name,
                user_a.initials AS bdm,
                user_b.initials AS surveyor,
                customer.name AS organization_name,
                contact.name AS contact_name,
                contact.title AS contact_title,
                contact.email AS contact_email,
                contact.phone_number AS contact_phone_number,
                contact.address AS contact_address,
                CASE
                    WHEN project.pricing_model = 1 THEN 'INCH_FOOT'
                    WHEN project.pricing_model = 2 THEN 'SQUARE_FOOT'
                    ELSE NULL
                END AS pricing_model
            FROM repairs_project project
                JOIN customers_customer customer ON project.customer_id = customer.id
                JOIN repairs_instruction instruction ON project.id = instruction.project_id AND instruction.stage = 'SURVEY'
                JOIN repairs_pricingsheet pricing ON project.id = pricing.project_id
                LEFT OUTER JOIN repairs_pricingsheetcontact contact ON pricing.id = contact.pricing_sheet_id
                LEFT OUTER JOIN accounts_user user_a ON project.business_development_manager_id = user_a.id
                LEFT OUTER JOIN accounts_user user_b ON instruction.surveyed_by_id = user_b.id
            WHERE project.id = %s
        """

        with self.get_db().cursor() as cursor:
            cursor.execute(sql, (self.project_id,))
            columns = [column.name for column in cursor.description]
            results = cursor.fetchone()
            return dict(zip(columns, results))

    def get_template(self):
        """Return the template for the pricing model"""

        pricing_model = self.project["pricing_model"]

        if pricing_model == "INCH_FOOT":
            return "templates/TEMP Pricing Inch Foot  - 8-29-2023- FINAL.xltx"

        if pricing_model == "SQUARE_FOOT":
            # TODO: add SQUARE_FOOT template
            return None

    def get_data(self):
        """Return the data for the pricing model/project"""

        pricing_model = self.project["pricing_model"]
        self.raw_data = self.get_raw_data()

        if pricing_model == "INCH_FOOT":
            return self.get_data_inch_foot()

        if pricing_model == "SQUARE_FOOT":
            return self.get_data_square_foot()

    def get_raw_data(self):
        """Return the raw data"""

        sql = """
            SELECT
                estimated_sidewalk_miles,
                surveyor_speed,
                survey_hazards,
                hazard_density,
                panel_size,
                distance_from_surveyor,
                distance_from_ops,
                commission_rate,
                base_rate,
                number_of_technicians
            FROM repairs_pricingsheet
            WHERE project_id = %s
        """

        with self.get_db().cursor() as cursor:
            cursor.execute(sql, (self.project_id,))
            columns = [column.name for column in cursor.description]
            results = cursor.fetchone()
            return dict(zip(columns, results))

    def get_data_inch_foot(self):
        """Return the data for the inch foot pricing model"""

        df = self.get_measurements(max_groups=20).fillna("")
        data = {}

        for group, group_df in df.groupby("survey_group", sort=True):
            sheet_data = {"C1": group}
            offset = 26

            for _, row in group_df.iterrows():
                sheet_data[f"B{offset}"] = int(row.quick_description == "S")
                sheet_data[f"C{offset}"] = int(row.quick_description == "M")
                sheet_data[f"D{offset}"] = int(row.quick_description == "L")
                sheet_data[f"E{offset}"] = row.linear_feet
                sheet_data[f"F{offset}"] = row.geocoded_address
                sheet_data[f"G{offset}"] = row.length
                sheet_data[f"H{offset}"] = row.width
                sheet_data[f"T{offset}"] = row.object_id

                offset += 1

            sheet_name = str(len(data) + 1)
            data[sheet_name] = sheet_data

        return {
            "Projected Survey Cost": {
                "D4": self.raw_data["estimated_sidewalk_miles"],
                "D5": self.raw_data["surveyor_speed"],
                "D7": int(self.raw_data["survey_hazards"] == 1),
                "D8": int(self.raw_data["survey_hazards"] == 2),
                "D9": int(self.raw_data["survey_hazards"] == 3),
                "D11": int(self.raw_data["hazard_density"] == 1),
                "D12": int(self.raw_data["hazard_density"] == 2),
                "D13": int(self.raw_data["hazard_density"] == 3),
                "D15": int(self.raw_data["panel_size"] == 1),
                "D16": int(self.raw_data["panel_size"] == 2),
                "D17": int(self.raw_data["panel_size"] == 3),
            },
            "JPC - Full Scope": {
                "C6": self.raw_data["distance_from_surveyor"],
                "C7": self.raw_data["distance_from_ops"],
            },
            "SUMMARY": {
                "D3": self.project["organization_name"],
                "E3": self.project["contact_address"],
                "F3": self.project["bdm"],
                "G3": self.project["surveyor"],
                "H3": "",  # TODO: alt deal owner
                "I3": self.project["contact_name"],
                "J3": self.project["contact_title"],
                "K3": self.project["contact_email"],
                "L3": self.project["contact_phone_number"],
            },
            "GREEN SAVINGS": {
                "E44": self.raw_data["number_of_technicians"],
                "F44": self.raw_data["number_of_technicians"],
            },
            **data,
        }

    def get_data_square_foot(self):
        """Return the data for the square foot pricing model"""
        return {}

    def get_measurements(self, max_groups=None):
        """Return the survey measurements"""

        sql = """
            SELECT
                object_id,
                quick_description,
                special_case,
                length,
                width,
                COALESCE(linear_feet, 0) AS linear_feet,
                geocoded_address,
                survey_group
            FROM repairs_measurement
            WHERE project_id = %s
                AND stage = 'SURVEY'
        """

        with self.get_db() as con:
            params = (self.project_id,)
            df = pandas.read_sql_query(sql, con, params=params)

        # If max_groups is specified, ensure that the number of survey
        # groups is less than or equal. Merge the smallest groups together
        # to reach the goal.
        if max_groups:
            groups = df.survey_group.unique()

            while len(groups) > max_groups:
                counts = df.survey_group.value_counts(ascending=True)
                values = counts.iloc[:2].index.values
                merged = " & ".join(values)

                df.loc[df.survey_group == values[0], "survey_group"] = merged
                df.loc[df.survey_group == values[1], "survey_group"] = merged

                groups = df.survey_group.unique()

        # Sort by the survey group and object id for consistent ordering
        df.sort_values(["survey_group", "object_id"], inplace=True)

        return df

    def insert_data(self, template, data):
        """Insert the data into the pricing sheet template"""

        workbook = Workbook(template)

        for sheet_name, sheet_data in data.items():
            for cell, value in sheet_data.items():
                workbook.update_cell(sheet_name, cell, value)

        _, ext = os.path.splitext(template)
        self.filename = f"/tmp/{self.request_id}{ext}"
        workbook.save(self.filename)

    def get_db(self):
        """Return the database connection"""
        return psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT", 5432),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            dbname=os.environ.get("DB_NAME"),
        )

    def convert_to(self):
        """Convert the file to use the extension"""
        if platform.machine() == "aarch64":
            return

        command = [
            "libreoffice7.6",
            "--headless",
            "--convert-to",
            "xlsx",
            "--outdir",
            "/tmp",
            self.filename,
        ]
        subprocess.call(command)
        self.filename = self.filename.replace(".xltx", ".xlsx")

    def upload_to_s3(self):
        """Upload the file to S3 and return the presigned URL"""
        project_name = self.project["name"]
        _, ext = os.path.splitext(self.filename)
        key = f"pricing_sheets/{self.request_id}/{project_name} - Pricing Sheet{ext}"

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
