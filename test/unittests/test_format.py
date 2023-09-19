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
import ast
import datetime
import json
import unittest
from pathlib import Path

from dateutil import tz

# TODO either write a getter for lingua_franca.internal._SUPPORTED_LANGUAGES,
# or make it public somehow
from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.format import (
    date_time_format,
    nice_date,
    nice_date_time,
    nice_number,
    nice_time,
    nice_year,
    nice_day,
    nice_month,
    nice_weekday,
    get_date_strings
)
from lingua_franca.lang.format_common import convert_to_mixed_fraction as cmf
from lingua_franca.time import default_timezone, set_default_tz, now_local, \
    to_local


def setUpModule():
    load_language("en")
    set_default_lang('en-us')


def tearDownModule():
    unload_language("en")


class TestNiceNumberFormat(unittest.TestCase):

    def test_unknown_language(self):
        """ An unknown / unhandled language should return the string
            representation of the input number.
        """

        def bypass_warning():
            self.assertEqual(
                nice_number(5.5, lang='as-df'), '5.5',
                'should format 5.5 '
                'as 5.5 not {}'.format(
                    nice_number(5.5, lang='as-df')))

        # Should throw a warning. Would raise the same text as a
        # NotImplementedError, but nice_number() bypasses and returns
        # its input as a string
        self.assertWarns(UserWarning, bypass_warning)


class TestTimezones(unittest.TestCase):
    def test_default_tz(self):
        default = default_timezone()
        set_default_tz("America/Chicago")

        local_time = now_local()
        local_tz = default_timezone()
        us_time = datetime.datetime.now(tz=tz.gettz("America/Chicago"))
        self.assertEqual(nice_date_time(local_time),
                         nice_date_time(us_time))
        self.assertEqual(local_time.tzinfo, local_tz)

        # naive datetimes assumed to be in default timezone already!
        # in the case of datetime.now this corresponds to tzlocal()
        # otherwise timezone is undefined and can not be guessed, we assume
        # the user means "my timezone" and that LF was configured to use it
        # beforehand, if unconfigured default == tzlocal()
        dt = datetime.datetime(2021, 6, 23, 00, 43, 39)
        dt_local = to_local(dt)
        self.assertEqual(nice_time(dt), nice_time(dt_local))

        set_default_tz(default)  # undo changes to default tz after test

    def test_tz_conversion(self):
        naive = datetime.datetime.now()
        system_time = datetime.datetime.now(tz.tzlocal())
        # naive == datetime.now() == tzlocal() internally
        # NOTE nice_date_time is not a localized function, it just formats
        # the datetime object directly
        self.assertEqual(nice_date_time(naive),
                         nice_date_time(system_time))


class TestNiceDateFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read date_time_test.json files for test data
        cls.test_config = {}
        p = Path(date_time_format.config_path)
        for sub_dir in [x for x in p.iterdir() if x.is_dir()]:
            if (sub_dir / 'date_time_test.json').exists():
                print("Getting test for " +
                      str(sub_dir / 'date_time_test.json'))
                with (sub_dir / 'date_time_test.json').open() as f:
                    cls.test_config[sub_dir.parts[-1]] = json.loads(f.read())

    def test_nice_date(self):
        for lang in self.test_config:
            load_language(lang)
            set_default_lang(lang)

            i = 1
            while (self.test_config[lang].get('test_nice_date') and
                   self.test_config[lang]['test_nice_date'].get(str(i))):
                p = self.test_config[lang]['test_nice_date'][str(i)]
                dp = ast.literal_eval(p['datetime_param'])
                np = ast.literal_eval(p['now'])
                dt = datetime.datetime(
                    dp[0], dp[1], dp[2], dp[3], dp[4], dp[5])
                now = None if not np else datetime.datetime(
                    np[0], np[1], np[2], np[3], np[4], np[5])
                print('Testing for ' + lang + ' that ' + str(dt) +
                      ' is date ' + p['assertEqual'])
                self.assertEqual(p['assertEqual'],
                                 nice_date(dt, lang=lang, now=now))
                i = i + 1

            unload_language(lang)

        # test all days in a year for all languages,
        # that some output is produced
        for lang in self.test_config:
            load_language(lang)
            set_default_lang(lang)

            for dt in (datetime.datetime(2017, 12, 30, 0, 2, 3) +
                       datetime.timedelta(n) for n in range(368)):
                self.assertTrue(len(nice_date(dt, lang=lang)) > 0)

            unload_language(lang)

        set_default_lang('en')

    def test_nice_date_time(self):
        # TODO: migrate these tests (in res files) to respect the new
        # language loading features. Right now, some of them break if
        # their languages are not default.
        for lang in self.test_config:
            load_language(lang)
            set_default_lang(lang)
            i = 1
            while (self.test_config[lang].get('test_nice_date_time') and
                   self.test_config[lang]['test_nice_date_time'].get(str(i))):
                p = self.test_config[lang]['test_nice_date_time'][str(i)]
                dp = ast.literal_eval(p['datetime_param'])
                np = ast.literal_eval(p['now'])
                dt = datetime.datetime(
                    dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                    tzinfo=default_timezone())
                now = None if not np else datetime.datetime(
                    np[0], np[1], np[2], np[3], np[4], np[5],
                    tzinfo=default_timezone())
                print('Testing for ' + lang + ' that ' + str(dt) +
                      ' is date time ' + p['assertEqual'])
                self.assertEqual(
                    p['assertEqual'],
                    nice_date_time(
                        dt, lang=lang, now=now,
                        use_24hour=ast.literal_eval(p['use_24hour']),
                        use_ampm=ast.literal_eval(p['use_ampm'])))
                i = i + 1
            unload_language(lang)
        set_default_lang('en')

    def test_nice_year(self):
        for lang in self.test_config:
            load_language(lang)
            set_default_lang(lang)

            i = 1
            while (self.test_config[lang].get('test_nice_year') and
                   self.test_config[lang]['test_nice_year'].get(str(i))):
                p = self.test_config[lang]['test_nice_year'][str(i)]
                dp = ast.literal_eval(p['datetime_param'])
                dt = datetime.datetime(
                    dp[0], dp[1], dp[2], dp[3], dp[4], dp[5])
                print('Testing for ' + lang + ' that ' + str(dt) +
                      ' is year ' + p['assertEqual'])
                self.assertEqual(p['assertEqual'], nice_year(
                    dt, lang=lang, bc=ast.literal_eval(p['bc'])))
                i = i + 1

            unload_language(lang)

        # Test all years from 0 to 9999 for all languages,
        # that some output is produced
        for lang in self.test_config:
            load_language(lang)
            set_default_lang(lang)

            print("Test all years in " + lang)
            for i in range(1, 9999):
                dt = datetime.datetime(i, 1, 31, 13, 2, 3, tzinfo=default_timezone())
                self.assertTrue(len(nice_year(dt, lang=lang)) > 0)
                # Looking through the date sequence can be helpful

            unload_language(lang)

        set_default_lang('en')


class TestNiceDateUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lang = 'en-us'

    def test_nice_day(self):
        # Test with include_month=True
        dt = datetime.datetime(2022, 10, 31)
        self.assertEqual(nice_day(dt, 'MDY', True, self.lang), "October 31")
        self.assertEqual(nice_day(dt, 'DMY', True, self.lang), "31 October")

        # Test with include_month=False
        self.assertEqual(nice_day(dt, include_month=False, lang=self.lang), "31")

    def test_nice_month(self):
        dt = datetime.datetime(2022, 10, 31)
        self.assertEqual(nice_month(dt, lang=self.lang), "October")

    def test_nice_weekday(self):
        dt = datetime.datetime(2022, 10, 31)
        self.assertEqual(nice_weekday(dt, lang=self.lang), "Monday")
    
    def test_get_date_strings(self):
        # Test with default arguments
        dt = datetime.datetime(2022, 10, 31, 13, 30, 0)
        expected_output = {
            "date_string": "10/31/2022",
            "time_string": "1:30",
            "month_string": "October",
            "day_string": "31",
            "year_string": "2022",
            "weekday_string": "Monday"
        }
        self.assertEqual(get_date_strings(dt,
                                          time_format="half",
                                          lang=self.lang), expected_output)

        # Test with different date_format
        expected_output = {
            "date_string": "31/10/2022",
            "time_string": "1:30",
            "month_string": "October",
            "day_string": "31",
            "year_string": "2022",
            "weekday_string": "Monday"
        }
        self.assertEqual(get_date_strings(dt,
                                          time_format="half",
                                          date_format='DMY',
                                          lang=self.lang), expected_output)

        # Test with different time_format
        expected_output = {
            "date_string": "10/31/2022",
            "time_string": "13:30",
            "month_string": "October",
            "day_string": "31",
            "year_string": "2022",
            "weekday_string": "Monday"
        }
        self.assertEqual(get_date_strings(dt, lang=self.lang), expected_output)        


class TestMixedFraction(unittest.TestCase):
    def test_convert_to_fraction(self):
        self.assertEqual(cmf(8), (8, 0, 1))
        self.assertEqual(cmf(8.00001), (8, 0, 1))
        self.assertEqual(cmf(8.5), (8, 1, 2))
        self.assertEqual(cmf(8.587465135), None)
        self.assertEqual(cmf(8.587465135, range(1, 101)), (8, 47, 80))


if __name__ == "__main__":
    unittest.main()
