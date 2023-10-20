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

import json
import unittest
import datetime
import ast
import sys
from pathlib import Path

from lingua_franca import get_default_lang, set_default_lang, \
    load_language, unload_language
from lingua_franca.format import date_time_format
from lingua_franca.format import join_list
from lingua_franca.format import nice_date
from lingua_franca.format import nice_date_time
from lingua_franca.format import nice_duration
from lingua_franca.format import nice_number
from lingua_franca.format import nice_time
from lingua_franca.format import nice_year
from lingua_franca.format import pronounce_number
from lingua_franca.time import default_timezone


def setUpModule():
    load_language("uk-ua")
    set_default_lang("uk")


def tearDownModule():
    unload_language("uk")


NUMBERS_FIXTURE_UK = {
    1.435634: "1.436",
    2: "2",
    5.0: "5",
    0.027: "0.027",
    0.5: "1 друга",
    1.333: "1 і 1 третя",
    2.666: "2 і 2 треті",
    0.25: "1 четверта",
    1.25: "1 і 1 четверта",
    0.75: "3 четверті",
    1.75: "1 і 3 четверті",
    3.4: "3 і 2 п'яті",
    16.8333: "16 і 5 шостих",
    12.5714: "12 і 4 сьомі",
    9.625: "9 і 5 восьмих",
    6.777: "6 і 7 дев'ятих",
    3.1: "3 і 1 десята",
    2.272: "2 і 3 одинадцяті",
    5.583: "5 і 7 дванадцятих",
    8.384: "8 і 5 тринадцятих",
    0.071: "1 чотирнадцята",
    6.466: "6 і 7 п'ятнадцятих",
    8.312: "8 і 5 шістнадцятих",
    2.176: "2 і 3 сімнадцяті",
    200.722: "200 і 13 вісімнадцятих",
    7.421: "7 і 8 дев'ятнадцятих",
    0.05: "1 двадцята"
}

def setUpModule():
    load_language("uk-ua")
    set_default_lang("uk")

class TestNiceNumberFormat(unittest.TestCase):
    load_language("uk-ua")
    set_default_lang("uk")

    def test_convert_float_to_nice_number(self):
        load_language("uk-ua")
        set_default_lang("uk")
        for number, number_str in NUMBERS_FIXTURE_UK.items():
            self.assertEqual(nice_number(number, speech=True), number_str,
                             "повинен відформатувати {} як {}, а не {}".format(
                                 number, number_str, nice_number(number, speech=True)))

    def test_specify_denominator(self):
        self.assertEqual(nice_number(5.5, speech=True, denominators=[1, 2, 3]),
                         "5 з половиною",
                         "повинен відформатувати 5.5 як 5 з половиною, а не {}".format(
                             nice_number(5.5, speech=True, denominators=[1, 2, 3])))
        self.assertEqual(nice_number(2.333, speech=True, denominators=[1, 2]),
                         "2.333",
                         "повинен відформатувати 2.333 як 2.333, а не {}".format(
                             nice_number(2.333, speech=True, denominators=[1, 2])))

    def test_no_speech(self):
        self.assertEqual(nice_number(6.777, speech=False),
                         "6 7/9",
                         "повинен відформатувати 6.777 як 6 7/9, а не {}".format(
                             nice_number(6.777, speech=False)))
        self.assertEqual(nice_number(6.0, speech=False),
                         "6",
                         "повинен відформатувати 6.0 як 6, а не {}".format(
                             nice_number(6.0, speech=False)))


class TestPronounceNumber(unittest.TestCase):

    def test_convert_int(self):
        self.assertEqual(pronounce_number(0), "нуль")
        self.assertEqual(pronounce_number(1), "один")
        self.assertEqual(pronounce_number(10), "десять")
        self.assertEqual(pronounce_number(15), "п'ятнадцять")
        self.assertEqual(pronounce_number(20), "двадцять")
        self.assertEqual(pronounce_number(27), "двадцять сім")
        self.assertEqual(pronounce_number(30), "тридцять")
        self.assertEqual(pronounce_number(33), "тридцять три")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1), "мінус один")
        self.assertEqual(pronounce_number(-10), "мінус десять")
        self.assertEqual(pronounce_number(-15), "мінус п'ятнадцять")
        self.assertEqual(pronounce_number(-20), "мінус двадцять")
        self.assertEqual(pronounce_number(-27), "мінус двадцять сім")
        self.assertEqual(pronounce_number(-30), "мінус тридцять")
        self.assertEqual(pronounce_number(-33), "мінус тридцять три")

    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(0.05), "нуль крапка нуль п'ять")
        self.assertEqual(pronounce_number(-0.05), "мінус нуль крапка нуль п'ять")
        self.assertEqual(pronounce_number(1.234),
                         "один крапка два три")
        self.assertEqual(pronounce_number(21.234),
                         "двадцять один крапка два три")
        self.assertEqual(pronounce_number(21.234, places=1),
                         "двадцять один крапка два")
        self.assertEqual(pronounce_number(21.234, places=0),
                         "двадцять один")
        self.assertEqual(pronounce_number(21.234, places=3),
                         "двадцять один крапка два три чотири")
        self.assertEqual(pronounce_number(21.234, places=4),
                         "двадцять один крапка два три чотири")
        self.assertEqual(pronounce_number(21.234, places=5),
                         "двадцять один крапка два три чотири")
        self.assertEqual(pronounce_number(-1.234),
                         "мінус один крапка два три")
        self.assertEqual(pronounce_number(-21.234),
                         "мінус двадцять один крапка два три")
        self.assertEqual(pronounce_number(-21.234, places=1),
                         "мінус двадцять один крапка два")
        self.assertEqual(pronounce_number(-21.234, places=0),
                         "мінус двадцять один")
        self.assertEqual(pronounce_number(-21.234, places=3),
                         "мінус двадцять один крапка два три чотири")
        self.assertEqual(pronounce_number(-21.234, places=4),
                         "мінус двадцять один крапка два три чотири")
        self.assertEqual(pronounce_number(-21.234, places=5),
                         "мінус двадцять один крапка два три чотири")

    def test_convert_stos(self):
        self.assertEqual(pronounce_number(100), "сто")
        self.assertEqual(pronounce_number(666), "шістсот шістдесят шість")
        self.assertEqual(pronounce_number(1456), "тисяча чотириста п'ятдесят шість")
        self.assertEqual(pronounce_number(103254654), "сто три мільйона "
                                                      "двісті п'ятдесят "
                                                      "чотири тисячі "
                                                      "шістсот "
                                                      "п'ятдесят чотири")
        self.assertEqual(pronounce_number(1512457), "мільйон п'ятсот"
                                                    " дванадцять тисяч "
                                                    "чотириста п'ятдесят "
                                                    "сім")
        self.assertEqual(pronounce_number(209996), "двісті дев'ять "
                                                   "тисяч дев'ятсот "
                                                   "дев'яносто шість")

    def test_convert_scientific_notation(self):
        self.assertEqual(pronounce_number(0, scientific=True), "нуль")
        self.assertEqual(pronounce_number(33, scientific=True),
                         "три крапка три на десять у ступені один")
        self.assertEqual(pronounce_number(299792458, scientific=True),
                         "два крапка дев'ять дев'ять на десять у ступені вісім")
        self.assertEqual(pronounce_number(299792458, places=6,
                                          scientific=True),
                         "два крапка дев'ять дев'ять сім дев'ять два п'ять "
                         "на десять у ступені вісім")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True),
                         "один крапка шість сім два на десять у ступені "
                         "мінус двадцять сім")

    def test_auto_scientific_notation(self):
        self.assertEqual(
            pronounce_number(1.1e-150), "один крапка один на десять у ступені "
                                        "мінус сто п'ятдесят")

    def test_large_numbers(self):
        self.maxDiff = None
        self.assertEqual(
            pronounce_number(299792458, short_scale=True),
            "двісті дев'яносто дев'ять мільйонів сімсот "
            "дев'яносто дві тисячі чотириста п'ятдесят вісім")
        self.assertEqual(
            pronounce_number(299792458, short_scale=False),
            "двісті дев'яносто дев'ять мільйонів сімсот "
            "дев'яносто дві тисячі чотириста п'ятдесят вісім")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=True),
            "сто квадрилліонів тридцять чотири більйона "
            "двісті дев'яносто дев'ять мільйонів сімсот "
            "дев'яносто дві тисячі чотириста п'ятдесят вісім")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=False),
            "сто більйонів тридцять чотири тисячі мільярдів "
            "двісті дев'яносто дев'ять мільйонів сімсот "
            "дев'яносто дві тисячі чотириста п'ятдесят вісім")
        self.assertEqual(
            pronounce_number(1e10, short_scale=True),
            "десять мільярдів")
        self.assertEqual(
            pronounce_number(1e12, short_scale=True),
            "більйон")
        # TODO maybe beautify this
        self.assertEqual(
            pronounce_number(1000001, short_scale=True),
            "мільйон один")
        self.assertEqual(pronounce_number(95505896639631893, short_scale=True),
                         "дев'яносто п'ять більйонів "
                         "п'ятсот п'ять квінтиліонів "
                         "вісімсот дев'яносто шість мільярдів "
                         "шістсот тридцять дев'ять мільйонів "
                         "шістсот тридцять одна тисяча "
                         "вісімсот дев'яносто три")
        self.assertEqual(pronounce_number(95505896639631893,
                                          short_scale=False),
                         "дев'яносто п'ять тисяч п'ятсот п'ять мільярдів "
                         "вісімсот дев'яносто шість тисяч "
                         "шістсот тридцять дев'ять мільйонів "
                         "шістсот тридцять одна тисяча "
                         "вісімсот дев'яносто три")
        self.assertEqual(pronounce_number(10e80, places=1),
                         "секснвігінтіліон")
        # TODO floating point rounding issues might happen
        # self.assertEqual(pronounce_number(1.9874522571e80, places=9),
        #                  "сто дев'яносто вісім квінвігінтільйонів "
        #                  # "сімсот сорок п'ять кватторвігінтільйонів "
        #                  "двісті двадцять п'ять тревігінтільйонів "
        #                  "сімсот дев'ять дуовігінтільйонів "
        #                  "дев'ятсот дев'яносто дев'ять унвігінтільйонів "
        #                  "дев'ятсот вісімдесят дев'ять вигінтильйонів "
        #                  "сімсот тридцять новемдециліонів "
        #                  "дев'ятсот девятнадцать октодецильйонів "
        #                  "дев'ятсот дев'яносто дев'ять септендециліонів "
        #                  "дев'ятсот п'ятдесят п'ять сексдециліонів "
        #                  "чотириста дев'яносто вісім квіндециліонів "
        #                  "двісті чотирнадцять кваттордециліонів "
        #                  "вісімсот сорок п'ять тредецільйонів "
        #                  "чотириста двадцять дев'ять дуодецильйонів "
        #                  "чотириста сорок чотири ундецильйона "
        #                  "триста тридцять шість дециліонів "
        #                  "сімсот двадцять чотири нонільйону "
        #                  "п'ятсот шістьдесят дев'ять октильйонів "
        #                  "триста сімдесят п'ять септільйонів "
        #                  "двісті тридцять дев'ять секстильйонів "
        #                  "шістсот сімдесят квінтільйонів "
        #                  "п'ятсот сімдесят чотири квадрильйона "
        #                  "сімсот тридцять дев'ять трильйонів "
        #                  "сімсот сорок вісім мільярдів "
        #                  "чотириста сімдесят мільйонів "
        #                  "дев'ятсот п'ятнадцять тысяч "
        #                  "сімдесят два")

        # infinity
        self.assertEqual(
            pronounce_number(sys.float_info.max * 2), "нескінченність")
        self.assertEqual(
            pronounce_number(float("inf")),
            "нескінченність")
        self.assertEqual(
            pronounce_number(float("-inf")),
            "мінус нескінченність")

    def test_ordinals(self):
        self.assertEqual(pronounce_number(1, ordinals=True), "перший")
        self.assertEqual(pronounce_number(10, ordinals=True), "десятий")
        self.assertEqual(pronounce_number(15, ordinals=True), "п'ятнадцятий")
        self.assertEqual(pronounce_number(20, ordinals=True), "двадцятий")
        self.assertEqual(pronounce_number(27, ordinals=True), "двадцять сьомий")
        self.assertEqual(pronounce_number(30, ordinals=True), "тридцятий")
        self.assertEqual(pronounce_number(33, ordinals=True), "тридцять третій")
        self.assertEqual(pronounce_number(100, ordinals=True), "сотий")
        self.assertEqual(pronounce_number(1000, ordinals=True), "тисячний")
        self.assertEqual(pronounce_number(10000, ordinals=True),
                         "десятитисячний")
        self.assertEqual(pronounce_number(18691, ordinals=True),
                         "вісімнадцять тисяч шістсот дев'яносто перший")
        self.assertEqual(pronounce_number(1567, ordinals=True),
                         "тисяча п'ятсот шістдесят сьомий")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True, ordinals=True),
                         "один крапка шість сім два на десять у мінус "
                         "двадцять сьомому ступені")
        self.assertEqual(pronounce_number(1e6, ordinals=True),
                         "мільйонний")
        self.assertEqual(pronounce_number(2e6, ordinals=True),
                         "двохмільйонний")
        self.assertEqual(pronounce_number(3e6, ordinals=True),
                         "трьохмільйонний")
        self.assertEqual(pronounce_number(4e6, ordinals=True),
                         "чотирьохмільйонний")
        self.assertEqual(pronounce_number(18e6, ordinals=True),
                         "вісімнадцятимільйонний")
        self.assertEqual(pronounce_number(18e12, ordinals=True),
                         "вісімнадцятибільйонний")
        self.assertEqual(pronounce_number(18e18, ordinals=True,
                                          short_scale=False), "вісімнадцятитрильйонний")


class TestNiceDateFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read date_time_test.json files for test data
        cls.test_config = {}
        p = Path(date_time_format.config_path)
        # print(p)
        for sub_dir in [x for x in p.iterdir() if x.is_dir()]:
            # print(sub_dir)
            if (sub_dir / "date_time_test.json").exists():
                # print(f"Loading test for {sub_dir}/date_time_test.json")
                with (sub_dir / "date_time_test.json").open() as f:
                    cls.test_config[sub_dir.parts[-1]] = json.loads(f.read())

    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven"t changed
        self.assertEqual(nice_time(dt),
                         nice_time(dt, speech=True, use_24hour=True, use_ampm=False))

        self.assertEqual(nice_time(dt, use_24hour=False),
                         "перша година двадцять два")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "перша година дня двадцять два ")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False),
                         "1:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "1:22 дня")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "тринадцять двадцять два")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "тринадцять двадцять два")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "перша година")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "перша година дня")
        self.assertEqual(nice_time(dt, use_24hour=False, speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "1:00 дня")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "тринадцять рівно")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "тринадцять рівно")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "перша година нуль два")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "перша година дня нуль два ")
        self.assertEqual(nice_time(dt, use_24hour=False, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, use_24hour=False, speech=False, use_ampm=True),
                         "1:02 дня")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "тринадцять нуль два")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "тринадцять нуль два")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "дванадцята година нуль два")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "дванадцята година нуль два ночі")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False),
                         "12:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "12:02 ночі")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "нуль нуль нуль два")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "нуль нуль нуль два")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "перша година нуль два")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "перша година нуль два ночі")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "1:02 ночі")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "нуль один нуль два")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "нуль один нуль два")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "чверть після дванадцятої години")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "чверть після дванадцятої години дня")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "половина після п'ятої години ранку")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "без четверті друга година")

    def test_nice_date(self):
        lang = "uk-ua"
        i = 1
        # print(self.test_config[lang]["test_nice_date"].get(str(i)))
        while (self.test_config[lang].get("test_nice_date") and
               self.test_config[lang]["test_nice_date"].get(str(i))):
            p = self.test_config[lang]["test_nice_date"][str(i)]
            dp = ast.literal_eval(p["datetime_param"])
            np = ast.literal_eval(p["now"])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            now = None if not np else datetime.datetime(
                np[0], np[1], np[2], np[3], np[4], np[5],
                tzinfo=default_timezone())
            # print("Testing for " + lang + " that " + str(dt) +
            #       " is date " + p["assertEqual"])
            self.assertEqual(p["assertEqual"],
                             nice_date(dt, lang=lang, now=now))
            i = i + 1

        # test all days in a year for all languages,
        # that some output is produced
        # for lang in self.test_config:
        for dt in (datetime.datetime(2017, 12, 30, 0, 2, 3,
                                     tzinfo=default_timezone()) +
                   datetime.timedelta(n) for n in range(368)):
            self.assertTrue(len(nice_date(dt, lang=lang)) > 0)

    def test_nice_date_time(self):
        lang = "uk-ua"
        i = 1
        while (self.test_config[lang].get("test_nice_date_time") and
               self.test_config[lang]["test_nice_date_time"].get(str(i))):
            p = self.test_config[lang]["test_nice_date_time"][str(i)]
            dp = ast.literal_eval(p["datetime_param"])
            np = ast.literal_eval(p["now"])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            now = None if not np else datetime.datetime(
                np[0], np[1], np[2], np[3], np[4], np[5])
            # print("Testing for " + lang + " that " + str(dt) +
            #       " is date time " + p["assertEqual"])
            self.assertEqual(
                p["assertEqual"],
                nice_date_time(
                    dt, lang=lang, now=now,
                    use_24hour=ast.literal_eval(p["use_24hour"]),
                    use_ampm=ast.literal_eval(p["use_ampm"])))
            i = i + 1

    def test_nice_year(self):
        lang = "uk-ua"
        i = 1
        while (self.test_config[lang].get("test_nice_year") and
               self.test_config[lang]["test_nice_year"].get(str(i))):
            p = self.test_config[lang]["test_nice_year"][str(i)]
            # print(p)
            dp = ast.literal_eval(p["datetime_param"])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            # print("Testing for " + lang + " that " + str(dt) +
            #           " is year " + p["assertEqual"])
            self.assertEqual(p["assertEqual"], nice_year(
                dt, lang=lang, bc=ast.literal_eval(p["bc"])))
            i = i + 1

        # Test all years from 0 to 9999 for all languages,
        # that some output is produced
        # print("Test all years in " + lang)
        for i in range(1, 9999):
            dt = datetime.datetime(i, 1, 31, 13, 2, 3,
                                   tzinfo=default_timezone())
            self.assertTrue(len(nice_year(dt, lang=lang)) > 0)

    def test_nice_duration(self):

        self.assertEqual(nice_duration(1), "одна секунда")
        self.assertEqual(nice_duration(3), "три секунди")
        self.assertEqual(nice_duration(1, speech=False), "0:01")
        self.assertEqual(nice_duration(61), "одна хвилина одна секунда")
        self.assertEqual(nice_duration(121), "дві хвилини одна секунда")
        self.assertEqual(nice_duration(61, speech=False), "1:01")
        self.assertEqual(nice_duration(5000),
                         "одна година двадцять три хвилини двадцять секунд")
        self.assertEqual(nice_duration(5000, speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000),
                         "тринадцять годин п'ятдесят три хвилини двадцять секунд")
        self.assertEqual(nice_duration(50000, speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000),
                         "п'ять днів вісімнадцять годин п'ятдесят три хвилини двадцять секунд")  # nopep8
        self.assertEqual(nice_duration(500000, speech=False), "5d 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000),
                                       speech=False),
                         "5d 18:53:20")

    def test_join(self):
        self.assertEqual(join_list(None, "і"), "")
        self.assertEqual(join_list([], "і"), "")

        self.assertEqual(join_list(["a"], "і"), "a")
        self.assertEqual(join_list(["a", "b"], "і"), "a і b")
        self.assertEqual(join_list(["a", "b"], "або"), "a або b")

        self.assertEqual(join_list(["a", "b", "c"], "і"), "a, b і c")
        self.assertEqual(join_list(["a", "b", "c"], "або"), "a, b або c")
        self.assertEqual(
            join_list(["a", "b", "c"], "або", ";"), "a; b або c")
        self.assertEqual(
            join_list(["a", "b", "c", "d"], "або"), "a, b, c або d")

        self.assertEqual(join_list([1, "b", 3, "d"], "або"), "1, b, 3 або d")


if __name__ == "__main__":
    unittest.main()
