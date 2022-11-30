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
from datetime import datetime, time, timedelta

from dateutil.relativedelta import relativedelta
from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration, extract_timespan
from lingua_franca.parse import extract_number
from lingua_franca.parse import normalize
from lingua_franca.time import DAYS_IN_1_YEAR, DAYS_IN_1_MONTH, TimespanUnit


def setUpModule():
    load_language("de-de")
    set_default_lang("de")


def tearDownModule():
    unload_language("de")


class TestNormalize(unittest.TestCase):
    def test_articles(self):
        self.assertEqual(
            normalize("dies ist der test", lang="de-de", remove_articles=True),
            "dies ist test")
        self.assertEqual(
            normalize("und noch ein Test", lang="de-de", remove_articles=True),
            "und noch ein Test")
        self.assertEqual(normalize("dies ist der Extra-Test", lang="de-de",
                                   remove_articles=False),
                         "dies ist der Extra-Test")

    def test_spaces(self):
        self.assertEqual(normalize("  dies   ist  ein    test", lang="de-de"),
                         "dies ist ein test")
        self.assertEqual(normalize("  dies   ist  ein    test  ",
                                   lang="de-de"), "dies ist ein test")

    def test_numbers(self):
        self.assertEqual(
            normalize("dies ist eins zwei drei test", lang="de-de"),
            "dies ist 1 2 3 test")
        self.assertEqual(
            normalize("es ist vier fünf sechs test", lang="de-de"),
            "es ist 4 5 6 test")
        self.assertEqual(
            normalize("es ist sieben acht neun test", lang="de-de"),
            "es ist 7 8 9 test")
        self.assertEqual(
            normalize("es ist sieben acht neun test", lang="de-de"),
            "es ist 7 8 9 test")
        self.assertEqual(
            normalize("dies ist zehn elf zwölf test", lang="de-de"),
            "dies ist 10 11 12 test")
        self.assertEqual(
            normalize("dies ist dreizehn vierzehn test", lang="de-de"),
            "dies ist 13 14 test")
        self.assertEqual(
            normalize("dies ist fünfzehn sechzehn siebzehn", lang="de-de"),
            "dies ist 15 16 17")
        self.assertEqual(
            normalize("dies ist achtzehn neunzehn zwanzig", lang="de-de"),
            "dies ist 18 19 20")

class TestExtractNumber(unittest.TestCase):
    def test_extract_number(self):
        self.assertEqual(extract_number("dies ist der 1. Test",
                                        lang="de-de"), 1)
        self.assertEqual(extract_number("dies ist der erste Test",
                                        lang="de-de"), 1)
        self.assertEqual(extract_number("dies ist 2 Test", lang="de-de"), 2)
        self.assertEqual(extract_number("dies ist zweiter Test", lang="de-de"),
                         2)
        self.assertEqual(
            extract_number("dies ist der dritte Test", lang="de-de"), 3)
        self.assertEqual(
            extract_number("dies ist der Test Nummer 4", lang="de-de"), 4)
        self.assertEqual(extract_number("ein drittel einer Tasse",
                                        lang="de-de"), 1.0 / 3.0)
        self.assertEqual(extract_number("drei Tassen", lang="de-de"), 3)
        self.assertEqual(extract_number("1/3 Tasse", lang="de-de"), 1.0 / 3.0)
        self.assertEqual(extract_number("eine viertel Tasse", lang="de-de"),
                         0.25)
        self.assertEqual(extract_number("1/4 Tasse", lang="de-de"), 0.25)
        self.assertEqual(extract_number("viertel Tasse", lang="de-de"), 0.25)
        self.assertEqual(extract_number("2/3 Tasse", lang="de-de"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 Tasse", lang="de-de"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 und 3/4 Tassen", lang="de-de"),
                         1.75)
        self.assertEqual(extract_number("1 Tasse und eine halbe",
                                        lang="de-de"), 1.5)
        self.assertEqual(
            extract_number("eine Tasse und eine halbe", lang="de-de"), 1.5)
        self.assertEqual(
            extract_number("eine und eine halbe Tasse", lang="de-de"), 1.5)
        self.assertEqual(extract_number("ein und ein halb Tassen",
                                        lang="de-de"), 1.5)
        self.assertEqual(extract_number("drei Viertel Tasse", lang="de-de"),
                         3.0 / 4.0)
        self.assertEqual(extract_number("drei Viertel Tassen", lang="de-de"),
                         3.0 / 4.0)
        self.assertEqual(extract_number("Drei Viertel Tassen", lang="de-de"),
                         3.0 / 4.0)

class TestExtractDateTime(unittest.TestCase):
    def test_extractdatetime_de(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0)
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang="de-de", )
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract("setze den frisörtermin auf 5 tage von heute",
                    "2017-07-02 00:00:00", "setze frisörtermin")
        testExtract("wie ist das wetter übermorgen?",
                    "2017-06-29 00:00:00", "wie ist das wetter")
        testExtract("erinnere mich um 10:45 abends",
                    "2017-06-27 22:45:00", "erinnere mich")
        testExtract("was ist das Wetter am freitag morgen",
                    "2017-06-30 08:00:00", "was ist das wetter")
        testExtract("wie ist das wetter morgen",
                    "2017-06-28 00:00:00", "wie ist das wetter")
        testExtract(
            "erinnere mich meine mutter anzurufen in 8 Wochen und 2 Tagen",
            "2017-08-24 00:00:00", "erinnere mich meine mutter anzurufen")
        testExtract("spiele rick astley musik 2 tage von freitag",
                    "2017-07-02 00:00:00", "spiele rick astley musik")
        testExtract("starte die invasion um 3:45 pm am Donnerstag",
                    "2017-06-29 15:45:00", "starte die invasion")
        testExtract("am montag bestelle kuchen von der bäckerei",
                    "2017-07-03 00:00:00", "bestelle kuchen von bäckerei")
        testExtract("spiele happy birthday musik 5 jahre von heute",
                    "2022-06-27 00:00:00", "spiele happy birthday musik")
        testExtract("skype mama um 12:45 pm nächsten Donnerstag",
                    "2017-07-06 12:45:00", "skype mama")
        testExtract("wie ist das wetter nächsten donnerstag?",
                    "2017-07-06 00:00:00", "wie ist das wetter")
        testExtract("wie ist das Wetter nächsten Freitag morgen",
                    "2017-07-07 08:00:00", "wie ist das wetter")
        testExtract("wie ist das wetter nächsten freitag abend",
                    "2017-07-07 19:00:00", "wie ist das wetter")
        testExtract("wie ist das wetter nächsten freitag nachmittag",
                    "2017-07-07 15:00:00", "wie ist das wetter")
        testExtract("erinnere mich mama anzurufen am dritten august",
                    "2017-08-03 00:00:00", "erinnere mich mama anzurufen")
        testExtract("kaufe feuerwerk am einundzwanzigsten juli",
                    "2017-07-21 00:00:00", "kaufe feuerwerk")
        testExtract("wie ist das wetter 2 wochen ab nächsten freitag",
                    "2017-07-21 00:00:00", "wie ist das wetter")
        testExtract("wie ist das wetter am mittwoch um 07:00",
                    "2017-06-28 07:00:00", "wie ist das wetter")
        testExtract("wie ist das wetter am mittwoch um 7 uhr",
                    "2017-06-28 07:00:00", "wie ist das wetter")
        testExtract("Mache einen Termin um 12:45 pm nächsten donnerstag",
                    "2017-07-06 12:45:00", "mache einen termin")
        testExtract("wie ist das wetter an diesem donnerstag?",
                    "2017-06-29 00:00:00", "wie ist das wetter")
        testExtract("vereinbare den besuch für 2 wochen und 6 tage ab samstag",
                    "2017-07-21 00:00:00", "vereinbare besuch")
        testExtract("beginne die invasion um 03:45 am donnerstag",
                    "2017-06-29 03:45:00", "beginne die invasion")
        testExtract("beginne die invasion um 3 uhr nachts am donnerstag",
                    "2017-06-29 03:00:00", "beginne die invasion")
        testExtract("beginne die invasion um 8 Uhr am donnerstag",
                    "2017-06-29 08:00:00", "beginne die invasion")
        testExtract("starte die party um 8 uhr abends am donnerstag",
                    "2017-06-29 20:00:00", "starte die party")
        testExtract("starte die invasion um 8 abends am donnerstag",
                    "2017-06-29 20:00:00", "starte die invasion")
        testExtract("starte die invasion am donnerstag um mittag",
                    "2017-06-29 12:00:00", "starte die invasion")
        testExtract("starte die invasion am donnerstag um mitternacht",
                    "2017-06-29 00:00:00", "starte die invasion")
        testExtract("starte die invasion am donnerstag um 5 uhr",
                    "2017-06-29 05:00:00", "starte die invasion")
        testExtract("erinnere mich aufzuwachen in 4 jahren",
                    "2021-06-27 00:00:00", "erinnere mich aufzuwachen")
        testExtract("erinnere mich aufzuwachen in 4 jahren und 4 tagen",
                    "2021-07-01 00:00:00", "erinnere mich aufzuwachen")
        testExtract("wie ist das wetter 3 Tage nach morgen?",
                    "2017-07-01 00:00:00", "wie ist das wetter")
        testExtract("dritter dezember",
                    "2017-12-03 00:00:00", "")
        testExtract("lass uns treffen um 8:00 abends",
                    "2017-06-27 20:00:00", "lass uns treffen")

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""
        self.assertEqual(extract_datetime('kein zeit', lang='de-de'), None)

    def test_extractdatetime_default_de(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime("lass uns treffen am freitag",
                               anchor, lang='de-de', default_time=default)
        self.assertEqual(default, res[0].time())

class TestExtractDuration(unittest.TestCase):
    def test_extract_duration_de(self):
        self.assertEqual(extract_duration("10 sekunden", lang="de-de"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minuten", lang="de-de"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 stunden", lang="de-de"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 tage", lang="de-de"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 wochen", lang="de-de"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("sieben stunden"),
                        (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7,5 sekunden", lang="de-de"),
                         (timedelta(seconds=7.5), ""))
        #self.assertEqual(extract_duration("eight and a half days thirty"
        #                                  " nine seconds"),
        #                 (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("starte timer für 30 minuten", lang="de-de"),
                         (timedelta(minutes=30), "starte timer für"))
        #self.assertEqual(extract_duration("Four and a half minutes until"
        #                                  " sunset"),
        #                 (timedelta(minutes=4.5), "until sunset"))
        #self.assertEqual(extract_duration("Nineteen minutes past the hour"),
        #                 (timedelta(minutes=19), "past the hour"))
        self.assertEqual(extract_duration("weck mich in 3 wochen,"
                                          " 497 tagen und"
                                          " 391.6 sekunden", lang="de-de"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "weck mich in ,  und"))
        #self.assertEqual(extract_duration("The movie is one hour, fifty seven"
        #                                  " and a half minutes long"),
        #                 (timedelta(hours=1, minutes=57.5),
        #                     "the movie is ,  long"))
        self.assertEqual(extract_duration("10-sekunden", lang="de-de"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minuten", lang="de-de"),
                         (timedelta(minutes=5), ""))

class TestExtractTimeSpan(unittest.TestCase):
    def test_extract_timespan_ambiguous(self):
        self.assertRaises(ValueError, extract_timespan, "1,3 monate",
                          time_unit=TimespanUnit.RELATIVEDELTA)
        self.assertRaises(ValueError, extract_timespan, "1,3 monate",
                          time_unit=TimespanUnit.RELATIVEDELTA_STRICT)
        self.assertEqual(
            extract_timespan("1,3 monate",
                             time_unit=TimespanUnit.RELATIVEDELTA_FALLBACK),
            (timedelta(days=1.3 * DAYS_IN_1_MONTH), ""))


        # NOTE: for some reason this test fails with
        #   (relativedelta(months=+1, days=+9.126), '') != (relativedelta(months=+1, days=+9.126), '')
        # correct result is being returned

        #self.assertEqual(
        #    extract_timespan("1.3 months",
        #                     resolution=TimespanUnit.RELATIVEDELTA_APPROXIMATE),
        #    (relativedelta(months=1, days=0.3 * DAYS_IN_1_MONTH), ""))

        self.assertEqual(
            extract_timespan("1,3 monate",
                             time_unit=TimespanUnit.RELATIVEDELTA_APPROXIMATE
                             )[0].months, 1)
        self.assertAlmostEquals(
            extract_timespan("1,3 monate",
                             time_unit=TimespanUnit.RELATIVEDELTA_APPROXIMATE
                             )[0].days, 0.3 * DAYS_IN_1_MONTH)

    def test_extract_timespan_de(self):
        self.assertEqual(extract_timespan("10 sekunden"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_timespan("5 minuten"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_timespan("2 stunden"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_timespan("3 tage"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_timespan("25 wochen"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_timespan("sieben stunden"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_timespan("7,5 sekunden"),
                         (timedelta(seconds=7.5), ""))
        # self.assertEqual(extract_timespan("neun einhalb tage"
        #                                   " neununddreißig sekunden"),
        #                  (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_timespan("starte einen timer für 30 minuten"),
                         (timedelta(minutes=30), "starte einen timer für"))
        # self.assertEqual(extract_timespan("vierunddreißig minuten bis"
        #                                   " sonnenuntergang"),
        #                  (timedelta(minutes=4.5), "bis sonnenuntergang"))
        self.assertEqual(extract_timespan("neunzehn minuten nach 3 uhr"),
                         (timedelta(minutes=19), "nach 3 uhr"))
        # self.assertEqual(extract_timespan("weck mich in 3 wochen, "
        #                                   "vierhundertneununddreißig tagen, und"
        #                                   " dreihundert 91.6 sekunden"),
        #                  (timedelta(weeks=3, days=497, seconds=391.6),
        #                   "weck mich in , , und"))
        # self.assertEqual(extract_timespan("der film ist eine stunde, siebenundfünfzig"
        #                                   " und eine halbe minute lang"),
        #                  (timedelta(hours=1, minutes=57.5),
        #                   "der film ist ,  und lang"))
        self.assertEqual(extract_timespan("1 monat"),
                         (timedelta(days=DAYS_IN_1_MONTH), ""))
        self.assertEqual(
            extract_timespan("1 monat",
                             time_unit=TimespanUnit.TIMEDELTA),
            (timedelta(days=DAYS_IN_1_MONTH), ""))

        self.assertEqual(extract_timespan("3 monate"),
                         (timedelta(days=DAYS_IN_1_MONTH * 3), ""))
        self.assertEqual(extract_timespan("ein jahr"),
                         (timedelta(days=DAYS_IN_1_YEAR), ""))
        self.assertEqual(extract_timespan("1 jahr"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1), ""))
        self.assertEqual(extract_timespan("5 jahre"),
                         (timedelta(days=DAYS_IN_1_YEAR * 5), ""))
        self.assertEqual(extract_timespan("ein jahrzehnt"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_timespan("1 jahrzehnt"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_timespan("5 jahrzehnt"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10 * 5), ""))
        self.assertEqual(extract_timespan("1 jahrhundert"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_timespan("ein jahrhundert"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_timespan("5 jahrhunderte"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100 * 5), ""))
        self.assertEqual(extract_timespan("5 jahrtausende"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000 * 5), ""))

    def test_extract_timespan_delta_de(self):
        self.assertEqual(
            extract_timespan("10 sekunden",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(seconds=10.0), ""))
        self.assertEqual(

            extract_timespan("5 minuten",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(minutes=5), ""))
        self.assertEqual(
            extract_timespan("2 stunden",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(hours=2), ""))
        self.assertEqual(
            extract_timespan("3 tage",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(days=3), ""))
        self.assertEqual(
            extract_timespan("25 wochen",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(weeks=25), ""))
        self.assertEqual(
            extract_timespan("sieben stunden",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(hours=7), ""))
        self.assertEqual(
            extract_timespan("7,5 sekunden",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(seconds=7.5), ""))
        # self.assertEqual(
        #     extract_timespan("achteinhalb tage neununddreißig sekunden",
        #                      time_unit=TimespanUnit.RELATIVEDELTA),
        #     (relativedelta(days=8.5, seconds=39), ""))
        self.assertEqual(
            extract_timespan("starte einen timer für 30 minuten",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(minutes=30), "starte einen timer für"))
        # self.assertEqual(
        #     extract_timespan("viereinhalb minuten bis sonnenuntergang",
        #                      time_unit=TimespanUnit.RELATIVEDELTA),
        #     (relativedelta(minutes=4.5), "bis sonnenuntergang"))
        self.assertEqual(
            extract_timespan("neunzehn minuten nach 3 uhr",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(minutes=19), "nach 3 uhr"))
        # self.assertEqual(
        #     extract_timespan("weck mich in 3 wochen, "
        #                      "vierhundertneununddreißig tagen, und"
        #                      " dreihundert 91.6 sekunden",
        #                      time_unit=TimespanUnit.RELATIVEDELTA),
        #     (relativedelta(weeks=3, days=497, seconds=391.6),
        #      "weck mich in , , und"))
        # self.assertEqual(
        #     extract_timespan("der film ist eine stunde, siebenundfünfzig"
        #                      " und eine halbe minute lang",
        #                      time_unit=TimespanUnit.RELATIVEDELTA),
        #     (relativedelta(hours=1, minutes=57.5),
        #      "der film ist ,  und lang"))
        self.assertEqual(
            extract_timespan("1 monat",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(months=1), ""))
        self.assertEqual(
            extract_timespan("3 monate",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(months=3), ""))
        self.assertEqual(
            extract_timespan("ein jahr",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(years=1), ""))
        self.assertEqual(
            extract_timespan("1 jahr",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(years=1), ""))
        self.assertEqual(
            extract_timespan("5 jahre",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(years=5), ""))
        self.assertEqual(
            extract_timespan("ein jahrzehnt",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(years=10), ""))
        self.assertEqual(
            extract_timespan("1 jahrzehnt",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(years=10), ""))
        self.assertEqual(
            extract_timespan("5 jahrzehnte",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(years=10 * 5), ""))
        self.assertEqual(
            extract_timespan("1 jahrhundert",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(years=100), ""))
        self.assertEqual(
            extract_timespan("ein jahrhundert",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(years=100), ""))
        self.assertEqual(
            extract_timespan("5 jahrhunderte",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(years=500), ""))
        self.assertEqual(
            extract_timespan("5 jahrtausende",
                             time_unit=TimespanUnit.RELATIVEDELTA),
            (relativedelta(years=5000), ""))

    def test_extract_timespan_microseconds_de(self):
        def test_milliseconds(duration_str, expected_duration,
                              expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_MICROSECONDS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_milliseconds("0,01 mikrosekunden", 0.01, "")
        test_milliseconds("1 mikrosekunde", 1, "")
        test_milliseconds("5 mikrosekunden", 5, "")
        test_milliseconds("1 millisekunde", 1 * 1000, "")
        test_milliseconds("5 millisekunden", 5 * 1000, "")
        test_milliseconds("100 millisekunden", 100 * 1000, "")
        test_milliseconds("1 sekunde", 1000 * 1000, "")
        test_milliseconds("10 sekunden", 10 * 1000 * 1000, "")
        test_milliseconds("5 minuten", 5 * 60 * 1000 * 1000, "")
        test_milliseconds("2 stunden", 2 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("3 tage", 3 * 24 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("25 wochen", 25 * 7 * 24 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("sieben stunden", 7 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("7,5 sekunden", 7.5 * 1000 * 1000, "")
        # test_milliseconds("achteinhalb tage 39 sekunden",
        #                   (8.5 * 24 * 60 * 60 + 39) * 1000 * 1000, "")
        test_milliseconds("starte einen timer für 30 minuten", 30 * 60 * 1000 * 1000,
                          "starte einen timer für")
        # test_milliseconds("viereinhalb minuten bis sonnenuntergang",
        #                   4.5 * 60 * 1000 * 1000,
        #                   "bis sonnenuntergang")
        test_milliseconds("neunzehn minuten nach 3 uhr",
                          19 * 60 * 1000 * 1000,
                          "nach 3 uhr")
        test_milliseconds("1 monat",
                          DAYS_IN_1_MONTH * 24 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("3 monate",
                          3 * DAYS_IN_1_MONTH * 24 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("ein jahr",
                          DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000 * 1000, "")

    def test_extract_timespan_milliseconds_de(self):
        def test_milliseconds(duration_str, expected_duration,
                              expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_MILLISECONDS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_milliseconds("1 mikrosekunde", 0, "")
        test_milliseconds("4,9 mikrosekunden", 0, "")
        test_milliseconds("5 mikrosekunden", 0.005, "")
        test_milliseconds("1 millisekunde", 1, "")
        test_milliseconds("5 millisekunden", 5, "")
        test_milliseconds("100 millisekunden", 100, "")
        test_milliseconds("1 sekunde", 1000, "")
        test_milliseconds("10 sekunden", 10 * 1000, "")
        test_milliseconds("5 minuten", 5 * 60 * 1000, "")
        test_milliseconds("2 stunden", 2 * 60 * 60 * 1000, "")
        test_milliseconds("3 tage", 3 * 24 * 60 * 60 * 1000, "")
        test_milliseconds("25 wochen", 25 * 7 * 24 * 60 * 60 * 1000, "")
        test_milliseconds("sieben stunden", 7 * 60 * 60 * 1000, "")
        test_milliseconds("7,5 sekunden", 7.5 * 1000, "")
        # test_milliseconds("achteinhalb tage 39 sekunden",
        #                   (8.5 * 24 * 60 * 60 + 39) * 1000, "")
        test_milliseconds("starte einen timer für 30 minuten", 30 * 60 * 1000,
                          "starte einen timer für")
        # test_milliseconds("viereinhalb minuten bis sonnenuntergang",
        #                   4.5 * 60 * 1000,
        #                   "bis sonnenuntergang")
        test_milliseconds("neunzehn minuten nach 3 uhr", 19 * 60 * 1000,
                          "nach 3 uhr")
        # test_milliseconds(
        #     "weck mich in 3 wochen, vierhundertneununddreißig tagen, und"
        #     " dreihundert 91.6 sekunden",
        #     (3 * 7 * 24 * 60 * 60 + 497 * 24 * 60 * 60 + 391.6) * 1000,
        #     "weck mich in , , und")
        # test_milliseconds("der film ist eine stunde, siebenundfünfzig"
        #                   " und eine halbe minute lang", (60 * 60 + 57.5 * 60) * 1000,
        #                   "der film ist ,  lang")
        test_milliseconds("1 monat", DAYS_IN_1_MONTH * 24 * 60 * 60 * 1000, "")
        test_milliseconds("3 monate",
                          3 * DAYS_IN_1_MONTH * 24 * 60 * 60 * 1000, "")
        test_milliseconds("ein jahr", DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("1 jahr", DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("5 jahre", 5 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000,
                          "")
        test_milliseconds("ein jahrzehnt",
                          10 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("1 jahrzehnt",
                          10 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("5 jahrzehnte",
                          5 * 10 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("1 jahrhundert",
                          100 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("ein jahrhundert",
                          100 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("5 jahrhunderte",
                          500 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")

    def test_extract_timespan_seconds_de(self):
        def test_seconds(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_SECONDS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_seconds("1 millisekunde", 0, "")
        test_seconds("4 millisekunden", 0, "")
        test_seconds("5 millisekunden", 0.005, "")
        test_seconds("100 millisekunden", 0.1, "")
        test_seconds("10 sekunden", 10, "")
        test_seconds("5 minuten", 5 * 60, "")
        test_seconds("2 stunden", 2 * 60 * 60, "")
        test_seconds("3 tage", 3 * 24 * 60 * 60, "")
        test_seconds("25 wochen", 25 * 7 * 24 * 60 * 60, "")
        test_seconds("sieben stunden", 7 * 60 * 60, "")
        test_seconds("7,5 sekunden", 7.5, "")
        # test_seconds("achteinhalb tage 39 sekunden",
        #              8.5 * 24 * 60 * 60 + 39, "")
        test_seconds("starte einen timer für 30 minuten", 30 * 60, "starte einen timer für")
        # test_seconds("viereinhalb minuten bis sonnenuntergang", 4.5 * 60,
        #              "bis sonnenuntergang")
        test_seconds("neunzehn minuten nach 3 uhr", 19 * 60,
                     "nach 3 uhr")
        # test_seconds("weck mich in 3 wochen, vierhundertneununddreißig tagen"
        #              " dreihundert 91.6 sekunden",
        #              3 * 7 * 24 * 60 * 60 + 497 * 24 * 60 * 60 + 391.6,
        #              "weck mich in")
        # test_seconds("der film ist eine stunde, siebenundfünfzig"
        #              " und eine halbe minute lang", 60 * 60 + 57.5 * 60,
        #              "der film ist ,  lang")
        test_seconds("1 monat", DAYS_IN_1_MONTH * 24 * 60 * 60, "")
        test_seconds("3 monate", 3 * DAYS_IN_1_MONTH * 24 * 60 * 60, "")
        test_seconds("ein jahr", DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 jahr", DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 jahre", 5 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("ein jahrzehnt", 10 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 jahrzehnt", 10 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 jahrzehnte", 5 * 10 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 jahrhundert", 100 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("ein jahrhundert", 100 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 jahrhunderte", 500 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")

    def test_extract_timespan_minutes_de(self):
        def test_minutes(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_MINUTES)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_minutes("10 sekunden", 10 / 60, "")
        test_minutes("5 minuten", 5, "")
        test_minutes("2 stunden", 2 * 60, "")
        test_minutes("3 tage", 3 * 24 * 60, "")
        test_minutes("25 wochen", 25 * 7 * 24 * 60, "")
        test_minutes("sieben stunden", 7 * 60, "")
        test_minutes("7,5 sekunden", 7.5 / 60, "")
        # test_minutes("achteinhalb tage 39 sekunden",
        #              8.5 * 24 * 60 + 39 / 60, "")
        test_minutes("starte einen timer für 30 minuten", 30, "starte einen timer für")
        # test_minutes("viereinhalb minuten bis sonnenuntergang", 4.5,
        #              "bis sonnenuntergang")
        test_minutes("neunzehn minuten nach 3 uhr", 19,
                     "nach 3 uhr")
        # test_minutes("weck mich in 3 wochen, vierhundertneununddreißig tagen"
        #              " dreihundert 91.6 sekunden",
        #              3 * 7 * 24 * 60 + 497 * 24 * 60 + 391.6 / 60,
        #              "weck mich in")
        # test_minutes("der film ist eine stunde, siebenundfünfzig"
        #              " und eine halbe minute lang", 60 + 57.5,
        #              "der film ist ,  lang")
        test_minutes("1 monat", DAYS_IN_1_MONTH * 24 * 60, "")
        test_minutes("3 monate", 3 * DAYS_IN_1_MONTH * 24 * 60, "")
        test_minutes("ein jahr", DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 jahr", DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 jahre", 5 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("ein jahrzehnt", 10 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 jahrzehnt", 10 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 jahrzehnte", 5 * 10 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 jahrhundert", 100 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("ein jahrhundert", 100 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 jahrhunderte", 500 * DAYS_IN_1_YEAR * 24 * 60, "")

    def test_extract_timespan_hours_de(self):
        def test_hours(duration_str, expected_duration,
                       expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_HOURS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_hours("10 sekunden", 0, "")
        test_hours("17,9 sekunden", 0, "")
        test_hours("5 minuten", 5 / 60, "")
        test_hours("2 stunden", 2, "")
        test_hours("3 tage", 3 * 24, "")
        test_hours("25 wochen", 25 * 7 * 24, "")
        test_hours("sieben stunden", 7, "")
        test_hours("7,5 sekunden", 0, "")
        # test_hours("achteinhalb tage 39 sekunden",
        #            8.5 * 24 + 39 / 60 / 60, "")
        test_hours("starte einen timer für 30 minuten", 30 / 60, "starte einen timer für")
        # test_hours("viereinhalb minuten bis sonnenuntergang", 4.5 / 60,
        #            "bis sonnenuntergang")
        test_hours("neunzehn minuten nach 3 uhr", 19 / 60,
                   "nach 3 uhr")
        # test_hours("weck mich in 3 wochen, vierhundertneununddreißig tagen"
        #            " dreihundert 91.6 sekunden",
        #            3 * 7 * 24 + 497 * 24 + 391.6 / 60 / 60,
        #            "weck mich in")
        # test_hours("der film ist eine stunde, siebenundfünfzig"
        #            " und eine halbe minute lang", 1 + 57.5 / 60,
        #            "der film ist ,  lang")
        test_hours("1 monat", DAYS_IN_1_MONTH * 24, "")
        test_hours("3 monate", 3 * DAYS_IN_1_MONTH * 24, "")
        test_hours("ein jahr", DAYS_IN_1_YEAR * 24, "")
        test_hours("1 jahr", DAYS_IN_1_YEAR * 24, "")
        test_hours("5 jahre", 5 * DAYS_IN_1_YEAR * 24, "")
        test_hours("ein jahrzehnt", 10 * DAYS_IN_1_YEAR * 24, "")
        test_hours("1 jahrzehnt", 10 * DAYS_IN_1_YEAR * 24, "")
        test_hours("5 jahrzehnt", 5 * 10 * DAYS_IN_1_YEAR * 24, "")
        test_hours("1 jahrhundert", 100 * DAYS_IN_1_YEAR * 24, "")
        test_hours("ein jahrhundert", 100 * DAYS_IN_1_YEAR * 24, "")
        test_hours("5 jahrhunderte", 500 * DAYS_IN_1_YEAR * 24, "")

    def test_extract_timespan_days_de(self):
        def test_days(duration_str, expected_duration,
                      expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_DAYS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_days("10 sekunden", 0, "")
        test_days("5 minuten", 0, "")
        test_days("7,1 minuten", 0, "")
        test_days("2 stunden", 2 / 24, "")
        test_days("3 tage", 3, "")
        test_days("25 wochen", 25 * 7, "")
        test_days("sieben stunden", 7 / 24, "")
        test_days("7,5 sekunden", 0, "")
        # test_days("achteinhalb tage 39 sekunden", 8.5, "")
        test_days("starte einen timer für 30 minuten", 30 / 60 / 24,
                  "starte einen timer für")
        # test_days("viereinhalb minuten bis sonnenuntergang", 0, "bis sonnenuntergang")
        test_days("neunzehn minuten nach 3 uhr", 19 / 60 / 24,
                  "nach 3 uhr")
        # test_days("weck mich in 3 wochen, vierhundertneununddreißig tagen"
        #           " dreihundert 91.6 sekunden",
        #           3 * 7 + 497 + 391.6 / 60 / 60 / 24,
        #           "weck mich in")
        # test_days("der film ist eine stunde, siebenundfünfzig"
        #           " und eine halbe minute lang", 1 / 24 + 57.5 / 60 / 24,
        #           "der film ist ,  lang")
        test_days("1 monat", DAYS_IN_1_MONTH, "")
        test_days("3 monate", 3 * DAYS_IN_1_MONTH, "")
        test_days("ein jahr", DAYS_IN_1_YEAR, "")
        test_days("1 jahr", DAYS_IN_1_YEAR, "")
        test_days("5 jahre", 5 * DAYS_IN_1_YEAR, "")
        test_days("ein jahrzehnt", 10 * DAYS_IN_1_YEAR, "")
        test_days("1 jahrzehnt", 10 * DAYS_IN_1_YEAR, "")
        test_days("5 jahrzehnte", 5 * 10 * DAYS_IN_1_YEAR, "")
        test_days("1 jahrhundert", 100 * DAYS_IN_1_YEAR, "")
        test_days("ein jahrhundert", 100 * DAYS_IN_1_YEAR, "")
        test_days("5 jahrhunderte", 500 * DAYS_IN_1_YEAR, "")

    def test_extract_timespan_weeks_de(self):
        def test_weeks(duration_str, expected_duration,
                       expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_WEEKS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_weeks("10 sekunden", 0, "")
        test_weeks("5 minuten", 0, "")
        test_weeks("50 minuten", 0, "")
        test_weeks("2 stunden", 2 / 24 / 7, "")
        test_weeks("3 tage", 3 / 7, "")
        test_weeks("25 wochen", 25, "")
        test_weeks("sieben stunden", 7 / 24 / 7, "")
        test_weeks("7,5 sekunden", 7.5 / 60 / 60 / 24 / 7, "")
        # test_weeks("achteinhalb tage 39 sekunden", 8.5 / 7, "")
        test_weeks("starte einen timer für 30 minuten", 0, "starte einen timer für")
        # test_weeks("viereinhalb minuten bis sonnenuntergang", 0,
        #            "bis sonnenuntergang")
        test_weeks("neunzehn minuten nach 3 uhr", 0, "nach 3 uhr")
        # test_weeks("weck mich in 3 wochen, vierhundertneununddreißig tagen"
        #            " dreihundert 91.6 sekunden", 3 + 497 / 7,
        #            "weck mich in")
        # test_weeks("der film ist eine stunde, siebenundfünfzig"
        #            " und eine halbe minute lang", 1 / 24 / 7 + 57.5 / 60 / 24 / 7,
        #            "der film ist ,  lang")
        test_weeks("1 monat", DAYS_IN_1_MONTH / 7, "")
        test_weeks("3 monate", 3 * DAYS_IN_1_MONTH / 7, "")
        test_weeks("ein jahr", DAYS_IN_1_YEAR / 7, "")
        test_weeks("1 jahr", DAYS_IN_1_YEAR / 7, "")
        test_weeks("5 jahre", 5 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("ein jahrzehnt", 10 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("1 jahrzehnt", 10 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("5 jahrzehnte", 5 * 10 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("1 jahrhundert", 100 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("ein jahrhundert", 100 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("5 jahrhunderte", 500 * DAYS_IN_1_YEAR / 7, "")

    def test_extract_timespan_months_de(self):
        def test_months(duration_str, expected_duration,
                        expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_MONTHS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_months("10 sekunden", 0, "")
        test_months("5 minuten", 0, "")
        test_months("2 stunden", 0, "")
        test_months("3 tage",
                    3 / DAYS_IN_1_MONTH, "")
        test_months("25 wochen",
                    25 * 7 / DAYS_IN_1_MONTH, "")
        test_months("sieben stunden",
                    7 / 24 / DAYS_IN_1_MONTH, "")
        test_months("7,5 sekunden", 0, "")
        # test_months("achteinhalb tage 39 sekunden",
        #             8.5 / DAYS_IN_1_MONTH, "")
        test_months("starte einen timer für 30 minuten", 0, "starte einen timer für")
        # test_months("viereinhalb minuten bis sonnenuntergang", 0, "bis sonnenuntergang")
        test_months("neunzehn minuten nach 3 uhr", 0, "nach 3 uhr")
        # test_months("weck mich in 3 wochen, vierhundertneununddreißig tagen"
        #             " dreihundert 91.6 sekunden",
        #             3 * 7 / DAYS_IN_1_MONTH + 497 / DAYS_IN_1_MONTH,
        #             "weck mich in")
        # test_months(
        #     "der film ist eine stunde, siebenundfünfzig und eine halbe minute lang", 0,
        #     "der film ist ,  lang")
        test_months("1 monat", 1, "")
        test_months("3 monate", 3, "")
        test_months("ein jahr", DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("1 jahr", DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("5 jahre", 5 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("ein jahrzehnt", 10 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("1 jahrzehnt", 10 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("5 jahrzehnte", 5 * 10 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("1 jahrhundert", 100 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("ein jahrhundert", 100 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("5 jahrhunderte", 500 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")

    def test_extract_timespan_years_de(self):
        def test_years(duration_str, expected_duration,
                       expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_YEARS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_years("10 sekunden", 0, "")
        test_years("5 minuten", 0, "")
        test_years("2 stunden", 0, "")
        test_years("1,5 tage", 0, "")
        test_years("3 tage", 3 / DAYS_IN_1_YEAR, "")
        test_years("25 wochen", 25 * 7 / DAYS_IN_1_YEAR, "")
        test_years("sieben stunden", 0, "")
        test_years("7,5 sekunden", 0, "")
        # test_years("achteinhalb tage 39 sekunden",
        #            8.5 / DAYS_IN_1_YEAR, "")
        test_years("starte einen timer für 30 minuten", 0, "starte einen timer für")
        # test_years("viereinhalb minuten bis sonnenuntergang", 0, "bis sonnenuntergang")
        test_years("neunzehn minuten nach 3 uhr", 0, "nach 3 uhr")
        # test_years("weck mich in 3 wochen, vierhundertneununddreißig tagen"
        #            " dreihundert 91.6 sekunden",
        #            3 * 7 / DAYS_IN_1_YEAR + 497 / DAYS_IN_1_YEAR,
        #            "weck mich in")
        # test_years(
        #     "der film ist eine stunde, siebenundfünfzig und eine halbe minute lang", 0,
        #     "der film ist ,  lang")
        test_years("1 monat", 1 / 12, "")
        test_years("3 monate", 3 / 12, "")
        test_years("ein jahr", 1, "")
        test_years("1 jahr", 1, "")
        test_years("5 jahre", 5, "")
        test_years("ein jahrzehnt", 10, "")
        test_years("1 jahrzehnt", 10, "")
        test_years("5 jahrzehnte", 50, "")
        test_years("1 jahrhundert", 100, "")
        test_years("ein jahrhundert", 100, "")
        test_years("5 jahrhunderte", 500, "")

    def test_extract_timespan_decades_de(self):
        def test_decades(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_DECADES)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_decades("10 sekunden", 0, "")
        test_decades("5 minuten", 0, "")
        test_decades("2 stunden", 0, "")
        test_decades("3 tage", 0, "")
        test_decades("25 wochen", 25 * 7 / DAYS_IN_1_YEAR / 10, "")
        test_decades("sieben stunden", 0, "")
        test_decades("7,5 sekunden", 0, "")
        # test_decades("achteinhalb tage 39 sekunden", 0, "")
        test_decades("starte einen timer für 30 minuten", 0, "starte einen timer für")
        # test_decades("viereinhalb minuten bis sonnenuntergang", 0,
        #              "bis sonnenuntergang")
        test_decades("neunzehn minuten nach 3 uhr", 0,
                     "nach 3 uhr")
        # test_decades(
        #     "der film ist eine stunde, siebenundfünfzig und eine halbe minute lang", 0,
        #     "der film ist ,  lang")
        test_decades("1 monat", 1 / 12 / 10, "")
        test_decades("3 monate", 3 / 12 / 10, "")
        test_decades("ein jahr", 1 / 10, "")
        test_decades("1 jahr", 1 / 10, "")
        test_decades("5 jahre", 5 / 10, "")
        test_decades("ein jahrzehnt", 1, "")
        test_decades("1 jahrzehnt", 1, "")
        test_decades("5 jahrzehnte", 5, "")
        test_decades("1 jahrhundert", 10, "")
        test_decades("ein jahrhundert", 10, "")
        test_decades("5 jahrhunderte", 50, "")

    def test_extract_timespan_centuries_de(self):
        def test_centuries(duration_str, expected_duration,
                           expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_CENTURIES)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_centuries("10 sekunden", 0, "")
        test_centuries("5 minuten", 0, "")
        test_centuries("2 stunden", 0, "")
        test_centuries("3 tage", 0, "")
        test_centuries("25 wochen", 0, "")
        test_centuries("sieben stunden", 0, "")
        test_centuries("7,5 sekunden", 0, "")
        # test_centuries("achteinhalb tage 39 sekunden", 0, "")
        test_centuries("starte einen timer für 30 minuten", 0, "starte einen timer für")
        # test_centuries("viereinhalb minuten bis sonnenuntergang", 0,
        #                "bis sonnenuntergang")
        test_centuries("neunzehn minuten nach 3 uhr", 0,
                       "nach 3 uhr")
        # test_centuries(
        #     "der film ist eine stunde, siebenundfünfzig und eine halbe minute lang", 0,
        #     "der film ist ,  lang")
        test_centuries("1 monat", 0, "")
        test_centuries("3 monate", 0, "")
        test_centuries("6 monate", 0, "")
        test_centuries("ein jahr", 1 / 100, "")
        test_centuries("1 jahr", 1 / 100, "")
        test_centuries("5 jahre", 5 / 100, "")
        test_centuries("ein jahrzehnt", 1 / 10, "")
        test_centuries("1 jahrzehnt", 1 / 10, "")
        test_centuries("5 jahrzehnte", 5 / 10, "")
        test_centuries("1 jahrhundert", 1, "")
        test_centuries("ein jahrhundert", 1, "")
        test_centuries("5 jahrhunderte", 5, "")

    def test_extract_timespan_millennia_de(self):
        def test_millennium(duration_str, expected_duration,
                            expected_remainder):
            duration, remainder = extract_timespan(
                duration_str, time_unit=TimespanUnit.TOTAL_MILLENNIUMS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)
        
        test_millennium("5 jahre", 5 / 1000, "")
        test_millennium("ein jahrzehnt", 1 / 100, "")
        test_millennium("1 jahrzehnt", 1 / 100, "")
        test_millennium("5 jahrzehnte", 5 / 100, "")
        test_millennium("1 jahrhundert", 1 / 10, "")
        test_millennium("ein jahrhundert", 1 / 10, "")
        test_millennium("5 jahrhunderte", 5 / 10, "")
        test_millennium("1 jahrtausend", 1, "")
        test_millennium("5 jahrtausende", 5, "")


if __name__ == "__main__":
    unittest.main()
