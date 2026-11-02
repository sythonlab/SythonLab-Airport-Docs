import io
from collections import defaultdict
from typing import List

from .normalize import short_date, short_date_without_year, keep_alphanumeric, number
from .entities import ContactInfo
from .entities import Pax
from .entities import Flight

# Longest line of a PNL / ADL: a longer remark goes on in `.RN/` lines
LINE_LIMIT = 64
CONTINUATION = '.RN/'


class PNL:
    """
    PNL (or ADL) of a flight: per destination and booked class, a name record per passenger
    (`1SURNAME/GIVEN NAMESTITLE`) followed by its booking locator (`.L/`), its tickets (`.R/TKNE`), its child / infant
    remarks (`.R/CHLD`, `.R/INFT`), its travel documents (`.R/DOCS`) and its services (`.R/XBAG`, `.R/AVIH`,
    `.R/PETC`, `.R/VGML`, `.R/WCHR`..., `.R/CKIN`). An infant has no name record of its own: its lines go in those of
    its adult. No value is required: a missing one leaves its place empty (`//`), a service not requested adds no line.
    """

    def __init__(self, contact_info: ContactInfo, pax_list: List[Pax], flight: Flight, line_limit: int = LINE_LIMIT,
                 is_adl: bool = False):
        self.prefix = ('PNL', 'ADL')[is_adl]
        self.lines = []
        self.contact_info = contact_info
        self.flight = flight
        self.pax_list = pax_list
        self.line_limit = line_limit
        self.is_adl = is_adl
        self.filename = f"{self.prefix}_{self.flight.flight_number}_{format(self.flight.local_departure_date, '%y%m%d')}_{self.flight.departure_airport_code}.txt"
        self.validate()

    def category(self, pax):
        return pax.get_category(self.flight.local_departure_date)

    def validate(self):
        infants = {id(pax.infant) for pax in self.pax_list if pax.infant}
        for pax in self.pax_list:
            if pax.infant and self.category(pax) == 'INF':
                raise ValueError(f'{pax} is an infant, it cannot travel with another infant')
            if pax.infant and self.category(pax.infant) != 'INF':
                raise ValueError(f'{pax.infant} is not an infant, it cannot travel with {pax}')
            if self.category(pax) == 'INF' and id(pax) not in infants:
                raise ValueError(f'The infant {pax} must travel with an adult of the list')

    @property
    def seated_pax(self):
        """The passengers with a name record: all but the infants, listed with their adults"""
        infants = {id(pax.infant) for pax in self.pax_list if pax.infant}
        return [pax for pax in self.pax_list if id(pax) not in infants]

    def generate(self):
        grouped = self.get_grouped()
        self.lines = [self.prefix]
        for part_number, (destination_code, pax_list) in enumerate(grouped.items(), start=1):
            self.lines += self.get_part(part_number, destination_code, pax_list, total_parts=len(grouped))
        if not grouped:
            # Nobody boards at this point (e.g. the stopover of a flight whose passengers all boarded before)
            self.lines += [self.get_flight_header(1), 'NIL']
        self.lines.append(f'END{self.prefix}')

    def get_part(self, part_number, destination_code, pax_list, *, total_parts=None):
        part = [] if part_number == 1 else ['']
        part.append(self.get_flight_header(part_number))

        # A destination line per booked class (-HAV002Y), followed by its passengers
        classes = defaultdict(list)
        for pax in pax_list:
            classes[pax.flight_class.code if pax.flight_class else ''].append(pax)
        for flight_class, class_pax in classes.items():
            part.append(f'-{destination_code}{str(len(class_pax)).zfill(3)}{flight_class}')
            for pax in class_pax:
                part += self.get_pax_lines(pax)

        if total_parts and total_parts > 1:
            part.append(f'ENDPART{part_number}')
        return part

    def get_flight_header(self, index):
        departure_date = short_date_without_year(self.flight.local_departure_date)
        return f'{self.flight.flight_number}/{departure_date} {self.flight.departure_airport_code} PART{index}'

    def get_pax_lines(self, pax):
        """The name record of a passenger and its lines (and those of its infant), in the order of the airline"""
        infant = pax.infant
        lines = [self.get_name_record(pax)]
        if pax.reservation_code:
            lines.append(f'.L/{pax.reservation_code}')
        lines += self.get_ticket_lines(pax)
        if infant:
            lines += self.get_ticket_lines(infant, prefix='INF')
            lines += self.split(f'.R/INFT HK1 {short_date(infant.birth_date)} {self.get_name(infant)}')
        elif self.category(pax) == 'CHD':
            lines.append(f'.R/CHLD HK1 {short_date(pax.birth_date)}')
        lines += self.get_doc_lines(pax)
        if infant:
            lines += self.get_doc_lines(infant)
        lines += self.get_service_lines(pax)
        return lines

    def get_service_lines(self, pax):
        """The services of a passenger, only those it has: hold baggage, pets, meal, assistance and check-in remark"""
        lines = []
        if pax.checked_bags:
            lines.append(f'.R/XBAG HK1 TTL {number(pax.checked_bags_weight)}KG {pax.checked_bags}PC')
        for pet in pax.pets:
            lines += self.split(f'.R/{pet.code} HK1 {self.get_pet_text(pet)}')
        if pax.vegetarian_meal:
            lines.append('.R/VGML HK1')
        for service, text in pax.special_services:
            lines += self.split(f'.R/{service.code} HK1 {keep_alphanumeric(text).upper()}'.rstrip())
        if pax.checkin_remark:
            lines += self.split(f'.R/CKIN {keep_alphanumeric(pax.checkin_remark).upper()}')
        return lines

    @staticmethod
    def get_pet_text(pet):
        """ANIMAL/LENGTHxWIDTHxHEIGHTCM WEIGHTKG/COMMENT, an empty place in the middle, none at the end"""
        sizes = [number(size) for size in (pet.length, pet.width, pet.height)]
        dimensions = f'{"X".join(sizes)}CM' if all(sizes) else ''
        weight = f'{number(pet.weight)}KG' if number(pet.weight) else ''
        # The empty places at the end are left out: no `/` closes the line
        text = f'{pet.animal_code}/{" ".join(filter(None, [dimensions, weight]))}/{keep_alphanumeric(pet.remark)}'
        return text.rstrip('/')

    @staticmethod
    def get_name(pax):
        """SURNAME/GIVEN NAMES: the surname without spaces, the given names as they are"""
        return f'{keep_alphanumeric(pax.last_name).replace(" ", "")}/{keep_alphanumeric(pax.given_names)}'

    def get_name_record(self, pax):
        return f'1{self.get_name(pax)}{keep_alphanumeric(pax.title)}'[:self.line_limit]

    @staticmethod
    def is_valid_ticket(ticket_number):
        """A ticket number is written as it is, unless it has fewer than 3 characters besides spaces and dots"""
        return len(ticket_number.replace(' ', '').replace('.', '')) >= 3

    def get_ticket_lines(self, pax, prefix=''):
        if not self.is_valid_ticket(pax.ticket_number):
            return []
        # A ticket number may already end in its coupon (.../2)
        coupon = '' if '/' in pax.ticket_number else f'/{pax.ticket_coupon}'
        return self.split(f'.R/TKNE HK1 {prefix}{pax.ticket_number}{coupon}')

    def get_doc_lines(self, pax):
        gender = (pax.gender.code if pax.gender else '') + ('I' if pax.gender and self.category(pax) == 'INF' else '')
        fields = [
            'HK1', pax.document_type.code if pax.document_type else '', pax.document_issuer_code, pax.document_number, pax.nationality_code,
            short_date(pax.birth_date), gender, short_date(pax.document_expiry_date),
            keep_alphanumeric(pax.last_name), keep_alphanumeric(pax.given_names),
        ]
        return self.split(f'.R/DOCS {"/".join(fields)}')

    def split(self, line):
        """A remark in lines of at most `line_limit` characters, the rest in `.RN/` continuation lines"""
        lines, line = [line[:self.line_limit]], line[self.line_limit:]
        size = self.line_limit - len(CONTINUATION)
        while line:
            lines.append(f'{CONTINUATION}{line[:size]}')
            line = line[size:]
        return lines

    def get_grouped(self):
        grouped = defaultdict(list)
        for pax in self.seated_pax:
            grouped[pax.destination_code].append(pax)
        return dict(grouped)

    def to_txt(self):
        return io.StringIO(self.get_content())

    def get_content(self):
        self.generate()
        return '\n'.join(self.lines)
