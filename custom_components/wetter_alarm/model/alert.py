"""Describe the data model returned from the /v7/alarms/meteo.json Endpoint."""

from datetime import datetime

from pydantic import BaseModel, Field, PositiveInt

from custom_components.wetter_alarm.model.canton import Canton


class RegionName(BaseModel):
    """Describe a Region Name."""

    name: str

    def __repr__(self) -> str:
        """Create a string representation."""
        return self.name


class Region(BaseModel):
    """Describe a Region."""

    srf_id: PositiveInt
    de: RegionName
    fr: RegionName
    it: RegionName
    en: RegionName

    def __repr__(self) -> str:
        """Create a string representation."""
        return f"{self.de} ({self.srf_id})"


class AlertDescription(BaseModel):
    """Describe an Alert Description."""

    title: str
    hint: str
    signature: str | None
    paragraph: str

    def __repr__(self) -> str:
        """Create a string representation."""
        return f"title: {self.title}, hint: {self.hint}, signature: {self.signature}"


class Alert(BaseModel):
    """Describe an alert."""

    alert_id: PositiveInt = Field(..., alias="id")
    valid_from: datetime
    valid_to: datetime
    priority: PositiveInt
    region: Region
    cantons: list[Canton]
    poi_ids: list[PositiveInt]
    code: PositiveInt
    de: AlertDescription
    fr: AlertDescription
    it: AlertDescription
    en: AlertDescription

    def __repr__(self) -> str:
        """Create a string representation."""
        return (
            f"alert_id: {self.alert_id},"
            f"valid_from: {self.valid_from},"
            f"valid_to: {self.valid_to}"
        )
