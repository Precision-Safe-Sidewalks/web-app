import json
import os

import boto3
import openpyxl
import pandas
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
                p.name,
                CASE
                    WHEN p.pricing_model = 1 THEN 'INCH_FOOT'
                    WHEN p.pricing_model = 2 THEN 'SQUARE_FOOT'
                    ELSE NULL
                END AS pricing_model,
                ubdm.full_name AS bdm,
                usur.full_name AS surveyor,
                c.name AS organization_name
            FROM repairs_project p
                JOIN customers_customer c ON p.customer_id = c.id
                JOIN repairs_instruction i ON p.id = i.project_id AND i.stage = 'SURVEY'
                LEFT OUTER JOIN accounts_user ubdm ON p.business_development_manager_id = ubdm.id
                LEFT OUTER JOIN accounts_user usur ON i.surveyed_by_id = usur.id
            WHERE p.id = %s
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

    def get_data_inch_foot(self, max_groups=20):
        """Return the data for the inch foot pricing model"""

        df = self.get_measurements()
        data = {}

        for group, group_df in df.groupby("survey_group", sort=True):
            sheet_data = {"C1": group}
            offset = 26

            for _, row in group_df.iterrows():
                sheet_data[f"B{offset}"] = int(row.quick_description == "S")
                sheet_data[f"C{offset}"] = int(row.quick_description == "M")
                sheet_data[f"D{offset}"] = int(row.quick_description == "L")
                sheet_data[f"E{offset}"] = int(row.special_case == "C")
                sheet_data[f"F{offset}"] = row.survey_address
                sheet_data[f"G{offset}"] = row.length
                sheet_data[f"H{offset}"] = row.width

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
                "E3": "",  # address
                "F3": self.project["bdm"],  # FIXME: make initials
                "G3": self.project["surveyor"],  # FIXME: make initials
                "H3": "",  # alt deal owner
                "I3": "",  # client name
                "J3": "",  # client title
                "K3": "",  # client email
                "L3": "",  # client phone number
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

    def get_measurements(self):
        """Return the survey measurements"""
        # TODO: use geocoded address

        sql = """
            SELECT
                quick_description,
                special_case,
                survey_address,
                length,
                width,
                TRIM(REGEXP_REPLACE(survey_address, '[[:digit:]]', '', 'g')) AS survey_group 
            FROM repairs_measurement
            WHERE project_id = %s
                AND stage = 'SURVEY'
                AND survey_address IS NOT NULL
        """

        with self.get_db() as con:
            params = (self.project_id,)
            df = pandas.read_sql_query(sql, con, params=params)

        return df

    def insert_data(self, template, data):
        """Insert the data into the pricing sheet template"""

        workbook = openpyxl.load_workbook(template, keep_vba=True)

        for sheet_name, sheet_data in data.items():
            worksheet = workbook[sheet_name]

            for cell, value in sheet_data.items():
                worksheet[cell].value = value

        _, ext = os.path.splitext(template)
        self.filename = f"/tmp/{self.request_id}{ext}"

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
