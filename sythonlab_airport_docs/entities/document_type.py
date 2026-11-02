from enum import Enum


class DocumentType(str, Enum):
    """
    Kind of travel document of a passenger (DOCS / PAXLST): the caller gives it and the library writes its
    letter. Its value is a plain word, so it can also be given as a string (`'passport'`).
    """
    PASSPORT = 'passport'  # P
    IDENTITY_CARD = 'identity_card'  # I

    @property
    def code(self):
        return PNL_CODES[self]


PNL_CODES = {
    DocumentType.PASSPORT: 'P',
    DocumentType.IDENTITY_CARD: 'I',
}
