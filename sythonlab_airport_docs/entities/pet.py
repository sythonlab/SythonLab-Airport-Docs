from typing import Optional


class Pet:
    """
    A pet travelling with a passenger: `transport_type` 'cabin' (PETC) or 'hold' (AVIH), `animal` (DOG, CAT or the
    one it is), its `weight` in kg and its `length` x `width` x `height` in cm, and an optional `comment`. No value is
    required: a missing one leaves its place empty in the PNL.
    """

    def __init__(self, transport_type: str, animal: str = '', weight: Optional[float] = None,
                 length: Optional[float] = None, width: Optional[float] = None, height: Optional[float] = None,
                 comment: str = ''):
        self.transport_type = (transport_type or '').strip().lower()
        self.animal = (animal or '').strip().upper()
        self.weight = weight
        self.length = length
        self.width = width
        self.height = height
        self.comment = (comment or '').strip().upper()

    @property
    def code(self):
        return 'PETC' if self.transport_type == 'cabin' else 'AVIH'

    def __str__(self):
        return self.animal
