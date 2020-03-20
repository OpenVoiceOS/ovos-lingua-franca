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
from datetime import datetime, timedelta, time
from dateutil import tz
from dateutil.relativedelta import relativedelta

from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.internal import FunctionNotLocalizedError
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import get_gender
from lingua_franca.parse import normalize
from lingua_franca.time import default_timezone, to_local
from lingua_franca.parse import extract_langcode
from lingua_franca.parse import yes_or_no
from lingua_franca.time import DAYS_IN_1_YEAR, DAYS_IN_1_MONTH
from lingua_franca.parse import DurationResolution
from lingua_franca.location import set_active_location
from lingua_franca.time import now_local, date_to_season, \
    get_week_range, get_weekend_range, DAYS_IN_1_YEAR, DAYS_IN_1_MONTH
from lingua_franca.lang.parse_common import DateTimeResolution, Season
from lingua_franca.location import Hemisphere
from lingua_franca.lang.parse_en import extract_date_en
from datetime import date, datetime, timedelta


def setUpModule():
    load_language('en')
    set_default_lang('en')


def tearDownModule():
    unload_language('en')


def extractWithFormat(text):
    date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
    [extractedDate, leftover] = extract_datetime(text, date)
    extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
    return [extractedDate, leftover]


class TestNormalize(unittest.TestCase):
    def test_articles(self):
        self.assertEqual(normalize("this is a test", remove_articles=True),
                         "this is test")
        self.assertEqual(normalize("this is the test", remove_articles=True),
                         "this is test")
        self.assertEqual(normalize("and another test", remove_articles=True),
                         "and another test")
        self.assertEqual(normalize("this is an extra test",
                                   remove_articles=False),
                         "this is an extra test")

    def test_extract_number_priority(self):
        # sanity check
        self.assertEqual(extract_number("third", ordinals=True), 3)
        self.assertEqual(extract_number("sixth", ordinals=True), 6)

        # TODO a suite of tests needs to be written depending on outcome of
        #  https://github.com/MycroftAI/lingua-franca/issues/152
        # the tests bellow are flagged as problematic, some of those ARE BROKEN
        # for now this is considered undefined behaviour!!!

        # NOTE this test is returning the first number, which seems to be
        # the consensus regarding correct behaviour
        self.assertEqual(extract_number("Twenty two and Three Fifths",
                                        ordinals=True), 22)

        # TODO these should return the 1st number, not the last, ordinals
        #  seem messed up, the rest of the codebase is returning first
        #  number most likely tests bellow are bugs, i repeat, tests bellow
        #  are testing FOR THE "WRONG" VALUE
        self.assertEqual(extract_number("sixth third", ordinals=True), 3)
        self.assertEqual(extract_number("third sixth", ordinals=True), 6)

    def test_extract_number_ambiguous(self):
        # test explicit ordinals
        self.assertEqual(extract_number("this is the 1st",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("this is the 2nd",
                                        ordinals=False), 2)
        self.assertEqual(extract_number("this is the 3rd",
                                        ordinals=None), 3)
        self.assertEqual(extract_number("this is the 4th",
                                        ordinals=None), 4)
        self.assertEqual(extract_number(
            "this is the 7th test", ordinals=True), 7)
        self.assertEqual(extract_number(
            "this is the 7th test", ordinals=False), 7)
        self.assertTrue(extract_number("this is the nth test") is False)
        self.assertEqual(extract_number("this is the 1st test"), 1)
        self.assertEqual(extract_number("this is the 2nd test"), 2)
        self.assertEqual(extract_number("this is the 3rd test"), 3)
        self.assertEqual(extract_number("this is the 31st test"), 31)
        self.assertEqual(extract_number("this is the 32nd test"), 32)
        self.assertEqual(extract_number("this is the 33rd test"), 33)
        self.assertEqual(extract_number("this is the 34th test"), 34)

        # test non ambiguous ordinals
        self.assertEqual(extract_number("this is the first test",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("this is the first test",
                                        ordinals=False), False)
        self.assertEqual(extract_number("this is the first test",
                                        ordinals=None), False)

        # test ambiguous ordinal/time unit
        self.assertEqual(extract_number("this is second test",
                                        ordinals=True), 2)
        self.assertEqual(extract_number("this is second test",
                                        ordinals=False), False)
        self.assertEqual(extract_number("remind me in a second",
                                        ordinals=True), 2)
        self.assertEqual(extract_number("remind me in a second",
                                        ordinals=False), False)
        self.assertEqual(extract_number("remind me in a second",
                                        ordinals=None), False)

        # test ambiguous ordinal/fractional
        self.assertEqual(extract_number("this is the third test",
                                        ordinals=True), 3.0)
        self.assertEqual(extract_number("this is the third test",
                                        ordinals=False), 1.0 / 3.0)
        self.assertEqual(extract_number("this is the third test",
                                        ordinals=None), False)

        self.assertEqual(extract_number("one third of a cup",
                                        ordinals=False), 1.0 / 3.0)
        self.assertEqual(extract_number("one third of a cup",
                                        ordinals=True), 3)
        self.assertEqual(extract_number("one third of a cup",
                                        ordinals=None), 1)

        # test plurals
        # NOTE plurals are never considered ordinals, but also not
        # considered explicit fractions
        self.assertEqual(extract_number("2 fifths",
                                        ordinals=True), 2)
        self.assertEqual(extract_number("2 fifth",
                                        ordinals=True), 5)
        self.assertEqual(extract_number("2 fifths",
                                        ordinals=False), 2 / 5)
        self.assertEqual(extract_number("2 fifths",
                                        ordinals=None), 2)

        self.assertEqual(extract_number("Twenty two and Three Fifths"), 22.6)

        # test multiple ambiguous
        self.assertEqual(extract_number("sixth third", ordinals=None), False)
        self.assertEqual(extract_number("thirty second", ordinals=False), 30)
        self.assertEqual(extract_number("thirty second", ordinals=None), 30)
        self.assertEqual(extract_number("thirty second", ordinals=True), 32)
        # TODO this test is imperfect, further discussion needed
        # "Sixth third" would probably refer to "the sixth instance of a third"
        # I dunno what should be returned here, don't think it should be cumulative.
        self.assertEqual(extract_number("sixth third", ordinals=False),
                         1 / 6 / 3)

        # test big numbers / short vs long scale
        self.assertEqual(extract_number("this is the billionth test",
                                        ordinals=True), 1e09)
        self.assertEqual(extract_number("this is the billionth test",
                                        ordinals=None), False)

        self.assertEqual(extract_number("this is the billionth test",
                                        ordinals=False), 1e-9)
        self.assertEqual(extract_number("this is the billionth test",
                                        ordinals=True,
                                        short_scale=False), 1e12)
        self.assertEqual(extract_number("this is the billionth test",
                                        ordinals=None,
                                        short_scale=False), False)
        self.assertEqual(extract_number("this is the billionth test",
                                        short_scale=False), 1e-12)

        # test the Nth one
        self.assertEqual(extract_number("the fourth one", ordinals=True), 4.0)
        self.assertEqual(extract_number("the thirty sixth one",
                                        ordinals=True), 36.0)
        self.assertEqual(extract_number(
            "you are the second one", ordinals=False), 1)
        self.assertEqual(extract_number(
            "you are the second one", ordinals=True), 2)
        self.assertEqual(extract_number("you are the 1st one",
                                        ordinals=None), 1)
        self.assertEqual(extract_number("you are the 2nd one",
                                        ordinals=None), 2)
        self.assertEqual(extract_number("you are the 3rd one",
                                        ordinals=None), 3)
        self.assertEqual(extract_number("you are the 8th one",
                                        ordinals=None), 8)

    def test_extract_number(self):
        self.assertEqual(extract_number("this is 2 test"), 2)
        self.assertEqual(extract_number("this is test number 4"), 4)
        self.assertEqual(extract_number("three cups"), 3)
        self.assertEqual(extract_number("1/3 cups"), 1.0 / 3.0)
        self.assertEqual(extract_number("quarter cup"), 0.25)
        self.assertEqual(extract_number("1/4 cup"), 0.25)
        self.assertEqual(extract_number("one fourth cup"), 0.25)
        self.assertEqual(extract_number("2/3 cups"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 cups"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 and 3/4 cups"), 1.75)
        self.assertEqual(extract_number("1 cup and a half"), 1.5)
        self.assertEqual(extract_number("one cup and a half"), 1.5)
        self.assertEqual(extract_number("one and a half cups"), 1.5)
        self.assertEqual(extract_number("one and one half cups"), 1.5)
        self.assertEqual(extract_number("three quarter cups"), 3.0 / 4.0)
        self.assertEqual(extract_number("three quarters cups"), 3.0 / 4.0)
        self.assertEqual(extract_number("twenty two"), 22)
        self.assertEqual(extract_number(
            "Twenty two with a leading capital letter"), 22)
        self.assertEqual(extract_number(
            "twenty Two with Two capital letters"), 22)
        self.assertEqual(extract_number(
            "twenty Two with mixed capital letters"), 22)
        self.assertEqual(extract_number("two hundred"), 200)
        self.assertEqual(extract_number("nine thousand"), 9000)
        self.assertEqual(extract_number("six hundred sixty six"), 666)
        self.assertEqual(extract_number("two million"), 2000000)
        self.assertEqual(extract_number("two million five hundred thousand "
                                        "tons of spinning metal"), 2500000)
        self.assertEqual(extract_number("six trillion"), 6000000000000.0)
        self.assertEqual(extract_number("six trillion", short_scale=False),
                         6e+18)
        self.assertEqual(extract_number("one point five"), 1.5)
        self.assertEqual(extract_number("three dot fourteen"), 3.14)
        self.assertEqual(extract_number("zero point two"), 0.2)
        self.assertEqual(extract_number("billions of years older"),
                         1000000000.0)
        self.assertEqual(extract_number("billions of years older",
                                        short_scale=False),
                         1000000000000.0)
        self.assertEqual(extract_number("one hundred thousand"), 100000)
        self.assertEqual(extract_number("minus 2"), -2)
        self.assertEqual(extract_number("negative seventy"), -70)
        self.assertEqual(extract_number("thousand million"), 1000000000)

        # Verify non-power multiples of ten no longer discard
        # adjacent multipliers
        self.assertEqual(extract_number("twenty thousand"), 20000)
        self.assertEqual(extract_number("fifty million"), 50000000)

        # Verify smaller powers of ten no longer cause miscalculation of larger
        # powers of ten (see MycroftAI#86)
        self.assertEqual(extract_number("twenty billion three hundred million \
                                        nine hundred fifty thousand six hundred \
                                        seventy five point eight"),
                         20300950675.8)
        self.assertEqual(extract_number("nine hundred ninety nine million nine \
                                        hundred ninety nine thousand nine \
                                        hundred ninety nine point nine"),
                         999999999.9)

        # TODO why does "trillion" result in xxxx.0?
        self.assertEqual(extract_number("eight hundred trillion two hundred \
                                        fifty seven"), 800000000000257.0)

        # TODO handle this case
        # self.assertEqual(
        #    extract_number("6 dot six six six"),
        #    6.666)
        self.assertTrue(extract_number("The tennis player is fast") is False)
        self.assertTrue(extract_number("fraggle") is False)

        self.assertTrue(extract_number("fraggle zero") is not False)
        self.assertEqual(extract_number("fraggle zero"), 0)

        self.assertTrue(extract_number("grobo 0") is not False)
        self.assertEqual(extract_number("grobo 0"), 0)

        self.assertEqual(extract_number("a couple of beers"), 2)
        self.assertEqual(extract_number("a couple hundred beers"), 200)
        self.assertEqual(extract_number("a couple thousand beers"), 2000)
        self.assertEqual(extract_number("totally 100%"), 100)

    def test_extract_duration_replace_token(self):
        self.assertEqual(extract_duration("10 seconds", replace_token="_"),
                         (timedelta(seconds=10.0), "_ _"))
        # TODO remainder is imperfect because "fifty seven and a half
        #  minutes" was normalized to a single word "57.5"
        self.assertEqual(extract_duration("The movie is one hour, fifty seven"
                                          " and a half minutes long",
                                          replace_token="_"),
                         (timedelta(hours=1, minutes=57.5),
                          "the movie is _ _, _ _ long"))

    def test_extract_duration_ambiguous(self):
        self.assertRaises(ValueError, extract_duration, "1.3 months",
                          resolution=DurationResolution.RELATIVEDELTA)
        self.assertRaises(ValueError, extract_duration, "1.3 months",
                          resolution=DurationResolution.RELATIVEDELTA_STRICT)
        self.assertEqual(
            extract_duration("1.3 months",
                             resolution=DurationResolution.RELATIVEDELTA_FALLBACK),
            (timedelta(days=1.3 * DAYS_IN_1_MONTH), ""))

        # NOTE: for some reason test bellow fails with
        #       (relativedelta(months=+1, days=+9.126), '') != \
        #       (relativedelta(months=+1, days=+9.126), '')
        # correct result is being returned

        # self.assertEqual(
        #    extract_duration("1.3 months",
        #                     resolution=DurationResolution.RELATIVEDELTA_APPROXIMATE),
        #    (relativedelta(months=1, days=0.3 * DAYS_IN_1_MONTH), ""))

        self.assertEqual(
            extract_duration("1.3 months",
                             resolution=DurationResolution.RELATIVEDELTA_APPROXIMATE
                             )[0].months, 1)
        self.assertAlmostEqual(
            extract_duration("1.3 months",
                             resolution=DurationResolution.RELATIVEDELTA_APPROXIMATE
                             )[0].days, 0.3 * DAYS_IN_1_MONTH)

    def test_extract_duration_en(self):
        self.assertEqual(extract_duration("10 seconds"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minutes"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 hours"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 days"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 weeks"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("seven hours"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 seconds"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("eight and a half days thirty"
                                          " nine seconds"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("wake me up in three weeks, four"
                                          " hundred ninety seven days, and"
                                          " three hundred 91.6 seconds"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "wake me up in , , and"))
        self.assertEqual(extract_duration("The movie is one hour, fifty seven"
                                          " and a half minutes long"),
                         (timedelta(hours=1, minutes=57.5),
                             "the movie is ,  long"))
        self.assertEqual(extract_duration("10-seconds"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minutes"),
                         (timedelta(minutes=5), ""))

        self.assertEqual(extract_duration("1 month"),
                         (timedelta(days=DAYS_IN_1_MONTH), ""))
        self.assertEqual(
            extract_duration("1 month",
                             resolution=DurationResolution.TIMEDELTA),
            (timedelta(days=DAYS_IN_1_MONTH), ""))

        self.assertEqual(extract_duration("3 months"),
                         (timedelta(days=DAYS_IN_1_MONTH * 3), ""))
        self.assertEqual(extract_duration("a year"),
                         (timedelta(days=DAYS_IN_1_YEAR), ""))
        self.assertEqual(extract_duration("1 year"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1), ""))
        self.assertEqual(extract_duration("5 years"),
                         (timedelta(days=DAYS_IN_1_YEAR * 5), ""))
        self.assertEqual(extract_duration("a decade"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("1 decade"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("5 decades"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10 * 5), ""))
        self.assertEqual(extract_duration("1 century"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("a century"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("5 centuries"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100 * 5), ""))
        self.assertEqual(extract_duration("1 millennium"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000), ""))
        self.assertEqual(extract_duration("5 millenniums"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000 * 5), ""))

    def test_extract_duration_delta_en(self):
        self.assertEqual(
            extract_duration("10 seconds",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(seconds=10.0), ""))
        self.assertEqual(

            extract_duration("5 minutes",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(minutes=5), ""))
        self.assertEqual(
            extract_duration("2 hours",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(hours=2), ""))
        self.assertEqual(
            extract_duration("3 days",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(days=3), ""))
        self.assertEqual(
            extract_duration("25 weeks",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(weeks=25), ""))
        self.assertEqual(
            extract_duration("seven hours",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(hours=7), ""))
        self.assertEqual(
            extract_duration("7.5 seconds",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(seconds=7.5), ""))
        self.assertEqual(
            extract_duration("eight and a half days thirty nine seconds",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(days=8.5, seconds=39), ""))
        self.assertEqual(
            extract_duration("Set a timer for 30 minutes",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(minutes=30), "set a timer for"))
        self.assertEqual(
            extract_duration("Four and a half minutes until sunset",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(minutes=4.5), "until sunset"))
        self.assertEqual(
            extract_duration("Nineteen minutes past the hour",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(minutes=19), "past the hour"))
        self.assertEqual(
            extract_duration("wake me up in three weeks, four hundred "
                             "ninety seven days, and three hundred 91.6 "
                             "seconds",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(weeks=3, days=497, seconds=391.6),
             "wake me up in , , and"))
        self.assertEqual(
            extract_duration("The movie is one hour, fifty seven"
                             " and a half minutes long",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(hours=1, minutes=57.5),
             "the movie is ,  long"))
        self.assertEqual(
            extract_duration("10-seconds",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(seconds=10.0), ""))
        self.assertEqual(
            extract_duration("5-minutes",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(minutes=5), ""))

        self.assertEqual(
            extract_duration("1 month",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(months=1), ""))
        self.assertEqual(
            extract_duration("3 months",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(months=3), ""))
        self.assertEqual(
            extract_duration("a year",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=1), ""))
        self.assertEqual(
            extract_duration("1 year",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=1), ""))
        self.assertEqual(
            extract_duration("5 years",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=5), ""))
        self.assertEqual(
            extract_duration("a decade",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=10), ""))
        self.assertEqual(
            extract_duration("1 decade",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=10), ""))
        self.assertEqual(
            extract_duration("5 decades",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=10 * 5), ""))
        self.assertEqual(
            extract_duration("1 century",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=100), ""))
        self.assertEqual(
            extract_duration("a century",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=100), ""))
        self.assertEqual(
            extract_duration("5 centuries",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=500), ""))
        self.assertEqual(
            extract_duration("1 millennium",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=1000), ""))
        self.assertEqual(
            extract_duration("5 millenniums",
                             resolution=DurationResolution.RELATIVEDELTA),
            (relativedelta(years=1000 * 5), ""))

    def test_extract_duration_microseconds_en(self):
        def test_milliseconds(duration_str, expected_duration,
                              expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_MICROSECONDS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_milliseconds("0.01 microseconds", 0.01, "")
        test_milliseconds("1 microsecond", 1, "")
        test_milliseconds("5 microseconds", 5, "")
        test_milliseconds("1 millisecond", 1 * 1000, "")
        test_milliseconds("5 milliseconds", 5 * 1000, "")
        test_milliseconds("100 milliseconds", 100 * 1000, "")
        test_milliseconds("1 second", 1000 * 1000, "")
        test_milliseconds("10 seconds", 10 * 1000 * 1000, "")
        test_milliseconds("5 minutes", 5 * 60 * 1000 * 1000, "")
        test_milliseconds("2 hours", 2 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("3 days", 3 * 24 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("25 weeks", 25 * 7 * 24 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("seven hours", 7 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("7.5 seconds", 7.5 * 1000 * 1000, "")
        test_milliseconds("eight and a half days thirty nine seconds",
                          (8.5 * 24 * 60 * 60 + 39) * 1000 * 1000, "")
        test_milliseconds("Set a timer for 30 minutes", 30 * 60 * 1000 * 1000,
                          "set a timer for")
        test_milliseconds("Four and a half minutes until sunset",
                          4.5 * 60 * 1000 * 1000,
                          "until sunset")
        test_milliseconds("Nineteen minutes past the hour",
                          19 * 60 * 1000 * 1000,
                          "past the hour")
        test_milliseconds("10-seconds", 10 * 1000 * 1000, "")
        test_milliseconds("5-minutes", 5 * 60 * 1000 * 1000, "")
        test_milliseconds("1 month",
                          DAYS_IN_1_MONTH * 24 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("3 months",
                          3 * DAYS_IN_1_MONTH * 24 * 60 * 60 * 1000 * 1000, "")
        test_milliseconds("a year",
                          DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000 * 1000, "")

    def test_extract_duration_milliseconds_en(self):
        def test_milliseconds(duration_str, expected_duration,
                              expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_MILLISECONDS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_milliseconds("1 microsecond", 0, "")
        test_milliseconds("4.9 microseconds", 0, "")
        test_milliseconds("5 microseconds", 0.005, "")
        test_milliseconds("1 millisecond", 1, "")
        test_milliseconds("5 milliseconds", 5, "")
        test_milliseconds("100 milliseconds", 100, "")
        test_milliseconds("1 second", 1000, "")
        test_milliseconds("10 seconds", 10 * 1000, "")
        test_milliseconds("5 minutes", 5 * 60 * 1000, "")
        test_milliseconds("2 hours", 2 * 60 * 60 * 1000, "")
        test_milliseconds("3 days", 3 * 24 * 60 * 60 * 1000, "")
        test_milliseconds("25 weeks", 25 * 7 * 24 * 60 * 60 * 1000, "")
        test_milliseconds("seven hours", 7 * 60 * 60 * 1000, "")
        test_milliseconds("7.5 seconds", 7.5 * 1000, "")
        test_milliseconds("eight and a half days thirty nine seconds",
                          (8.5 * 24 * 60 * 60 + 39) * 1000, "")
        test_milliseconds("Set a timer for 30 minutes", 30 * 60 * 1000,
                          "set a timer for")
        test_milliseconds("Four and a half minutes until sunset",
                          4.5 * 60 * 1000,
                          "until sunset")
        test_milliseconds("Nineteen minutes past the hour", 19 * 60 * 1000,
                          "past the hour")
        test_milliseconds(
            "wake me up in three weeks, four hundred ninety seven "
            "days, and three hundred 91.6 seconds",
            (3 * 7 * 24 * 60 * 60 + 497 * 24 * 60 * 60 + 391.6) * 1000,
            "wake me up in , , and")
        test_milliseconds("The movie is one hour, fifty seven and a half "
                          "minutes long", (60 * 60 + 57.5 * 60) * 1000,
                          "the movie is ,  long")
        test_milliseconds("10-seconds", 10 * 1000, "")
        test_milliseconds("5-minutes", 5 * 60 * 1000, "")
        test_milliseconds("1 month", DAYS_IN_1_MONTH * 24 * 60 * 60 * 1000, "")
        test_milliseconds("3 months",
                          3 * DAYS_IN_1_MONTH * 24 * 60 * 60 * 1000, "")
        test_milliseconds("a year", DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("1 year", DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("5 years", 5 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000,
                          "")
        test_milliseconds("a decade",
                          10 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("1 decade",
                          10 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("5 decades",
                          5 * 10 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("1 century",
                          100 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("a century",
                          100 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("5 centuries",
                          500 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("1 millennium",
                          1000 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")
        test_milliseconds("5 millenniums",
                          5000 * DAYS_IN_1_YEAR * 24 * 60 * 60 * 1000, "")

    def test_extract_duration_seconds_en(self):
        def test_seconds(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_SECONDS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_seconds("1 millisecond", 0, "")
        test_seconds("4 milliseconds", 0, "")
        test_seconds("5 milliseconds", 0.005, "")
        test_seconds("100 milliseconds", 0.1, "")
        test_seconds("10 seconds", 10, "")
        test_seconds("5 minutes", 5 * 60, "")
        test_seconds("2 hours", 2 * 60 * 60, "")
        test_seconds("3 days", 3 * 24 * 60 * 60, "")
        test_seconds("25 weeks", 25 * 7 * 24 * 60 * 60, "")
        test_seconds("seven hours", 7 * 60 * 60, "")
        test_seconds("7.5 seconds", 7.5, "")
        test_seconds("eight and a half days thirty nine seconds",
                     8.5 * 24 * 60 * 60 + 39, "")
        test_seconds("Set a timer for 30 minutes", 30 * 60, "set a timer for")
        test_seconds("Four and a half minutes until sunset", 4.5 * 60,
                     "until sunset")
        test_seconds("Nineteen minutes past the hour", 19 * 60,
                     "past the hour")
        test_seconds("wake me up in three weeks, four hundred ninety seven "
                     "days, and three hundred 91.6 seconds",
                     3 * 7 * 24 * 60 * 60 + 497 * 24 * 60 * 60 + 391.6,
                     "wake me up in , , and")
        test_seconds("The movie is one hour, fifty seven and a half "
                     "minutes long", 60 * 60 + 57.5 * 60,
                     "the movie is ,  long")
        test_seconds("10-seconds", 10, "")
        test_seconds("5-minutes", 5 * 60, "")
        test_seconds("1 month", DAYS_IN_1_MONTH * 24 * 60 * 60, "")
        test_seconds("3 months", 3 * DAYS_IN_1_MONTH * 24 * 60 * 60, "")
        test_seconds("a year", DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 year", DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 years", 5 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("a decade", 10 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 decade", 10 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 decades", 5 * 10 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 century", 100 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("a century", 100 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 centuries", 500 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("1 millennium", 1000 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")
        test_seconds("5 millenniums", 5000 * DAYS_IN_1_YEAR * 24 * 60 * 60, "")

    def test_extract_duration_minutes_en(self):
        def test_minutes(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_MINUTES)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_minutes("10 seconds", 10 / 60, "")
        test_minutes("5 minutes", 5, "")
        test_minutes("2 hours", 2 * 60, "")
        test_minutes("3 days", 3 * 24 * 60, "")
        test_minutes("25 weeks", 25 * 7 * 24 * 60, "")
        test_minutes("seven hours", 7 * 60, "")
        test_minutes("7.5 seconds", 7.5 / 60, "")
        test_minutes("eight and a half days thirty nine seconds",
                     8.5 * 24 * 60 + 39 / 60, "")
        test_minutes("Set a timer for 30 minutes", 30, "set a timer for")
        test_minutes("Four and a half minutes until sunset", 4.5,
                     "until sunset")
        test_minutes("Nineteen minutes past the hour", 19,
                     "past the hour")
        test_minutes("wake me up in three weeks, four hundred ninety seven "
                     "days, and three hundred 91.6 seconds",
                     3 * 7 * 24 * 60 + 497 * 24 * 60 + 391.6 / 60,
                     "wake me up in , , and")
        test_minutes("The movie is one hour, fifty seven and a half "
                     "minutes long", 60 + 57.5,
                     "the movie is ,  long")
        test_minutes("10-seconds", 10 / 60, "")
        test_minutes("5-minutes", 5, "")
        test_minutes("1 month", DAYS_IN_1_MONTH * 24 * 60, "")
        test_minutes("3 months", 3 * DAYS_IN_1_MONTH * 24 * 60, "")
        test_minutes("a year", DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 year", DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 years", 5 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("a decade", 10 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 decade", 10 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 decades", 5 * 10 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 century", 100 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("a century", 100 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 centuries", 500 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("1 millennium", 1000 * DAYS_IN_1_YEAR * 24 * 60, "")
        test_minutes("5 millenniums", 5000 * DAYS_IN_1_YEAR * 24 * 60, "")

    def test_extract_duration_hours_en(self):
        def test_hours(duration_str, expected_duration,
                       expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_HOURS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_hours("10 seconds", 0, "")
        test_hours("17.9 seconds", 0, "")
        test_hours("5 minutes", 5 / 60, "")
        test_hours("2 hours", 2, "")
        test_hours("3 days", 3 * 24, "")
        test_hours("25 weeks", 25 * 7 * 24, "")
        test_hours("seven hours", 7, "")
        test_hours("7.5 seconds", 0, "")
        test_hours("eight and a half days thirty nine seconds",
                   8.5 * 24 + 39 / 60 / 60, "")
        test_hours("Set a timer for 30 minutes", 30 / 60, "set a timer for")
        test_hours("Four and a half minutes until sunset", 4.5 / 60,
                   "until sunset")
        test_hours("Nineteen minutes past the hour", 19 / 60,
                   "past the hour")
        test_hours("wake me up in three weeks, four hundred ninety seven "
                   "days, and three hundred 91.6 seconds",
                   3 * 7 * 24 + 497 * 24 + 391.6 / 60 / 60,
                   "wake me up in , , and")
        test_hours("The movie is one hour, fifty seven and a half "
                   "minutes long", 1 + 57.5 / 60,
                   "the movie is ,  long")
        test_hours("10-seconds", 0, "")
        test_hours("5-minutes", 5 / 60, "")
        test_hours("1 month", DAYS_IN_1_MONTH * 24, "")
        test_hours("3 months", 3 * DAYS_IN_1_MONTH * 24, "")
        test_hours("a year", DAYS_IN_1_YEAR * 24, "")
        test_hours("1 year", DAYS_IN_1_YEAR * 24, "")
        test_hours("5 years", 5 * DAYS_IN_1_YEAR * 24, "")
        test_hours("a decade", 10 * DAYS_IN_1_YEAR * 24, "")
        test_hours("1 decade", 10 * DAYS_IN_1_YEAR * 24, "")
        test_hours("5 decades", 5 * 10 * DAYS_IN_1_YEAR * 24, "")
        test_hours("1 century", 100 * DAYS_IN_1_YEAR * 24, "")
        test_hours("a century", 100 * DAYS_IN_1_YEAR * 24, "")
        test_hours("5 centuries", 500 * DAYS_IN_1_YEAR * 24, "")
        test_hours("1 millennium", 1000 * DAYS_IN_1_YEAR * 24, "")
        test_hours("5 millenniums", 5000 * DAYS_IN_1_YEAR * 24, "")

    def test_extract_duration_days_en(self):
        def test_days(duration_str, expected_duration,
                      expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_DAYS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_days("10 seconds", 0, "")
        test_days("5 minutes", 0, "")
        test_days("7.1 minutes", 0, "")
        test_days("2 hours", 2 / 24, "")
        test_days("3 days", 3, "")
        test_days("25 weeks", 25 * 7, "")
        test_days("seven hours", 7 / 24, "")
        test_days("7.5 seconds", 0, "")
        test_days("eight and a half days thirty nine seconds", 8.5, "")
        test_days("Set a timer for 30 minutes", 30 / 60 / 24,
                  "set a timer for")
        test_days("Four and a half minutes until sunset", 0, "until sunset")
        test_days("Nineteen minutes past the hour", 19 / 60 / 24,
                  "past the hour")
        test_days("wake me up in three weeks, four hundred ninety seven "
                  "days, and three hundred 91.6 seconds",
                  3 * 7 + 497 + 391.6 / 60 / 60 / 24,
                  "wake me up in , , and")
        test_days("The movie is one hour, fifty seven and a half "
                  "minutes long", 1 / 24 + 57.5 / 60 / 24,
                  "the movie is ,  long")
        test_days("10-seconds", 0, "")
        test_days("5-minutes", 0, "")
        test_days("1 month", DAYS_IN_1_MONTH, "")
        test_days("3 months", 3 * DAYS_IN_1_MONTH, "")
        test_days("a year", DAYS_IN_1_YEAR, "")
        test_days("1 year", DAYS_IN_1_YEAR, "")
        test_days("5 years", 5 * DAYS_IN_1_YEAR, "")
        test_days("a decade", 10 * DAYS_IN_1_YEAR, "")
        test_days("1 decade", 10 * DAYS_IN_1_YEAR, "")
        test_days("5 decades", 5 * 10 * DAYS_IN_1_YEAR, "")
        test_days("1 century", 100 * DAYS_IN_1_YEAR, "")
        test_days("a century", 100 * DAYS_IN_1_YEAR, "")
        test_days("5 centuries", 500 * DAYS_IN_1_YEAR, "")
        test_days("1 millennium", 1000 * DAYS_IN_1_YEAR, "")
        test_days("5 millenniums", 5000 * DAYS_IN_1_YEAR, "")

    def test_extract_duration_weeks_en(self):
        def test_weeks(duration_str, expected_duration,
                       expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_WEEKS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_weeks("10 seconds", 0, "")
        test_weeks("5 minutes", 0, "")
        test_weeks("50 minutes", 0, "")
        test_weeks("2 hours", 2 / 24 / 7, "")
        test_weeks("3 days", 3 / 7, "")
        test_weeks("25 weeks", 25, "")
        test_weeks("seven hours", 7 / 24 / 7, "")
        test_weeks("7.5 seconds", 7.5 / 60 / 60 / 24 / 7, "")
        test_weeks("eight and a half days thirty nine seconds", 8.5 / 7, "")
        test_weeks("Set a timer for 30 minutes", 0, "set a timer for")
        test_weeks("Four and a half minutes until sunset", 0,
                   "until sunset")
        test_weeks("Nineteen minutes past the hour", 0, "past the hour")
        test_weeks("wake me up in three weeks, four hundred ninety seven "
                   "days, and three hundred 91.6 seconds", 3 + 497 / 7,
                   "wake me up in , , and")
        test_weeks("The movie is one hour, fifty seven and a half "
                   "minutes long", 1 / 24 / 7 + 57.5 / 60 / 24 / 7,
                   "the movie is ,  long")
        test_weeks("10-seconds", 0, "")
        test_weeks("5-minutes", 0, "")
        test_weeks("1 month", DAYS_IN_1_MONTH / 7, "")
        test_weeks("3 months", 3 * DAYS_IN_1_MONTH / 7, "")
        test_weeks("a year", DAYS_IN_1_YEAR / 7, "")
        test_weeks("1 year", DAYS_IN_1_YEAR / 7, "")
        test_weeks("5 years", 5 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("a decade", 10 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("1 decade", 10 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("5 decades", 5 * 10 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("1 century", 100 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("a century", 100 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("5 centuries", 500 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("1 millennium", 1000 * DAYS_IN_1_YEAR / 7, "")
        test_weeks("5 millenniums", 5000 * DAYS_IN_1_YEAR / 7, "")

    def test_extract_duration_months_en(self):
        def test_months(duration_str, expected_duration,
                        expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_MONTHS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_months("10 seconds", 0, "")
        test_months("5 minutes", 0, "")
        test_months("2 hours", 0, "")
        test_months("3 days",
                    3 / DAYS_IN_1_MONTH, "")
        test_months("25 weeks",
                    25 * 7 / DAYS_IN_1_MONTH, "")
        test_months("seven hours",
                    7 / 24 / DAYS_IN_1_MONTH, "")
        test_months("7.5 seconds", 0, "")
        test_months("eight and a half days thirty nine seconds",
                    8.5 / DAYS_IN_1_MONTH, "")
        test_months("Set a timer for 30 minutes", 0, "set a timer for")
        test_months("Four and a half minutes until sunset", 0, "until sunset")
        test_months("Nineteen minutes past the hour", 0, "past the hour")
        test_months("wake me up in three weeks, four hundred ninety seven "
                    "days, and three hundred 91.6 seconds",
                    3 * 7 / DAYS_IN_1_MONTH + 497 / DAYS_IN_1_MONTH,
                    "wake me up in , , and")
        test_months(
            "The movie is one hour, fifty seven and a half minutes long", 0,
            "the movie is ,  long")
        test_months("10-seconds", 0, "")
        test_months("5-minutes", 0, "")
        test_months("1 month", 1, "")
        test_months("3 months", 3, "")
        test_months("a year", DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("1 year", DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("5 years", 5 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("a decade", 10 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("1 decade", 10 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("5 decades", 5 * 10 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("1 century", 100 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("a century", 100 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("5 centuries", 500 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("1 millennium",
                    1000 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")
        test_months("5 millenniums",
                    5000 * DAYS_IN_1_YEAR / DAYS_IN_1_MONTH, "")

    def test_extract_duration_years_en(self):
        def test_years(duration_str, expected_duration,
                       expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_YEARS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_years("10 seconds", 0, "")
        test_years("5 minutes", 0, "")
        test_years("2 hours", 0, "")
        test_years("1.5 days", 0, "")
        test_years("3 days", 3 / DAYS_IN_1_YEAR, "")
        test_years("25 weeks", 25 * 7 / DAYS_IN_1_YEAR, "")
        test_years("seven hours", 0, "")
        test_years("7.5 seconds", 0, "")
        test_years("eight and a half days thirty nine seconds",
                   8.5 / DAYS_IN_1_YEAR, "")
        test_years("Set a timer for 30 minutes", 0, "set a timer for")
        test_years("Four and a half minutes until sunset", 0, "until sunset")
        test_years("Nineteen minutes past the hour", 0, "past the hour")
        test_years("wake me up in three weeks, four hundred ninety seven "
                   "days, and three hundred 91.6 seconds",
                   3 * 7 / DAYS_IN_1_YEAR + 497 / DAYS_IN_1_YEAR,
                   "wake me up in , , and")
        test_years(
            "The movie is one hour, fifty seven and a half minutes long", 0,
            "the movie is ,  long")
        test_years("10-seconds", 0, "")
        test_years("5-minutes", 0, "")
        test_years("1 month", 1 / 12, "")
        test_years("3 months", 3 / 12, "")
        test_years("a year", 1, "")
        test_years("1 year", 1, "")
        test_years("5 years", 5, "")
        test_years("a decade", 10, "")
        test_years("1 decade", 10, "")
        test_years("5 decades", 50, "")
        test_years("1 century", 100, "")
        test_years("a century", 100, "")
        test_years("5 centuries", 500, "")
        test_years("1 millennium", 1000, "")
        test_years("5 millenniums", 5000, "")

    def test_extract_duration_decades_en(self):
        def test_decades(duration_str, expected_duration,
                         expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_DECADES)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_decades("10 seconds", 0, "")
        test_decades("5 minutes", 0, "")
        test_decades("2 hours", 0, "")
        test_decades("3 days", 0, "")
        test_decades("25 weeks", 25 * 7 / DAYS_IN_1_YEAR / 10, "")
        test_decades("seven hours", 0, "")
        test_decades("7.5 seconds", 0, "")
        test_decades("eight and a half days thirty nine seconds", 0, "")
        test_decades("Set a timer for 30 minutes", 0, "set a timer for")
        test_decades("Four and a half minutes until sunset", 0,
                     "until sunset")
        test_decades("Nineteen minutes past the hour", 0,
                     "past the hour")
        test_decades(
            "The movie is one hour, fifty seven and a half minutes long", 0,
            "the movie is ,  long")
        test_decades("10-seconds", 0, "")
        test_decades("5-minutes", 0, "")
        test_decades("1 month", 1 / 12 / 10, "")
        test_decades("3 months", 3 / 12 / 10, "")
        test_decades("a year", 1 / 10, "")
        test_decades("1 year", 1 / 10, "")
        test_decades("5 years", 5 / 10, "")
        test_decades("a decade", 1, "")
        test_decades("1 decade", 1, "")
        test_decades("5 decades", 5, "")
        test_decades("1 century", 10, "")
        test_decades("a century", 10, "")
        test_decades("5 centuries", 50, "")
        test_decades("1 millennium", 100, "")
        test_decades("5 millenniums", 500, "")

    def test_extract_duration_centuries_en(self):
        def test_centuries(duration_str, expected_duration,
                           expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_CENTURIES)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_centuries("10 seconds", 0, "")
        test_centuries("5 minutes", 0, "")
        test_centuries("2 hours", 0, "")
        test_centuries("3 days", 0, "")
        test_centuries("25 weeks", 0, "")
        test_centuries("seven hours", 0, "")
        test_centuries("7.5 seconds", 0, "")
        test_centuries("eight and a half days thirty nine seconds", 0, "")
        test_centuries("Set a timer for 30 minutes", 0, "set a timer for")
        test_centuries("Four and a half minutes until sunset", 0,
                       "until sunset")
        test_centuries("Nineteen minutes past the hour", 0,
                       "past the hour")
        test_centuries(
            "The movie is one hour, fifty seven and a half minutes long", 0,
            "the movie is ,  long")
        test_centuries("10-seconds", 0, "")
        test_centuries("5-minutes", 0, "")
        test_centuries("1 month", 0, "")
        test_centuries("3 months", 0, "")
        test_centuries("6 months", 0, "")
        test_centuries("a year", 1 / 100, "")
        test_centuries("1 year", 1 / 100, "")
        test_centuries("5 years", 5 / 100, "")
        test_centuries("a decade", 1 / 10, "")
        test_centuries("1 decade", 1 / 10, "")
        test_centuries("5 decades", 5 / 10, "")
        test_centuries("1 century", 1, "")
        test_centuries("a century", 1, "")
        test_centuries("5 centuries", 5, "")
        test_centuries("1 millennium", 10, "")
        test_centuries("5 millenniums", 50, "")

    def test_extract_duration_millennia_en(self):
        def test_millennium(duration_str, expected_duration,
                            expected_remainder):
            duration, remainder = extract_duration(
                duration_str, resolution=DurationResolution.TOTAL_MILLENNIUMS)

            self.assertEqual(remainder, expected_remainder)

            # allow small floating point errors
            self.assertAlmostEqual(expected_duration, duration, places=2)

        test_millennium("10 seconds", 0, "")
        test_millennium("5 minutes", 0, "")
        test_millennium("2 hours", 0, "")
        test_millennium("3 days", 0, "")
        test_millennium("25 weeks", 0, "")
        test_millennium("seven hours", 0, "")
        test_millennium("7.5 seconds", 0, "")
        test_millennium("eight and a half days thirty nine seconds", 0, "")
        test_millennium("Set a timer for 30 minutes", 0, "set a timer for")
        test_millennium("Four and a half minutes until sunset", 0,
                        "until sunset")
        test_millennium("Nineteen minutes past the hour", 0,
                        "past the hour")
        test_millennium("wake me up in three weeks, four hundred ninety seven "
                        "days, and three hundred 91.6 seconds", 0,
                        "wake me up in , , and")
        test_millennium(
            "The movie is one hour, fifty seven and a half minutes long", 0,
            "the movie is ,  long")
        test_millennium("10-seconds", 0, "")
        test_millennium("5-minutes", 0, "")
        test_millennium("1 month", 0, "")
        test_millennium("3 months", 0, "")
        test_millennium("6 months", 0, "")
        test_millennium("a year", 0, "")
        test_millennium("1 year", 0, "")
        test_millennium("4.99 years", 0, "")
        test_millennium("5 years", 5 / 1000, "")
        test_millennium("a decade", 1 / 100, "")
        test_millennium("1 decade", 1 / 100, "")
        test_millennium("5 decades", 5 / 100, "")
        test_millennium("1 century", 1 / 10, "")
        test_millennium("a century", 1 / 10, "")
        test_millennium("5 centuries", 5 / 10, "")
        test_millennium("1 millennium", 1, "")
        test_millennium("5 millenniums", 5, "")

    def test_extract_duration_case_en(self):
        self.assertEqual(extract_duration("Set a timer for 30 minutes"),
                         (timedelta(minutes=30), "Set a timer for"))
        self.assertEqual(extract_duration("The movie is one hour, fifty seven"
                                          " and a half minutes long"),
                         (timedelta(hours=1, minutes=57.5),
                          "The movie is ,  long"))
        self.assertEqual(extract_duration("Four and a Half minutes until"
                                          " sunset"),
                         (timedelta(minutes=4.5), "until sunset"))
        self.assertEqual(extract_duration("Nineteen minutes past THE hour"),
                         (timedelta(minutes=19), "past THE hour"))

    def test_extractdatetime_fractions_en(self):
        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("Set the ambush for half an hour",
                    "2017-06-27 13:34:00", "set ambush")
        testExtract("remind me to call mom in half an hour",
                    "2017-06-27 13:34:00", "remind me to call mom")
        testExtract("remind me to call mom in a half hour",
                    "2017-06-27 13:34:00", "remind me to call mom")
        testExtract("remind me to call mom in a quarter hour",
                    "2017-06-27 13:19:00", "remind me to call mom")
        testExtract("remind me to call mom in a quarter of an hour",
                    "2017-06-27 13:19:00", "remind me to call mom")

    def test_extractdatetime_year_multiples_en(self):
        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("in a decade",
                    "2027-06-27 00:00:00", "")
        testExtract("in a couple of decades",
                    "2037-06-27 00:00:00", "")
        testExtract("next decade",
                    "2027-06-27 00:00:00", "")
        testExtract("in a century",
                    "2117-06-27 00:00:00", "")
        testExtract("in a millennium",
                    "3017-06-27 00:00:00", "")
        testExtract("in a couple decades",
                    "2037-06-27 00:00:00", "")
        testExtract("in 5 decades",
                    "2067-06-27 00:00:00", "")
        testExtract("in a couple centuries",
                    "2217-06-27 00:00:00", "")
        testExtract("in a couple of centuries",
                    "2217-06-27 00:00:00", "")
        testExtract("in 2 centuries",
                    "2217-06-27 00:00:00", "")
        testExtract("in a couple millenniums",
                    "4017-06-27 00:00:00", "")
        testExtract("in a couple of millenniums",
                    "4017-06-27 00:00:00", "")

        # in {float} year multiple
        for i in range(1, 500):
            testExtract(f"in {i} decades",
                        f"{2017 + 10 * i}-06-27 00:00:00", "")
            for j in range(1, 9):  # TODO fix higher numbers
                testExtract(f"in {i}.{j} decades",
                            f"{2017 + j + 10 * i}-06-27 00:00:00", "")
        for i in range(1, 50):
            testExtract(f"in {i} centuries",
                        f"{2017 + 100 * i}-06-27 00:00:00", "")
            for j in range(1, 9):  # TODO fix higher numbers
                testExtract(f"in {i}.{j} centuries",
                            f"{2017 + j * 10 + 100 * i}-06-27 00:00:00", "")
        for i in range(1, 8):
            testExtract(f"in {i} millenniums",
                        f"{2017 + 1000 * i}-06-27 00:00:00", "")
            for j in range(1, 9):  # TODO fix higher numbers
                testExtract(f"in {i}.{j} millenniums",
                            f"{2017 + j * 100 + 1000 * i}-06-27 00:00:00", "")

    def test_extractdatetime_en(self):
        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("now is the time",
                    "2017-06-27 13:04:00", "is time")
        testExtract("in a second",
                    "2017-06-27 13:04:01", "")
        testExtract("in a minute",
                    "2017-06-27 13:05:00", "")
        testExtract("in a couple minutes",
                    "2017-06-27 13:06:00", "")
        testExtract("in a couple of minutes",
                    "2017-06-27 13:06:00", "")
        testExtract("in a couple hours",
                    "2017-06-27 15:04:00", "")
        testExtract("in a couple of hours",
                    "2017-06-27 15:04:00", "")
        testExtract("in a couple weeks",
                    "2017-07-11 00:00:00", "")
        testExtract("in a couple of weeks",
                    "2017-07-11 00:00:00", "")
        testExtract("in a couple months",
                    "2017-08-27 00:00:00", "")
        testExtract("in a couple years",
                    "2019-06-27 00:00:00", "")
        testExtract("in a couple of months",
                    "2017-08-27 00:00:00", "")
        testExtract("in a couple of years",
                    "2019-06-27 00:00:00", "")
        testExtract("in an hour",
                    "2017-06-27 14:04:00", "")
        testExtract("i want it within the hour",
                    "2017-06-27 14:04:00", "i want it")
        testExtract("in 1 second",
                    "2017-06-27 13:04:01", "")
        testExtract("in 2 seconds",
                    "2017-06-27 13:04:02", "")
        testExtract("Set the ambush in 1 minute",
                    "2017-06-27 13:05:00", "set ambush")
        testExtract("Set the ambush for 5 days from today",
                    "2017-07-02 00:00:00", "set ambush")
        testExtract("day after tomorrow",
                    "2017-06-29 00:00:00", "")
        testExtract("What is the day after tomorrow's weather?",
                    "2017-06-29 00:00:00", "what is weather")
        testExtract("Remind me at 10:45 pm",
                    "2017-06-27 22:45:00", "remind me")
        testExtract("what is the weather on friday morning",
                    "2017-06-30 08:00:00", "what is weather")
        testExtract("what is tomorrow's weather",
                    "2017-06-28 00:00:00", "what is weather")
        testExtract("what is this afternoon's weather",
                    "2017-06-27 15:00:00", "what is weather")
        testExtract("what is this evening's weather",
                    "2017-06-27 19:00:00", "what is weather")
        testExtract("what was this morning's weather",
                    "2017-06-27 08:00:00", "what was weather")
        testExtract("remind me to call mom in 8 weeks and 2 days",
                    "2017-08-24 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom on august 3rd",
                    "2017-08-03 00:00:00", "remind me to call mom")
        testExtract("remind me tomorrow to call mom at 7am",
                    "2017-06-28 07:00:00", "remind me to call mom")
        testExtract("remind me tomorrow to call mom at 10pm",
                    "2017-06-28 22:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7am",
                    "2017-06-28 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom in an hour",
                    "2017-06-27 14:04:00", "remind me to call mom")
        testExtract("remind me to call mom at 1730",
                    "2017-06-27 17:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 0630",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 06 30 hours",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 06 30",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 06 30 hours",
                    "2017-06-28 06:30:00", "remind me to call mom")
        testExtract("remind me to call mom at 7 o'clock",
                    "2017-06-27 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom this evening at 7 o'clock",
                    "2017-06-27 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom  at 7 o'clock tonight",
                    "2017-06-27 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7 o'clock in the morning",
                    "2017-06-28 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom Thursday evening at 7 o'clock",
                    "2017-06-29 19:00:00", "remind me to call mom")
        testExtract("remind me to call mom Thursday morning at 7 o'clock",
                    "2017-06-29 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7 o'clock Thursday morning",
                    "2017-06-29 07:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 7:00 Thursday morning",
                    "2017-06-29 07:00:00", "remind me to call mom")
        # TODO: This test is imperfect due to the "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("remind me to call mom at 7:00 Thursday evening",
                    "2017-06-29 19:00:00", "remind me to call mom at 7:00")
        testExtract("remind me to call mom at 8 Wednesday evening",
                    "2017-06-28 20:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 8 Wednesday in the evening",
                    "2017-06-28 20:00:00", "remind me to call mom")
        testExtract("remind me to call mom Wednesday evening at 8",
                    "2017-06-28 20:00:00", "remind me to call mom")
        testExtract("remind me to call mom in two hours",
                    "2017-06-27 15:04:00", "remind me to call mom")
        testExtract("remind me to call mom in 2 hours",
                    "2017-06-27 15:04:00", "remind me to call mom")
        testExtract("remind me to call mom in 15 minutes",
                    "2017-06-27 13:19:00", "remind me to call mom")
        testExtract("remind me to call mom in fifteen minutes",
                    "2017-06-27 13:19:00", "remind me to call mom")
        testExtract("remind me to call mom at 10am 2 days after this saturday",
                    "2017-07-03 10:00:00", "remind me to call mom")
        testExtract("Play Rick Astley music 2 days from Friday",
                    "2017-07-02 00:00:00", "play rick astley music")
        testExtract("Begin the invasion at 3:45 pm on Thursday",
                    "2017-06-29 15:45:00", "begin invasion")
        testExtract("On Monday, order pie from the bakery",
                    "2017-07-03 00:00:00", "order pie from bakery")
        testExtract("Play Happy Birthday music 5 years from today",
                    "2022-06-27 00:00:00", "play happy birthday music")
        testExtract("Skype Mom at 12:45 pm next Thursday",
                    "2017-07-06 12:45:00", "skype mom")
        testExtract("What's the weather next Friday?",
                    "2017-06-30 00:00:00", "what weather")
        testExtract("What's the weather next Wednesday?",
                    "2017-07-05 00:00:00", "what weather")
        testExtract("What's the weather next Thursday?",
                    "2017-07-06 00:00:00", "what weather")
        testExtract("what is the weather next friday morning",
                    "2017-06-30 08:00:00", "what is weather")
        testExtract("what is the weather next friday evening",
                    "2017-06-30 19:00:00", "what is weather")
        testExtract("what is the weather next friday afternoon",
                    "2017-06-30 15:00:00", "what is weather")
        testExtract("remind me to call mom on august 3rd",
                    "2017-08-03 00:00:00", "remind me to call mom")
        testExtract("Buy fireworks on the 4th of July",
                    "2017-07-04 00:00:00", "buy fireworks")
        testExtract("what is the weather 2 weeks from next friday",
                    "2017-07-14 00:00:00", "what is weather")
        testExtract("what is the weather wednesday at 0700 hours",
                    "2017-06-28 07:00:00", "what is weather")
        testExtract("set an alarm wednesday at 7 o'clock",
                    "2017-06-28 07:00:00", "set alarm")
        testExtract("Set up an appointment at 12:45 pm next Thursday",
                    "2017-07-06 12:45:00", "set up appointment")
        testExtract("What's the weather this Thursday?",
                    "2017-06-29 00:00:00", "what weather")
        testExtract("set up the visit for 2 weeks and 6 days from Saturday",
                    "2017-07-21 00:00:00", "set up visit")
        testExtract("Begin the invasion at 03 45 on Thursday",
                    "2017-06-29 03:45:00", "begin invasion")
        testExtract("Begin the invasion at o 800 hours on Thursday",
                    "2017-06-29 08:00:00", "begin invasion")
        testExtract("Begin the party at 8 o'clock in the evening on Thursday",
                    "2017-06-29 20:00:00", "begin party")
        testExtract("Begin the invasion at 8 in the evening on Thursday",
                    "2017-06-29 20:00:00", "begin invasion")
        testExtract("Begin the invasion on Thursday at noon",
                    "2017-06-29 12:00:00", "begin invasion")
        testExtract("Begin the invasion on Thursday at midnight",
                    "2017-06-29 00:00:00", "begin invasion")
        testExtract("Begin the invasion on Thursday at 0500",
                    "2017-06-29 05:00:00", "begin invasion")
        testExtract("remind me to wake up in 4 years",
                    "2021-06-27 00:00:00", "remind me to wake up")
        testExtract("remind me to wake up in 4 years and 4 days",
                    "2021-07-01 00:00:00", "remind me to wake up")
        testExtract("What is the weather 3 days after tomorrow?",
                    "2017-07-01 00:00:00", "what is weather")
        testExtract("december 3",
                    "2017-12-03 00:00:00", "")
        testExtract("lets meet at 8:00 tonight",
                    "2017-06-27 20:00:00", "lets meet")
        testExtract("lets meet at 5pm",
                    "2017-06-27 17:00:00", "lets meet")
        testExtract("lets meet at 8 a.m.",
                    "2017-06-28 08:00:00", "lets meet")
        testExtract("remind me to wake up at 8 a.m",
                    "2017-06-28 08:00:00", "remind me to wake up")
        testExtract("what is the weather on tuesday",
                    "2017-06-27 00:00:00", "what is weather")
        testExtract("what is the weather on monday",
                    "2017-07-03 00:00:00", "what is weather")
        testExtract("what is the weather this wednesday",
                    "2017-06-28 00:00:00", "what is weather")
        testExtract("on thursday what is the weather",
                    "2017-06-29 00:00:00", "what is weather")
        testExtract("on this thursday what is the weather",
                    "2017-06-29 00:00:00", "what is weather")
        testExtract("on last monday what was the weather",
                    "2017-06-26 00:00:00", "what was weather")
        testExtract("set an alarm for wednesday evening at 8",
                    "2017-06-28 20:00:00", "set alarm")
        testExtract("set an alarm for wednesday at 3 o'clock in the afternoon",
                    "2017-06-28 15:00:00", "set alarm")
        testExtract("set an alarm for wednesday at 3 o'clock in the morning",
                    "2017-06-28 03:00:00", "set alarm")
        testExtract("set an alarm for wednesday morning at 7 o'clock",
                    "2017-06-28 07:00:00", "set alarm")
        testExtract("set an alarm for today at 7 o'clock",
                    "2017-06-27 19:00:00", "set alarm")
        testExtract("set an alarm for this evening at 7 o'clock",
                    "2017-06-27 19:00:00", "set alarm")
        # TODO: This test is imperfect due to the "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("set an alarm for this evening at 7:00",
                    "2017-06-27 19:00:00", "set alarm at 7:00")
        testExtract("on the evening of june 5th 2017 remind me to" +
                    " call my mother",
                    "2017-06-05 19:00:00", "remind me to call my mother")
        # TODO: This test is imperfect due to the missing "for" in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("update my calendar for a morning meeting with julius" +
                    " on march 4th",
                    "2018-03-04 08:00:00",
                    "update my calendar meeting with julius")
        testExtract("remind me to call mom next tuesday",
                    "2017-07-04 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 3 weeks",
                    "2017-07-18 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 8 weeks",
                    "2017-08-22 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 8 weeks and 2 days",
                    "2017-08-24 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 4 days",
                    "2017-07-01 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 3 months",
                    "2017-09-27 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom in 2 years and 2 days",
                    "2019-06-29 00:00:00", "remind me to call mom")

        testExtract("remind me to call mom at 10am on saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 10am this saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 10 next saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        testExtract("remind me to call mom at 10am next saturday",
                    "2017-07-01 10:00:00", "remind me to call mom")
        # test yesterday
        testExtract("what day was yesterday",
                    "2017-06-26 00:00:00", "what day was")
        testExtract("what day was the day before yesterday",
                    "2017-06-25 00:00:00", "what day was")
        testExtract("i had dinner yesterday at 6",
                    "2017-06-26 06:00:00", "i had dinner")
        testExtract("i had dinner yesterday at 6 am",
                    "2017-06-26 06:00:00", "i had dinner")
        testExtract("i had dinner yesterday at 6 pm",
                    "2017-06-26 18:00:00", "i had dinner")

        # Below two tests, ensure that time is picked
        # even if no am/pm is specified
        # in case of weekdays/tonight
        testExtract("set alarm for 9 on weekdays",
                    "2017-06-27 21:00:00", "set alarm weekdays")
        testExtract("for 8 tonight",
                    "2017-06-27 20:00:00", "")
        testExtract("for 8:30pm tonight",
                    "2017-06-27 20:30:00", "")
        # Tests a time with ':' & without am/pm
        testExtract("set an alarm for tonight 9:30",
                    "2017-06-27 21:30:00", "set alarm")
        testExtract("set an alarm at 9:00 for tonight",
                    "2017-06-27 21:00:00", "set alarm")
        # Check if it picks the intent irrespective of correctness
        testExtract("set an alarm at 9 o'clock for tonight",
                    "2017-06-27 21:00:00", "set alarm")
        testExtract("remind me about the game tonight at 11:30",
                    "2017-06-27 23:30:00", "remind me about game")
        testExtract("set alarm at 7:30 on weekdays",
                    "2017-06-27 19:30:00", "set alarm on weekdays")

        #  "# days <from X/after X>"
        testExtract("my birthday is 2 days from today",
                    "2017-06-29 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days after today",
                    "2017-06-29 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days from tomorrow",
                    "2017-06-30 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days after tomorrow",
                    "2017-06-30 00:00:00", "my birthday is")
        testExtract("remind me to call mom at 10am 2 days after next saturday",
                    "2017-07-10 10:00:00", "remind me to call mom")
        testExtract("my birthday is 2 days from yesterday",
                    "2017-06-28 00:00:00", "my birthday is")
        testExtract("my birthday is 2 days after yesterday",
                    "2017-06-28 00:00:00", "my birthday is")

        #  "# days ago>"
        testExtract("my birthday was 1 day ago",
                    "2017-06-26 00:00:00", "my birthday was")
        testExtract("my birthday was 2 days ago",
                    "2017-06-25 00:00:00", "my birthday was")
        testExtract("my birthday was 3 days ago",
                    "2017-06-24 00:00:00", "my birthday was")
        testExtract("my birthday was 4 days ago",
                    "2017-06-23 00:00:00", "my birthday was")
        # TODO this test is imperfect due to "tonight" in the reminder, but let is pass since the date is correct
        testExtract("lets meet tonight",
                    "2017-06-27 22:00:00", "lets meet tonight")
        # TODO this test is imperfect due to "at night" in the reminder, but let is pass since the date is correct
        testExtract("lets meet later at night",
                    "2017-06-27 22:00:00", "lets meet later at night")
        # TODO this test is imperfect due to "night" in the reminder, but let is pass since the date is correct
        testExtract("what's the weather like tomorrow night",
                    "2017-06-28 22:00:00", "what is weather like night")
        # TODO this test is imperfect due to "night" in the reminder, but let is pass since the date is correct
        testExtract("what's the weather like next tuesday night",
                    "2017-07-04 22:00:00", "what is weather like night")

    def test_extractdatetime_with_default_time_en(self):
        def extractWithFormat(text):
            default_time = time(15, 4, tzinfo=default_timezone())
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
            [extractedDate, leftover] = extract_datetime(text, date, default_time=default_time)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        # ignore default time arg
        testExtract("in a second",
                    "2017-06-27 13:04:01", "")
        testExtract("in a minute",
                    "2017-06-27 13:05:00", "")
        testExtract("in an hour",
                    "2017-06-27 14:04:00", "")

        # use default time
        testExtract("in a couple weeks",
                    "2017-07-11 15:04:00", "")
        testExtract("in a couple of weeks",
                    "2017-07-11 15:04:00", "")
        testExtract("in a couple months",
                    "2017-08-27 15:04:00", "")
        testExtract("in a couple years",
                    "2019-06-27 15:04:00", "")
        testExtract("in a couple of months",
                    "2017-08-27 15:04:00", "")
        testExtract("in a couple of years",
                    "2019-06-27 15:04:00", "")
        testExtract("in a decade",
                    "2027-06-27 15:04:00", "")
        testExtract("in a couple of decades",
                    "2037-06-27 15:04:00", "")
        testExtract("next decade",
                    "2027-06-27 15:04:00", "")
        testExtract("in a century",
                    "2117-06-27 15:04:00", "")
        testExtract("in a millennium",
                    "3017-06-27 15:04:00", "")
        testExtract("in a couple decades",
                    "2037-06-27 15:04:00", "")
        testExtract("in 5 decades",
                    "2067-06-27 15:04:00", "")
        testExtract("in a couple centuries",
                    "2217-06-27 15:04:00", "")
        testExtract("in a couple of centuries",
                    "2217-06-27 15:04:00", "")
        testExtract("in 2 centuries",
                    "2217-06-27 15:04:00", "")
        testExtract("in a couple millenniums",
                    "4017-06-27 15:04:00", "")
        testExtract("in a couple of millenniums",
                    "4017-06-27 15:04:00", "")

    def test_extract_date_years(self):
        date = datetime(2017, 6, 27, tzinfo=default_timezone())  # Tue June 27, 2017
        self.assertEqual(extract_datetime('in 2007', date)[0],
                         datetime(2007, 6, 27, tzinfo=date.tzinfo))

    def test_extract_ambiguous_month_en(self):
        dec = datetime(2017, 12, 27, 8, 1, 2)
        jun = datetime(2017, 6, 27, 20, 1, 2)
        self.assertEqual(
            extract_datetime('when is september', jun)[0],
            datetime(2017, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('when was september', dec)[0],
            datetime(2017, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('when was september', jun)[0],
            datetime(2016, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('when is september', dec)[0],
            datetime(2018, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i did the thing last september', jun)[0],
            datetime(2016, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('past september the thing was done', dec)[0],
            datetime(2017, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i will do the thing in september', jun)[0],
            datetime(2017, 9, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('next september the thing will be done', dec)[0],
            datetime(2018, 9, 1, tzinfo=default_timezone()))

    def test_extract_ambiguous_time_en(self):
        morning = datetime(2017, 6, 27, 8, 1, 2, tzinfo=default_timezone())
        evening = datetime(2017, 6, 27, 20, 1, 2, tzinfo=default_timezone())
        noonish = datetime(2017, 6, 27, 12, 1, 2, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('feed the fish'), None)
        self.assertEqual(
            extract_datetime('day'), None)
        self.assertEqual(
            extract_datetime('week'), None)
        self.assertEqual(
            extract_datetime('month'), None)
        self.assertEqual(
            extract_datetime('year'), None)
        self.assertEqual(
            extract_datetime(' '), None)
        self.assertEqual(
            extract_datetime('feed fish at 10 o\'clock', morning)[0],
            datetime(2017, 6, 27, 10, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('feed fish at 10 o\'clock', noonish)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('feed fish at 10 o\'clock', evening)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))

    def test_extract_later_en(self):
        dt = datetime(2017, 1, 1, 13, 12, 30)
        self.assertEqual(
            extract_datetime('10 seconds later', dt)[0],
            datetime(2017, 1, 1, 13, 12, 40, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('15 minutes later', dt)[0],
            datetime(2017, 1, 1, 13, 27, 30, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('12 hours later', dt)[0],
            datetime(2017, 1, 2, 1, 12, 30, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('28 days later', dt)[0],
            datetime(2017, 1, 29, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('2 weeks later', dt)[0],
            datetime(2017, 1, 15, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('6 months later', dt)[0],
            datetime(2017, 7, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('10 years later', dt)[0],
            datetime(2027, 1, 1, tzinfo=default_timezone()))

    def test_extract_date_with_may_I_en(self):
        now = datetime(2019, 7, 4, 8, 1, 2, tzinfo=default_timezone())
        may_date = datetime(2019, 5, 2, 10, 11, 20, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('May I know what time it is tomorrow', now)[0],
            datetime(2019, 7, 5, 0, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('May I when 10 o\'clock is', now)[0],
            datetime(2019, 7, 4, 10, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('On 24th of may I want a reminder', may_date)[0],
            datetime(2019, 5, 24, 0, 0, 0, tzinfo=default_timezone()))

    def test_extract_weekend_en(self):
        dt = datetime(2017, 6, 1)  # thursday <- reference date
        self.assertEqual(
            extract_datetime('i have things to do next weekend', dt)[0],
            datetime(2017, 6, 3, tzinfo=default_timezone()))
        # TODO next saturday extraction seems to be wrong
        # datetime(2017, 6, 1) -> thursday
        # datetime(2017, 6, 3) -> saturday <- this should be extracted
        # datetime(2017, 6, 10) -> saturday  <- this is being extracted
        # self.assertEqual(
        #    extract_datetime('i have things to do next weekend', dt)[0],
        #    extract_datetime('i have things to do next saturday', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in a weekend', dt)[0],
            datetime(2017, 6, 5, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a weekend', dt)[0],
            extract_datetime('i have things to do next monday', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in 1 weekend', dt)[0],
            extract_datetime('i have things to do next monday', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in 1 weekend', dt)[0],
            datetime(2017, 6, 5, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in 2 weekends', dt)[0],
            datetime(2017, 6, 12, tzinfo=default_timezone()))

        self.assertEqual(
            extract_datetime('i had things to do last weekend', dt)[0],
            extract_datetime('i had things to do last saturday', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last weekend', dt)[0],
            datetime(2017, 5, 27, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do past weekend', dt)[0],
            datetime(2017, 5, 27, tzinfo=default_timezone()))

        self.assertEqual(
            extract_datetime('i had things to do a weekend ago', dt)[0],
            extract_datetime('i had things to do last friday', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do a weekend ago', dt)[0],
            datetime(2017, 5, 26, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do 2 weekends ago', dt)[0],
            datetime(2017, 5, 19, tzinfo=default_timezone()))

    def test_extract_next_en(self):
        dt = datetime(2017, 6, 1, 0, 0, 0)
        # next {timedelta unit}
        self.assertEqual(
            extract_datetime('i have things to do next second', dt)[0],
            datetime(2017, 6, 1, 0, 0, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do next minute', dt)[0],
            datetime(2017, 6, 1, 0, 1, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do next hour', dt)[0],
            datetime(2017, 6, 1, 1, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do next day', dt)[0],
            datetime(2017, 6, 2, tzinfo=default_timezone()))

        # 1st day of {calendar unit}
        self.assertEqual(
            extract_datetime('i have things to do next week', dt)[0],
            extract_datetime('i have things to do next monday', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do next week', dt)[0],
            datetime(2017, 6, 5, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do next month', dt)[0],
            datetime(2017, 7, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do next year', dt)[0],
            datetime(2018, 1, 1, tzinfo=default_timezone()))

        # old test moved here due to new disambiguation between "next week" and "in a week"
        # testExtract("remind me to call mom next week",
        #            "2017-07-04 00:00:00", "remind me to call mom")

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("remind me to call mom in a week",  # + 7 days
                    "2017-07-04 00:00:00", "remind me to call mom")
        testExtract("remind me to call mom next week",  # next monday
                    "2017-07-03 00:00:00", "remind me to call mom")

    def test_extract_in_en(self):
        dt = datetime(2017, 6, 1, 0, 0, 0)

        self.assertEqual(
            extract_datetime('i have things to do in a second', dt)[0],
            datetime(2017, 6, 1, 0, 0, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a minute', dt)[0],
            datetime(2017, 6, 1, 0, 1, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a minute', dt)[0],
            extract_datetime('i have things to do in 60 seconds', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in an hour', dt)[0],
            datetime(2017, 6, 1, 1, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a day', dt)[0],
            extract_datetime('i have things to do in 24 hours', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in a day', dt)[0],
            datetime(2017, 6, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a week', dt)[0],
            datetime(2017, 6, 8, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a week', dt)[0],
            extract_datetime('i have things to do in 7 days', dt)[0])
        self.assertEqual(
            extract_datetime('i have things to do in a month', dt)[0],
            datetime(2017, 7, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a year', dt)[0],
            datetime(2018, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in a year', dt)[0],
            extract_datetime('i have things to do in 365 days', dt)[0])

        self.assertEqual(
            extract_datetime('i have things to do in 1 day', dt)[0],
            datetime(2017, 6, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in 2 days', dt)[0],
            datetime(2017, 6, 3, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in 1 week', dt)[0],
            datetime(2017, 6, 8, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in 1 month', dt)[0],
            datetime(2017, 7, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i have things to do in 1 year', dt)[0],
            datetime(2018, 6, 1, tzinfo=default_timezone()))

    def test_extract_within_a_en(self):
        dt = datetime(2017, 6, 1, 0, 0, 0, tzinfo=default_timezone())

        self.assertEqual(extract_datetime('i have things to do within a second', dt)[0],
                         dt + timedelta(seconds=1))
        self.assertEqual(extract_datetime('i have things to do within a minute', dt)[0],
                         dt + timedelta(minutes=1))
        self.assertEqual(extract_datetime('i have things to do within an hour', dt)[0],
                         dt + timedelta(hours=1))
        self.assertEqual(extract_datetime('i have things to do within a day', dt)[0],
                         dt + timedelta(days=1))
        self.assertEqual(extract_datetime('i have things to do within a week', dt)[0],
                         dt + timedelta(days=7))
        self.assertEqual(extract_datetime('i have things to do within a month', dt)[0],
                         dt + timedelta(days=30))
        self.assertEqual(extract_datetime('i have things to do within a year', dt)[0],
                         dt + timedelta(days=365))

    @unittest.skip("currently can not disambiguate a/the because of normalization")
    def test_extract_within_the_en(self):
        # TODO we can not disambiguate a/the because of normalization
        # this is not really a LF problem but a mycroft problem... will give it a think
        #  "within a month" -> month is a timedelta of 30 days
        #  "with the month" -> before 1st day of next month

        dt = datetime(2017, 6, 1, 12, 30, 30, tzinfo=default_timezone())  # thursday  - weekday 3

        self.assertEqual(extract_datetime('i have things to do within the second', dt)[0],
                         dt.replace(second=dt.second + 1))
        self.assertEqual(extract_datetime('i have things to do within the second', dt)[0],
                         extract_datetime('i have things to do before the next second', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the minute', dt)[0],
                         dt.replace(minute=dt.minute + 1, second=0))
        self.assertEqual(extract_datetime('i have things to do within the minute', dt)[0],
                         extract_datetime('i have things to do before the next minute', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the hour', dt)[0],
                         dt.replace(hour=dt.hour + 1, minute=0, second=0))
        self.assertEqual(extract_datetime('i have things to do within the hour', dt)[0],
                         extract_datetime('i have things to do before the next hour', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the day', dt)[0],
                         dt.replace(day=dt.day + 1, hour=0, minute=0, second=0))
        self.assertEqual(extract_datetime('i have things to do within the day', dt)[0],
                         extract_datetime('i have things to do before the next day', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the month', dt)[0],
                         dt.replace(day=1, month=dt.month + 1, hour=0, minute=0, second=0))
        self.assertEqual(extract_datetime('i have things to do within the month', dt)[0],
                         extract_datetime('i have things to do before the next month', dt)[0])

        self.assertEqual(extract_datetime('i have things to do within the week', dt)[0],
                         extract_datetime('i have things to do before next week', dt)[0])  # next monday
        self.assertEqual(extract_datetime('i have things to do within the week', dt)[0],
                         extract_datetime('i have things to do before next monday', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the week', dt)[0],
                         dt.replace(day=dt.day + 7 - dt.weekday(), hour=0, minute=0, second=0))
        self.assertEqual(extract_datetime('i have things to do within the year', dt)[0],
                         extract_datetime('i have things to do before next year', dt)[0])
        self.assertEqual(extract_datetime('i have things to do within the year', dt)[0],
                         dt.replace(day=1, month=1, year=dt.year + 1, hour=0, minute=0, second=0))

    def test_extract_last_int_timeunit_en(self):
        dt = datetime(2017, 6, 1)
        self.assertEqual(
            extract_datetime('i wrote a lot of unittests in the past second', dt)[0],
            datetime(2017, 5, 31, 23, 59, 59, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i wrote a lot of unittests in the past minute', dt)[0],
            datetime(2017, 5, 31, 23, 59, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i wrote a lot of unittests in the past hour', dt)[0],
            datetime(2017, 5, 31, 23, 0, 0, tzinfo=default_timezone()))

        for i in range(1, 1500):
            expected = to_local(dt - timedelta(seconds=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} seconds', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} seconds', dt)[0],
                expected)

        for i in range(1, 1500):
            expected = to_local(dt - timedelta(minutes=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} minutes', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} minutes', dt)[0],
                expected)

        # this is also testing conflicts with military time,
        # the parser ignores 100 <= N <= 2400 unless there is a past_marker word
        for i in range(1, 1500):
            expected = to_local(dt - timedelta(hours=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} hours', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} hours', dt)[0],
                expected)

    def test_extract_last_int_dateunit_en(self):
        dt = datetime(2017, 6, 1)

        for i in range(1, 1500):
            expected = to_local(dt - timedelta(days=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} days', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} days', dt)[0],
                expected)

        for i in range(1, 1500):
            expected = to_local(dt - timedelta(days=i * 7))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} weeks', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} weeks', dt)[0],
                expected)

        for i in range(1, 150):
            expected = to_local(dt - relativedelta(months=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} months', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} months', dt)[0],
                expected)

        for i in range(1, 150):
            expected = to_local(dt - relativedelta(years=i))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} years', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} years', dt)[0],
                expected)

        for i in range(1, 150):
            expected = to_local(dt - relativedelta(years=i * 10))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} decades', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} decades', dt)[0],
                expected)

        for i in range(1, 15):
            expected = to_local(dt - relativedelta(years=i * 100))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} centuries', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} centuries', dt)[0],
                expected)

        for i in range(1, 2):
            expected = to_local(dt - relativedelta(years=i * 1000))
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the past {i} millenniums', dt)[0],
                expected)
            self.assertEqual(
                extract_datetime(f'i wrote a lot of unittests in the last {i} millenniums', dt)[0],
                expected)

    def test_extract_last_X_en(self):
        dt = datetime(2017, 6, 1)
        self.assertEqual(
            extract_datetime('i had things to do last second', dt)[0],
            datetime(2017, 5, 31, 23, 59, 59, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past second', dt)[0],
            extract_datetime('i had things to do last second', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last minute', dt)[0],
            datetime(2017, 5, 31, 23, 59, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past minute', dt)[0],
            extract_datetime('i had things to do last minute', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last hour', dt)[0],
            datetime(2017, 5, 31, 23, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past hour', dt)[0],
            extract_datetime('i had things to do last hour', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last day', dt)[0],
            datetime(2017, 5, 31, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past day', dt)[0],
            extract_datetime('i had things to do last day', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last week', dt)[0],
            datetime(2017, 5, 25, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past week', dt)[0],
            extract_datetime('i had things to do last week', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last month', dt)[0],
            datetime(2017, 5, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past month', dt)[0],
            extract_datetime('i had things to do last month', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last year', dt)[0],
            datetime(2016, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past year', dt)[0],
            extract_datetime('i had things to do last year', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last decade', dt)[0],
            datetime(2007, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past decade', dt)[0],
            extract_datetime('i had things to do last decade', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last century', dt)[0],
            datetime(1917, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past century', dt)[0],
            extract_datetime('i had things to do last century', dt)[0])
        self.assertEqual(
            extract_datetime('i had things to do last millennium', dt)[0],
            datetime(1017, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do the past millennium', dt)[0],
            extract_datetime('i had things to do last millennium', dt)[0])

    def test_extract_ago_en(self):
        dt = datetime(2017, 6, 1, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('i had things to do a day ago', dt)[0],
            datetime(2017, 5, 31, tzinfo=default_timezone()))
        for i in range(1, 1500):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} days ago', dt)[0],
                dt - timedelta(days=i))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} days earlier', dt)[0],
                dt - timedelta(days=i))

        self.assertEqual(
            extract_datetime('i had things to do a week ago', dt)[0],
            datetime(2017, 5, 25, tzinfo=default_timezone()))
        for i in range(1, 1500):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} weeks ago', dt)[0],
                dt - relativedelta(weeks=i))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} weeks earlier', dt)[0],
                dt - relativedelta(weeks=i))

        self.assertEqual(
            extract_datetime('i had things to do a month ago', dt)[0],
            datetime(2017, 5, 1, tzinfo=default_timezone()))
        for i in range(1, 1500):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} months ago', dt)[0],
                dt - relativedelta(months=i))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} months earlier', dt)[0],
                dt - relativedelta(months=i))

        self.assertEqual(
            extract_datetime('i had things to do a year ago', dt)[0],
            datetime(2016, 6, 1, tzinfo=default_timezone()))
        for i in range(1, 1500):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} years ago', dt)[0],
                dt - relativedelta(years=i))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} years earlier', dt)[0],
                dt - relativedelta(years=i))
        self.assertEqual(
            extract_datetime('i had things to do 2 years ago', dt)[0],
            datetime(2015, 6, 1, tzinfo=default_timezone()))

    def test_extract_centuries_ago_en(self):
        dt = datetime(2017, 6, 1, tzinfo=default_timezone())

        self.assertEqual(
            extract_datetime('i had things to do a decade ago', dt)[0],
            datetime(2007, 6, 1, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('i had things to do 2 decades ago', dt)[0],
            datetime(1997, 6, 1, tzinfo=default_timezone()))

        for i in range(1, 9):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} decades ago', dt)[0],
                dt - relativedelta(years=i * 10))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} decades earlier', dt)[0],
                dt - relativedelta(years=i * 10))

        for i in range(1, 9):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} centuries ago', dt)[0],
                dt - relativedelta(years=i * 100))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} centuries earlier', dt)[0],
                dt - relativedelta(years=i * 100))

        for i in range(1, 2):
            self.assertEqual(
                extract_datetime(f'i had things to do {i} millenniums ago', dt)[0],
                dt - relativedelta(years=i * 1000))
            self.assertEqual(
                extract_datetime(f'i had things to do {i} millenniums earlier', dt)[0],
                dt - relativedelta(years=i * 1000))

    def test_extract_with_other_tzinfo(self):
        local_tz = default_timezone()
        local_dt = datetime(2019, 7, 4, 7, 1, 2, tzinfo=local_tz)
        local_tz_offset = local_tz.utcoffset(local_dt)
        not_local_offset = local_tz_offset + timedelta(hours=1)
        not_local_tz = tz.tzoffset('TST', not_local_offset.total_seconds())
        not_local_dt = datetime(2019, 7, 4, 8, 1, 2, tzinfo=not_local_tz)
        test_dt, remainder = extract_datetime("now is the time", not_local_dt)
        self.assertEqual((test_dt.year, test_dt.month, test_dt.day,
                          test_dt.hour, test_dt.minute, test_dt.second,
                          test_dt.tzinfo),
                         (not_local_dt.year, not_local_dt.month, not_local_dt.day,
                          not_local_dt.hour, not_local_dt.minute, not_local_dt.second,
                          not_local_dt.tzinfo))
        self.assertNotEqual((test_dt.year, test_dt.month, test_dt.day,
                             test_dt.hour, test_dt.minute, test_dt.second,
                             test_dt.tzinfo),
                            (local_dt.year, local_dt.month, local_dt.day,
                             local_dt.hour, local_dt.minute, local_dt.second,
                             local_dt.tzinfo))

    def test_extract_relativedatetime_en(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("lets meet in 5 minutes",
                    "2017-06-27 10:06:02", "lets meet")
        testExtract("lets meet in 5minutes",
                    "2017-06-27 10:06:02", "lets meet")
        testExtract("lets meet in 5 seconds",
                    "2017-06-27 10:01:07", "lets meet")
        testExtract("lets meet in 1 hour",
                    "2017-06-27 11:01:02", "lets meet")
        testExtract("lets meet in 2 hours",
                    "2017-06-27 12:01:02", "lets meet")
        testExtract("lets meet in 2hours",
                    "2017-06-27 12:01:02", "lets meet")
        testExtract("lets meet in 1 minute",
                    "2017-06-27 10:02:02", "lets meet")
        testExtract("lets meet in 1 second",
                    "2017-06-27 10:01:03", "lets meet")
        testExtract("lets meet in 5seconds",
                    "2017-06-27 10:01:07", "lets meet")

    def test_normalize_numbers(self):
        self.assertEqual(normalize("remind me to do something at two to two"),
                         "remind me to do something at 2 to 2")
        self.assertEqual(normalize('what time will it be in two minutes'),
                         'what time will it be in 2 minutes')
        self.assertEqual(normalize('What time will it be in twenty two minutes'),
                         'What time will it be in 22 minutes')
        self.assertEqual(normalize("remind me to do something at twenty to two"),
                         "remind me to do something at 20 to 2")

        # TODO imperfect test, maybe should return 'my favorite numbers are 20 2',
        #  let is pass for now since this is likely a STT issue if ever
        #  encountered in the wild and is somewhat ambiguous, if this was
        #  spoken by a human the result is what we expect, if in written form
        #  it is ambiguous but could mean separate numbers
        self.assertEqual(normalize('my favorite numbers are twenty 2'),
                         'my favorite numbers are 22')
        # TODO imperfect test, same as above, fixing would impact
        #  extract_numbers quite a bit and require a non trivial ammount of
        #  refactoring
        self.assertEqual(normalize('my favorite numbers are 20 2'),
                         'my favorite numbers are 22')

        # test ordinals
        self.assertEqual(normalize('this is the first'),
                         'this is first')
        self.assertEqual(normalize('this is the first second'),
                         'this is first second')
        self.assertEqual(normalize('this is the first second and third'),
                         'this is first second and third')

        # test fractions
        self.assertEqual(normalize('whole hour'),
                         'whole hour')
        self.assertEqual(normalize('quarter hour'),
                         'quarter hour')
        self.assertEqual(normalize('halve hour'),
                         'halve hour')
        self.assertEqual(normalize('half hour'),
                         'half hour')

    def test_extract_date_with_number_words(self):
        now = datetime(2019, 7, 4, 8, 1, 2, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('What time will it be in 2 minutes', now)[0],
            datetime(2019, 7, 4, 8, 3, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('What time will it be in two minutes', now)[0],
            datetime(2019, 7, 4, 8, 3, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('What time will it be in two hundred minutes', now)[0],
            datetime(2019, 7, 4, 11, 21, 2, tzinfo=default_timezone()))

    def test_spaces(self):
        self.assertEqual(normalize("  this   is  a    test"),
                         "this is test")
        self.assertEqual(normalize("  this   is  a    test  "),
                         "this is test")
        self.assertEqual(normalize("  this   is  one    test"),
                         "this is 1 test")

    def test_numbers(self):
        self.assertEqual(normalize("this is a one two three  test"),
                         "this is 1 2 3 test")
        self.assertEqual(normalize("  it's  a four five six  test"),
                         "it is 4 5 6 test")
        self.assertEqual(normalize("it's  a seven eight nine test"),
                         "it is 7 8 9 test")
        self.assertEqual(normalize("it's a seven eight nine  test"),
                         "it is 7 8 9 test")
        self.assertEqual(normalize("that's a ten eleven twelve test"),
                         "that is 10 11 12 test")
        self.assertEqual(normalize("that's a thirteen fourteen test"),
                         "that is 13 14 test")
        self.assertEqual(normalize("that's fifteen sixteen seventeen"),
                         "that is 15 16 17")
        self.assertEqual(normalize("that's eighteen nineteen twenty"),
                         "that is 18 19 20")
        self.assertEqual(normalize("that's one nineteen twenty two"),
                         "that is 1 19 22")
        self.assertEqual(normalize("that's one hundred"),
                         "that is 100")
        self.assertEqual(normalize("that's one two twenty two"),
                         "that is 1 2 22")
        self.assertEqual(normalize("that's one and a half"),
                         "that is 1 and half")
        self.assertEqual(normalize("that's one and a half and five six"),
                         "that is 1 and half and 5 6")

    def test_multiple_numbers(self):
        self.assertEqual(extract_numbers("this is a one two three  test"),
                         [1.0, 2.0, 3.0])
        self.assertEqual(extract_numbers("it's  a four five six  test"),
                         [4.0, 5.0, 6.0])
        self.assertEqual(extract_numbers("this is a ten eleven twelve  test"),
                         [10.0, 11.0, 12.0])
        self.assertEqual(extract_numbers("this is a one twenty one  test"),
                         [1.0, 21.0])
        self.assertEqual(extract_numbers("1 dog, seven pigs, macdonald had a "
                                         "farm, 3 times 5 macarena"),
                         [1, 7, 3, 5])
        self.assertEqual(extract_numbers("two beers for two bears"),
                         [2.0, 2.0])
        self.assertEqual(extract_numbers("twenty 20 twenty"),
                         [20, 20, 20])
        self.assertEqual(extract_numbers("twenty 20 22"),
                         [20.0, 20.0, 22.0])
        self.assertEqual(extract_numbers("twenty twenty two twenty"),
                         [20, 22, 20])
        self.assertEqual(extract_numbers("twenty 2"),
                         [22.0])
        self.assertEqual(extract_numbers("twenty 20 twenty 2"),
                         [20, 20, 22])
        self.assertEqual(extract_numbers("third one"),
                         [1 / 3, 1])
        self.assertEqual(extract_numbers("third one", ordinals=True), [3])
        self.assertEqual(extract_numbers("six trillion", short_scale=True),
                         [6e12])
        self.assertEqual(extract_numbers("six trillion", short_scale=False),
                         [6e18])
        self.assertEqual(extract_numbers("two pigs and six trillion bacteria",
                                         short_scale=True), [2, 6e12])
        self.assertEqual(extract_numbers("two pigs and six trillion bacteria",
                                         short_scale=False), [2, 6e18])
        self.assertEqual(extract_numbers("thirty second or first",
                                         ordinals=True), [32, 1])
        self.assertEqual(extract_numbers("this is a seven eight nine and a"
                                         " half test"),
                         [7.0, 8.0, 9.5])

    def test_contractions(self):
        self.assertEqual(normalize("ain't"), "is not")
        self.assertEqual(normalize("aren't"), "are not")
        self.assertEqual(normalize("can't"), "can not")
        self.assertEqual(normalize("could've"), "could have")
        self.assertEqual(normalize("couldn't"), "could not")
        self.assertEqual(normalize("didn't"), "did not")
        self.assertEqual(normalize("doesn't"), "does not")
        self.assertEqual(normalize("don't"), "do not")
        self.assertEqual(normalize("gonna"), "going to")
        self.assertEqual(normalize("gotta"), "got to")
        self.assertEqual(normalize("hadn't"), "had not")
        self.assertEqual(normalize("hadn't have"), "had not have")
        self.assertEqual(normalize("hasn't"), "has not")
        self.assertEqual(normalize("haven't"), "have not")
        # TODO: Ambiguous with "he had"
        self.assertEqual(normalize("he'd"), "he would")
        self.assertEqual(normalize("he'll"), "he will")
        # TODO: Ambiguous with "he has"
        self.assertEqual(normalize("he's"), "he is")
        # TODO: Ambiguous with "how would"
        self.assertEqual(normalize("how'd"), "how did")
        self.assertEqual(normalize("how'll"), "how will")
        # TODO: Ambiguous with "how has" and "how does"
        self.assertEqual(normalize("how's"), "how is")
        # TODO: Ambiguous with "I had"
        self.assertEqual(normalize("I'd"), "I would")
        self.assertEqual(normalize("I'll"), "I will")
        self.assertEqual(normalize("I'm"), "I am")
        self.assertEqual(normalize("I've"), "I have")
        self.assertEqual(normalize("I haven't"), "I have not")
        self.assertEqual(normalize("isn't"), "is not")
        self.assertEqual(normalize("it'd"), "it would")
        self.assertEqual(normalize("it'll"), "it will")
        # TODO: Ambiguous with "it has"
        self.assertEqual(normalize("it's"), "it is")
        self.assertEqual(normalize("it isn't"), "it is not")
        self.assertEqual(normalize("mightn't"), "might not")
        self.assertEqual(normalize("might've"), "might have")
        self.assertEqual(normalize("mustn't"), "must not")
        self.assertEqual(normalize("mustn't have"), "must not have")
        self.assertEqual(normalize("must've"), "must have")
        self.assertEqual(normalize("needn't"), "need not")
        self.assertEqual(normalize("oughtn't"), "ought not")
        self.assertEqual(normalize("shan't"), "shall not")
        # TODO: Ambiguous wiht "she had"
        self.assertEqual(normalize("she'd"), "she would")
        self.assertEqual(normalize("she hadn't"), "she had not")
        self.assertEqual(normalize("she'll"), "she will")
        self.assertEqual(normalize("she's"), "she is")
        self.assertEqual(normalize("she isn't"), "she is not")
        self.assertEqual(normalize("should've"), "should have")
        self.assertEqual(normalize("shouldn't"), "should not")
        self.assertEqual(normalize("shouldn't have"), "should not have")
        self.assertEqual(normalize("somebody's"), "somebody is")
        # TODO: Ambiguous with "someone had"
        self.assertEqual(normalize("someone'd"), "someone would")
        self.assertEqual(normalize("someone hadn't"), "someone had not")
        self.assertEqual(normalize("someone'll"), "someone will")
        # TODO: Ambiguous with "someone has"
        self.assertEqual(normalize("someone's"), "someone is")
        self.assertEqual(normalize("that'll"), "that will")
        # TODO: Ambiguous with "that has"
        self.assertEqual(normalize("that's"), "that is")
        # TODO: Ambiguous with "that had"
        self.assertEqual(normalize("that'd"), "that would")
        # TODO: Ambiguous with "there had"
        self.assertEqual(normalize("there'd"), "there would")
        self.assertEqual(normalize("there're"), "there are")
        # TODO: Ambiguous with "there has"
        self.assertEqual(normalize("there's"), "there is")
        # TODO: Ambiguous with "they had"
        self.assertEqual(normalize("they'd"), "they would")
        self.assertEqual(normalize("they'll"), "they will")
        self.assertEqual(normalize("they won't have"), "they will not have")
        self.assertEqual(normalize("they're"), "they are")
        self.assertEqual(normalize("they've"), "they have")
        self.assertEqual(normalize("they haven't"), "they have not")
        self.assertEqual(normalize("wasn't"), "was not")
        # TODO: Ambiguous wiht "we had"
        self.assertEqual(normalize("we'd"), "we would")
        self.assertEqual(normalize("we would've"), "we would have")
        self.assertEqual(normalize("we wouldn't"), "we would not")
        self.assertEqual(normalize("we wouldn't have"), "we would not have")
        self.assertEqual(normalize("we'll"), "we will")
        self.assertEqual(normalize("we won't have"), "we will not have")
        self.assertEqual(normalize("we're"), "we are")
        self.assertEqual(normalize("we've"), "we have")
        self.assertEqual(normalize("weren't"), "were not")
        self.assertEqual(normalize("what'd"), "what did")
        self.assertEqual(normalize("what'll"), "what will")
        self.assertEqual(normalize("what're"), "what are")
        # TODO: Ambiguous with "what has" / "what does")
        self.assertEqual(normalize("whats"), "what is")
        self.assertEqual(normalize("what's"), "what is")
        self.assertEqual(normalize("what've"), "what have")
        # TODO: Ambiguous with "when has"
        self.assertEqual(normalize("when's"), "when is")
        self.assertEqual(normalize("where'd"), "where did")
        # TODO: Ambiguous with "where has" / where does"
        self.assertEqual(normalize("where's"), "where is")
        self.assertEqual(normalize("where've"), "where have")
        # TODO: Ambiguous with "who had" "who did")
        self.assertEqual(normalize("who'd"), "who would")
        self.assertEqual(normalize("who'd've"), "who would have")
        self.assertEqual(normalize("who'll"), "who will")
        self.assertEqual(normalize("who're"), "who are")
        # TODO: Ambiguous with "who has" / "who does"
        self.assertEqual(normalize("who's"), "who is")
        self.assertEqual(normalize("who've"), "who have")
        self.assertEqual(normalize("why'd"), "why did")
        self.assertEqual(normalize("why're"), "why are")
        # TODO: Ambiguous with "why has" / "why does"
        self.assertEqual(normalize("why's"), "why is")
        self.assertEqual(normalize("won't"), "will not")
        self.assertEqual(normalize("won't've"), "will not have")
        self.assertEqual(normalize("would've"), "would have")
        self.assertEqual(normalize("wouldn't"), "would not")
        self.assertEqual(normalize("wouldn't've"), "would not have")
        self.assertEqual(normalize("ya'll"), "you all")
        self.assertEqual(normalize("y'all"), "you all")
        self.assertEqual(normalize("y'ain't"), "you are not")
        # TODO: Ambiguous with "you had"
        self.assertEqual(normalize("you'd"), "you would")
        self.assertEqual(normalize("you'd've"), "you would have")
        self.assertEqual(normalize("you'll"), "you will")
        self.assertEqual(normalize("you're"), "you are")
        self.assertEqual(normalize("you aren't"), "you are not")
        self.assertEqual(normalize("you've"), "you have")
        self.assertEqual(normalize("you haven't"), "you have not")

    def test_combinations(self):
        self.assertEqual(normalize("I couldn't have guessed there'd be two"),
                         "I could not have guessed there would be 2")
        self.assertEqual(normalize("I wouldn't have"), "I would not have")
        self.assertEqual(normalize("I hadn't been there"),
                         "I had not been there")
        self.assertEqual(normalize("I would've"), "I would have")
        self.assertEqual(normalize("it hadn't"), "it had not")
        self.assertEqual(normalize("it hadn't have"), "it had not have")
        self.assertEqual(normalize("it would've"), "it would have")
        self.assertEqual(normalize("she wouldn't have"), "she would not have")
        self.assertEqual(normalize("she would've"), "she would have")
        self.assertEqual(normalize("someone wouldn't have"),
                         "someone would not have")
        self.assertEqual(normalize("someone would've"), "someone would have")
        self.assertEqual(normalize("what's the weather like"),
                         "what is weather like")
        self.assertEqual(normalize("that's what I told you"),
                         "that is what I told you")

        self.assertEqual(normalize("whats 8 + 4"), "what is 8 + 4")

    # TODO not localized; needed in english?
    def test_gender(self):
        self.assertRaises((AttributeError, FunctionNotLocalizedError),
                          get_gender, "person", None)


class TestYesNo(unittest.TestCase):
    def test_yesno(self):

        def test_utt(text, expected):
            res = yes_or_no(text, "en-us")
            self.assertEqual(res, expected)

        test_utt("yes", True)
        test_utt("no", False)
        test_utt("don't think so", False)
        test_utt("i think not", False)
        test_utt("that's affirmative", True)
        test_utt("beans", None)
        test_utt("no, but actually, yes", True)
        test_utt("yes, but actually, no", False)
        test_utt("yes, yes, yes, but actually, no", False)
        test_utt("please", True)
        test_utt("please don't", False)

        # test "neutral_yes" -> only count as yes word if there isn't a "no" in sentence
        test_utt("no! please! I beg you", False)
        test_utt("yes, i don't want it for sure", False)
        test_utt("please! I beg you", True)
        test_utt("i want it for sure", True)
        test_utt("obviously", True)
        test_utt("indeed", True)
        test_utt("no, I obviously hate it", False)

        # test "neutral_no" -> only count as no word if there isn't a "yes" in sentence
        test_utt("do I hate it when companies sell my data? yes, that's certainly undesirable", True)
        test_utt("that's certainly undesirable", False)
        test_utt("yes, it's a lie", True)
        test_utt("no, it's a lie", False)
        test_utt("he is lying", False)
        test_utt("correct, he is lying", True)
        test_utt("it's a lie", False)
        test_utt("you are mistaken", False)
        test_utt("that's a mistake", False)
        test_utt("wrong answer", False)

        # test double negation
        test_utt("it's not a lie", True)
        test_utt("he is not lying", True)
        test_utt("you are not mistaken", True)
        test_utt("tou are not wrong", True)


class TestLangcode(unittest.TestCase):
    def test_parse_lang_code(self):

        def test_with_conf(text, expected_lang, min_conf=0.8):
            lang, conf = extract_langcode(text)
            self.assertEqual(lang, expected_lang)
            self.assertGreaterEqual(conf, min_conf)

        test_with_conf("English", 'en', 1.0)
        test_with_conf("Portuguese", 'pt', 1.0)

    def test_parse_lang2_code(self):
        def test_with_conf(text, expected_lang, min_conf=0.8):
            lang, conf = extract_langcode(text)
            self.assertEqual(lang, expected_lang)
            self.assertGreaterEqual(conf, min_conf)

        # TODO should be "pt-br", but let it pass for now
        test_with_conf("Brazilian Portuguese", 'pt')
        # TODO should be "en-us", but let it pass for now
        test_with_conf("American English", 'en')

        test_with_conf("Brazilian", 'pt-br')
        test_with_conf("American", 'en-us')


class TestExtractDate(unittest.TestCase):
    ref_date = date(2117, 2, 3)
    now = now_local()
    default_time = now.time()

    def _test_date(self, date_str, expected_date,
                   resolution=DateTimeResolution.DAY,
                   anchor=None, hemi=Hemisphere.NORTH, greedy=False):
        anchor = anchor or self.ref_date
        if isinstance(expected_date, datetime):
            expected_date = expected_date.date()
        extracted_date, remainder = extract_date_en(date_str, anchor,
                                                    resolution,
                                                    hemisphere=hemi,
                                                    greedy=greedy)

        # print("expected   | extracted  | input")
        # print(expected_date, "|", extracted_date, "|", date_str, )
        # print(date_str, "///", remainder)
        self.assertEqual(extracted_date, expected_date)

    def test_now(self):
        self._test_date("now", self.now)
        self._test_date("today", self.ref_date)
        self._test_date("tomorrow", self.ref_date + relativedelta(days=1))
        self._test_date("yesterday", self.ref_date - relativedelta(days=1))
        self._test_date("twenty two thousand days before now",
                        self.now - relativedelta(days=22000))
        self._test_date("10 days from now",
                        self.now + relativedelta(days=10))

    def test_duration_ago(self):
        self._test_date("twenty two weeks ago",
                        self.ref_date - relativedelta(weeks=22))
        self._test_date("twenty two months ago",
                        self.ref_date - relativedelta(months=22))
        self._test_date("twenty two decades ago",
                        self.ref_date - relativedelta(years=10 * 22))
        self._test_date("1 century ago",
                        self.ref_date - relativedelta(years=100))
        self._test_date("ten centuries ago",
                        self.ref_date - relativedelta(years=1000))
        self._test_date("two millenniums ago",
                        self.ref_date - relativedelta(years=2000))
        self._test_date("twenty two thousand days ago",
                        self.ref_date - relativedelta(days=22000))
        # years BC not supported
        self.assertRaises(ValueError, extract_date_en,
                          "twenty two thousand years ago", self.ref_date)

    def test_spoken_date(self):
        self._test_date("13 may 1992", date(month=5, year=1992, day=13))
        self._test_date("march 1st 2020", date(month=3, year=2020, day=1))
        self._test_date("29 november", date(month=11,
                                            year=self.ref_date.year,
                                            day=29))
        self._test_date("january 2020", date(month=1,
                                             year=2020,
                                             day=1))
        self._test_date("day 1", date(month=self.ref_date.month,
                                      year=self.ref_date.year,
                                      day=1))
        self._test_date("1 of september",
                        self.ref_date.replace(day=1, month=9,
                                              year=self.ref_date.year))
        self._test_date("march 13th",
                        self.ref_date.replace(day=13, month=3,
                                              year=self.ref_date.year))
        self._test_date("12 may",
                        self.ref_date.replace(day=12, month=5,
                                              year=self.ref_date.year))

    def test_from(self):
        self._test_date("10 days from today",
                        self.ref_date + relativedelta(days=10))
        self._test_date("10 days from tomorrow",
                        self.ref_date + relativedelta(days=11))
        self._test_date("10 days from yesterday",
                        self.ref_date + relativedelta(days=9))
        # self._test_date("10 days from after tomorrow",  # TODO fix me
        #          self.ref_date + relativedelta(days=12))

        # years > 9999 not supported
        self.assertRaises(ValueError, extract_date_en,
                          "twenty two million years from now", self.ref_date)

    def test_ordinals(self):
        self._test_date("the 5th day", self.ref_date.replace(day=5))
        self._test_date("the fifth day",
                        date(month=self.ref_date.month,
                             year=self.ref_date.year, day=5))
        self._test_date("the 20th day of 4th month",
                        self.ref_date.replace(month=4, day=20))
        self._test_date("the 20th day of month 4",
                        self.ref_date.replace(month=4, day=20))
        self._test_date("6th month of 1992", date(month=6, year=1992, day=1))
        self._test_date("first day of the 10th month of 1969",
                        self.ref_date.replace(day=1, month=10, year=1969))
        self._test_date("2nd day of 2020",
                        self.ref_date.replace(day=2, month=1, year=2020))
        self._test_date("300 day of 2020",
                        self.ref_date.replace(day=1, month=1, year=2020) +
                        relativedelta(days=299))

    def test_plus(self):
        self._test_date("now plus 10 days",
                        self.now + relativedelta(days=10))
        self._test_date("today plus 10 days",
                        self.ref_date + relativedelta(days=10))
        self._test_date("yesterday plus 10 days",
                        self.ref_date + relativedelta(days=9))
        self._test_date("tomorrow plus 10 days",
                        self.ref_date + relativedelta(days=11))
        self._test_date("today plus 10 months",
                        self.ref_date + relativedelta(months=10))
        self._test_date("today plus 10 years",
                        self.ref_date + relativedelta(years=10))
        self._test_date("today plus 10 years, 10 months and 1 day",
                        self.ref_date + relativedelta(
                            days=1, months=10, years=10))
        # TODO Fix me
        # self._test_date("tomorrow + 10 days",
        #           self.ref_date + relativedelta(days=11))

    def test_minus(self):
        self._test_date("now minus 10 days",
                        self.now - relativedelta(days=10))
        self._test_date("today minus 10 days",
                        self.ref_date - relativedelta(days=10))
        # TODO fix me
        # self._test_date("today - 10 days",
        #           self.ref_date - relativedelta(days=10))
        # self._test_date("yesterday - 10 days",
        #           self.ref_date - relativedelta(days=11))
        # self._test_date("today - 10 years",
        #            self.ref_date.replace(year=self.ref_date.year - 10))

        self._test_date("tomorrow minus 10 days",
                        self.ref_date - relativedelta(days=9))
        self._test_date("today minus 10 months",
                        self.ref_date - relativedelta(months=10))
        self._test_date("today minus 10 years, 10 months and 1 day",
                        self.ref_date - relativedelta(days=1, months=10,
                                                      years=10))

    def test_timedelta_fallback(self):
        self._test_date("now plus 10 months",
                        self.now + relativedelta(months=10))
        self._test_date("today plus 10.5 months",
                        self.ref_date + timedelta(days=10.5 * DAYS_IN_1_MONTH))
        self._test_date("now plus 10 years",
                        self.now + relativedelta(years=10))
        self._test_date("today plus 10.5 years",
                        self.ref_date + timedelta(days=10.5 * DAYS_IN_1_YEAR))

    def test_before(self):
        # before -> nearest DateResolution.XXX
        self._test_date("before today",
                        self.ref_date - relativedelta(days=1))
        self._test_date("before tomorrow", self.ref_date)
        self._test_date("before yesterday",
                        self.ref_date - relativedelta(days=2))
        self._test_date("before march 12",
                        self.ref_date.replace(month=3, day=11))

        self._test_date("before 1992", date(year=1991, month=12, day=31))
        self._test_date("before 1992", date(year=1991, day=1, month=1),
                        DateTimeResolution.YEAR)
        self._test_date("before 1992", date(year=1990, day=1, month=1),
                        DateTimeResolution.DECADE)
        self._test_date("before 1992", date(year=1900, day=1, month=1),
                        DateTimeResolution.CENTURY)

        self._test_date("before april",
                        date(month=3, day=31, year=self.ref_date.year))
        self._test_date("before april",
                        date(month=1, day=1, year=self.ref_date.year - 1),
                        DateTimeResolution.YEAR)
        self._test_date("before april",
                        date(month=1, day=1, year=2110),
                        DateTimeResolution.DECADE)

        self._test_date("before april 1992",
                        date(month=3, day=31, year=1992))
        self._test_date("before april 1992",
                        date(month=1, day=1, year=1991),
                        DateTimeResolution.YEAR)
        self._test_date("before april 1992",
                        date(month=1, day=1, year=1990),
                        DateTimeResolution.DECADE)

    def test_after(self):
        # after -> next DateResolution.XXX
        self._test_date("after today",
                        self.ref_date + relativedelta(days=1))
        self._test_date("after yesterday", self.ref_date)
        self._test_date("after tomorrow",
                        self.ref_date + relativedelta(days=2))

        self._test_date("after today",
                        self.ref_date.replace(day=8),
                        DateTimeResolution.WEEK)
        self._test_date("after today",
                        date(day=1, month=self.ref_date.month + 1,
                             year=self.ref_date.year),
                        DateTimeResolution.MONTH)
        self._test_date("after tomorrow",
                        date(day=1, month=1, year=2120),
                        DateTimeResolution.DECADE)

        self._test_date("after march 12",
                        self.ref_date.replace(month=3, day=12) +
                        relativedelta(days=1))

        self._test_date("after 1992", date(year=1992, day=2, month=1))
        self._test_date("after 1992", date(year=1992, day=6, month=1),
                        DateTimeResolution.WEEK)
        self._test_date("after 1992", date(year=1992, day=1, month=2),
                        DateTimeResolution.MONTH)
        self._test_date("after 1992", date(year=1993, day=1, month=1),
                        DateTimeResolution.YEAR)
        self._test_date("after 1992", date(year=2000, day=1, month=1),
                        DateTimeResolution.DECADE)
        self._test_date("after 1992", date(year=2000, day=1, month=1),
                        DateTimeResolution.CENTURY)
        self._test_date("after 1992", date(year=2000, day=1, month=1),
                        DateTimeResolution.MILLENNIUM)

        self._test_date("after april",
                        date(day=2, month=4, year=self.ref_date.year))
        self._test_date("after april",
                        date(day=1, month=4, year=self.ref_date.year) +
                        relativedelta(days=1))
        self._test_date("after april",
                        date(year=self.ref_date.year, day=5, month=4),
                        DateTimeResolution.WEEK)
        self._test_date("after april",
                        date(year=self.ref_date.year, day=1, month=5),
                        DateTimeResolution.MONTH)
        self._test_date("after april", date(year=2120, day=1, month=1),
                        DateTimeResolution.DECADE)

        self._test_date("after april 1992", date(year=1992, day=1, month=5),
                        DateTimeResolution.MONTH)
        self._test_date("after april 1992", date(year=1993, day=1, month=1),
                        DateTimeResolution.YEAR)
        self._test_date("after april 1992", date(year=2000, day=1, month=1),
                        DateTimeResolution.CENTURY)

        self._test_date("after 2600", date(year=2600, day=2, month=1))
        self._test_date("after 2600", date(year=2600, day=1, month=2),
                        DateTimeResolution.MONTH)
        self._test_date("after 2600", date(year=2601, day=1, month=1),
                        DateTimeResolution.YEAR)

        self._test_date("after 2600", date(year=2610, day=1, month=1),
                        DateTimeResolution.DECADE)
        self._test_date("after 2600", date(year=2700, day=1, month=1),
                        DateTimeResolution.CENTURY)

    def test_this(self):
        _current_century = ((self.ref_date.year // 100) - 1) * 100
        _current_decade = (self.ref_date.year // 10) * 10

        self._test_date("this month", self.ref_date.replace(day=1))
        self._test_date("this week", self.ref_date - relativedelta(
            days=self.ref_date.weekday()))
        self._test_date("this year", self.ref_date.replace(day=1, month=1))
        self._test_date("current year", self.ref_date.replace(day=1, month=1))
        self._test_date("present day", self.ref_date)
        self._test_date("current decade", date(day=1, month=1, year=2110))
        self._test_date("current century", date(day=1, month=1, year=2100))
        self._test_date("this millennium", date(day=1, month=1, year=2000))

    def test_next(self):
        self._test_date("next month",
                        (self.ref_date + relativedelta(
                            days=DAYS_IN_1_MONTH)).replace(day=1))
        self._test_date("next week",
                        get_week_range(self.ref_date + relativedelta(weeks=1))[
                            0])
        self._test_date("next century",
                        date(year=2200, day=1, month=1))
        self._test_date("next year",
                        date(year=self.ref_date.year + 1, day=1, month=1))

    def test_last(self):
        self._test_date("last month",
                        (self.ref_date - relativedelta(
                            days=DAYS_IN_1_MONTH)).replace(day=1))
        self._test_date("last week",
                        get_week_range(self.ref_date - relativedelta(weeks=1))[
                            0])
        self._test_date("last year", date(year=self.ref_date.year - 1,
                                          day=1,
                                          month=1))
        self._test_date("last century", date(year=2000, day=1, month=1))

        self._test_date("last day of the 10th century",
                        date(day=31, month=12, year=999))

        self._test_date("last day of this month",
                        self.ref_date.replace(day=28))
        self._test_date("last day of the month",
                        self.ref_date.replace(day=28))

        self._test_date("last day of this year",
                        date(day=31, month=12, year=self.ref_date.year))
        self._test_date("last day of the year",
                        date(day=31, month=12, year=self.ref_date.year))

        self._test_date("last day of this century",
                        date(day=31, month=12, year=2199))
        self._test_date("last day of the century",
                        date(day=31, month=12, year=2199))

        self._test_date("last day of this decade",
                        date(day=31, month=12, year=2119))
        self._test_date("last day of the decade",
                        date(day=31, month=12, year=2119))
        self._test_date("last day of this millennium",
                        date(day=31, month=12, year=2999))
        self._test_date("last day of the millennium",
                        date(day=31, month=12, year=2999))
        self._test_date("last day of the 20th month of the 5th millennium",
                        date(year=4000, day=31, month=1) +
                        relativedelta(months=19))
        self._test_date("last day of the 9th decade of the 5th millennium",
                        date(day=31, month=12, year=4089))
        self._test_date("last day of the 10th millennium",
                        date(day=31, month=12, year=9999))

    def test_first(self):
        self._test_date("first day", self.ref_date.replace(day=1))
        self._test_date("first day of this month",
                        self.ref_date.replace(day=1))
        self._test_date("first day of this year",
                        self.ref_date.replace(day=1, month=1))
        self._test_date("first day of this decade", date(day=1, month=1,
                                                         year=2110))
        self._test_date("first day of this century", date(day=1, month=1,
                                                          year=2100))
        self._test_date("first day of this millennium", date(day=1, month=1,
                                                             year=2000))

        self._test_date("first month", self.ref_date.replace(day=1, month=1))

        self._test_date("first decade", date(year=1, day=1, month=1))
        self._test_date("first year", date(year=1, day=1, month=1))
        self._test_date("first century", date(year=1, day=1, month=1))

        self._test_date("first day of the 10th century",
                        date(day=1, month=1, year=900))

        self._test_date("first day of the month",
                        self.ref_date.replace(day=1))
        self._test_date("first day of the year",
                        date(day=1, month=1, year=self.ref_date.year))

        self._test_date("first day of the century",
                        date(day=1, month=1, year=2100))
        self._test_date("first day of the decade",
                        date(day=1, month=1, year=2110))
        self._test_date("first day of the millennium",
                        date(day=1, month=1, year=2000))

        self._test_date("first day of the 10th millennium",
                        date(day=1, month=1, year=9000))

    def test_seasons(self):
        _ref_season = date_to_season(self.ref_date)
        self.assertEqual(_ref_season, Season.WINTER)

        # TODO start/end of season/winter/summer/fall/spring...

        def _test_season_north(test_date, expected_date, season):
            self._test_date(test_date, expected_date, hemi=Hemisphere.NORTH)
            self.assertEqual(date_to_season(expected_date,
                                            hemisphere=Hemisphere.NORTH),
                             season)

        def _test_season_south(test_date, expected_date, season):
            self._test_date(test_date, expected_date, hemi=Hemisphere.SOUTH)
            self.assertEqual(date_to_season(expected_date,
                                            hemisphere=Hemisphere.SOUTH),
                             season)

        # test "season" literal
        _test_season_north("this season",
                           date(day=1, month=12, year=self.ref_date.year - 1),
                           _ref_season)
        _test_season_north("next season",
                           date(day=1, month=3, year=self.ref_date.year),
                           Season.SPRING)

        _test_season_north("last season",
                           date(day=1, month=9, year=self.ref_date.year - 1),
                           Season.FALL)

        # test named season in {hemisphere}
        _test_season_north("this spring in north hemisphere",
                           self.ref_date.replace(day=1, month=3),
                           Season.SPRING)
        _test_season_north("this spring in northern hemisphere",
                           self.ref_date.replace(day=1, month=3),
                           Season.SPRING)

        _test_season_south("this spring in south hemisphere",
                           self.ref_date.replace(day=1, month=9),
                           Season.SPRING)
        _test_season_south("this spring in southern hemisphere",
                           self.ref_date.replace(day=1, month=9),
                           Season.SPRING)

        try:
            import simple_NER

            # test named season in {country}
            _test_season_north("this spring in Portugal",
                               self.ref_date.replace(day=1, month=3),
                               Season.SPRING)
            _test_season_north("last spring in Portugal",
                               date(day=1, month=3,
                                    year=self.ref_date.year - 1),
                               Season.SPRING)
            _test_season_north("next winter in Portugal",
                               date(day=1, month=12,
                                    year=self.ref_date.year),
                               Season.WINTER)

            _test_season_south("this spring in Brazil",
                               self.ref_date.replace(day=1, month=9),
                               Season.SPRING)
            _test_season_south("next winter in Brazil",
                               self.ref_date.replace(day=1, month=6),
                               Season.WINTER)

            # test named season in {capital city}
            _test_season_north("this spring in Lisbon",
                               self.ref_date.replace(day=1, month=3),
                               Season.SPRING)
            _test_season_south("this spring in Canberra",
                               self.ref_date.replace(day=1, month=9),
                               Season.SPRING)

        except ImportError:
            print("Could not test location tagging")

        # test named season
        _test_season_north("winter is coming",
                           self.ref_date.replace(day=1, month=12),
                           Season.WINTER)

        _test_season_north("spring",
                           self.ref_date.replace(day=1, month=3),
                           Season.SPRING)
        _test_season_north("spring of 1991",
                           date(day=1, month=3, year=1991),
                           Season.SPRING)
        _test_season_south("summer of 1969",
                           date(day=1, month=12, year=1969),
                           Season.SUMMER)

        _test_season_north("this spring",
                           self.ref_date.replace(day=1, month=3),
                           Season.SPRING)
        _test_season_south("this spring",
                           self.ref_date.replace(day=1, month=9),
                           Season.SPRING)

        _test_season_north("next spring",
                           self.ref_date.replace(day=1, month=3),
                           Season.SPRING)
        _test_season_south("next spring",
                           self.ref_date.replace(day=1, month=9),
                           Season.SPRING)

        _test_season_north("last spring",
                           date(day=1, month=3, year=self.ref_date.year - 1),
                           Season.SPRING)
        _test_season_south("last spring",
                           date(day=1, month=9, year=self.ref_date.year - 1),
                           Season.SPRING)

        _test_season_north("this summer",
                           self.ref_date.replace(day=1, month=6),
                           Season.SUMMER)
        _test_season_north("next summer",
                           self.ref_date.replace(day=1, month=6),
                           Season.SUMMER)
        _test_season_north("last summer", date(day=1, month=6,
                                               year=self.ref_date.year - 1),
                           Season.SUMMER)

        _test_season_north("this fall", self.ref_date.replace(day=1, month=9),
                           Season.FALL)
        _test_season_north("next fall", self.ref_date.replace(day=1, month=9),
                           Season.FALL)
        _test_season_north("last autumn",
                           date(day=1, month=9, year=self.ref_date.year - 1),
                           Season.FALL)

        _test_season_north("this winter",
                           self.ref_date.replace(day=1, month=12),
                           Season.WINTER)
        _test_season_north("next winter",
                           self.ref_date.replace(day=1, month=12),
                           Season.WINTER)
        _test_season_north("last winter",
                           self.ref_date.replace(day=1, month=12,
                                                 year=self.ref_date.year - 1),
                           Season.WINTER)

    def test_weekends(self):
        # TODO plus / minus / after N weekends
        # TODO N weekends ago
        saturday, sunday = get_weekend_range(self.ref_date)
        assert saturday.weekday() == 5
        assert sunday.weekday() == 6

        self._test_date("this weekend", saturday)
        self._test_date("next weekend", saturday)
        self._test_date("last weekend", saturday - relativedelta(days=7))

        self._test_date("this weekend", saturday,
                        anchor=saturday)
        self._test_date("this weekend", saturday,
                        anchor=sunday)
        self._test_date("next weekend", saturday + relativedelta(days=7),
                        anchor=saturday)
        self._test_date("next weekend", saturday + relativedelta(days=7),
                        anchor=sunday)
        self._test_date("last weekend", saturday - relativedelta(days=7),
                        anchor=saturday)
        self._test_date("last weekend", saturday - relativedelta(days=7),
                        anchor=sunday)

    def test_is(self):
        self._test_date("the year is 2100", date(year=2100, month=1, day=1))
        self._test_date("the year was 1969", date(year=1969, month=1, day=1))
        self._test_date("the day is 2", self.ref_date.replace(day=2))
        self._test_date("the month is 8",
                        self.ref_date.replace(month=8, day=1))

        self._test_date("this is the second day of the third "
                        "month of the first year of the 9th millennium,",
                        date(day=2, month=3, year=8000))
        self._test_date("this is the second day of the third "
                        "month of the 9th millennium,",
                        date(day=2, month=3, year=8000))

    def test_of(self):
        self._test_date("first day of the first millennium",
                        date(day=1, month=1, year=1))
        self._test_date("first day of the first century",
                        date(day=1, month=1, year=1))
        self._test_date("first day of the first decade",
                        date(day=1, month=1, year=1))
        self._test_date("first day of the first year",
                        date(day=1, month=1, year=1))

        self._test_date("first day of the first week",
                        date(day=1, month=1, year=self.ref_date.year))

        self._test_date("3rd day",
                        self.ref_date.replace(day=3))
        self._test_date("3rd day of may",
                        self.ref_date.replace(day=3, month=5))
        self._test_date("3rd day of the 5th century",
                        date(day=3, month=1, year=400))
        self._test_date("3rd day of the 5th month of the 10 century",
                        date(day=3, month=5, year=900))
        self._test_date("25th month of the 10 century",
                        date(day=1, month=1, year=902))
        self._test_date("3rd day of the 25th month of the 10 century",
                        date(day=3, month=1, year=902))
        self._test_date("3rd day of 1973",
                        date(day=3, month=1, year=1973))
        self._test_date("3rd day of the 17th decade",
                        date(day=3, month=1, year=160))
        self._test_date("3rd day of the 10th millennium",
                        date(day=3, month=1, year=9000))
        self._test_date("301st day of the 10th century",
                        date(day=28, month=10, year=900))
        self._test_date("first century of the 6th millennium",
                        date(day=1, month=1, year=5000))
        self._test_date("first decade of the 6th millennium",
                        date(day=1, month=1, year=5000))
        self._test_date("39th decade of the 6th millennium",
                        date(day=1, month=1, year=5380))
        self._test_date("the 20th year of the 6th millennium",
                        date(day=1, month=1, year=5019))
        self._test_date("the 20th day of the 6th millennium",
                        date(day=20, month=1, year=5000))
        self._test_date("last day of the 39th decade of the 6th millennium",
                        date(day=31, month=12, year=5389))

    def test_months(self):
        self._test_date("january", self.ref_date.replace(day=1, month=1))
        self._test_date("last january", self.ref_date.replace(day=1, month=1))
        self._test_date("next january", date(day=1, month=1,
                                             year=self.ref_date.year + 1))

        self._test_date("in 29 november", date(day=29, month=11,
                                               year=self.ref_date.year))
        self._test_date("last november 27", date(day=27, month=11,
                                                 year=self.ref_date.year - 1))
        self._test_date("next 3 november", date(day=3, month=11,
                                                year=self.ref_date.year))
        self._test_date("last 3 november 1872",
                        date(day=3, month=11, year=1872))

    def test_week(self):

        def _test_week(date_str, expected_date, anchor=self.ref_date):
            extracted, _ = extract_date_en(date_str, anchor)
            self.assertEqual(extracted, expected_date)
            # NOTE: weeks start on sunday
            # TODO start on thursdays?
            self.assertEqual(extracted.weekday(), 0)

        _test_week("this week", self.ref_date.replace(day=1))
        _test_week("next week", self.ref_date.replace(day=8))
        _test_week("last week", self.ref_date.replace(day=25, month=1))
        _test_week("first week", self.ref_date.replace(day=4, month=1))

        # test Nth week
        self.assertRaises(ValueError, extract_date_en,
                          "5th week of this month", now_local())

        # test week of month  -  day=1 in week
        assert self.ref_date.replace(day=1).weekday() == 0
        _test_week("first week of this month",
                   self.ref_date.replace(day=1))
        _test_week("second week of this month",
                   self.ref_date.replace(day=8, month=2))
        _test_week("3rd week of this month",
                   self.ref_date.replace(day=15, month=2))
        _test_week("4th week of this month",
                   self.ref_date.replace(day=22, month=2))

        # test week of month - month day=1 not in week (weeks start on sundays)
        _anchor = date(day=1, month=2, year=1991)
        assert _anchor.replace(day=1).weekday() != 0

        _test_week("first week of this month",
                   _anchor.replace(day=4), anchor=_anchor)
        _test_week("second week of this month",
                   _anchor.replace(day=11), anchor=_anchor)
        _test_week("3rd week of this month",
                   _anchor.replace(day=18), anchor=_anchor)
        _test_week("4th week of this month",
                   _anchor.replace(day=25), anchor=_anchor)

        # test week of year
        _test_week("first week of this year",
                   self.ref_date.replace(day=4, month=1))
        _test_week("2nd week of this year",
                   self.ref_date.replace(day=11, month=1))
        _test_week("3rd week of this year",
                   self.ref_date.replace(day=18, month=1))
        _test_week("10th week of this year",
                   self.ref_date.replace(day=8, month=3))

        # test week of decade
        _test_week("first week of this decade",
                   date(day=6, month=1, year=2110))
        _test_week("2nd week of this decade",
                   date(day=13, month=1, year=2110))
        _test_week("third week of this decade",
                   date(day=20, month=1, year=2110))
        _test_week("100 week of this decade",
                   date(day=30, month=11, year=2111))

        # test week of century
        _test_week("first week of this century",
                   date(day=4, month=1, year=2100))
        _test_week("2 week of this century",
                   date(day=11, month=1, year=2100))
        _test_week("3 week of this century",
                   date(day=18, month=1, year=2100))
        _test_week("1000 week of this century",
                   date(day=27, month=2, year=2119))

        # test week of millennium
        _test_week("first week of this millennium",
                   date(day=3, month=1, year=2000))
        _test_week("2 week of this millennium",
                   date(day=10, month=1, year=2000))
        _test_week("3 week of this millennium",
                   date(day=17, month=1, year=2000))
        _test_week("10000 week of this millennium",
                   date(day=22, month=8, year=2191))

        # test last week
        _test_week("last week of this month",
                   self.ref_date.replace(day=22))
        _test_week("last week of this year",
                   self.ref_date.replace(day=27, month=12))
        _test_week("last week of this decade",
                   date(day=25, month=12, year=2119))
        _test_week("last week of this century",
                   date(day=30, month=12, year=2199))
        _test_week("last week of this millennium",
                   date(day=30, month=12, year=2999))

    def test_years(self):
        _anchor = date(day=10, month=5, year=2020)

        # test explicit year (of YYYY)
        self._test_date("january of 90",
                        date(day=1, month=1, year=1990),
                        anchor=_anchor)
        self._test_date("january of 69",
                        date(day=1, month=1, year=1969),
                        anchor=_anchor)
        self._test_date("january of 19",
                        date(day=1, month=1, year=2019),
                        anchor=_anchor)

        self._test_date("january of 09",
                        date(day=1, month=1, year=2009),
                        anchor=_anchor)

        # test implicit years, "the 90s", "the 900s"
        self._test_date("the 70s",
                        _anchor.replace(year=1970),
                        anchor=_anchor)
        self._test_date("the 600s",
                        _anchor.replace(year=600),
                        anchor=_anchor)

        # test greedy flag - standalone numbers are years
        self._test_date("january 69",
                        _anchor.replace(day=1, month=1),
                        anchor=_anchor)
        self._test_date("january 69",
                        date(day=1, month=1, year=1969),
                        anchor=_anchor,
                        greedy=True)

        self._test_date("1992",
                        _anchor.replace(year=1992),
                        anchor=_anchor,
                        greedy=True)
        self._test_date("1992", None, anchor=_anchor)

        self._test_date("992",
                        _anchor.replace(year=992),
                        anchor=_anchor,
                        greedy=True)
        self._test_date("992", None, anchor=_anchor)

        self._test_date("132",
                        _anchor.replace(year=132),
                        anchor=_anchor,
                        greedy=True)
        self._test_date("132", None, anchor=_anchor)

        self._test_date("79",
                        _anchor.replace(year=1979),
                        anchor=_anchor,
                        greedy=True)
        self._test_date("79", None, anchor=_anchor)

        self._test_date("13",
                        _anchor.replace(year=2013),
                        anchor=_anchor,
                        greedy=True)
        self._test_date("13", None, anchor=_anchor)

        self._test_date("01",
                        _anchor.replace(year=2001),
                        anchor=_anchor,
                        greedy=True)
        self._test_date("0",
                        _anchor.replace(year=2000),
                        anchor=_anchor,
                        greedy=True)
        self._test_date("9", None, anchor=_anchor)

    def test_named_dates(self):
        _anchor = date(day=10, month=5, year=2020)

        self._test_date("christmas eve",
                        date(day=24, month=12, year=2020), anchor=_anchor)
        self._test_date("this christmas",
                        date(day=25, month=12, year=2020), anchor=_anchor)
        self._test_date("this easter",
                        date(day=12, month=4, year=2020), anchor=_anchor)

        # test location based holidays
        self._test_date("independence day",
                        date(day=4, month=7, year=2020), anchor=_anchor)
        self._test_date("Restauração da Independência", None)

        set_active_location("PT")
        self._test_date("Restauração da Independência",
                        date(day=1, month=12, year=2020), anchor=_anchor)
        self._test_date("independence day", None)
        self._test_date("this easter",  # named dates still available
                        date(day=12, month=4, year=2020), anchor=_anchor)

        # restore location
        set_active_location("US")
        self._test_date("independence day",
                        date(day=4, month=7, year=2020), anchor=_anchor)

        # self._test_date("last christmas",
        #                date(day=25, month=12, year=2019), anchor=_anchor)
        # self._test_date("next christmas",
        #                date(day=25, month=12, year=2020), anchor=_anchor)

        _anchor = date(day=31, month=12, year=2020)

        self._test_date("this christmas",
                        date(day=25, month=12, year=2020), anchor=_anchor)
        # self._test_date("last christmas",
        #                date(day=25, month=12, year=2020), anchor=_anchor)
        # self._test_date("next christmas",
        #                date(day=25, month=12, year=2021), anchor=_anchor)

    def test_named_eras(self):
        # test {Nth X} of {era}
        self._test_date("20th day of the common era",
                        date(day=20, month=1, year=1))
        self._test_date("20th month of the common era",
                        date(day=1, month=8, year=2))
        self._test_date("20th year of the common era",
                        date(day=1, month=1, year=20))
        self._test_date("20th decade of the common era",
                        date(day=1, month=1, year=190))
        self._test_date("21th century of the common era",
                        date(day=1, month=1, year=2000))
        self._test_date("2nd millennium of the common era",
                        date(day=1, month=1, year=1000))

        # test {date} of {era}
        self._test_date("20 may 1992 anno domini",
                        date(day=20, month=5, year=1992))

        # test {year} of {era}
        self._test_date("1992 christian era",
                        date(day=1, month=1, year=1992))

        # test ambiguous year
        self._test_date("1 january christian era",
                        date(day=1, month=1, year=1))

    def test_negative_eras(self):
        bp = date(day=1, month=1, year=1950)
        self._test_date("before present", bp)
        self._test_date("2 years before present",
                        date(day=1, month=1, year=1948))
        self._test_date("556 before present",
                        date(day=1, month=1, year=1394))
        self._test_date("march 1st 556 before present",
                        date(day=1, month=3, year=1394))
        self._test_date("10th day of the 1st year before present",
                        (bp - relativedelta(years=1)).replace(day=10))
        self._test_date("364th day before present",
                        bp - timedelta(days=364))
        self._test_date("364th month before present",
                        bp - relativedelta(months=364))
        self._test_date("364th week before present",
                        bp - timedelta(weeks=364))
        self._test_date("3rd century before present",
                        bp - relativedelta(years=300))
        self._test_date("11th decade before present",
                        bp - relativedelta(years=110))
        self._test_date("1st millennium before present",
                        bp - relativedelta(years=1000))

    def test_ambiguous(self):
        # TODO review all these, add more tests for ambiguous cases
        # these are to be considered bugs / missing features

        _anchor = date(day=10, month=5, year=2020)

        # multiple dates

        self._test_date("this is the 9th millennium,"
                        " the second day of the third month of the first year",
                        date(day=2, month=3, year=1))
        # desired: date(day=2, month=3, year=8000))

        # {month1} of {month2} .... of {monthN}
        # parsed as:
        #   month1
        #   TODO fix remainder (everything is consumed)
        self._test_date("january of october",
                        date(day=1, month=1, year=2020),
                        anchor=_anchor)
        self._test_date("january of october of december in november",
                        date(day=1, month=1, year=2020),
                        anchor=_anchor)

        # {day} {month1} of {month2} .... of {monthN}
        # parsed as:
        #   day of monthN
        #   TODO fix remainder (everything is consumed)
        self._test_date("12 december of october",
                        date(day=12, month=10, year=2020),
                        anchor=_anchor)
        self._test_date("12 january of october",
                        date(day=12, month=10, year=2020),
                        anchor=_anchor)
        self._test_date("12 january of december at october",
                        date(day=12, month=10, year=2020),
                        anchor=_anchor)

        # {year} of {year}
        # parsed as:
        #   Nth day of {year}
        #   TODO not matching?
        # self._test_date("1992 of 2020",
        #                _anchor + relativedelta(days=1992),
        #                anchor=_anchor)

        # {season} of {season2} ..... of {seasonN}
        # parsed as:
        #   {seasonN}
        #   TODO fix remainder (everything is consumed)
        self._test_date("summer in winter",
                        date(day=1, month=12, year=_anchor.year),
                        anchor=_anchor)
        self._test_date("winter in spring",
                        date(day=1, month=3, year=_anchor.year),
                        anchor=_anchor)
        self._test_date("summer in winter in fall",
                        date(day=1, month=9, year=_anchor.year),
                        anchor=_anchor)
