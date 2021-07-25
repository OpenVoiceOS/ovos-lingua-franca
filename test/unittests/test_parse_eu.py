#
# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import unittest
from datetime import datetime

from lingua_franca.internal import load_language, set_default_lang, unload_language
from lingua_franca.lang.parse_eu import extract_datetime_eu, isFractional_eu
from lingua_franca.parse import (normalize, extract_numbers, extract_number,
                                 extract_datetime)
from lingua_franca.time import now_local, default_timezone


def setUpModule():
    load_language('eu')
    set_default_lang('eu')


def tearDownModule():
    unload_language('eu')


class TestNormalize(unittest.TestCase):
    """
        Test cases for Euskara parsing
    """

    # TODO: Hau ez dakit behar dugun
    def test_articles_eu(self):
        self.assertEqual(normalize("hau da froga", lang="eu",
                                   remove_articles=True),
                         "hau da froga")
        self.assertEqual(normalize("eta hau beste froga", lang="eu",
                                   remove_articles=True),
                         "eta hau beste froga")

    def test_numbers_eu(self):
        self.assertEqual(normalize("hau da bat", lang="eu"),
                         "hau da 1")
        self.assertEqual(normalize("hau da bi hiru froga", lang="eu"),
                         "hau da 2 3 froga")
        self.assertEqual(normalize("hau da lau bost sei froga",
                                   lang="eu"),
                         "hau da 4 5 6 froga")
        self.assertEqual(normalize("zazpi gehi zortzi gehi bederatzi", lang="eu"),
                         "7 gehi 8 gehi 9")
        self.assertEqual(normalize("hamar hamaika hamabi hamahiru hamalau hamabost",
                                   lang="eu"),
                         "10 11 12 13 14 15")
        self.assertEqual(normalize("hamasei hamazazpi", lang="eu"),
                         "16 17")
        self.assertEqual(normalize("hemezortzi hemeretzi", lang="eu"),
                         "18 19")
        self.assertEqual(normalize("hogei hogeita hamar berrogeita bat", lang="eu"),
                         "20 30 41")
        self.assertEqual(normalize("hogeita hamabi zaldi", lang="eu"),
                         "32 zaldi")
        self.assertEqual(normalize("ehun zaldi", lang="eu"),
                         "100 zaldi")
        self.assertEqual(normalize("ehun eta hamaika zaldi", lang="eu"),
                         "111 zaldi")
        self.assertEqual(normalize("laurehun eta bat behi zeuden",
                                   lang="eu"),
                         "401 behi zeuden")
        self.assertEqual(normalize("bi mila", lang="eu"),
                         "2000")
        self.assertEqual(normalize("bi mila hirurehun eta berrogeita bost",
                                   lang="eu"),
                         "2345")
        self.assertEqual(normalize(
            "ehun eta hogeita hiru mila laurehun eta berrogeita hamasei",
            lang="eu"),
            "123456")
        self.assertEqual(normalize(
            "bostehun eta hogeita bost mila", lang="eu"),
            "525000")
        self.assertEqual(normalize(
            "bederatzirehun eta laurogeita hemeretzi mila bederatzirehun eta laurogeita hemeretzi",
            lang="eu"),
            "999999")

    def test_extract_number_eu(self):
        self.assertEqual(sorted(extract_numbers(
            "1 7 lau hamalau zortzi 157", lang='eu')), [1, 4, 7, 8, 14, 157])
        self.assertEqual(sorted(extract_numbers(
            "1 7 lau albuquerque laranja John Doe hamalau zortzi 157",
            lang='eu')), [1, 4, 7, 8, 14, 157])
        self.assertEqual(extract_number("sei puntu bi", lang='eu'), 6.2)
        self.assertEqual(extract_number("sei puntu Bi", lang='eu'), 6.2)
        self.assertEqual(extract_number("sei koma bi", lang='eu'), 6.2)
        self.assertEqual(extract_numbers("erdi bat", lang='eu'), [0.5])
        self.assertEqual(extract_number("laurdena", lang='eu'), 0.25)

        self.assertEqual(extract_number("2.0", lang='eu'), 2.0)
        self.assertEqual(extract_number("1/4", lang='eu'), 0.25)

        self.assertEqual(extract_number("bi eta erdi", lang='eu'), 2.5)
        self.assertEqual(extract_number(
            "hamalau eta milarena", lang='eu'), 14.001)

        self.assertEqual(extract_number("bi puntu zero bi", lang='eu'), 2.02)

    def test_isFraction_eu(self):
        self.assertEqual(isFractional_eu("hogeirena"), 1.0 / 20)
        self.assertEqual(isFractional_eu("hogeita hamarrena"), 1.0 / 30)
        self.assertEqual(isFractional_eu("ehunena"), 1.0 / 100)
        self.assertEqual(isFractional_eu("milarena"), 1.0 / 1000)

    @unittest.skip("unwritten logic")
    def test_comma_fraction_logic_eu(self):
        # Logic has not been written to parse "#,#" as "#.#"
        # English-style decimal numbers work because they just get float(str)ed
        self.assertEqual(extract_number("2,0", lang='eu'), 2.0)


class TestDatetime_eu(unittest.TestCase):

    def test_datetime_by_date_eu(self):
        # test currentDate==None
        _now = now_local()
        relative_year = _now.year if (_now.month == 1 and _now.day < 11) else \
            (_now.year + 1)
        self.assertEqual(extract_datetime_eu("11 urt")[0],
                         datetime(relative_year, 1, 11))

        # test months
        self.assertEqual(extract_datetime(
            "11 urt", lang='eu', anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 ots", lang='eu', anchorDate=datetime(1998, 2, 1))[0],
                         datetime(1998, 2, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 mar", lang='eu', anchorDate=datetime(1998, 3, 1))[0],
                         datetime(1998, 3, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 api", lang='eu', anchorDate=datetime(1998, 4, 1))[0],
                         datetime(1998, 4, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 mai", lang='eu', anchorDate=datetime(1998, 5, 1))[0],
                         datetime(1998, 5, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 eka", lang='eu', anchorDate=datetime(1998, 6, 1))[0],
                         datetime(1998, 6, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 ekaina", lang='eu', anchorDate=datetime(1998, 6, 1))[0],
                         datetime(1998, 6, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 uztaila", lang='eu', anchorDate=datetime(1998, 7, 1))[0],
                         datetime(1998, 7, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 abu", lang='eu', anchorDate=datetime(1998, 8, 1))[0],
                         datetime(1998, 8, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 ira", lang='eu', anchorDate=datetime(1998, 9, 1))[0],
                         datetime(1998, 9, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 urr", lang='eu', anchorDate=datetime(1998, 10, 1))[0],
                         datetime(1998, 10, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 aza", lang='eu', anchorDate=datetime(1998, 11, 1))[0],
                         datetime(1998, 11, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 abe", lang='eu', anchorDate=datetime(1998, 12, 1))[0],
                         datetime(1998, 12, 11, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("", lang='eu'), None)

    # TODO fix bug causing these tests to fail (MycroftAI/mycroft-core#2348)
    #         reparar error de traducción preveniendo las funciones abajo de
    #         retornar correctamente
    #         (escrito con disculpas por un Inglés hablante)
    #      further broken tests are below their respective working tests.
    @unittest.skip("currently processing these months incorrectly")
    def test_bugged_output_wastebasket(self):
        # It's failing on years
        self.assertEqual(extract_datetime("11 abu 1998", lang='eu')[0],
                         datetime(1998, 8, 11, tzinfo=default_timezone()))

    def test_extract_datetime_relative(self):
        self.assertEqual(extract_datetime("gaurko gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu'), [datetime(1998, 1, 1, 21, 0, 0, tzinfo=default_timezone()), ''])
        self.assertEqual(extract_datetime("gau honetan", anchorDate=datetime(1998, 1, 1),
                                          lang='eu'),
                         [datetime(1998, 1, 1, 21, 0, 0, tzinfo=default_timezone()), 'honetan'])
        self.assertEqual(extract_datetime("atzoko gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 31, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("herenegungo gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 30, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("duela 3 eguneko gaua", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 29, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("biharko goiza", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1998, 1, 2, 8, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("atzoko arratsaldea", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 31, 15, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("duela 2 egun", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 30, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("gaurko goizeko 2", lang='eu', anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 2, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("gaurko arratsaldeko 2", lang='eu', anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 14, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("datorren urtea", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1999, 1, 1, tzinfo=default_timezone()))

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""
        self.assertEqual(extract_datetime('ez dago denborarik', lang='eu-eu'), None)

    @unittest.skip("These phrases are not parsing correctly.")
    def test_extract_datetime_relative_failing(self):
        self.assertEqual(extract_datetime("bart", anchorDate=datetime(1998, 1, 1),
                                          lang='eu')[0], datetime(1997, 12, 31, 21, tzinfo=default_timezone()))


if __name__ == "__main__":
    unittest.main()
