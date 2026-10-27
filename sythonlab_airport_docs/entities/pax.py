import datetime
from typing import Optional


class Pax:
    """
    A passenger of the flight. `reservation_code` is the booking locator (PNR); `ticket_number` / `ticket_coupon` its
    electronic ticket and the coupon of this flight in it (not added when the ticket number already ends in it,
    `.../2`); `title` (MR, MRS, MS...) is appended to its name record.
    An infant travels on the lap of an adult: give it as the `infant` of that adult (and it still goes in the pax
    list, the API lists every passenger).
    """

    def __init__(self, first_name: str, second_name: Optional[str], last_name: str, gender: str, birth_date: str,
                 nationality_code: str, document_type: str, document_number: str, document_expiry_date: str,
                 document_issuer_code: str, flight_class: str, origin_code: str, destination_code: str,
                 reservation_code: str, ticket_number: str = '', ticket_coupon: int = 1, title: str = '',
                 infant: Optional['Pax'] = None):
        self.first_name = first_name.strip().upper()
        self.second_name = (second_name or '').strip().upper()
        self.last_name = last_name.strip().upper()
        self.gender = gender.strip().upper()
        self.reservation_code = reservation_code.strip().upper()
        self.ticket_number = (ticket_number or '').strip().upper()
        self.ticket_coupon = ticket_coupon
        self.title = (title or '').strip().upper()
        self.infant = infant

        try:
            self.birth_date = datetime.datetime.strptime(birth_date.strip(), '%Y-%m-%d')
        except ValueError:
            raise ValueError('Birth date must be in format YYYY-MM-DD')

        try:
            self.document_expiry_date = datetime.datetime.strptime(document_expiry_date.strip(), '%Y-%m-%d')
        except ValueError:
            raise ValueError('Document expiry date must be in format YYYY-MM-DD')

        self.nationality_code = nationality_code.strip().upper()
        self.document_type = document_type.strip().upper()
        self.document_number = document_number.strip().upper()
        self.document_issuer_code = document_issuer_code.strip().upper()
        self.flight_class = flight_class.strip().upper()
        self.origin_code = origin_code.strip().upper()
        self.destination_code = destination_code.strip().upper()

        self.validate()

    def validate(self):
        if self.gender not in ['M', 'F']:
            raise ValueError('Gender must be "M" or "F"')

        if len(self.nationality_code) != 3:
            raise ValueError('Nationality code must be 3 characters long')

        if len(self.document_issuer_code) != 3:
            raise ValueError('Document issuer country code must be 3 characters long')

        if len(self.origin_code) != 3:
            raise ValueError('Origin code country code must be 3 characters long')

        if len(self.destination_code) != 3:
            raise ValueError('Destination code country code must be 3 characters long')

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
        age = self.get_age(date)
        if age < 2:
            return 'INF'
        if age < 12:
            return 'CHD'
        return 'ADU'
