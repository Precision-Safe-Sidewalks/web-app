import csv
import uuid
from datetime import datetime, timezone
from typing import Optional

from dateutil.parser import parse as parse_dt
from django.contrib.gis.geos import Point
from pydantic import BaseModel, Field, validator

from repairs.models.constants import QuickDescription, SpecialCase


class BaseMeasurement(BaseModel):
    """Base measurement record with common attributes"""

    object_id: int = Field(alias="OBJECTID")
    global_id: uuid.UUID = Field(alias="GlobalID")
    length: Optional[float] = Field(alias="Length")
    width: Optional[float] = Field(alias="Width")
    x: float = Field(alias="x")
    y: float = Field(alias="y")
    coordinate: Optional[Point] = None
    h1: Optional[float] = Field(alias="H1")
    h2: Optional[float] = Field(alias="H2")
    special_case: Optional[str] = Field(alias="Special Case")
    quick_description: Optional[str] = Field(alias="Quick Description")
    surveyor: str = Field(alias="Creator")
    note: Optional[str] = Field(alias="Notes")
    measured_at: datetime = Field(alias="CreationDate")

    class Config:
        arbitrary_types_allowed = True

    @validator("coordinate", pre=False, always=True)
    @classmethod
    def validate_point(cls, _, values):
        return Point(values["x"], values["y"])

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
            if v == alias:
                return key

        if v:
            raise ValueError(f"Invalid special_case: {v}")

        return None

    @validator("quick_description", pre=True)
    @classmethod
    def validate_quick_description(cls, v):
        for key, alias in QuickDescription.choices:
            if v == alias:
                return key

        if v:
            raise ValueError(f"Invalid quick_description: {v}")

        return None

    @classmethod
    def from_csv(cls, file_obj):
        """Return a list of measurements parsed from a CSV file"""
        measurements = []

        for data in csv.DictReader(file_obj):
            for key, value in data.items():
                if value.strip() == "":
                    data[key] = None

            measurement = cls.parse_obj(data)
            measurements.append(measurement)

        return measurements

    def model_dump(self, **kwargs):
        kwargs["exclude"] = kwargs.get("exclude", {"x", "y"})
        return super().model_dump(**kwargs)


class SurveyMeasurement(BaseMeasurement):
    """Measurement record from a survey CSV"""

    curb_length: Optional[float] = Field(alias="Curb Length")
    survey_address: Optional[str] = Field(alias="Survey Address")


class ProductionMeasurement(BaseMeasurement):
    """Measurement record from a production CSV"""

    h1: float = Field(alias="H1")
    inch_feet: float = Field(alias="Inch Feet")
    linear_feet: Optional[float] = Field(alias="Linear Feet")
    slope: Optional[str] = Field(alias="Slope")
