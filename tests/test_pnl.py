"""The PNL against the examples of the check-in specification (Amadeus Altéa). Run: python -m unittest discover tests"""
import unittest

from sythonlab_airport_docs.entities import ContactInfo, Flight, Pax, Pet
from sythonlab_airport_docs.pnl import PNL

CONTACT = ContactInfo('AGENCY', '1', 'a@b.c', 'AG')
FLIGHT = Flight('CP123', 'C', 'KIN', 'HAV', '2026-11-10', '2026-11-10', '10:00', '11:00', 'CP')


def pax(first, second, last, gender, birth, document, number, expiry, locator, ticket='', **kwargs):
    return Pax(first, second, last, gender, birth, 'CUB', document, number, expiry, 'CUB', kwargs.pop('cls', 'Y'),
               'KIN', 'HAV', locator, ticket, **kwargs)


def lines(*pax_list):
    return PNL(CONTACT, list(pax_list), FLIGHT).get_content().split('\n')


class PNLTest(unittest.TestCase):

    def test_adult_with_infant(self):
        infant = pax('DIAGO', 'MANUEL', 'ROJAS PENA', 'M', '2026-01-06', 'NI', '24031568106', '2036-04-12', 'A5DXEO',
                     '1362401119428')
        adult = pax('DAYANA', 'BEATRIZ', 'PENA PERDOMO', 'F', '2000-02-02', 'I', '00020279051', '2036-04-12',
                    'A5DXEO', '1362401119425', infant=infant)
        self.assertEqual(lines(adult, infant)[2:-1], [
            '-HAV001Y',
            '1PENAPERDOMO/DAYANA BEATRIZ',
            '.L/A5DXEO',
            '.R/TKNE HK1 1362401119425/1',
            '.R/TKNE HK1 INF1362401119428/1',
            '.R/INFT HK1 06JAN26 ROJASPENA/DIAGO MANUEL',
            '.R/DOCS HK1/I/CUB/00020279051/CUB/02FEB00/F/12APR36/PENA PERDOMO',
            '.RN//DAYANA BEATRIZ',
            '.R/DOCS HK1/I/CUB/24031568106/CUB/06JAN26/MI/12APR36/ROJAS PENA/',
            '.RN/DIAGO MANUEL',
        ])

    def test_services(self):
        entry = pax('CLARA', '', 'STEINEBACH', 'F', '2020-12-11', 'PASSPORT', 'C3JWXZGNT', '2030-01-14', 'YJI7NF',
                    '1362401116722', checked_bags=2, checked_bags_weight=46.0, vegetarian_meal=True,
                    special_services=['WCHR', 'DPNA'], checkin_remark='Pax carries baby stroller',
                    pets=[Pet('hold', 'dog', 20, 30, 25, 50, 'comentario'), Pet('cabin', 'cat')])
        self.assertEqual(lines(entry)[-11:-1], [
            '.R/CHLD HK1 11DEC20',
            '.R/DOCS HK1/P/CUB/C3JWXZGNT/CUB/11DEC20/F/14JAN30/STEINEBACH/CLA',
            '.RN/RA',
            '.R/XBAG HK1 TTL 46KG 2PC',
            '.R/AVIH HK1 DOG/30X25X50CM 20KG/COMENTARIO',
            '.R/PETC HK1 CAT//',
            '.R/VGML HK1',
            '.R/WCHR HK1',
            '.R/DPNA HK1',
            '.R/CKIN PAX CARRIES BABY STROLLER',
        ])

    def test_missing_values_leave_their_place_empty(self):
        entry = pax('SELENA', 'TALIA', 'NAPOLES PADILLA', 'F', '1990-01-11', '', '', '', 'XB2O5U', ' . ')
        content = lines(entry)
        self.assertIn('.R/DOCS HK1//CUB//CUB/11JAN90/F//NAPOLES PADILLA/SELENA TALIA', content)
        # Fewer than 3 characters besides spaces and dots: no ticket line
        self.assertFalse([line for line in content if 'TKNE' in line])

    def test_ticket_written_as_typed(self):
        entry = pax('REYLER', '', 'NAPOLES', 'M', '1991-01-09', 'P', 'X1', '2030-01-01', '123', '169.297 81', title='MR')
        content = lines(entry)
        self.assertIn('1NAPOLES/REYLERMR', content)
        self.assertIn('.R/TKNE HK1 169.297 81/1', content)
        self.assertIn('.L/123', content)

    def test_a_destination_line_per_class(self):
        economy = pax('A', '', 'ONE', 'M', '1990-01-01', 'P', 'X1', '2030-01-01', '1')
        business = pax('B', '', 'TWO', 'M', '1990-01-01', 'P', 'X2', '2030-01-01', '2', cls='C')
        content = lines(economy, business)
        self.assertEqual(content[1], 'CP123/10NOV KIN PART1')
        self.assertEqual([line for line in content if line.startswith('-HAV')], ['-HAV001Y', '-HAV001C'])


if __name__ == '__main__':
    unittest.main()
