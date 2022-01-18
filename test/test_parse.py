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

from dateutil import tz
from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import fuzzy_match
from lingua_franca.parse import match_one
from lingua_franca.time import default_timezone, now_local, set_default_tz


def setUpModule():
    load_language('en')
    set_default_lang('en')


def tearDownModule():
    unload_language('en')


class TestTimezones(unittest.TestCase):
    def test_default_tz(self):
        default = default_timezone()

        naive = datetime.now()

        # convert to default tz
        set_default_tz("Europe/London")
        dt = extract_datetime("tomorrow", anchorDate=naive)[0]
        self.assertEqual(dt.tzinfo, tz.gettz("Europe/London"))

        set_default_tz("America/Chicago")
        dt = extract_datetime("tomorrow", anchorDate=naive)[0]
        self.assertEqual(dt.tzinfo, tz.gettz("America/Chicago"))

        set_default_tz(default)  # undo changes to default tz after test

    def test_convert_to_anchorTZ(self):
        default = default_timezone()
        naive = datetime.now()
        local = now_local()
        london_time = datetime.now(tz=tz.gettz("Europe/London"))
        us_time = datetime.now(tz=tz.gettz("America/Chicago"))

        # convert to anchor date
        dt = extract_datetime("tomorrow", anchorDate=naive)[0]
        self.assertEqual(dt.tzinfo, default_timezone())
        dt = extract_datetime("tomorrow", anchorDate=local)[0]
        self.assertEqual(dt.tzinfo, local.tzinfo)
        dt = extract_datetime("tomorrow", anchorDate=london_time)[0]
        self.assertEqual(dt.tzinfo, london_time.tzinfo)
        dt = extract_datetime("tomorrow", anchorDate=us_time)[0]
        self.assertEqual(dt.tzinfo, us_time.tzinfo)

        # test naive == default tz
        set_default_tz("America/Chicago")
        dt = extract_datetime("tomorrow", anchorDate=naive)[0]
        self.assertEqual(dt.tzinfo, default_timezone())
        set_default_tz("Europe/London")
        dt = extract_datetime("tomorrow", anchorDate=naive)[0]
        self.assertEqual(dt.tzinfo, default_timezone())

        set_default_tz(default)  # undo changes to default tz after test


class TestFuzzyMatch(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(fuzzy_match("you and me", "you and me") >= 1.0)
        self.assertTrue(fuzzy_match("you and me", "you") < 0.5)
        self.assertTrue(fuzzy_match("You", "you") > 0.5)
        self.assertTrue(fuzzy_match("you and me", "you") ==
                        fuzzy_match("you", "you and me"))
        self.assertTrue(fuzzy_match("you and me", "he or they") < 0.2)

    def test_match_one(self):
        # test list of choices
        choices = ['frank', 'kate', 'harry', 'henry']
        self.assertEqual(match_one('frank', choices)[0], 'frank')
        self.assertEqual(match_one('fran', choices)[0], 'frank')
        self.assertEqual(match_one('enry', choices)[0], 'henry')
        self.assertEqual(match_one('katt', choices)[0], 'kate')
        # test dictionary of choices
        choices = {'frank': 1, 'kate': 2, 'harry': 3, 'henry': 4}
        self.assertEqual(match_one('frank', choices)[0], 1)
        self.assertEqual(match_one('enry', choices)[0], 4)


if __name__ == "__main__":
    unittest.main()
