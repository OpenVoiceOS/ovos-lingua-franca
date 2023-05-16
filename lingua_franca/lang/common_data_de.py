from collections import OrderedDict
from lingua_franca.lang.parse_common import invert_dict

_ARTICLES = {'der', 'das', 'die', 'dem', 'den'}

#_SPOKEN_NUMBER
_NUM_STRING = {
    0: 'null',
    1: 'eins',
    2: 'zwei',
    3: 'drei',
    4: 'vier',
    5: 'fünf',
    6: 'sechs',
    7: 'sieben',
    8: 'acht',
    9: 'neun',
    10: 'zehn',
    11: 'elf',
    12: 'zwölf',
    13: 'dreizehn',
    14: 'vierzehn',
    15: 'fünfzehn',
    16: 'sechzehn',
    17: 'siebzehn',
    18: 'achtzehn',
    19: 'neunzehn',
    20: 'zwanzig',
    30: 'dreißig',
    40: 'vierzig',
    50: 'fünfzig',
    60: 'sechzig',
    70: 'siebzig',
    80: 'achtzig',
    90: 'neunzig',
    100: 'hundert',
    200: 'zweihundert',
    300: 'dreihundert',
    400: 'vierhundert',
    500: 'fünfhundert',
    600: 'sechshundert',
    700: 'siebenhundert',
    800: 'achthundert',
    900: 'neunhundert',
    1000: 'tausend',
    1000000: 'million'
}

_STRING_NUM = invert_dict(_NUM_STRING)
_STRING_NUM.update({
    'ein': 1,
    'eine': 1,
    'einer': 1,
    'eines': 1,
    'einem': 1,
    'einen': 1
})

_MONTHS = ['januar', 'februar', 'märz', 'april', 'mai', 'juni',
              'juli', 'august', 'september', 'oktober', 'november',
              'dezember']

# German uses "long scale" https://en.wikipedia.org/wiki/Long_and_short_scales
# Currently, numbers are limited to 1000000000000000000000000,
# but _NUM_POWERS_OF_TEN can be extended to include additional number words


_NUM_POWERS_OF_TEN = [
    '', 'tausend', 'Million', 'Milliarde', 'Billion', 'Billiarde', 'Trillion',
    'Trilliarde'
]

_FRACTION_STRING = {
    2: 'halb',
    3: 'drittel',
    4: 'viertel',
    5: 'fünftel',
    6: 'sechstel',
    7: 'siebtel',
    8: 'achtel',
    9: 'neuntel',
    10: 'zehntel',
    11: 'elftel',
    12: 'zwölftel',
    13: 'dreizehntel',
    14: 'vierzehntel',
    15: 'fünfzehntel',
    16: 'sechzehntel',
    17: 'siebzehntel',
    18: 'achtzehntel',
    19: 'neunzehntel',
    20: 'zwanzigstel'
}

_STRING_FRACTION = invert_dict(_FRACTION_STRING)
_STRING_FRACTION.update({
    'halb': 2,
    'halbe': 2,
    'halben': 2,
    'halbes': 2,
    'halber': 2,
    'halbem': 2
})

# Numbers below 1 million are written in one word in German, yielding very
# long words
# In some circumstances it may better to seperate individual words
# Set _EXTRA_SPACE_DA=" " for separating numbers below 1 million (
# orthographically incorrect)
# Set _EXTRA_SPACE_DA="" for correct spelling, this is standard

# _EXTRA_SPACE_DA = " "
_EXTRA_SPACE = ""

_ORDINAL_BASE = {
    "1.": "erst",
    "2.": "zweit",
    "3.": "dritt",
    "4.": "viert",
    "5.": "fünft",
    "6.": "sechst",
    "7.": "siebt",
    "8.": "acht",
    "9.": "neunt",
    "10.": "zehnt",
    "11.": "elft",
    "12.": "zwölft",
    "13.": "dreizehnt",
    "14.": "vierzehnt",
    "15.": "fünfzehnt",
    "16.": "sechzehnt",
    "17.": "siebzehnt",
    "18.": "achtzehnt",
    "19.": "neunzehnt",
    "20.": "zwanzigst",
    "21.": "einundzwanzigst",
    "22.": "zweiundzwanzigst",
    "23.": "dreiundzwanzigst",
    "24.": "vierundzwanzigst",
    "25.": "fünfundzwanzigst",
    "26.": "sechsundzwanzigst",
    "27.": "siebenundzwanzigst",
    "28.": "achtundzwanzigst",
    "29.": "neunundzwanzigst",
    "30.": "dreißigst",
    "31.": "einunddreißigst",
    "32.": "zweiunddreißigst",
    "33.": "dreiunddreißigst",
    "34.": "vierunddreißigst",
    "35.": "fünfunddreißigst",
    "36.": "sechsunddreißigst",
    "37.": "siebenunddreißigst",
    "38.": "achtunddreißigst",
    "39.": "neununddreißigst",
    "40.": "vierzigst",
    "41.": "einundvierzigst",
    "42.": "zweiundvierzigst",
    "43.": "dreiundvierzigst",
    "44.": "vierundvierzigst",
    "45.": "fünfundvierzigst",
    "46.": "sechsundvierzigst",
    "47.": "siebenundvierzigst",
    "48.": "achtundvierzigst",
    "49.": "neunundvierzigst",
    "50.": "fünfzigst",
    "51.": "einundfünfzigst",
    "52.": "zweiundfünfzigst",
    "53.": "dreiundfünfzigst",
    "60.": "sechzigst",
    "70.": "siebzigst",
    "80.": "achtzigst",
    "90.": "neunzigst",
    "100.": "einhundertst",
    "1000.": "eintausendst",
    "1000000.": "millionst"
    }

_LONG_SCALE = OrderedDict([
    (100, 'hundert'),
    (1000, 'tausend'),
    (1000000, 'million'),
    (1e9, "milliarde"),
    (1e12, 'billion'),
    (1e15, "billiarde"),
    (1e18, "trillion"),
    (1e21, "trilliarde"),
    (1e24, "quadrillion"),
    (1e27, "quadrilliarde")
])

_MULTIPLIER = set(_LONG_SCALE.values())

_STRING_LONG_SCALE = invert_dict(_LONG_SCALE)

# ending manipulation
for number, item in _LONG_SCALE.items():
    if int(number) > 1000:
        if item.endswith('e'):
            name = item + 'n'
            _MULTIPLIER.add(name)
            _STRING_LONG_SCALE[name] = number
        else:
            name = item + 'en'
            _MULTIPLIER.add(name)
            _STRING_LONG_SCALE[name] = number

_LONG_ORDINAL = {
    1e6: "millionst",
    1e9: "milliardst",
    1e12: "billionst",
    1e15: "billiardst",
    1e18: "trillionst",
    1e21: "trilliardst",
    1e24: "quadrillionst",
    1e27: "quadrilliardst"
}

_LONG_ORDINAL.update(_ORDINAL_BASE)

# dict für erste, drittem, millionstes ...
_STRING_LONG_ORDINAL = {ord+ending: num for ord, num in invert_dict(_LONG_ORDINAL).items()
                        for ending in ("en", "em", "es", "er", "e")}

_FRACTION_MARKER = set()

_NEGATIVES = {"minus"}

_NUMBER_CONNECTORS = {"und"}

_COMMA = {"komma", "comma", "punkt"}
