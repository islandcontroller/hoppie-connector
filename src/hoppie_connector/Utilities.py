import re

ICAO_AIRPORT_REGEX: str = r'[A-Z]{4}'
STATION_NAME_REGEX: str = r'[A-Z0-9]{3,8}'

def is_valid_airport_code(designator: str) -> bool:
    """Simple helper function to determine validity of a 4-letter ICAO airport designator.

    Args:
        designator (str): ICAO airport designator

    Returns:
        bool: Designator validity
    """
    return bool(re.match(r'^' + ICAO_AIRPORT_REGEX + r'$', designator))

def is_valid_station_name(name: str) -> bool:
    """Simple helper function to determine validity of a station name

    Args:
        name (str): Station name

    Returns:
        bool: Name validity
    """
    return bool(re.match(r'^' + STATION_NAME_REGEX + r'$', name))

def get_fixed_width_float_str(value: float, width: int) -> str:
    """Format floating-point value into fixed-width string

    Args:
        value (float): Floating-point value
        width (int): String field width
    """
    def _count_leading(x: float) -> int:
        n = 2 if x < 0.0 else 1
        while not (abs(x) < 10.0):
            n += 1
            x /= 10.0
        return n
    leading = _count_leading(value)
    if leading >= width:
        return f"{value:.1f}"
    else:
        return f"{value:{leading}.{width-leading-1}f}"