from dataclasses import dataclass
from enum import StrEnum
from datetime import datetime

@dataclass
class BasicGroup:
    """BasicGroup(timestamp, position, altitude)
    
    ADS-C Basic Group.

    Args:
        timestamp (datetime): Report timestamp (day, hour, minute)
        position (tuple[float, float]): Latitude, Longitude
        altitude (float): Altitude in ft
    """
    timestamp: datetime
    position: tuple[float, float]
    altitude: float

    def __eq__(self, value: object) -> bool:
        return isinstance(value, BasicGroup) and \
            (value.altitude == self.altitude) and \
            (value.position == self.position) and \
            (value.timestamp.day == self.timestamp.day) and \
            (value.timestamp.hour == self.timestamp.hour) and \
            (value.timestamp.minute == self.timestamp.minute)

@dataclass
class FlightIdentGroup:
    """FlightIdentGroup(acft_ident)
    
    ADS-C Flight Identification Group.
    
    Args:
        acft_ident (str): Aircraft identification ("callsign")
    """
    acft_ident: str

@dataclass
class EarthRefGroup:
    """EarthRefGroup(true_track, ground_speed [, vertical_rate])

    ADS-C Earth Reference Group.

    Args:
        true_track (float): True track in degrees
        ground_speed (float): Ground speed in knots
        vertical_rate (VerticalRate | None, optional): Vertical rate (climb, level or descent)
    """
    class VerticalRate(StrEnum):
        CLIMB = 'CLB'
        LEVEL = 'LVL'
        DESCENT = 'DES'

    true_track: float
    ground_speed: float
    vertical_rate: VerticalRate | None = None

@dataclass
class MeteoGroup:
    """MeteoGroup(wind, temperature)
    
    ADS-C Meteorological Group.

    Args:
        wind (tuple[float, float]): Wind direction and speed (kts)
        temperature (float): Outside Air Temperature(?) in degrees Celsius
    """
    wind: tuple[float, float]
    temperature: float

@dataclass
class AdscData:
    """AdscData(basic, flight_ident[, earth_ref[, meteo]])
    
    ADS-C Report Data

    Args:
        basic (BasicGroup): ADS-C Basic Group data
        flight_ident (FlightIdentGroup): ADS-C Flight Identification Group data
        earth_ref (EarthRefGroup | None, optional): ADS-C Earth Reference Group data
        meteo (MeteoGroup | None, optional): ADS-C Meteorological Group data
    """
    basic: BasicGroup
    flight_ident: FlightIdentGroup
    earth_ref: EarthRefGroup | None = None
    meteo: MeteoGroup | None = None