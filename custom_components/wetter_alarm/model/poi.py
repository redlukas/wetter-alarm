"""Describe the data model returned from the /v7/pois Endpoint."""

from datetime import date, datetime
from enum import Enum
from xmlrpc.client import Boolean
from zoneinfo import ZoneInfo

from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    field_validator,
)

from custom_components.wetter_alarm.model.alert import Alert
from custom_components.wetter_alarm.model.canton import (
    CANTON_ABBR_LEN,
    Canton,
    get_canton_abbr,
)


class Kind(str, Enum):
    """Hold the kinds a POI can be."""

    airport = "airport"
    alpine_hut = "alpine_hut"
    building_of_interest = "building_of_interest"
    campground = "campground"
    golf = "golf"
    pass_kind = "pass"  # noqa: S105
    peak = "peak"
    ski_area = "ski_area"
    stadium = "stadium"
    town = "town"
    town_section = "town_section"
    unknown = "unknown"
    valley = "valley"
    viewpoint = "viewpoint"
    zoo = "zoo"


class PoiDescription(BaseModel):
    """Describe the description of a POI."""

    label: str | None
    parent_label: str | None
    external_url: str | None
    geo_subdivision_label: str
    country_label: str
    geo_subdivisions: dict[str, str]


class StatusV2(str, Enum):
    """Hold the status a livecam image can have."""

    fresh = "fresh"
    working = "working"
    not_working = "not_working"
    idle = "idle"
    late = "late"
    stale = "stale"


class Geolocation(BaseModel):
    """Describe a single geolocated point."""

    lat: float
    long: float


class BoundingBox(BaseModel):
    """Describe a bounding box."""

    sw: Geolocation
    ne: Geolocation


class LivecamStatus(str, Enum):
    """Hold the status a livecam can have."""

    working = "working"
    broken = "broken"
    late = "late"
    idle = "idle"


class LivecamCategory(str, Enum):
    """Hold the categories a livecam can have."""

    cities = "Cities"
    tourism_associations = "Tourism associations"
    hotels = "Hotels"
    airports = "Airports"
    harbors = "Harbors"
    hospitals = "Hospitals"
    villages = "Villages"
    ski_resorts = "Ski resorts"
    corporates = "Corporates"
    restaurants = "Restaurants"
    unknown = "unknown"
    schools = "Schools"
    construction_sites = "Construction sites"
    museums = "Museums"
    golf_clubs = "Golf clubs"
    sport_clubs = "Sport clubs"
    wineries = "Wineries"


class LivecamImage(BaseModel):
    """Describe a single livecam image."""

    url: str
    height: int


class LivecamImages(BaseModel):
    """Describe the possible livecam images."""

    full: LivecamImage
    xlarge: LivecamImage
    large: LivecamImage
    medium: LivecamImage
    small: LivecamImage
    xsmall: LivecamImage


class NearbyNearbylivecamivecam(BaseModel):
    """Describe a nearby livecam."""

    livecam_id: PositiveInt = Field(..., alias="id")
    label: str
    distance: NonNegativeFloat


class LivecamDescription(BaseModel):
    """Describe the description of a livecam."""

    external_url: str
    country: str
    geo_subdivisions: dict[str, str]
    geo_subdivision_label: str


class Livecam(BaseModel):
    """Describe a Livecam."""

    livecam_id: PositiveInt = Field(..., alias="id")
    label: str
    roundshot_id: str
    angle: NonNegativeInt
    long: float
    lat: float
    altitude: int
    nightly: Boolean
    poi_id: PositiveInt
    status: LivecamStatus
    town: str | None
    canton: Canton | None
    customer_name: str
    category: LivecamCategory
    customer_address: str | None
    website: str | None
    region: str
    interval: PositiveInt | None
    shot_timestamp: datetime
    taken_at: datetime
    image: str
    image_medium: str
    thumbnail: str
    images: LivecamImages
    de: PoiDescription | LivecamDescription
    fr: PoiDescription | LivecamDescription
    it: PoiDescription | LivecamDescription
    en: PoiDescription | LivecamDescription
    time_zone: ZoneInfo
    status_v2: StatusV2
    published_at: datetime | None
    zip_value: PositiveInt | None
    country_bounding_box: BoundingBox | None
    alignment: float

    @field_validator("time_zone", mode="before")
    def parse_timezone(cls, v: str | ZoneInfo) -> ZoneInfo:  # noqa: N805
        """Parse timezone from string."""
        return v if isinstance(v, ZoneInfo) else ZoneInfo(v)

    @field_validator("canton", mode="before")
    @classmethod
    def normalize_canton(cls, v: str) -> str:
        """Normalize canton input."""
        if isinstance(v, str):
            if len(v) <= CANTON_ABBR_LEN:
                return v.upper()
            return get_canton_abbr(v)
        return v


class LivecamPoi(BaseModel):
    """Describe a POI that is pure livecam."""

    livecams: list[Livecam]
    livecam: Livecam


class LunarPhase(str, Enum):
    """Hold the values the moon can have."""

    full_moon = "full_moon"
    waxing = "waxing"


class Mood(str, Enum):
    """Hold the values the mood can have."""

    partlymoony = "partlymoony"
    rainy = "rainy"
    partlycloudy = "partlycloudy"
    sunny = "sunny"
    rainynight = "rainynight"
    stormy = "stormy"
    moony = "moony"
    stormynight = "stormynight"
    cloudy = "cloudy"
    cloudynight = "cloudynight"
    snowy = "snowy"
    snowynight = "snowynight"


class WindDirectionName(str, Enum):
    """Hold the values the wind direction can have."""

    N = "N"
    NE = "NE"
    NW = "NW"
    S = "S"
    SE = "SE"
    SW = "SW"
    W = "W"
    E = "E"


class BoundaryForecast(BaseModel):
    """Describe a forecast for whatever."""

    valid_time: datetime
    temperature: int
    precipitation_probability: int
    precipitation_amount: float
    wind_speed_mean: NonNegativeInt
    wind_speed_max: NonNegativeInt
    wind_direction: NonNegativeInt
    symbol: int
    lunar_phase: LunarPhase
    mood: Mood
    wind_chill_temperature: float | None
    symbol_v2: int | None
    wind_direction_name: WindDirectionName | None


class DayForecast(BaseModel):
    """Describe the forecast for a day."""

    date: date
    insolation: float
    wind_speed_max: NonNegativeInt
    wind_direction: NonNegativeInt
    temperature_max: int
    temperature_min: int
    precipitation_amount: NonNegativeFloat
    precipitation_probability: NonNegativeInt
    symbol: int
    lunar_phase: LunarPhase
    mood: Mood
    lunar_phase_time: NonNegativeInt | None
    sunrise: datetime
    sunset: datetime
    symbol_v2: int
    wind_direction_name: WindDirectionName
    insolation_max: NonNegativeFloat
    lunar_phase_percentage: NonNegativeInt


class HourForecast(BaseModel):
    """Describe an hourly forecast."""

    valid_time: datetime
    temperature: int
    precipitation_probability: NonNegativeInt
    precipitation_amount: NonNegativeFloat
    wind_speed_mean: NonNegativeInt
    wind_speed_max: NonNegativeInt
    wind_direction: NonNegativeInt
    symbol: int
    lunar_phase: LunarPhase
    mood: Mood
    wind_chill_temperature: float | None
    symbol_v2: int
    wind_direction_name: WindDirectionName | None


class POI(BaseModel):
    """Describe a Point of interest."""

    poi_id: PositiveInt = Field(..., alias="id")
    kind: Kind
    lat: float
    long: float
    geoname_id: PositiveInt | None = None
    time_zone: ZoneInfo
    livecams_nearby: list[NearbyNearbylivecamivecam]
    canton: Canton
    zip_value: PositiveInt
    de: PoiDescription
    fr: PoiDescription
    en: PoiDescription
    is_international: bool
    boundary_day_forecasts: list[BoundaryForecast]
    day_forecasts: list[DayForecast]
    hour_forecasts: list[HourForecast]
    livecams: list[Livecam] | None
    alerts: list[Alert] = []

    def __repr__(self) -> str:
        """Create a string representation."""
        return (
            f"POI(id={self.poi_id},"
            f"kind={self.kind},"
            f"{len(self.alerts)}"
            f"alerts: {self.alerts})"
        )

    @field_validator("time_zone", mode="before")
    def parse_timezone(cls, v: str | ZoneInfo) -> ZoneInfo:  # noqa: N805
        """Parse timezone from string."""
        return v if isinstance(v, ZoneInfo) else ZoneInfo(v)

    @field_validator("canton", mode="before")
    @classmethod
    def normalize_canton(cls, v: str) -> str:
        """Normalize canton input."""
        if isinstance(v, str):
            if len(v) <= CANTON_ABBR_LEN:
                return v.upper()
            return get_canton_abbr(v)
        return v
