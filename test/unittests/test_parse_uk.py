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
from lingua_franca import set_default_lang, load_language, unload_language
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import fuzzy_match
from lingua_franca.parse import match_one
from lingua_franca.parse import normalize
from lingua_franca.parse import yes_or_no


def setUpModule():
    load_language("uk-ua")
    set_default_lang("uk")


def tearDownModule():
    unload_language("uk")

class TestYesNo(unittest.TestCase):
    def test_yesno(self):
        def test_utt(text, expected):
            res = yes_or_no(text, "uk-ua")
            self.assertEqual(res, expected)

        test_utt("ні", False)
        test_utt("так", True)
        test_utt("так але ні", False)
        test_utt("не думаю", False)
        test_utt("не згодна", False)
        test_utt("думаю, що ні", False)
        test_utt("горіх", None)
        test_utt("ні, але насправді, так", True)
        test_utt("так але насправді ні", False)
        test_utt("будь ласка", True)
        test_utt("будь ласка, не треба", False)
        test_utt("задовільняє", True)
        test_utt("незадовільно", False)
        test_utt("правильно", True)


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
        load_language("uk-ua")
        set_default_lang("uk")

        # # TODO handle this case returns 6.6
        # self.assertEqual(
        #    extract_number("6 крапка шість шість шість"),
        #    6.666)

        self.assertEqual(extract_number("половина чашки"), 0.5)
        self.assertEqual(extract_number("пів чашки"), 0.5)
        self.assertEqual(extract_number("чверть чашки"), 0.25)
        self.assertEqual(extract_number("одна третя чашки"), 1.0 / 3.0)
        self.assertEqual(extract_number("немає одної третьої чашки"), 1.0 / 3.0)
        self.assertEqual(extract_number("одної другої чашки"), 1.0 / 2.0)
        self.assertEqual(extract_number("одної шостої чашки"), 1.0 / 6.0)
        self.assertEqual(extract_number("одна п'ята чашки"), 1.0 / 5.0)
        self.assertEqual(extract_number("одна третя чашки"), 1.0 / 3.0)

        self.assertEqual(extract_number("три чашки"), 3)
        self.assertEqual(extract_number("1/3 чашки"), 1.0 / 3.0)
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
        self.assertEqual(extract_number("вісімсот трильйонів двісті п'ятдесят сім"), 800*1e18+200+57)

        self.assertTrue(extract_number("Тенісист швидкий") is False)
        self.assertTrue(extract_number("тендітний") is False)

        self.assertTrue(extract_number("тендітний нуль") is not False)
        self.assertEqual(extract_number("тендітний нуль"), 0)


        self.assertTrue(extract_number("грубий 0") is not False)
        self.assertEqual(extract_number("грубий 0"), 0)

        self.assertEqual(extract_number("пара пива"), 2)
        self.assertEqual(extract_number("пара тисяч пива"), 2000)
        self.assertEqual(extract_number("три пари пива"), 6)

        self.assertEqual(extract_number("пара сотень пива"), 200)
        self.assertEqual(extract_number("дві сотні"), 200)
        self.assertEqual(extract_number("три сотні"), 300)

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

    def test_spaces(self):
        self.assertEqual(normalize("ось це тест"),
                         "ось це тест")
        self.assertEqual(normalize("ось     це тест  "),
                         "ось це тест")
        self.assertEqual(normalize("ось це один     тест"),
                         "ось це 1 тест")

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
                         "ось це 1 100")
        self.assertEqual(normalize("ось це один два двадцять два"),
                         "ось це 1 2 20 2")
        self.assertEqual(normalize("ось це один і половина"),
                         "ось це 1 і половина")
        self.assertEqual(normalize("ось це один і половина і п'ять шість"),
                         "ось це 1 і половина і 5 6")

    def test_multiple_numbers(self):
        load_language("uk-ua")
        set_default_lang("uk")
        self.assertEqual(extract_number("шістсот шістдесят шість"), 666)
        self.assertEqual(extract_number("чотирьохсот тридцяти шести"), 436)
        self.assertEqual(extract_numbers("ось це сім вісім дев'ять і"
                                         " половина тест"),
                         [7.0, 8.0, 9.5])
        self.assertEqual(extract_numbers("нема семи восьми дев'яти і"
                                         " половини тестів"),
                         [7.0, 8.0, 9.5])
        self.assertEqual(extract_numbers("ось це шість шість шість тест"), [6.0, 6.0, 6.0])
        self.assertEqual(extract_number("чотириста тридцять шість"), 436)

        self.assertEqual(436.0, extract_number("немає чотирьохсот тридцяти шести ведмідів"))

        self.assertEqual([400.0], extract_numbers("немає чотирьохсот ведмідів"))
        self.assertEqual([2.0], extract_numbers("немає двох ведмідів"))
        self.assertEqual([400.0], extract_numbers("немає чотирьохсот ведмідів"))

        self.assertEqual(extract_numbers("немає шістдесятьох ведмідів"),
                         [60.0])
        self.assertEqual(extract_numbers("немає двадцяти ведмідів"),
                         [20.0])
        self.assertEqual(extract_numbers("немає дев'ятнадцяти ведмідів"),
                         [19.0])
        self.assertEqual(extract_numbers("немає одинадцяти ведмідів"),
                         [11.0])
        self.assertEqual(extract_numbers("немає трьох ведмідів"),
                         [3.0])
        self.assertEqual(extract_numbers("два пива для двох ведмідів"),
                         [2.0, 2.0])
        self.assertEqual(extract_numbers("ось це один два три тест"),
                         [1.0, 2.0, 3.0])
        self.assertEqual(extract_numbers("ось це чотири п'ять шість тест"),
                         [4.0, 5.0, 6.0])
        self.assertEqual(extract_numbers("ось це десять одинадцять дванадцять тест"),
                         [10.0, 11.0, 12.0])
        self.assertEqual(extract_numbers("ось це один двадцять один тест"),
                         [1.0, 21.0])
        self.assertEqual(extract_numbers("1 собака, сім свиней, у макдональда "
                                         "була ферма ферма, 3 рази по 5 макарен"),
                         [1, 7, 3, 5])
        self.assertEqual(extract_numbers("два пива для двох ведмідів"),
                         [2.0, 2.0])
        self.assertEqual(extract_numbers("двадцять 20 двадцять"),
                         [20, 20, 20])
        # self.assertEqual(extract_numbers("двадцять 20 22"),
        #                  [20.0, 20.0, 22.0])
        self.assertEqual(extract_numbers("двадцять двадцять два двадцять"),
                         [20, 22, 20])
        self.assertEqual(extract_numbers("двадцять 2"),
                         [22.0])
        self.assertEqual(extract_numbers("двадцять 20 двадцять 2"),
                         [20, 20, 22])
        self.assertEqual(extract_numbers("третина один"),
                         [1 / 3, 1])
        self.assertEqual(extract_numbers("третій", ordinals=True), [3])

        self.assertEqual(extract_numbers("шість трильйонів", short_scale=True),
                         [6e18])
        self.assertEqual(extract_numbers("шість трильйонів", short_scale=False),
                         [6e18])
        self.assertEqual(extract_numbers("два порося і шість трильйонів бактерій",
                                         short_scale=True), [2, 6e+18])

        self.assertEqual(extract_numbers("два порося і шість трильйонів бактерій",
                                         short_scale=False), [2, 6e+18])
        self.assertEqual(extract_numbers("тридцять другий або перший",
                                         ordinals=True), [32, 1])
        self.assertEqual(extract_numbers("ось це сім вісім дев'ять і"
                                         " половина тест"),
                         [7.0, 8.0, 9.5])



if __name__ == "__main__":
    unittest.main()

