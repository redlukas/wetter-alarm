"""Describe a Canton."""

from enum import Enum

CANTON_ABBR_LEN = 2


def get_canton_abbr(long_form: str) -> str:
    """Get the canton abbreviation from the long form string."""
    match long_form.lower():
        case "thurgau":
            return "TG"


class Canton(str, Enum):
    """Hold the values a canton can have."""

    AG = "AG"
    AI = "AI"
    AR = "AR"
    BE = "BE"
    BL = "BL"
    BS = "BS"
    FL = "FL"
    FR = "FR"
    GE = "GE"
    GL = "GL"
    GR = "GR"
    INTERNATIONAL = "I"
    JU = "JU"
    LU = "LU"
    NE = "NE"
    NW = "NW"
    OW = "OW"
    SG = "SG"
    SH = "SH"
    SO = "SO"
    SZ = "SZ"
    TG = "TG"
    TI = "TI"
    UR = "UR"
    VD = "VD"
    VS = "VS"
    ZG = "ZG"
    ZH = "ZH"
