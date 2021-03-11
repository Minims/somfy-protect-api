"""Devices Categories"""
from enum import Enum, unique


@unique
class Category(Enum):
    """List of Known Devices"""

    LINK = "Link"
    INDOOR_CAMERA = "Somfy Indoor Camera"
    INDOOR_SIREN = "Myfox Security Siren"
    OUTDDOR_CAMERA = "Somfy Outdoor Camera"
    OUTDOOR_SIREN = "Myfox Security Outdoor Siren"
    INTELLITAG = "IntelliTag"
    KEY_FOB = "Key Fob"
    MOTION = "Myfox Security Infrared Sensor"
