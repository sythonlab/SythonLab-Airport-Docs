from enum import Enum


class CabinClass(str, Enum):
    """
    Cabin class of a passenger: the caller gives the class and the library writes its PNL letter. Its value is a plain
    word, so it can also be given as a string (`'economy'`).
    """
    ECONOMY = 'economy'  # Y
    PREMIUM_ECONOMY = 'premium_economy'  # W
    BUSINESS = 'business'  # C
    FIRST = 'first'  # F

    @property
    def code(self):
        return PNL_CODES[self]


PNL_CODES = {
    CabinClass.ECONOMY: 'Y',
    CabinClass.PREMIUM_ECONOMY: 'W',
    CabinClass.BUSINESS: 'C',
    CabinClass.FIRST: 'F',
}
