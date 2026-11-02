from enum import Enum


class SpecialService(str, Enum):
    """
    Assistance services of a passenger: the caller gives the service and the library writes its PNL code. Its value is
    a plain word, so it can also be given as a string (`'wheelchair_ramp'`).
    """
    WHEELCHAIR_RAMP = 'wheelchair_ramp'  # WCHR: wheelchair to the aircraft, can climb stairs
    WHEELCHAIR_STEPS = 'wheelchair_steps'  # WCHS: wheelchair, cannot climb stairs
    WHEELCHAIR_CABIN = 'wheelchair_cabin'  # WCHC: wheelchair to the seat
    UNACCOMPANIED_DISABLED = 'unaccompanied_disabled'  # DPNA: special assistance

    @property
    def code(self):
        return PNL_CODES[self]


PNL_CODES = {
    SpecialService.WHEELCHAIR_RAMP: 'WCHR',
    SpecialService.WHEELCHAIR_STEPS: 'WCHS',
    SpecialService.WHEELCHAIR_CABIN: 'WCHC',
    SpecialService.UNACCOMPANIED_DISABLED: 'DPNA',
}
