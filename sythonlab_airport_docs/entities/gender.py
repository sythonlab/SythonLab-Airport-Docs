from enum import Enum


class Gender(str, Enum):
    """
    Gender of a passenger: the caller gives it and the library writes its letter. Its value is a plain word, so
    it can also be given as a string (`'male'`).
    """
    MALE = 'male'  # M
    FEMALE = 'female'  # F

    @property
    def code(self):
        return PNL_CODES[self]


PNL_CODES = {
    Gender.MALE: 'M',
    Gender.FEMALE: 'F',
}
