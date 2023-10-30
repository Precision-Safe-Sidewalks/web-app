import csv
from datetime import datetime, timezone
from typing import Optional

from dateutil.parser import parse as parse_dt
from django.contrib.gis.geos import Point
from pydantic import BaseModel, Field, validator

from repairs.models.constants import QuickDescription, SpecialCase, Stage


class BaseMeasurement(BaseModel):
    """Base measurement record with common attributes"""

    object_id: int = Field(alias="OBJECTID")
    length: Optional[float] = Field(alias="Length")
    width: Optional[float] = Field(alias="Width")
    area: Optional[float] = Field(alias="SQFT")
    long: float = Field(alias="x")
    lat: float = Field(alias="y")
    coordinate: Optional[Point] = None
    h1: Optional[float] = Field(alias="H1")
    h2: Optional[float] = Field(alias="H2")
    curb_length: Optional[float] = Field(alias="Curb Length (feet)")
    measured_hazard_length: Optional[float] = Field(
        alias="Measured Hazard Length (inches)"
    )
    inch_feet: Optional[float] = Field(alias="Inch Feet")
    special_case: Optional[str] = Field(alias="Special Case")
    hazard_size: Optional[str] = Field(alias="Hazard Size")
    tech: str = Field(alias="Creator")
    note: Optional[str] = Field(alias="Notes")
    survey_address: Optional[str] = Field(alias="Address", default="")
    measured_at: datetime = Field(alias="CreationDate")

    class Config:
        arbitrary_types_allowed = True

    @validator("coordinate", pre=False, always=True)
    @classmethod
    def validate_point(cls, _, values):
        long = values.get("long")
        lat = values.get("lat")

        if long is None or lat is None:
            raise ValueError("Invalid longitude and latitude must not be null")

        return Point(long, lat)

    @validator("measured_at", pre=True)
    @classmethod
    def validate_measured_at(cls, v):
        measured_at = parse_dt(v)
        measured_at = measured_at.replace(tzinfo=timezone.utc)
        return measured_at

    @validator("special_case", pre=True)
    @classmethod
    def validate_special_case(cls, v):
        for key, alias in SpecialCase.choices:
            if str(v).lower() == alias.lower():
                return key

        if v:
            raise ValueError(f"Invalid special_case: {v}")

        return None

    @validator("hazard_size", pre=True)
    @classmethod
    def validate_hazard_size(cls, v):
        for key, alias in QuickDescription.choices:
            if str(v).lower() == alias.lower():
                return key

        if v:
            raise ValueError(f"Invalid hazard size: {v}")

        return None

    @classmethod
    def from_csv(cls, file_obj):
        """Return a list of measurements parsed from a CSV file"""
        measurements = []

        group = "default"
        group_alias = None

        if "survey_group" in cls.__fields__:
            group_alias = cls.__fields__["survey_group"].alias

        for data in csv.DictReader(file_obj):
            for key, value in data.items():
                if value.strip() == "":
                    data[key] = None

            data[group_alias] = data.get(group_alias) or group
            group = data[group_alias]

            measurement = cls.parse_obj(data)
            measurements.append(measurement)

        return measurements

    @classmethod
    def order(cls) -> list[str]:
        """Return the field order"""
        return list(cls.__fields__)

    def model_dump(self, **kwargs):
        return super().model_dump(**kwargs)


class SurveyMeasurement(BaseMeasurement):
    """Measurement record from a survey CSV"""

    survey_group: Optional[str] = Field(alias="Start Street - Area")

    @classmethod
    def order(cls) -> list[str]:
        """Return the field order"""
        return [
            "object_id",
            "survey_group",
            "width",
            "length",
            "area",
            "hazard_size",
            "special_case",
            "curb_length",
            "note",
            "h1",
            "h2",
            "measured_hazard_length",
            "inch_feet",
            "lat",
            "long",
            "measured_at",
            "tech",
        ]


class ProductionMeasurement(BaseMeasurement):
    """Measurement record from a production CSV"""

    inch_feet: float = Field(alias="Inch Feet")
    slope: Optional[str] = Field(alias="Slope")

    @classmethod
    def order(cls) -> list[str]:
        """Return the field order"""
        return [
            "object_id",
            "measured_at",
            "tech",
            "width",
            "length",
            "area",
            "h1",
            "h2",
            "measured_hazard_length",
            "hazard_size",
            "slope",
            "inch_feet",
            "special_case",
            "curb_length",
            "note",
            "lat",
            "long",
        ]


def get_parser_class(stage):
    """Return the parser class for the stage"""
    if stage == Stage.SURVEY:
        return SurveyMeasurement

    if stage == Stage.PRODUCTION:
        return ProductionMeasurement

    raise ValueError(f"No parser for stage: {stage}")
