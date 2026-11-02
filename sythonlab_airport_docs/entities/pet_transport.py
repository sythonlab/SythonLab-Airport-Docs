from enum import Enum


class PetTransport(str, Enum):
    """
    How a pet travels: the caller gives it and the library writes its PNL code. Its value is a plain word, so it
    can also be given as a string (`'cabin'`).
    """
    CABIN = 'cabin'  # PETC: in the cabin
    HOLD = 'hold'  # AVIH: in the cargo hold

    @property
    def code(self):
        return PNL_CODES[self]


PNL_CODES = {
    PetTransport.CABIN: 'PETC',
    PetTransport.HOLD: 'AVIH',
}
