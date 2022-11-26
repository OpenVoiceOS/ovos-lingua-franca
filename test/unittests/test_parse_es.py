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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import unittest

from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.parse import (normalize, extract_numbers, extract_number,
                                 extract_datetime, yes_or_no)
from lingua_franca.lang.parse_es import extract_datetime_es, is_fractional_es
from lingua_franca.parse import get_gender, extract_datetime, extract_number, normalize, yes_or_no, extract_timespan
from lingua_franca.time import default_timezone, to_local, DAYS_IN_1_YEAR, DAYS_IN_1_MONTH, TimespanUnit


def setUpModule():
    load_language('es-es')
    set_default_lang('es')


def tearDownModule():
    unload_language('es')


class TestNormalize(unittest.TestCase):
    """
        Test cases for Spanish parsing
    """

    def test_articles_es(self):
        self.assertEqual(normalize("esta es la prueba", lang="es",
                                   remove_articles=True),
                         "esta es prueba")
        self.assertEqual(normalize("y otra prueba", lang="es",
                                   remove_articles=True),
                         "y otra prueba")

    def test_numbers_es(self):
        self.assertEqual(normalize("esto es un uno una", lang="es"),
                         "esto es 1 1 1")
        self.assertEqual(normalize("esto es dos tres prueba", lang="es"),
                         "esto es 2 3 prueba")
        self.assertEqual(normalize("esto es cuatro cinco seis prueba",
                                   lang="es"),
                         "esto es 4 5 6 prueba")
        self.assertEqual(normalize("siete más ocho más nueve", lang="es"),
                         "7 más 8 más 9")
        self.assertEqual(normalize("diez once doce trece catorce quince",
                                   lang="es"),
                         "10 11 12 13 14 15")
        self.assertEqual(normalize("dieciséis diecisiete", lang="es"),
                         "16 17")
        self.assertEqual(normalize("dieciocho diecinueve", lang="es"),
                         "18 19")
        self.assertEqual(normalize("veinte treinta cuarenta", lang="es"),
                         "20 30 40")
        self.assertEqual(normalize("treinta y dos caballos", lang="es"),
                         "32 caballos")
        self.assertEqual(normalize("cien caballos", lang="es"),
                         "100 caballos")
        self.assertEqual(normalize("ciento once caballos", lang="es"),
                         "111 caballos")
        self.assertEqual(normalize("había cuatrocientas una vacas",
                                   lang="es"),
                         "había 401 vacas")
        self.assertEqual(normalize("dos mil", lang="es"),
                         "2000")
        self.assertEqual(normalize("dos mil trescientas cuarenta y cinco",
                                   lang="es"),
                         "2345")
        self.assertEqual(normalize(
            "ciento veintitrés mil cuatrocientas cincuenta y seis",
            lang="es"),
            "123456")
        self.assertEqual(normalize(
            "quinientas veinticinco mil", lang="es"),
            "525000")
        self.assertEqual(normalize(
            "novecientos noventa y nueve mil novecientos noventa y nueve",
            lang="es"),
            "999999")

    def test_extract_number_es(self):
        self.assertEqual(sorted(extract_numbers(
            "1 7 cuatro catorce ocho 157", lang='es')), [1, 4, 7, 8, 14, 157])
        self.assertEqual(sorted(extract_numbers(
            "1 7 cuatro albuquerque naranja John Doe catorce ocho 157",
            lang='es')), [1, 4, 7, 8, 14, 157])
        self.assertEqual(extract_number("seis punto dos", lang='es'), 6.2)
        self.assertEqual(extract_number("seis punto Dos", lang='es'), 6.2)
        self.assertEqual(extract_number("seis coma dos", lang='es'), 6.2)
        self.assertEqual(extract_numbers("un medio", lang='es'), [0.5])
        self.assertEqual(extract_number("cuarto", lang='es'), 0.25)

        self.assertEqual(extract_number("2.0", lang='es'), 2.0)
        self.assertEqual(extract_number("1/4", lang='es'), 0.25)

        self.assertEqual(extract_number("dos y media", lang='es'), 2.5)
        self.assertEqual(extract_number(
            "catorce y milésima", lang='es'), 14.001)

        self.assertEqual(extract_number("dos punto cero dos", lang='es'), 2.02)

    def test_isFraction_es(self):
        self.assertEqual(is_fractional_es("vigésimo"), 1.0 / 20)
        self.assertEqual(is_fractional_es("vigésima"), 1.0 / 20)
        self.assertEqual(is_fractional_es("trigésimo"), 1.0 / 30)
        self.assertEqual(is_fractional_es("centésima"), 1.0 / 100)
        self.assertEqual(is_fractional_es("centésimo"), 1.0 / 100)
        self.assertEqual(is_fractional_es("milésima"), 1.0 / 1000)

    @unittest.skip("unwritten logic")
    def test_comma_fraction_logic_es(self):
        # Logic has not been written to parse "#,#" as "#.#"
        # English-style decimal numbers work because they just get float(str)ed
        self.assertEqual(extract_number("2,0", lang='es'), 2.0)


class TestDatetime_es(unittest.TestCase):

    def test_datetime_by_date_es(self):
        # test currentDate==None
        _now = datetime.now()
        relative_year = _now.year if (_now.month == 1 and _now.day < 11) else \
            (_now.year + 1)
        self.assertEqual(extract_datetime_es("11 ene", anchorDate=_now)[0],
                         datetime(relative_year, 1, 11))

        # test months
        self.assertEqual(extract_datetime(
            "11 ene", lang='es', anchorDate=datetime(1998, 1, 1))[0],
            datetime(1998, 1, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 feb", lang='es', anchorDate=datetime(1998, 2, 1))[0],
            datetime(1998, 2, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 mar", lang='es', anchorDate=datetime(1998, 3, 1))[0],
            datetime(1998, 3, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 abr", lang='es', anchorDate=datetime(1998, 4, 1))[0],
            datetime(1998, 4, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 may", lang='es', anchorDate=datetime(1998, 5, 1))[0],
            datetime(1998, 5, 11, tzinfo=default_timezone()))
        # there is an issue with the months of june through september (below)
        # hay un problema con las meses junio hasta septiembre (lea abajo)
        self.assertEqual(extract_datetime(
            "11 oct", lang='es', anchorDate=datetime(1998, 10, 1))[0],
            datetime(1998, 10, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 nov", lang='es', anchorDate=datetime(1998, 11, 1))[0],
            datetime(1998, 11, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 dic", lang='es', anchorDate=datetime(1998, 12, 1))[0],
            datetime(1998, 12, 11, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("", lang='es'), None)

    # TODO fix bug causing these tests to fail (MycroftAI/mycroft-core#2348)
    #         reparar error de traducción preveniendo las funciones abajo de
    #         retornar correctamente
    #         (escrito con disculpas por un Inglés hablante)
    #      further broken tests are below their respective working tests.
    @unittest.skip("currently processing these months incorrectly")
    def test_bugged_output_wastebasket(self):
        self.assertEqual(extract_datetime(
            "11 jun", lang='es', anchorDate=datetime(1998, 6, 1))[0],
            datetime(1998, 6, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 junio", lang='es', anchorDate=datetime(1998, 6, 1))[0],
            datetime(1998, 6, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 jul", lang='es', anchorDate=datetime(1998, 7, 1))[0],
            datetime(1998, 7, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 ago", lang='es', anchorDate=datetime(1998, 8, 1))[0],
            datetime(1998, 8, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 sep", lang='es', anchorDate=datetime(1998, 9, 1))[0],
            datetime(1998, 9, 11, tzinfo=default_timezone()))

        # It's also failing on years
        self.assertEqual(extract_datetime(
            "11 ago 1998", lang='es')[0],
                         datetime(1998, 8, 11, tzinfo=default_timezone()))

    def test_extract_datetime_relative(self):
        self.assertEqual(extract_datetime(
            "esta noche", anchorDate=datetime(1998, 1, 1),
            lang='es'), [datetime(1998, 1, 1, 21, 0, 0, tzinfo=default_timezone()), 'esta'])
        self.assertEqual(extract_datetime(
            "ayer noche", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 31, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "el noche anteayer", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 30, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "el noche ante ante ayer", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 29, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "mañana por la mañana", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1998, 1, 2, 8, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "ayer por la tarde", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 31, 15, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("hoy 2 de la mañana", lang='es',
                                          anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 2, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("hoy 2 de la tarde", lang='es',
                                          anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 14, tzinfo=default_timezone()))

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""
        self.assertEqual(extract_datetime('no hay tiempo', lang='es-es'), None)

    @unittest.skip("These phrases are not parsing correctly.")
    def test_extract_datetime_relative_failing(self):
        # parses as "morning" and returns 8:00 on anchorDate
        self.assertEqual(extract_datetime(
            "mañana", anchorDate=datetime(1998, 1, 1), lang='es')[0],
            datetime(1998, 1, 2))

        # unimplemented logic
        self.assertEqual(extract_datetime(
            "anoche", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 31, 21))
        self.assertEqual(extract_datetime(
            "anteanoche", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 30, 21))
        self.assertEqual(extract_datetime(
            "hace tres noches", anchorDate=datetime(1998, 1, 1),
            lang='es')[0], datetime(1997, 12, 29, 21))


class TestYesNo(unittest.TestCase):
    def test_yesno(self):

        def test_utt(text, expected):
            res = yes_or_no(text, lang="es-es")
            self.assertEqual(res, expected)

        test_utt("por supuesto", True)
        test_utt("no", False)
        test_utt("sí", True)
        test_utt("jajajaja", None)
        test_utt("por favor", True)
        test_utt("por favor no", False)


class TestExtractTimeSpan(unittest.TestCase):
    def test_extract_timespan(self):
        self.assertEqual(extract_timespan("10 segundos"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_timespan("5 minutos"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_timespan("2 horas"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_timespan("3 dias"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_timespan("25 semanas"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_timespan("7.5 segundos"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_timespan(" 30 minutos"),
                         (timedelta(minutes=30), ""))
        self.assertEqual(extract_timespan("10-segundos"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_timespan("5-minutos"),
                         (timedelta(minutes=5), ""))

    def test_extract_timespan_delta(self):
        self.assertEqual(
            extract_timespan("10 segundos",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(seconds=10.0), ""))
        self.assertEqual(

            extract_timespan("5 minutos",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(minutes=5), ""))
        self.assertEqual(
            extract_timespan("2 horas",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(hours=2), ""))
        self.assertEqual(
            extract_timespan("3 dias",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(days=3), ""))
        self.assertEqual(
            extract_timespan("25 semanas",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(weeks=25), ""))
        self.assertEqual(
            extract_timespan("7.5 segundos",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(seconds=7.5), ""))
        self.assertEqual(
            extract_timespan(" 30 minutos",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(minutes=30), ""))
        self.assertEqual(
            extract_timespan("10-segundos",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(seconds=10.0), ""))
        self.assertEqual(
            extract_timespan("5-minutos",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(minutes=5), ""))

    def test_extract_timespan_microsegundos(self):
        def test_microsegundos(duration_str, expected_duration,
                              expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_MICROSECONDS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_microsegundos("0.01 microsegundos", 0, "")
        test_microsegundos("1 microsegundo", 1, "")
        test_microsegundos("5 microsegundos", 5, "")
        test_microsegundos("1 milisegundo", 1 * 1000, "")
        test_microsegundos("5 milisegundos", 5 * 1000, "")
        test_microsegundos("100 milisegundos", 100 * 1000, "")
        test_microsegundos("1 segundo", 1000 * 1000, "")
        test_microsegundos("10 segundos", 10 * 1000 * 1000, "")
        test_microsegundos("5 minutos", 5 * 60 * 1000 * 1000, "")
        test_microsegundos("2 horas", 2 * 60 * 60 * 1000 * 1000, "")
        test_microsegundos("3 dias", 3 * 24 * 60 * 60 * 1000 * 1000, "")
        test_microsegundos("25 semanas", 25 * 7 * 24 * 60 * 60 * 1000 * 1000, "")
        test_microsegundos("7.5 segundos", 7.5 * 1000 * 1000, "")
        test_microsegundos(" 30 minutos", 30 * 60 * 1000 * 1000,
                          "")
        test_microsegundos("10-segundos", 10 * 1000 * 1000, "")
        test_microsegundos("5-minutos", 5 * 60 * 1000 * 1000, "")

    def test_extract_timespan_milisegundos(self):
        def test_milisegundos(duration_str, expected_duration,
                              expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_MILLISECONDS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_milisegundos("1 microsegundo", 0.001, "")
        test_milisegundos("4.9 microsegundos", 0.005, "")
        test_milisegundos("5 microsegundos", 0.005, "")
        test_milisegundos("1 milisegundo", 1, "")
        test_milisegundos("5 milisegundos", 5, "")
        test_milisegundos("100 milisegundos", 100, "")
        test_milisegundos("1 segundo", 1000, "")
        test_milisegundos("10 segundos", 10 * 1000, "")
        test_milisegundos("5 minutos", 5 * 60 * 1000, "")
        test_milisegundos("2 horas", 2 * 60 * 60 * 1000, "")
        test_milisegundos("3 dias", 3 * 24 * 60 * 60 * 1000, "")
        test_milisegundos("25 semanas", 25 * 7 * 24 * 60 * 60 * 1000, "")
        test_milisegundos("7.5 segundos", 7.5 * 1000, "")
        test_milisegundos(" 30 minutos", 30 * 60 * 1000,
                          "")
        test_milisegundos("10-segundos", 10 * 1000, "")
        test_milisegundos("5-minutos", 5 * 60 * 1000, "")

    def test_extract_timespan_segundos(self):
        def test_segundos(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_SECONDS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_segundos("1 milisegundo", 0, "")
        test_segundos("4 milisegundos", 0, "")
        test_segundos("5 milisegundos", 0.005, "")
        test_segundos("100 milisegundos", 0.1, "")
        test_segundos("10 segundos", 10, "")
        test_segundos("5 minutos", 5 * 60, "")
        test_segundos("2 horas", 2 * 60 * 60, "")
        test_segundos("3 dias", 3 * 24 * 60 * 60, "")
        test_segundos("25 semanas", 25 * 7 * 24 * 60 * 60, "")
        test_segundos("7.5 segundos", 7.5, "")
        test_segundos(" 30 minutos", 30 * 60, "")
        test_segundos("10-segundos", 10, "")
        test_segundos("5-minutos", 5 * 60, "")

    def test_extract_timespan_minutos(self):
        def test_minutos(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_MINUTES)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_minutos("10 segundos", 10 / 60, "")
        test_minutos("5 minutos", 5, "")
        test_minutos("2 horas", 2 * 60, "")
        test_minutos("3 dias", 3 * 24 * 60, "")
        test_minutos("25 semanas", 25 * 7 * 24 * 60, "")
        test_minutos("7.5 segundos", 7.5 / 60, "")
        test_minutos(" 30 minutos", 30, "")
        test_minutos("10-segundos", 10 / 60, "")
        test_minutos("5-minutos", 5, "")

    def test_extract_timespan_horas(self):
        def test_horas(duration_str, expected_duration,
                       expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_HOURS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_horas("10 segundos", 0, "")
        test_horas("17.9 segundos", 0, "")
        test_horas("5 minutos", 5 / 60, "")
        test_horas("2 horas", 2, "")
        test_horas("3 dias", 3 * 24, "")
        test_horas("25 semanas", 25 * 7 * 24, "")
        test_horas("7.5 segundos", 0, "")
        test_horas(" 30 minutos", 30 / 60, "")
        test_horas("10-segundos", 0, "")
        test_horas("5-minutos", 5 / 60, "")

    def test_extract_timespan_dias(self):
        def test_dias(duration_str, expected_duration,
                      expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_DAYS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_dias("10 segundos", 0, "")
        test_dias("5 minutos", 0, "")
        test_dias("7.1 minutos", 0, "")
        test_dias("2 horas", 2 / 24, "")
        test_dias("3 dias", 3, "")
        test_dias("25 semanas", 25 * 7, "")
        test_dias("7.5 segundos", 0, "")
        test_dias(" 30 minutos", 30 / 60 / 24,
                  "")
        test_dias("10-segundos", 0, "")
        test_dias("5-minutos", 0, "")

    def test_extract_timespan_semanas(self):
        def test_semanas(duration_str, expected_duration,
                       expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_WEEKS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_semanas("10 segundos", 0, "")
        test_semanas("5 minutos", 0, "")
        test_semanas("50 minutos", 0, "")
        test_semanas("2 horas", 2 / 24 / 7, "")
        test_semanas("3 dias", 3 / 7, "")
        test_semanas("25 semanas", 25, "")
        test_semanas("7.5 segundos", 7.5 / 60 / 60 / 24 / 7, "")
        test_semanas(" 30 minutos", 0, "")
        test_semanas("10-segundos", 0, "")
        test_semanas("5-minutos", 0, "")

    def test_extract_timespan_months(self):
        def test_months(duration_str, expected_duration,
                        expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_MONTHS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_months("10 segundos", 0, "")
        test_months("5 minutos", 0, "")
        test_months("2 horas", 0, "")
        test_months("3 dias",
                    3 / DAYS_IN_1_MONTH, "")
        test_months("25 semanas",
                    25 * 7 / DAYS_IN_1_MONTH, "")
        test_months("7.5 segundos", 0, "")
        test_months(" 30 minutos", 0, "")
        test_months("10-segundos", 0, "")
        test_months("5-minutos", 0, "")

    def test_extract_timespan_years(self):
        def test_years(duration_str, expected_duration,
                       expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_YEARS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_years("10 segundos", 0, "")
        test_years("5 minutos", 0, "")
        test_years("2 horas", 0, "")
        test_years("1.5 dias", 0, "")
        test_years("3 dias", 3 / DAYS_IN_1_YEAR, "")
        test_years("25 semanas", 25 * 7 / DAYS_IN_1_YEAR, "")
        test_years("7.5 segundos", 0, "")
        test_years(" 30 minutos", 0, "")
        test_years("10-segundos", 0, "")
        test_years("5-minutos", 0, "")

    def test_extract_timespan_decades(self):
        def test_decades(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_DECADES)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_decades("10 segundos", 0, "")
        test_decades("5 minutos", 0, "")
        test_decades("2 horas", 0, "")
        test_decades("3 dias", 0, "")
        test_decades("25 semanas", 25 * 7 / DAYS_IN_1_YEAR / 10, "")
        test_decades("7.5 segundos", 0, "")
        test_decades(" 30 minutos", 0, "")
        test_decades("10-segundos", 0, "")
        test_decades("5-minutos", 0, "")

    def test_extract_timespan_centuries(self):
        def test_centuries(duration_str, expected_duration,
                           expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_CENTURIES)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_centuries("10 segundos", 0, "")
        test_centuries("5 minutos", 0, "")
        test_centuries("2 horas", 0, "")
        test_centuries("3 dias", 0, "")
        test_centuries("25 semanas", 0, "")
        test_centuries("7.5 segundos", 0, "")
        test_centuries(" 30 minutos", 0, "")
        test_centuries("10-segundos", 0, "")
        test_centuries("5-minutos", 0, "")

    def test_extract_timespan_millennia(self):
        def test_millennium(duration_str, expected_duration,
                            expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_MILLENNIUMS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_millennium("10 segundos", 0, "")
        test_millennium("5 minutos", 0, "")
        test_millennium("2 horas", 0, "")
        test_millennium("3 dias", 0, "")
        test_millennium("25 semanas", 0, "")
        test_millennium("7.5 segundos", 0, "")
        test_millennium(" 30 minutos", 0, "")
        test_millennium("10-segundos", 0, "")
        test_millennium("5-minutos", 0, "")


if __name__ == "__main__":
    unittest.main()
