from enum import Enum


class FlightType(str, Enum):
    """Kind of flight. Its value is a plain word, so it can also be given as a string (`'charter'`)."""
    REGULAR = 'regular'
    CHARTER = 'charter'
