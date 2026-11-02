from enum import Enum


class PetAnimal(str, Enum):
    """
    Kind of animal of a pet: the caller gives it and the library writes its PNL code. Its value is a plain word,
    so it can also be given as a string (`'dog'`).
    """
    DOG = 'dog'  # DOG
    CAT = 'cat'  # CAT
    OTHER = 'other'  # OTH: any other animal, named in Pet.animal_name

    @property
    def code(self):
        return PNL_CODES[self]


PNL_CODES = {
    PetAnimal.DOG: 'DOG',
    PetAnimal.CAT: 'CAT',
    PetAnimal.OTHER: 'OTH',
}
