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
from lingua_franca.lang.parse_common import tokenize, Token, Normalizer
from lingua_franca.parse import extract_datetime, fuzzy_match, match_one, extract_langcode, yes_or_no
from lingua_franca.time import default_timezone, now_local, set_default_tz
from lingua_franca.internal import FunctionNotLocalizedError


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


class TestTokenize(unittest.TestCase):
    def test_tokenize(self):
        self.assertEqual(tokenize('One small step for man'),
                         [Token('One', 0), Token('small', 1), Token('step', 2),
                          Token('for', 3), Token('man', 4)])

        self.assertEqual(tokenize('15%'),
                         [Token('15', 0), Token('%', 1)])

        self.assertEqual(tokenize('I am #1'),
                         [Token('I', 0), Token('am', 1), Token('#', 2),
                          Token('1', 3)])

        self.assertEqual(tokenize('hashtag #1world'),
                         [Token('hashtag', 0), Token('#', 1), Token('1world', 2)])
        
        self.assertEqual(tokenize(",;_!?<>|()=[]{}»«*~^`."),
                         [Token(",", 0), Token(";", 1), Token("_",2), Token("!",3),
                          Token("?", 4), Token("<", 5), Token(">", 6), Token("|", 7),
                          Token("(", 8), Token(")", 9), Token("=", 10), Token("[", 11),
                          Token("]", 12), Token("{", 13), Token("}", 14), Token("»", 15),
                          Token("«", 16), Token("*", 17), Token("~", 18), Token("^", 19),
                          Token("`", 20), Token(".", 21)])


class TestRemoveSymbols(unittest.TestCase):
    def test_remove_symbols_empty_string(self):
        self.assertEqual(Normalizer().remove_symbols(""), "")

    def test_remove_symbols_no_symbols(self):
        self.assertEqual(Normalizer().remove_symbols("Hello world"), "Hello world")

    def test_remove_symbols_one_symbol(self):
        self.assertEqual(Normalizer().remove_symbols("Hello, world?!"), "Hello world")

    def test_remove_symbols_only_symbols(self):
        self.assertEqual(Normalizer().remove_symbols(",;_!?<>|()=[]{}»«*~^`"), "")

    def test_remove_symbols_contraction(self):
        self.assertEqual(Normalizer().remove_symbols("It's sunny and warm outside."),
                         "It's sunny and warm outside")
        
    def test_remove_symbols_dates(self):
        self.assertEqual(Normalizer().remove_symbols("(* 15/2/2018)"),
                         "15/2/2018")
        

class TestLangcode(unittest.TestCase):
    def test_parse_lang_code(self):

        def test_with_conf(text, expected_lang, min_conf=0.8):
            lang, conf = extract_langcode(text, lang="unk")
            self.assertEqual(lang, expected_lang)
            self.assertGreaterEqual(conf, min_conf)

        # test fallback to english and fuzzy match
        test_with_conf("English", 'en', 1.0)
        test_with_conf("Portuguese", 'pt', 1.0)
        test_with_conf("Português", 'pt', 0.8)
        test_with_conf("Inglês", 'en', 0.6)


class TestYesNo(unittest.TestCase):
    def test_bad_lang(self):

        def test_utt():
            yes_or_no("pretend this is klingon text", lang="unk")

        self.assertRaises(FunctionNotLocalizedError, test_utt)


if __name__ == "__main__":
    unittest.main()
