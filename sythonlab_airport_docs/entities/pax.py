import datetime
from typing import List, Optional, Tuple, Union

from .pet import Pet
from .special_service import SpecialService


def parse_date(value, label):
    """A YYYY-MM-DD date, None when missing (a missing value leaves its place empty in the documents)"""
    if not value or not str(value).strip():
        return None
    try:
        return datetime.datetime.strptime(str(value).strip(), '%Y-%m-%d')
    except ValueError:
        raise ValueError(f'{label} must be in format YYYY-MM-DD')


def clean(value):
    return str(value or '').strip().upper()


class Pax:
    """
    A passenger of the flight. No value is required: a missing one leaves its place empty in the documents (`//`).
    `reservation_code` is the booking locator; `ticket_number` / `ticket_coupon` its electronic ticket and the coupon of
    this flight in it (not added when the ticket number already ends in it, `.../2`); `title` (MR, MRS, MS...) is
    appended to its name record; `flight_class` the PNL code of its booked class (Y, C, F...).
    An infant travels on the lap of an adult: give it as the `infant` of that adult (and it still goes in the pax
    list, the API lists every passenger).
    Services of the PNL: `checked_bags` / `checked_bags_weight` (kg) its hold baggage (XBAG), `pets` (AVIH / PETC),
    `vegetarian_meal` (VGML), `special_services` its assistance services (WCHR, WCHS, WCHC, DPNA), each a SpecialService
    (or its value) or a (SpecialService, text) pair, and `checkin_remark` a note for the check-in staff (CKIN).
    """

    def __init__(self, first_name: str, second_name: Optional[str], last_name: str, gender: str, birth_date: str,
                 nationality_code: str, document_type: str, document_number: str, document_expiry_date: str,
                 document_issuer_code: str, flight_class: str, origin_code: str, destination_code: str,
                 reservation_code: str, ticket_number: str = '', ticket_coupon: int = 1, title: str = '',
                 infant: Optional['Pax'] = None, checked_bags: int = 0, checked_bags_weight: float = 0,
                 pets: Optional[List[Pet]] = None, vegetarian_meal: bool = False,
                 special_services: Optional[List[Union[SpecialService, str, Tuple[Union[SpecialService, str], str]]]] = None, checkin_remark: str = ''):
        self.first_name = clean(first_name)
        self.second_name = clean(second_name)
        self.last_name = clean(last_name)
        self.gender = clean(gender)
        self.reservation_code = clean(reservation_code)
        self.ticket_number = clean(ticket_number)
        self.ticket_coupon = ticket_coupon
        self.title = clean(title)
        self.infant = infant
        self.birth_date = parse_date(birth_date, 'Birth date')
        self.document_expiry_date = parse_date(document_expiry_date, 'Document expiry date')
        self.nationality_code = clean(nationality_code)
        self.document_type = clean(document_type)
        self.document_number = clean(document_number)
        self.document_issuer_code = clean(document_issuer_code)
        self.flight_class = clean(flight_class)
        self.origin_code = clean(origin_code)
        self.destination_code = clean(destination_code)
        self.checked_bags = checked_bags or 0
        self.checked_bags_weight = checked_bags_weight or 0
        self.pets = pets or []
        self.vegetarian_meal = bool(vegetarian_meal)
        # (SpecialService, text) of each service, without the empty ones
        self.special_services = [(SpecialService(service), (text or '').strip()) for service, text in (
            (item, '') if isinstance(item, str) else item for item in special_services or []) if service]
        self.checkin_remark = (checkin_remark or '').strip()

        self.validate()

    def validate(self):
        """Only the values given: a missing one is allowed"""
        if self.gender and self.gender not in ['M', 'F']:
            raise ValueError('Gender must be "M" or "F"')

        for label, code in (('Nationality code', self.nationality_code),
                            ('Document issuer country code', self.document_issuer_code),
                            ('Origin code', self.origin_code), ('Destination code', self.destination_code)):
            if code and len(code) != 3:
                raise ValueError(f'{label} must be 3 characters long')

    def __str__(self):
        return ' '.join(filter(None, [self.first_name, self.second_name, self.last_name]))

    @property
    def given_names(self):
        return ' '.join(filter(None, [self.first_name, self.second_name]))

    def get_age(self, date):
        if date and type(date) is str:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        if not date:
            date = datetime.datetime.now().date()
        return date.year - self.birth_date.year - (
                (date.month, date.day) < (self.birth_date.month, self.birth_date.day))

    def get_category(self, date):
        # Without a birth date the age is unknown: an adult
        if not self.birth_date:
            return 'ADU'
        age = self.get_age(date)
        if age < 2:
            return 'INF'
        if age < 12:
            return 'CHD'
        return 'ADU'
