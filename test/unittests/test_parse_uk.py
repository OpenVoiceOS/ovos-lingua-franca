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
from datetime import datetime, timedelta
from lingua_franca import set_default_lang, load_language, unload_language
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import fuzzy_match
from lingua_franca.parse import match_one
from lingua_franca.parse import normalize
from lingua_franca.time import default_timezone


def setUpModule():
    load_language("uk-uk")
    set_default_lang("uk")


def tearDownModule():
    unload_language("uk")


class TestFuzzyMatch(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(fuzzy_match("ти і ми", "ти і ми") >= 1.0)
        self.assertTrue(fuzzy_match("ти і ми", "ти") < 0.5)
        self.assertTrue(fuzzy_match("Ти", "ти") >= 0.5)
        self.assertTrue(fuzzy_match("ти і ми", "ти") ==
                        fuzzy_match("ти", "ти і ми"))
        self.assertTrue(fuzzy_match("ти і ми", "він або вони") < 0.36)

    def test_match_one(self):
        #test list of choices
        choices = ['френк', 'кейт', 'гаррі', 'генрі']
        self.assertEqual(match_one('френк', choices)[0], 'френк')
        self.assertEqual(match_one('френ', choices)[0], 'френк')
        self.assertEqual(match_one('енрі', choices)[0], 'генрі')
        self.assertEqual(match_one('кетт', choices)[0], 'кейт')
        # test dictionary of choices
        choices = {'френк': 1, 'кейт': 2, 'гаррі': 3, 'генрі': 4}
        self.assertEqual(match_one('френк', choices)[0], 1)
        self.assertEqual(match_one('енрі', choices)[0], 4)


class TestNormalize(unittest.TestCase):

    def test_extract_number(self):
        load_language("uk-uk")
        set_default_lang("uk")
        #self.assertEqual(extract_number("одної третьої чашки"), 1.0 / 3.0)
        self.assertEqual(extract_number("це перший тест",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("це 2 тест"), 2)
        self.assertEqual(extract_number("це другий тест",
                                        ordinals=True), 2)
        self.assertEqual(extract_number("це одна третя тесту"), 1.0 / 3.0)
        self.assertEqual(extract_number("цей перший третій тест",
                                        ordinals=True), 3.0)
        self.assertEqual(extract_number("це четвертий", ordinals=True), 4.0)
        self.assertEqual(extract_number(
            "це тридцять шостий", ordinals=True), 36.0)
        self.assertEqual(extract_number("це тест на число 4"), 4)
        self.assertEqual(extract_number("одна третя чашки"), 1.0 / 3.0)
        self.assertEqual(extract_number("три чашки"), 3)
        self.assertEqual(extract_number("1/3 чашки"), 1.0 / 3.0)
        self.assertEqual(extract_number("чверть чашки"), 0.25)
        self.assertEqual(extract_number("одна четверта чашки"), 0.25)
        self.assertEqual(extract_number("1/4 чашки"), 0.25)
        self.assertEqual(extract_number("2/3 чашки"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 чашки"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 і 3/4 чашки"), 1.75)
        self.assertEqual(extract_number("1 чашка з половиною"), 1.5)
        self.assertEqual(extract_number("одна чашка з половиною"), 1.5)
        self.assertEqual(extract_number("одна і половина чашки"), 1.5)
        self.assertEqual(extract_number("одна з половиною чашка"), 1.5)
        self.assertEqual(extract_number("одна і одна половина чашки"), 1.5)
        self.assertEqual(extract_number("три чверті чашки"), 3.0 / 4.0)
        self.assertEqual(extract_number("двадцять два"), 22)
        self.assertEqual(extract_number("Двадцять два з великої букви на початку"), 22)
        self.assertEqual(extract_number(
            "Двадцять Два з двома великими буквами"), 22)
        self.assertEqual(extract_number(
            "двадцять Два з другою великою буквою"), 22)
        self.assertEqual(extract_number("три шостих"), 0.5)
        self.assertEqual(extract_number("Двадцять два і Три П'ятих"), 22.6)
        self.assertEqual(extract_number("двісті"), 200)
        self.assertEqual(extract_number("дев'ять тисяч"), 9000)
        self.assertEqual(extract_number("шістсот шістдесят шість"), 666)
        self.assertEqual(extract_number("два мільйона"), 2000000)
        self.assertEqual(extract_number("два мільйона п'ятсот тисяч "
                                        "тонн чугуна"), 2500000)
        self.assertEqual(extract_number("шість трильйонів", short_scale=False),
                         6e+18)
        self.assertEqual(extract_number("один крапка п'ять"), 1.5)
        self.assertEqual(extract_number("три крапка чотирнадцять"), 3.14)
        self.assertEqual(extract_number("нуль крапка два"), 0.2)
        self.assertEqual(extract_number("мільярд років"),
                         1000000000.0)
        self.assertEqual(extract_number("більйон років",
                                        short_scale=False),
                         1000000000000.0)
        self.assertEqual(extract_number("сто тисяч"), 100000)
        self.assertEqual(extract_number("мінус 2"), -2)
        self.assertEqual(extract_number("мінус сімдесят"), -70)
        self.assertEqual(extract_number("тисяча мільйонів"), 1000000000)
        self.assertEqual(extract_number("мільярд", short_scale=False),
                         1000000000)

        self.assertEqual(extract_number("тридцять секунд"), 30)
        self.assertEqual(extract_number("тридцять два", ordinals=True), 32)

        self.assertEqual(extract_number("ось це мільярдний тест",
                             ordinals=True), 1000000000)

        self.assertEqual(extract_number("ось це мільйонний тест",
                                       ordinals=True), 1000000)

        self.assertEqual(extract_number("ось це одна мільярдна теста"), 1e-9)

        self.assertEqual(extract_number("ось це більйонний тест",
                                        ordinals=True,
                                        short_scale=False), 1e12)
        self.assertEqual(extract_number("ось це одна більйонна теста",
                                        short_scale=False), 1000000000000.0)

        self.assertEqual(extract_number("двадцять тисяч"), 20000)
        self.assertEqual(extract_number("п'ятдесят мільйонів"), 50000000)

        self.assertEqual(extract_number("двадцять мільярдів триста мільйонів "
                                        "дев'ятсот п'ятдесят тисяч "
                                        "шістсот сімдесят п'ять крапка вісім"),
                         20300950675.8)
        self.assertEqual(extract_number("дев'ятсот дев'яносто дев'ять мільйонів "
                                        "дев'ятсот дев'яносто дев'ять тисяч "
                                        "дев'ятсот дев'яносто дев'ять крапка дев'ять"),
                         999999999.9)

        self.assertEqual(extract_number("шість трильйонів"), 6e18)

        # TODO handle this case 'трильйонів' error
        # self.assertEqual(extract_number("вісімсот трильйонів двісті \
        #                                 п'ятдесят сім"), 800+1e+18+200+57)

        # # TODO handle this case returns 6.6
        # self.assertEqual(
        #    extract_number("6 крапка шість шість шість"),
        #    6.666)

        self.assertTrue(extract_number("Тенісист швидкий") is False)
        self.assertTrue(extract_number("тендітний") is False)

        self.assertTrue(extract_number("тендітний нуль") is not False)
        self.assertEqual(extract_number("тендітний нуль"), 0)


        self.assertTrue(extract_number("грубий 0") is not False)
        self.assertEqual(extract_number("грубий 0"), 0)

        self.assertEqual(extract_number("пара пива"), 2)
        self.assertEqual(extract_number("пара тисяч пива"), 2000)

        # # Todo problem in line 502 parse_uk.py
        # print(extract_number("три сотні"))
        # self.assertEqual(extract_number("пара сотень пива"), 200)
        # print(extract_number("пара сотень пива"))

        self.assertEqual(extract_number(
            "ось це 7 тест", ordinals=True), 7)
        self.assertEqual(extract_number(
            "ось це 7 тест", ordinals=False), 7)
        self.assertTrue(extract_number("ось це n. тест") is False)
        self.assertEqual(extract_number("ось це 1. тест"), 1)
        self.assertEqual(extract_number("ось це 2. тест"), 2)
        self.assertEqual(extract_number("ось це 3. тест"), 3)
        self.assertEqual(extract_number("ось це 31. тест"), 31)
        self.assertEqual(extract_number("ось це 32. тест"), 32)
        self.assertEqual(extract_number("ось це 33. тест"), 33)
        self.assertEqual(extract_number("ось це 34. тест"), 34)
        self.assertEqual(extract_number("о цілому 100%"), 100)

    def test_extract_duration_uk(self):
        load_language("uk-uk")
        set_default_lang("uk")
        print(extract_duration("25 днів"))
        # self.assertEqual(extract_duration("25 днів"),
        #                  (timedelta(days=25.0), ""))
        self.assertEqual(extract_duration("10 секунд"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 хвилин"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 години"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 дні"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 тижні"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("сім годин"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 секунд"),
                         (timedelta(seconds=7.5), ""))

        # todo why returns "в"
        self.assertEqual(extract_duration("вісім з половиною днів "
                                          "тридцять дев'ять секунд"),
                         (timedelta(days=8.5, seconds=39), "в"))
        self.assertEqual(extract_duration("встанови таймер на 30 хвилин"),
                         (timedelta(minutes=30), "встанови таймер на"))
        self.assertEqual(extract_duration("чотири з половиною хвилини до"
                                          " заходу сонця"),
                         (timedelta(minutes=4.5), "до заходу сонця"))
        self.assertEqual(extract_duration("дев'ятнадцять хвилин після першої години"),
                         (timedelta(minutes=19), "після першої години"))

        # # todo fix this issue
        # self.assertEqual(extract_duration("розбуди меня через три тижня, "
        #                                   "чотириста дев'яносто сім днів "
        #                                   "і триста 91.6 секунд"),
        #                  (timedelta(weeks=3, days=497, seconds=391.6),
        #                   "разбуди меня через , a"))

        self.assertEqual(extract_duration("фільм одну годину п'ятдесят сім"
                                          " і пів хвилин довжиною"),
                         (timedelta(hours=1, minutes=57.5),
                          "фільм   довжиною"))
        self.assertEqual(extract_duration("10-секунд"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-хвилин"),
                         (timedelta(minutes=5), ""))

    def test_extractdatetime_uk(self):
        load_language("uk-uk")
        set_default_lang("uk")

        def extractWithFormat(text):

            # Tue June 27, 2017 @ 1:04pm
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            print(res)
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())
        load_language("uk-uk")
        set_default_lang("uk")

        # testExtract("зараз година",
        #             "2017-06-27 13:04:00", "година")
        # self.u = "секунду"
        # testExtract("через %s" % self.u,
        #             "2017-06-27 13:04:01", "")
        # testExtract("через хвилину",
        #             "2017-06-27 13:05:00", "")
        testExtract("через дві хвилини",
                    "2017-06-27 13:06:00", "")

        # # TODO non-iterable NoneType object
        # testExtract("через пару хвилин",
        #            "2017-06-27 13:06:00", "")

        # TODO handle this case adds only 1h
        # testExtract("через дві години",
        #             "2017-06-27 15:04:00", "")
        # testExtract("через пару годин",
        #            "2017-06-27 15:04:00", "")

        # TODO non-iterable NoneType object
        # testExtract("через два тижні",
        #             "2017-07-11 00:00:00", "")
        # testExtract("через пару тижнів",
        #            "2017-07-11 00:00:00", "")

        testExtract("через два місяці",
                    "2017-08-27 00:00:00", "")
        testExtract("через два роки",
                    "2019-06-27 00:00:00", "")
        # testExtract("через пару місяців",
        #            "2017-08-27 00:00:00", "")
        # testExtract("через пару років",
        #            "2019-06-27 00:00:00", "")
        testExtract("через десятиліття",
                    "2027-06-27 00:00:00", "")
        testExtract("наступне десятиліття",
                    "2027-06-27 00:00:00", "")
        testExtract("через століття",
                    "2117-06-27 00:00:00", "")
        testExtract("через тисячоліття",
                    "3017-06-27 00:00:00", "")
        testExtract("через два десятиліття",
                    "2037-06-27 00:00:00", "")

        # TODO non-iterable NoneType object
        # testExtract("через 5 десятиліть",
        #             "2067-06-27 00:00:00", "")

        # testExtract("через два века",
        #             "2217-06-27 00:00:00", "")
        # testExtract("через пару веков",
        #            "2217-06-27 00:00:00", "")
        # testExtract("через два тысячелетия",
        #             "4017-06-27 00:00:00", "")
        # testExtract("через дві тисячі років",
        #             "4017-06-27 00:00:00", "")
        # testExtract("через пару тысячелетий",
        #            "4017-06-27 00:00:00", "")
        # testExtract("через пару тисяч років",
        #            "4017-06-27 00:00:00", "")
        testExtract("через рік",
                    "2018-06-27 00:00:00", "")
        testExtract("хочу морозиво через годину",
                    "2017-06-27 14:04:00", "хочу морозиво")
        testExtract("через 1 секунду",
                    "2017-06-27 13:04:01", "")
        testExtract("через 2 секунди",
                    "2017-06-27 13:04:02", "")
        # testExtract("встанови таймер на 1 хвилину",
        #             "2017-06-27 13:05:00", "встанови таймер")
        testExtract("встанови таймер на пів години",
                    "2017-06-27 13:34:00", "встанови таймер")
        # testExtract("встанови таймер на 5 днів з сьогодні",
        #             "2017-07-02 00:00:00", "встанови таймер")
        testExtract("післязавтра",
                    "2017-06-29 00:00:00", "")
        testExtract("після завтра",
                    "2017-06-29 00:00:00", "")
        testExtract("яка погода післязавтра?",
                    "2017-06-29 00:00:00", "яка погода")
        testExtract("нагадай мені о 10:45 pm",
                    "2017-06-27 22:45:00", "нагадай мені")
        testExtract("нагадай мені о 10:45 вечора",
                    "2017-06-27 22:45:00", "нагадай мені")
        testExtract("яка погода у п'ятницю вранці",
                    "2017-06-30 08:00:00", "яка погода")
        testExtract("яка завтра погода",
                    "2017-06-28 00:00:00", "яка погода")
        testExtract("яка погода сьогодні вдень",
                    "2017-06-27 15:00:00", "яка погода")
        testExtract("яка погода сьогодні ввечері",
                    "2017-06-27 19:00:00", "яка погода")
        testExtract("яка була погода сьогодні вранці",
                    "2017-06-27 08:00:00", "яка була погода")
        # testExtract("нагадай мені зателефонувати мамі через 8 тижнів і 2 дні",
        #             "2017-08-24 00:00:00", "нагадай мені зателефонувати мамі")
        # testExtract("нагадай мені зателефонувати мамі у серпні 3",
        #             "2017-08-03 00:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені завтра зателефонувати мамі о 7am",
                    "2017-06-28 07:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені завтра зателефонувати мамі о 7 ранку",
                    "2017-06-28 07:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені завтра зателефонувати мамі о 10pm",
                    "2017-06-28 22:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені завтра зателефонувати мамі о 7 вечора",
                    "2017-06-28 19:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені завтра зателефонувати мамі о 10 вечора",
                    "2017-06-28 22:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені завтра зателефонувати мамі о 7 годині вечора",
                    "2017-06-28 19:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені завтра зателефонувати мамі о 10 годині вечора",
                    "2017-06-28 22:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 7am",
                    "2017-06-28 07:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 7 ранку",
                    "2017-06-28 07:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через годину",
                    "2017-06-27 14:04:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 1730",
                    "2017-06-27 17:30:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 0630",
                    "2017-06-28 06:30:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 06 30 годин",
                    "2017-06-28 06:30:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 06 30",
                    "2017-06-28 06:30:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 06 30 годин",
                    "2017-06-28 06:30:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 7 годині",
                    "2017-06-27 19:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі ввечері о 7 годин",
                    "2017-06-27 19:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 7 годині вечора",
                    "2017-06-27 19:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 7 годині ранку",
                    "2017-06-28 07:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі у четвер ввечері о 7 годині",
                    "2017-06-29 19:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі у четвер вранці о 7 годині",
                    "2017-06-29 07:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 7 годині у четвер вранці",
                    "2017-06-29 07:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 7:00 у четвер вранці",
                    "2017-06-29 07:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 7:00 у четвер ввечері",
                    "2017-06-29 19:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 8 вечора середи",
                    "2017-06-28 20:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 8 у середу ввечері",
                    "2017-06-28 20:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі ввечері середи о 8",
                    "2017-06-28 20:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через дві години",
                    "2017-06-27 15:04:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через 2 години",
                    "2017-06-27 15:04:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через 15 хвилин",
                    "2017-06-27 13:19:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через п'ятнадцять хвилин",
                    "2017-06-27 13:19:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через пів години",
                    "2017-06-27 13:34:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через чверть години",
                    "2017-06-27 13:19:00", "нагадай мені зателефонувати мамі")
        # testExtract("нагадай мені зателефонувати мамі о 10am на 2 день после этой суботи",
        #             "2017-07-03 10:00:00", "нагадай мені зателефонувати мамі")
        testExtract("слухайте музику Ріка Естлі через 2 дні з п'ятниці",
                    "2017-07-02 00:00:00", "слухайте музику ріка естлі")
        testExtract("почати вторгнення о 3:45 pm у четвер",
                    "2017-06-29 15:45:00", "почати вторгнення")
        testExtract("почати вторгнення о 3:45 вечора у четвер",
                    "2017-06-29 15:45:00", "почати вторгнення")
        testExtract("почати вторгнення о 3:45 дні у четвер",
                    "2017-06-29 15:45:00", "почати вторгнення")
        testExtract("у понеділок замов торт з пекарні",
                    "2017-07-03 00:00:00", "замов торт з пекарні")
        testExtract("увімкни музику з днем народження через 5 років",
                    "2022-06-27 00:00:00", "увімкни музику з днем народження")
        testExtract("Скайп мамі о 12:45 pm наступного четверга",
                    "2017-07-06 12:45:00", "скайп мамі")
        testExtract("Скайп мамі о 12:45 дні наступного четверга",
                    "2017-07-06 12:45:00", "скайп мамі")
        testExtract("яка погода у наступну п'ятницю?",
                    "2017-06-30 00:00:00", "яка погода")
        testExtract("яка погода у наступну середу?",
                    "2017-07-05 00:00:00", "яка погода")
        testExtract("яка погода наступного четверга?",
                    "2017-07-06 00:00:00", "яка погода")
        testExtract("яка погода у наступну п'ятницю вранці",
                    "2017-06-30 08:00:00", "яка погода")
        testExtract("яка погода у наступну п'ятницю ввечері",
                    "2017-06-30 19:00:00", "яка погода")
        testExtract("яка погода у наступну п'ятницю днем",
                    "2017-06-30 15:00:00", "яка погода")
        testExtract("яка погода у наступну п'ятницю опівдні",
                    "2017-06-30 12:00:00", "яка погода")
        testExtract("нагадай мені зателефонувати мамі третього серпня",
                    "2017-08-03 00:00:00", "нагадай мені зателефонувати мамі")
        # testExtract("купить фейерверк о 4 у четвер",
        #             "2017-07-04 00:00:00", "купить фейерверк")
        testExtract("яка погода через 2 тижня з наступної п'ятниці",
                    "2017-07-14 00:00:00", "яка погода")
        testExtract("яка погода у середу о 0700 годин",
                    "2017-06-28 07:00:00", "яка погода")
        testExtract("встанови будильник у середу о 7 годин",
                    "2017-06-28 07:00:00", "встанови будильник")
        testExtract("признач зустріч о 12:45 pm наступного четверга",
                    "2017-07-06 12:45:00", "признач зустріч")
        testExtract("признач зустріч о 12:45 дні наступного четверга",
                    "2017-07-06 12:45:00", "признач зустріч")
        testExtract("яка погода у цей четвер?",
                    "2017-06-29 00:00:00", "яка погода")
        testExtract("признач зустріч через 2 тижні і 6 днів з суботи",
                    "2017-07-21 00:00:00", "признач зустріч")
        testExtract("почати вторгнення о 03 45 у четвер",
                    "2017-06-29 03:45:00", "почати вторгнення")
        testExtract("почати вторгнення о 800 годин у четвер",
                    "2017-06-29 08:00:00", "почати вторгнення")
        testExtract("Начать вечеринку о 8 годині ввечері у четвер",
                    "2017-06-29 20:00:00", "начать вечеринку")
        testExtract("почати вторгнення о 8 вечора у четвер",
                    "2017-06-29 20:00:00", "почати вторгнення")
        testExtract("почати вторгнення у четвер опівдні",
                    "2017-06-29 12:00:00", "почати вторгнення")
        testExtract("почати вторгнення у четвер опівночі",
                    "2017-06-29 00:00:00", "почати вторгнення")
        testExtract("почати вторгнення у четвер о 0500",
                    "2017-06-29 05:00:00", "почати вторгнення")
        testExtract("нагадай мені встати через 4 роки",
                    "2021-06-27 00:00:00", "нагадай мені встати")
        testExtract("нагадай мені встати через 4 роки і 4 дні",
                    "2021-07-01 00:00:00", "нагадай мені встати")
        # testExtract("яка погода 3 дні после завтра?",
        #             "2017-07-01 00:00:00", "яка погода")
        testExtract("3 декабря",
                    "2017-12-03 00:00:00", "")
        testExtract("ми зустрінемось о 8:00 сьогодні ввечері",
                    "2017-06-27 20:00:00", "ми зустрінемось")
        testExtract("ми зустрінемось о 5pm",
                    "2017-06-27 17:00:00", "ми зустрінемось")
        testExtract("ми зустрінемось о 5 дні",
                    "2017-06-27 17:00:00", "ми зустрінемось")
        testExtract("ми зустрінемось о 8 am",
                    "2017-06-28 08:00:00", "ми зустрінемось")
        testExtract("ми зустрінемось о 8 ранку",
                    "2017-06-28 08:00:00", "ми зустрінемось")
        testExtract("ми зустрінемось о 8 вечора",
                    "2017-06-27 20:00:00", "ми зустрінемось")
        testExtract("нагадати мені прокинутись о 8 am",
                    "2017-06-28 08:00:00", "нагадати мені прокинутись")
        testExtract("нагадати мені прокинутись о 8 ранку",
                    "2017-06-28 08:00:00", "нагадати мені прокинутись")
        testExtract("яка погода у вівторок",
                    "2017-06-27 00:00:00", "яка погода")
        testExtract("яка погода у понеділок",
                    "2017-07-03 00:00:00", "яка погода")
        testExtract("яка погода у цю середу",
                    "2017-06-28 00:00:00", "яка погода")
        testExtract("у четвер яка погода",
                    "2017-06-29 00:00:00", "яка погода")
        testExtract("у цей четвер яка погода",
                    "2017-06-29 00:00:00", "яка погода")
        testExtract("о минулий понеділок яка була погода",
                    "2017-06-26 00:00:00", "яка була погода")
        testExtract("встанови будильник на середу вечір о 8",
                    "2017-06-28 20:00:00", "встанови будильник")
        testExtract("встанови будильник на середу о 3 години дні",
                    "2017-06-28 15:00:00", "встанови будильник")
        testExtract("встанови будильник на середу о 3 годині ранку",
                    "2017-06-28 03:00:00", "встанови будильник")
        testExtract("встанови будильник на середу вранці о 7 годин",
                    "2017-06-28 07:00:00", "встанови будильник")
        testExtract("встанови будильник на сьогодні о 7 годин",
                    "2017-06-27 19:00:00", "встанови будильник")
        testExtract("встанови будильник на цей вечір о 7 годин",
                    "2017-06-27 19:00:00", "встанови будильник")
        testExtract("встанови будильник на цей вечір о 7:00",
                    "2017-06-27 19:00:00", "встанови будильник")
        # testExtract("встанови будильник этим ввечері о 7:00",
        #             "2017-06-27 19:00:00", "встанови будильник")
        testExtract("ввечері 5 июня 2017 нагадай мені зателефонувати мамі",
                    "2017-06-05 19:00:00", "нагадай мені зателефонувати мамі")
        testExtract("обнови мій календар вранці побачення з юлиусом" +
                    " 4 березня",
                    "2018-03-04 08:00:00",
                    "обнови мій календар побачення з юлиусом")
        testExtract("нагадай мені зателефонувати мамі наступного вівторок",
                    "2017-07-04 00:00:00", "нагадай мені зателефонувати мамі")
        # testExtract("нагадай мені зателефонувати мамі 3 тижня",
        #             "2017-07-18 00:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через 8 тижнів",
                    "2017-08-22 00:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через 8 тижнів і 2 дні",
                    "2017-08-24 00:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через 4 дні",
                    "2017-07-01 00:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через 3 місяці",
                    "2017-09-27 00:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі через 2 роки і 2 дні",
                    "2019-06-29 00:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі наступного тижня",
                    "2017-07-04 00:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 10am у субботу",
                    "2017-07-01 10:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 10 ранку у субботу",
                    "2017-07-01 10:00:00", "нагадай мені зателефонувати мамі")
        # testExtract("нагадай мені зателефонувати мамі о 10am о цю субботу",
        #             "2017-07-01 10:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 10 у наступну субботу",
                    "2017-07-01 10:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 10am у наступну субботу",
                    "2017-07-01 10:00:00", "нагадай мені зателефонувати мамі")
        testExtract("нагадай мені зателефонувати мамі о 10 ранку у наступну субботу",
                    "2017-07-01 10:00:00", "нагадай мені зателефонувати мамі")
        # test yesterday testExtract("який був день вчора",
        #            "2017-06-26 00:00:00", "який був день")
        testExtract("який був день позавчора",
                    "2017-06-25 00:00:00", "який був день")
        testExtract("я поснідав вчора о 6",
                    "2017-06-26 06:00:00", "я поснідав")
        testExtract("я поснідав вчора о 6 am",
                    "2017-06-26 06:00:00", "я поснідав")
        testExtract("я поснідав вчора о 6 ранку",
                    "2017-06-26 06:00:00", "я поснідав")

        # Below two tests, ensure that time is picked
        # even if no am/pm is specified
        # in case of weekdays/tonight testExtract("встанови будильник на 9 на вихідні",
        #            "2017-06-27 21:00:00", "встанови будильник вихідні")
        testExtract("на 8 сьогодні ввечері",
                    "2017-06-27 20:00:00", "")
        testExtract("на 8:30pm сьогодні ввечері",
                    "2017-06-27 20:30:00", "")
        testExtract("на 8:30 вечора сьогодні",
                    "2017-06-27 20:30:00", "")
        testExtract("на 8:30 вечора сьогодні",
                    "2017-06-27 20:30:00", "")
        # Tests a time with ':' & without am/pm testExtract("встанови будильник сьогодні ввечері на 9:30",
        #            "2017-06-27 21:30:00", "встанови будильник")
        testExtract("встанови будильник на 9:00 сьогодні ввечері",
                    "2017-06-27 21:00:00", "встанови будильник")
        # Check if it picks intent irrespective of correctness testExtract("встанови будильник о 9 годині сьогодні ввечері",
        #            "2017-06-27 21:00:00", "встанови будильник")
        testExtract("нагадай мені про гру сьогодні ввечері о 11:30",
                    "2017-06-27 23:30:00", "нагадай мені про гру")
        testExtract("встанови будильник о 7:30 на вихідні",
                    "2017-06-27 19:30:00", "встанови будильник на вихідні")

        #  "# days <from X/after X>"
        testExtract("мій день рождения через 2 дні від сьогодні",
                    "2017-06-29 00:00:00", "мій день рождения")
        testExtract("мій день рождения через 2 дні від сьогодні",
                    "2017-06-29 00:00:00", "мій день рождения")
        testExtract("мій день рождения через 2 дні від завтра",
                    "2017-06-30 00:00:00", "мій день рождения")
        testExtract("мій день рождения через 2 дні від завтра",
                    "2017-06-30 00:00:00", "мій день рождения")
        # testExtract("нагадай мені зателефонувати мамі о 10am через 2 дні после наступної суботи",
        #             "2017-07-10 10:00:00", "нагадай мені зателефонувати мамі")
        testExtract("мій день рождения через 2 дні від вчора",
                    "2017-06-28 00:00:00", "мій день рождения")
        testExtract("мій день рождения через 2 дні від вчора",
                    "2017-06-28 00:00:00", "мій день рождения")

        #  "# days ago>"
        testExtract("мій день рождения був 1 день тому",
                    "2017-06-26 00:00:00", "мій день рождения був")
        testExtract("мій день рождения був 2 дні тому",
                    "2017-06-25 00:00:00", "мій день рождения був")
        testExtract("мій день рождения був 3 дні тому",
                    "2017-06-24 00:00:00", "мій день рождения був")
        testExtract("мій день рождения був 4 дні тому",
                    "2017-06-23 00:00:00", "мій день рождения був")
        testExtract("мій день рождения був 5 днів тому",
                    "2017-06-22 00:00:00", "мій день рождения був")
        testExtract("зустрінемось сьогодні вночі",
                    "2017-06-27 22:00:00", "зустрінемось вночі")
        testExtract("зустрінемось пізніше вночі",
                    "2017-06-27 22:00:00", "зустрінемось пізніше вночі")
        testExtract("яка будет погода завтра вночі",
                    "2017-06-28 22:00:00", "яка будет погода вночі")
        testExtract("яка будет погода наступного вівторок вночі",
                    "2017-07-04 22:00:00", "яка будет погода вночі")

    def test_extract_ambiguous_time_uk(self):
        morning = datetime(2017, 6, 27, 8, 1, 2, tzinfo=default_timezone())
        evening = datetime(2017, 6, 27, 20, 1, 2, tzinfo=default_timezone())
        noonish = datetime(2017, 6, 27, 12, 1, 2, tzinfo=default_timezone())
        self.assertEqual(extract_datetime('годування риб'), None)
        self.assertEqual(extract_datetime('день'), None)
        # self.assertEqual(extract_datetime('сьогодні'), None)
        self.assertEqual(extract_datetime('місяць'), None)
        self.assertEqual(extract_datetime('рік'), None)
        self.assertEqual(extract_datetime(' '), None)
        self.assertEqual(
            extract_datetime('погодувати риб о 10 годині', morning)[0],
            datetime(2017, 6, 27, 10, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('погодувати риб о 10 годині', noonish)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('погодувати риб о 10 годині', evening)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))

    def test_extract_relativedatetime_uk(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("ми зустрінемось через 5 хвилин",
                    "2017-06-27 10:06:02", "ми зустрінемось")
        testExtract("ми зустрінемось через 5 секунд",
                    "2017-06-27 10:01:07", "ми зустрінемось")
        testExtract("ми зустрінемось через 1 годину",
                    "2017-06-27 11:01:02", "ми зустрінемось")
        testExtract("ми зустрінемось через 2 години",
                    "2017-06-27 12:01:02", "ми зустрінемось")
        testExtract("ми зустрінемось через 1 хвилину",
                    "2017-06-27 10:02:02", "ми зустрінемось")
        testExtract("ми зустрінемось через 1 секунду",
                    "2017-06-27 10:01:03", "ми зустрінемось")

        #To do: spaces error
        # testExtract("ми зустрінемось через 5хвилин",
        #             "2017-06-27 10:06:02", "ми зустрінемось")
        # testExtract("ми зустрінемось через 5секунд",
        #             "2017-06-27 10:01:07", "ми зустрінемось")

    # PASSED
    def test_spaces(self):
        self.assertEqual(normalize("ось це тест"),
                         "ось це тест")
        self.assertEqual(normalize("ось     це тест  "),
                         "ось це тест")
        self.assertEqual(normalize("ось це один     тест"),
                         "ось це 1 тест")

    # PASSED
    def test_numbers(self):
        self.assertEqual(normalize("ось це один два три тест"),
                         "ось це 1 2 3 тест")
        self.assertEqual(normalize("  ось це чотири п'ять шість тест"),
                         "ось це 4 5 6 тест")
        self.assertEqual(normalize("ось це сім вісім дев'ять тест"),
                         "ось це 7 8 9 тест")
        self.assertEqual(normalize("ось це сім вісім дев'ять тест"),
                         "ось це 7 8 9 тест")
        self.assertEqual(normalize("ось це десять одинадцять дванадцять тест"),
                         "ось це 10 11 12 тест")
        self.assertEqual(normalize("ось це тринадцять чотирнадцять тест"),
                         "ось це 13 14 тест")
        self.assertEqual(normalize("ось це п'ятнадцять шістнадцять сімнадцять"),
                         "ось це 15 16 17")
        self.assertEqual(normalize("ось це  вісімнадцять дев'ятнадцять двадцять"),
                         "ось це 18 19 20")
        self.assertEqual(normalize("ось це один дев'ятнадцять двадцять два"),
                         "ось це 1 19 20 2")
        self.assertEqual(normalize("ось це один сто"),
                         "ось це 1 сто")
        self.assertEqual(normalize("ось це один два двадцять два"),
                         "ось це 1 2 20 2")
        self.assertEqual(normalize("ось це один і половина"),
                         "ось це 1 і половина")
        self.assertEqual(normalize("ось це один і половина і п'ять шість"),
                         "ось це 1 і половина і 5 6")

    # PASSED
    def test_multiple_numbers(self):
        load_language("uk-uk")
        set_default_lang("uk")
        self.assertEqual(extract_number("шістсот шістдесят шість"), 666)
        self.assertEqual(extract_number("чотириста тридцять шість"), 436)
        self.assertEqual([400.0], extract_numbers("немає чотириста ведмідів"))
        self.assertEqual([436.0], extract_numbers("немає чотириста тридцять шість ведмідів"))
        # self.assertEqual(extract_numbers("немає шістдесятьох ведмідів"),
        #                  [60.0])
        # self.assertEqual(extract_numbers("немає двадцяти ведмідів"),
        #                  [20.0])
        # self.assertEqual(extract_numbers("немає дев'ятнадцяти ведмідів"),
        #                  [19.0])
        # self.assertEqual(extract_numbers("немає одинадцяти ведмідів"),
        #                  [11.0])
        # self.assertEqual(extract_numbers("немає трьох ведмідів"),
        #                  [3.0])
        # self.assertEqual(extract_numbers("два пива для двох ведмідів"),
        #                  [2.0, 2.0])
        # self.assertEqual(extract_numbers("ось це один два три тест"),
        #                  [1.0, 2.0, 3.0])
        # self.assertEqual(extract_numbers("ось це чотири п'ять шість тест"),
        #                  [4.0, 5.0, 6.0])
        # self.assertEqual(extract_numbers("ось це десять одинадцять дванадцять тест"),
        #                  [10.0, 11.0, 12.0])
        # self.assertEqual(extract_numbers("ось це один двадцять один тест"),
        #                  [1.0, 21.0])
        # self.assertEqual(extract_numbers("1 собака, сім свиней, у макдональда "
        #                                  "була ферма ферма, 3 рази по 5 макарен"),
        #                  [1, 7, 3, 5])
        # self.assertEqual(extract_numbers("два пива для двох ведмідів"),
        #                  [2.0, 2.0])
        # self.assertEqual(extract_numbers("двадцять 20 двадцять"),
        #                  [20, 20, 20])
        # self.assertEqual(extract_numbers("двадцять 20 22"),
        #                  [20.0, 20.0, 22.0])
        # self.assertEqual(extract_numbers("двадцять двадцять два двадцять"),
        #                  [20, 22, 20])
        # self.assertEqual(extract_numbers("двадцять 2"),
        #                  [22.0])
        # self.assertEqual(extract_numbers("двадцять 20 двадцять 2"),
        #                  [20, 20, 22])
        # self.assertEqual(extract_numbers("третина один"),
        #                  [1 / 3, 1])
        # self.assertEqual(extract_numbers("третій", ordinals=True), [3])
        #
        # #To do: long scale and short scale are same
        # self.assertEqual(extract_numbers("шість трильйонів", short_scale=True),
        #                  [6e18])
        # print(extract_numbers("шість трильйонів", short_scale=False))
        # self.assertEqual(extract_numbers("шість трильйонів", short_scale=False),
        #                  [6e18])
        # self.assertEqual(extract_numbers("два порося і шість трильйонів бактерій",
        #                                  short_scale=True), [2, 6e+18])
        #
        # self.assertEqual(extract_numbers("два порося і шість трильйонів бактерій",
        #                                  short_scale=False), [2, 6e+18])
        # self.assertEqual(extract_numbers("тридцять другий або перший",
        #                                  ordinals=True), [32, 1])
        # self.assertEqual(extract_numbers("ось це сім вісім дев'ять і"
        #                                  " половина тест"),
        #                  [7.0, 8.0, 9.5])



if __name__ == "__main__":
    unittest.main()

