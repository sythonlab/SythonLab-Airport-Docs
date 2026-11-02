from dataclasses import dataclass
from typing import Optional

from .pet_animal import PetAnimal
from .pet_transport import PetTransport


@dataclass
class Pet:
    """
    A pet travelling with a passenger: how it travels (`transport_type`, a PetTransport), the kind of `animal` (a
    PetAnimal; for OTHER, the name of the animal in `animal_name`), its `weight` in kg and its `length` x `width` x
    `height` in cm, and an optional `comment`. Only the transport is required: a missing value leaves its place empty
    in the PNL.
    """
    transport_type: PetTransport
    animal: Optional[PetAnimal] = None
    animal_name: str = ''
    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    comment: str = ''

    def __post_init__(self):
        self.transport_type = PetTransport(self.transport_type)
        self.animal = PetAnimal(self.animal) if self.animal else None
        self.animal_name = (self.animal_name or '').strip().upper()
        self.comment = (self.comment or '').strip().upper()

    @property
    def code(self):
        return self.transport_type.code

    @property
    def animal_code(self):
        return self.animal.code if self.animal else ''

    @property
    def remark(self):
        """The comment, with the name of another animal before it"""
        name = self.animal_name if self.animal == PetAnimal.OTHER else ''
        return ' '.join(filter(None, [name, self.comment]))

    def __str__(self):
        return self.animal_code
