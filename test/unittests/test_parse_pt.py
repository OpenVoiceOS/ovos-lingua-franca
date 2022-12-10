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

from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.parse import get_color, extract_color_spans
from lingua_franca.parse import get_gender, extract_datetime, extract_number, normalize, yes_or_no, \
    extract_duration
from lingua_franca.time import default_timezone, DAYS_IN_1_YEAR, DAYS_IN_1_MONTH
from lingua_franca.util.colors import Color, ColorOutOfSpace


def setUpModule():
    load_language('pt-pt')
    set_default_lang('pt')


def tearDownModule():
    unload_language('pt')


class TestNormalize(unittest.TestCase):
    """
        Test cases for Portuguese parsing
    """

    def test_articles_pt(self):
        self.assertEqual(normalize("isto é o teste",
                                   lang="pt", remove_articles=True),
                         "isto é teste")
        self.assertEqual(
            normalize("isto é a frase", lang="pt", remove_articles=True),
            "isto é frase")
        self.assertEqual(
            normalize("e outro teste", lang="pt", remove_articles=True),
            "outro teste")
        self.assertEqual(normalize("isto é o teste extra",
                                   lang="pt",
                                   remove_articles=False), "isto é o teste extra")

    def test_extractnumber_pt(self):
        self.assertEqual(extract_number("isto e o primeiro teste", lang="pt"),
                         1)
        self.assertEqual(extract_number("isto e o 2 teste", lang="pt"), 2)
        self.assertEqual(extract_number("isto e o segundo teste", lang="pt"),
                         2)
        self.assertEqual(extract_number("isto e um terço de teste",
                                        lang="pt"), 1.0 / 3.0)
        self.assertEqual(extract_number("isto e o teste numero quatro",
                                        lang="pt"), 4)
        self.assertEqual(extract_number("um terço de chavena", lang="pt"),
                         1.0 / 3.0)
        self.assertEqual(extract_number("3 canecos", lang="pt"), 3)
        self.assertEqual(extract_number("1/3 canecos", lang="pt"), 1.0 / 3.0)
        self.assertEqual(extract_number("quarto de hora", lang="pt"), 0.25)
        self.assertEqual(extract_number("1/4 hora", lang="pt"), 0.25)
        self.assertEqual(extract_number("um quarto hora", lang="pt"), 0.25)
        self.assertEqual(extract_number("2/3 pinga", lang="pt"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 pinga", lang="pt"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 e 3/4 cafe", lang="pt"), 1.75)
        self.assertEqual(extract_number("1 cafe e meio", lang="pt"), 1.5)
        self.assertEqual(extract_number("um cafe e um meio", lang="pt"), 1.5)
        self.assertEqual(
            extract_number("tres quartos de chocolate", lang="pt"),
            3.0 / 4.0)
        self.assertEqual(
            extract_number("Tres quartos de chocolate", lang="pt"),
            3.0 / 4.0)
        self.assertEqual(extract_number("três quarto de chocolate",
                                        lang="pt"), 3.0 / 4.0)
        self.assertEqual(extract_number("sete ponto cinco", lang="pt"), 7.5)
        self.assertEqual(extract_number("sete ponto 5", lang="pt"), 7.5)
        self.assertEqual(extract_number("sete e meio", lang="pt"), 7.5)
        self.assertEqual(extract_number("sete e oitenta", lang="pt"), 7.80)
        self.assertEqual(extract_number("sete e oito", lang="pt"), 7.8)
        self.assertEqual(extract_number("sete e zero oito",
                                        lang="pt"), 7.08)
        self.assertEqual(extract_number("sete e zero zero oito",
                                        lang="pt"), 7.008)
        self.assertEqual(extract_number("vinte treze avos", lang="pt"),
                         20.0 / 13.0)
        self.assertEqual(extract_number("seis virgula seiscentos e sessenta",
                                        lang="pt"), 6.66)
        self.assertEqual(extract_number("seiscentos e sessenta e seis",
                                        lang="pt"), 666)

        self.assertEqual(extract_number("seiscentos ponto zero seis",
                                        lang="pt"), 600.06)
        self.assertEqual(extract_number("seiscentos ponto zero zero seis",
                                        lang="pt"), 600.006)
        self.assertEqual(extract_number("seiscentos ponto zero zero zero seis",
                                        lang="pt"), 600.0006)

    def test_agressive_pruning_pt(self):
        self.assertEqual(normalize("uma palavra", lang="pt"),
                         "1 palavra")
        self.assertEqual(normalize("esta palavra um", lang="pt"),
                         "palavra 1")
        self.assertEqual(normalize("o homem batia-lhe", lang="pt"),
                         "homem batia")
        self.assertEqual(normalize("quem disse asneira nesse dia", lang="pt"),
                         "quem disse asneira dia")

    def test_spaces_pt(self):
        self.assertEqual(normalize("  isto   e  o    teste", lang="pt"),
                         "isto teste")
        self.assertEqual(normalize("  isto   sao os    testes  ", lang="pt"),
                         "isto sao testes")
        self.assertEqual(normalize("  isto   e  um    teste", lang="pt",
                                   remove_articles=False),
                         "isto 1 teste")

    def test_numbers_pt(self):
        self.assertEqual(normalize("isto e o um dois três teste", lang="pt"),
                         "isto 1 2 3 teste")
        self.assertEqual(normalize("é a sete oito nove  test", lang="pt"),
                         "é 7 8 9 test")
        self.assertEqual(
            normalize("teste zero dez onze doze treze", lang="pt"),
            "teste 0 10 11 12 13")
        self.assertEqual(
            normalize("teste mil seiscentos e sessenta e seis", lang="pt",
                      remove_articles=False),
            "teste 1000 600 60 6")
        self.assertEqual(
            normalize("teste sete e meio", lang="pt",
                      remove_articles=False),
            "teste 7 meio")
        self.assertEqual(
            normalize("teste dois ponto nove", lang="pt"),
            "teste 2 ponto 9")
        self.assertEqual(
            normalize("teste cento e nove", lang="pt",
                      remove_articles=False),
            "teste 100 9")
        self.assertEqual(
            normalize("teste vinte e 1", lang="pt"),
            "teste 20 1")

    def test_extractdatetime_pt(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang="pt")
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract("que dia é hoje",
                    "2017-06-27 00:00:00", "dia")
        testExtract("que dia é amanha",
                    "2017-06-28 00:00:00", "dia")
        testExtract("que dia foi ontem",
                    "2017-06-26 00:00:00", "dia")
        testExtract("que dia foi antes de ontem",
                    "2017-06-25 00:00:00", "dia")
        testExtract("que dia foi ante ontem",
                    "2017-06-25 00:00:00", "dia")
        testExtract("que dia foi ante ante ontem",
                    "2017-06-24 00:00:00", "dia")
        testExtract("marca o jantar em 5 dias",
                    "2017-07-02 00:00:00", "marca jantar")
        testExtract("como esta o tempo para o dia depois de amanha?",
                    "2017-06-29 00:00:00", "como tempo")
        testExtract("lembra me ás 10:45 pm",
                    "2017-06-27 22:45:00", "lembra")
        testExtract("como esta o tempo na sexta de manha",
                    "2017-06-30 08:00:00", "como tempo")
        testExtract("lembra me para ligar a mãe daqui "
                    "a 8 semanas e 2 dias",
                    "2017-08-24 00:00:00", "lembra ligar mae")
        testExtract("Toca black metal 2 dias a seguir a sexta",
                    "2017-07-02 00:00:00", "toca black metal")
        testExtract("Toca satanic black metal 2 dias para esta sexta",
                    "2017-07-02 00:00:00", "toca satanic black metal")
        testExtract("Toca super black metal 2 dias a partir desta sexta",
                    "2017-07-02 00:00:00", "toca super black metal")
        testExtract("Começa a invasão ás 3:45 pm de quinta feira",
                    "2017-06-29 15:45:00", "comeca invasao")
        testExtract("na segunda, compra queijo",
                    "2017-07-03 00:00:00", "compra queijo")
        testExtract("Toca os parabéns daqui a 5 anos",
                    "2022-06-27 00:00:00", "toca parabens")
        testExtract("manda Skype a Mãe ás 12:45 pm próxima quinta",
                    "2017-06-29 12:45:00", "manda skype mae")
        testExtract("como está o tempo esta sexta?",
                    "2017-06-30 00:00:00", "como tempo")
        testExtract("como está o tempo esta sexta de tarde?",
                    "2017-06-30 15:00:00", "como tempo")
        testExtract("como está o tempo esta sexta as tantas da manha?",
                    "2017-06-30 04:00:00", "como tempo")
        testExtract("como está o tempo esta sexta a meia noite?",
                    "2017-06-30 00:00:00", "como tempo")
        testExtract("como está o tempo esta sexta ao meio dia?",
                    "2017-06-30 12:00:00", "como tempo")
        testExtract("como está o tempo esta sexta ao fim da tarde?",
                    "2017-06-30 19:00:00", "como tempo")
        testExtract("como está o tempo esta sexta ao meio da manha?",
                    "2017-06-30 10:00:00", "como tempo")
        testExtract("lembra me para ligar a mae no dia 3 de agosto",
                    "2017-08-03 00:00:00", "lembra ligar mae")

        testExtract("compra facas no 13º dia de maio",
                    "2018-05-13 00:00:00", "compra facas")
        testExtract("gasta dinheiro no maio dia 13",
                    "2018-05-13 00:00:00", "gasta dinheiro")
        testExtract("compra velas a maio 13",
                    "2018-05-13 00:00:00", "compra velas")
        testExtract("bebe cerveja a 13 maio",
                    "2018-05-13 00:00:00", "bebe cerveja")
        testExtract("como esta o tempo 1 dia a seguir a amanha",
                    "2017-06-29 00:00:00", "como tempo")
        testExtract("como esta o tempo ás 0700 horas",
                    "2017-06-27 07:00:00", "como tempo")
        testExtract("como esta o tempo amanha ás 7 em ponto",
                    "2017-06-28 07:00:00", "como tempo")
        testExtract("como esta o tempo amanha pelas 2 da tarde",
                    "2017-06-28 14:00:00", "como tempo")
        testExtract("como esta o tempo amanha pelas 2",
                    "2017-06-28 02:00:00", "como tempo")
        testExtract("como esta o tempo pelas 2 da tarde da proxima sexta",
                    "2017-06-30 14:00:00", "como tempo")
        testExtract("lembra-me de acordar em 4 anos",
                    "2021-06-27 00:00:00", "lembra acordar")
        testExtract("lembra-me de acordar em 4 anos e 4 dias",
                    "2021-07-01 00:00:00", "lembra acordar")
        testExtract("dorme 3 dias depois de amanha",
                    "2017-07-02 00:00:00", "dorme")
        testExtract("marca consulta para 2 semanas e 6 dias depois de Sabado",
                    "2017-07-21 00:00:00", "marca consulta")
        testExtract("começa a festa ás 8 em ponto da noite de quinta",
                    "2017-06-29 20:00:00", "comeca festa")

    def test_extractdatetime_default_pt(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime(
            'marca consulta para 2 semanas e 6 dias depois de Sabado',
            anchor, lang='pt-pt', default_time=default)
        self.assertEqual(default, res[0].time())


class TestExtractDuration(unittest.TestCase):
    def test_extract_duration(self):
        self.assertEqual(extract_duration("10 segundos"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minutos"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 horas"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 dias"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 semanas"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("sete horas"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 segundos"),
                         (timedelta(seconds=7.5), ""))
        # TODO - imperfect remainder
        self.assertEqual(extract_duration("oito dias e 39 segundos"),
                         (timedelta(days=8, seconds=39), "e"))
        # TODO - imperfect remainder
        self.assertEqual(extract_duration("acorda-me daqui a três semanas, quatro dias e noventa segundos"),
                         (timedelta(weeks=3, days=4, seconds=90),
                          "acorda - me daqui a ,  e"))
        self.assertEqual(extract_duration("10-segundos"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minutos"),
                         (timedelta(minutes=5), ""))

    def test_non_std_units(self):
        self.assertEqual(extract_duration("1 mês"),
                         (timedelta(days=DAYS_IN_1_MONTH), ""))
        self.assertEqual(
            extract_duration("1 mês"),
            (timedelta(days=DAYS_IN_1_MONTH), ""))

        self.assertEqual(extract_duration("3 meses"),
                         (timedelta(days=DAYS_IN_1_MONTH * 3), ""))
        self.assertEqual(extract_duration("um ano"),
                         (timedelta(days=DAYS_IN_1_YEAR), ""))
        self.assertEqual(extract_duration("1 ano"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1), ""))
        self.assertEqual(extract_duration("5 anos"),
                         (timedelta(days=DAYS_IN_1_YEAR * 5), ""))
        self.assertEqual(extract_duration("uma década"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("1 decada"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10), ""))
        self.assertEqual(extract_duration("5 decadas"),
                         (timedelta(days=DAYS_IN_1_YEAR * 10 * 5), ""))
        self.assertEqual(extract_duration("1 século"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("um seculo"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100), ""))
        self.assertEqual(extract_duration("5 séculos"),
                         (timedelta(days=DAYS_IN_1_YEAR * 100 * 5), ""))
        self.assertEqual(extract_duration("1 milénio"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000), ""))
        self.assertEqual(extract_duration("5 milenios"),
                         (timedelta(days=DAYS_IN_1_YEAR * 1000 * 5), ""))


class TestExtractGender(unittest.TestCase):
    def test_gender_pt(self):
        # words with well defined grammatical gender rules
        self.assertEqual(get_gender("vaca", lang="pt"), "f")
        self.assertEqual(get_gender("cavalo", lang="pt"), "m")
        self.assertEqual(get_gender("vacas", lang="pt"), "f")

        # words specifically defined in a lookup dictionary
        self.assertEqual(get_gender("homem", lang="pt"), "m")
        self.assertEqual(get_gender("mulher", lang="pt"), "f")
        self.assertEqual(get_gender("homems", lang="pt"), "m")
        self.assertEqual(get_gender("mulheres", lang="pt"), "f")

        # words where gender rules do not work but context does
        self.assertEqual(get_gender("boi", lang="pt"), None)
        self.assertEqual(get_gender("boi", "o boi come erva", lang="pt"), "m")
        self.assertEqual(get_gender("homem", "este homem come bois",
                                    lang="pt"), "m")
        self.assertEqual(get_gender("ponte", lang="pt"), None)
        self.assertEqual(get_gender("ponte", "essa ponte caiu",
                                    lang="pt"), "f")


class TestYesNo(unittest.TestCase):
    def test_yesno(self):
        def test_utt(text, expected):
            res = yes_or_no(text, lang="pt-pt")
            self.assertEqual(res, expected)

        test_utt("sim", True)
        test_utt("não", False)
        test_utt("bacalhau", None)
        test_utt("por favor", True)
        test_utt("por favor não", False)
        test_utt("claro", True)
        test_utt("obviamente", True)
        test_utt("é obvio", True)
        test_utt("é mentira", False)
        test_utt("claro que não", False)
        test_utt("isso está claramente errado", False)
        test_utt("isso ẽ claramente verdade", True)
        test_utt("efetivamente isso aconteceu", True)
        test_utt("efetivamente isso não aconteceu", False)
        test_utt("de facto isso aconteceu", True)
        test_utt("de facto isso não é verdade", False)
        test_utt("efetivamente isso não é verdade", False)
        test_utt("obviamente falso", False)
        test_utt("é obvio que não", False)

        # double negatives
        # it's not a lie -> True
        test_utt("não é mentira", True)


class TestColors(unittest.TestCase):

    def test_color_obj(self):
        self.assertEqual(Color.from_description("branco"),
                         Color.from_rgb(255, 255, 255))
        self.assertEqual(Color.from_description("preto"),
                         Color.from_rgb(0, 0, 0))

    def test_get_color(self):
        self.assertEqual(get_color("branco"),
                         Color.from_rgb(255, 255, 255))
        self.assertEqual(get_color("preto"),
                         Color.from_rgb(0, 0, 0))
        self.assertEqual(get_color("branca"),
                         Color.from_rgb(255, 255, 255))
        self.assertEqual(get_color("preta"),
                         Color.from_rgb(0, 0, 0))
        self.assertEqual(get_color("branco"),
                         Color.from_rgb(255, 255, 255))
        self.assertEqual(get_color("pretos"),
                         Color.from_rgb(0, 0, 0))
        self.assertEqual(get_color("brancas"),
                         Color.from_rgb(255, 255, 255))
        self.assertEqual(get_color("pretas"),
                         Color.from_rgb(0, 0, 0))

        # "dark reddish gray"
        desc = "cinzento escuro avermelhado"
        color = get_color(desc)
        self.assertTrue(isinstance(color, ColorOutOfSpace))
        self.assertTrue(color.luminance <= 0.3)  # escuro
        self.assertTrue(color.saturation <= 0.25)  # cinzento
        self.assertTrue(color.hue == 0.0)  # vermelho

    def test_color_spans(self):
        utt = "antigamente a televisão era a preto e branco"
        spans = extract_color_spans(utt)
        self.assertTrue(len(spans) == 2)
        self.assertEqual(spans[0][1], (30, 35))
        self.assertEqual(utt[30:35], "preto")
        self.assertEqual(spans[0][0], Color.from_hex("#000000"))
        self.assertEqual(spans[1][1], (38, 44))
        self.assertEqual(utt[38:44], "branco")
        self.assertEqual(spans[1][0], Color.from_hex("#FFFFFF"))

        # female gender
        utt = "a minha gata é preta e branca"
        spans = extract_color_spans(utt)
        self.assertTrue(len(spans) == 2)
        self.assertEqual(spans[0][1], (15, 20))
        self.assertEqual(utt[15:20], "preta")
        self.assertEqual(spans[0][0], Color.from_hex("#000000"))
        self.assertEqual(spans[1][1], (23, 29))
        self.assertEqual(utt[23:29], "branca")
        self.assertEqual(spans[1][0], Color.from_hex("#FFFFFF"))

        # plural
        utt = "os gatos são pretos e as gatas são brancas"
        spans = extract_color_spans(utt)
        self.assertTrue(len(spans) == 2)
        self.assertEqual(spans[0][1], (13, 19))
        self.assertEqual(utt[13:19], "pretos")
        self.assertEqual(spans[0][0], Color.from_hex("#000000"))
        self.assertEqual(spans[1][1], (35, 42))
        self.assertEqual(utt[35:42], "brancas")
        self.assertEqual(spans[1][0], Color.from_hex("#FFFFFF"))


if __name__ == "__main__":
    unittest.main()
