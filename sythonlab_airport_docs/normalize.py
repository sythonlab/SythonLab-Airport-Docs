import re
import unicodedata
import datetime


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def normalize_string(string: str, as_upper=False) -> str:
    string = unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore').decode('utf-8')

    if as_upper:
        return string.upper()
    return string


def short_date(date: datetime.date):
    """A date as the IATA messages write it: two-digit day, month and year (02FEB00); empty when missing"""
    return format(date, '%d%b%y').upper() if date else ''


def format_date(date: datetime.date, data_format: str):
    """A date in `data_format`, empty when missing"""
    return format(date, data_format) if date else ''


# Document type of the travel documents (DOCS / PAXLST): P passport, I identity card. Other names are mapped to these;
# a one-letter IATA code is kept as it is and any other value leaves the place empty.
DOCUMENT_TYPES = {
    'P': 'P', 'PP': 'P', 'PASSPORT': 'P',
    'I': 'I', 'ID': 'I', 'NI': 'I', 'DNI': 'I', 'IDENTITY CARD': 'I',
}


def document_type_code(document_type: str):
    value = (document_type or '').strip().upper()
    return DOCUMENT_TYPES.get(value, value if len(value) == 1 else '')


def number(value):
    """A quantity without a needless decimal part (20.0 -> 20, 20.5 -> 20.5); empty when missing"""
    if value in (None, ''):
        return ''
    value = float(value)
    return str(int(value)) if value.is_integer() else str(value)


def short_date_without_year(date: datetime.date, data_format: str = '%d%b'):
    return format(date, data_format).upper()


def keep_alphanumeric(input_string):
    """Only ASCII letters, digits and single spaces; accented letters lose the accent (PEÑA -> PENA), not the letter"""
    text = re.sub(r'[^a-zA-Z0-9 ]', '', normalize_string(input_string or ''))
    return ' '.join(text.split())
