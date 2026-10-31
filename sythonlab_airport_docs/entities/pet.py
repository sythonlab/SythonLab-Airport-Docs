from typing import Optional

# Code of the kinds of animal in the PNL: any other one is OTH
ANIMAL_CODES = {'DOG': 'DOG', 'CAT': 'CAT'}


class Pet:
    """
    A pet travelling with a passenger: `transport_type` 'cabin' (PETC) or 'hold' (AVIH), `animal` (dog, cat, or the
    animal it is: it goes as OTH, with its name before the comment), its `weight` in kg and its `length` x `width` x
    `height` in cm, and an optional `comment`. No value is required: a missing one leaves its place empty in the PNL.
    """

    def __init__(self, transport_type: str, animal: str = '', weight: Optional[float] = None,
                 length: Optional[float] = None, width: Optional[float] = None, height: Optional[float] = None,
                 comment: str = ''):
        self.transport_type = (transport_type or '').strip().lower()
        animal = (animal or '').strip().upper()
        self.animal = ANIMAL_CODES.get(animal, 'OTH') if animal else ''
        self.weight = weight
        self.length = length
        self.width = width
        self.height = height
        # The name of another animal goes before the comment ("other" alone has no name)
        name = animal if self.animal == 'OTH' and animal != 'OTHER' else ''
        self.comment = ' '.join(filter(None, [name, (comment or '').strip().upper()]))

    @property
    def code(self):
        return 'PETC' if self.transport_type == 'cabin' else 'AVIH'

    def __str__(self):
        return self.animal
