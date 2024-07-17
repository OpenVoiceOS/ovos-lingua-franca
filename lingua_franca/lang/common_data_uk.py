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
from collections import OrderedDict


_NUM_STRING_UK = {
    0: "нуль",
    1: "один",
    2: "два",
    3: "три",
    4: "чотири",
    5: "п'ять",
    6: "шість",
    7: "сім",
    8: "вісім",
    9: "дев'ять",
    10: "десять",
    11: "одинадцять",
    12: "дванадцять",
    13: "тринадцять",
    14: "чотирнадцять",
    15: "п'ятнадцять",
    16: "шістнадцять",
    17: "сімнадцять",
    18: "вісімнадцять",
    19: "дев'ятнадцять",
    20: "двадцять",
    30: "тридцять",
    40: "сорок",
    50: "п'ятдесят",
    60: "шістдесят",
    70: "сімдесят",
    80: "вісімдесят",
    90: "дев'яносто",
    100: "сто",
    200: "двісті",
    300: "триста",
    400: "чотириста",
    500: "п'ятсот",
    600: "шістсот",
    700: "сімсот",
    800: "вісімсот",
    900: "дев'ятсот"
}

_PLURALS = {
    'двох': 2, 'двум': 2, 'двома': 2, 'дві': 2, "двоє": 2, "двійка": 2,
    'обидва': 2, 'обидвох': 2, 'обидві': 2, 'обох': 2, 'обома': 2, 'обом': 2,
    'пара': 2, 'пари': 2, 'парою': 2, 'парами': 2, 'парі': 2, 'парах': 2, 'пару': 2,
    'трьох': 3, 'трьома': 3, 'трьом': 3,
    'чотирьох': 4, 'чотирьом': 4, 'чотирма': 4,
    "п'ятьох": 5, "п'ятьом": 5, "п'ятьома": 5,
    "шістьом": 6, "шести": 6, "шістьох": 6, "шістьма": 6, "шістьома": 6,
    "семи": 7, "сімом": 7, "сімох": 7, "сімома": 7, "сьома": 7,
    "восьми": 8, "вісьмох": 8, "вісьмом": 8, "вісьма": 8, "вісьмома": 8,
    "дев'яти": 9, "дев'ятьох": 9, "дев'ятьом": 9, "дев'ятьма": 9,
    "десяти": 10, "десятьох": 10, "десятьма": 10, "десятьома": 10,
    "сорока": 40,
    "сот": 100, "сотень": 100, "сотні": 100, "сотня": 100,
    "двохсот": 200, "двомстам": 200, "двомастами": 200, "двохстах": 200,
    "тисяч": 1000, "тисячі": 1000, "тисячу": 1000, "тисячах": 1000,
    "тисячами": 1000, "тисячею": 1000
    }


_FRACTION_STRING_UK = {
    2: "друга",
    3: "третя",
    4: "четверта",
    5: "п'ята",
    6: "шоста",
    7: "сьома",
    8: "восьма",
    9: "дев'ята",
    10: "десята",
    11: "одинадцята",
    12: "дванадцята",
    13: "тринадцята",
    14: "чотирнадцята",
    15: "п'ятнадцята",
    16: "шістнадцята",
    17: "сімнадцята",
    18: "вісімнадцята",
    19: "дев'ятнадцята",
    20: "двадцята",
    30: "тридцята",
    40: "сорокова",
    50: "п'ятдесята",
    60: "шістдесята",
    70: "сімдесята",
    80: "вісімдесята",
    90: "дев'яноста",
    1e2: "сота",
    1e3: "тисячна",
    1e6: "мільйонна",
    1e9: "мільярдна",
    1e-12: "більйонна",
}


_SHORT_SCALE_UK = OrderedDict([
    (1e3, "тисяча"),
    (1e6, "мільйон"),
    (1e9, "мільярд"),
    (1e18, "трильйон"),
    (1e12, "більйон"),
    (1e15, "квадрилліон"),
    (1e18, "квінтиліон"),
    (1e21, "секстильйон"),
    (1e24, "септилліон"),
    (1e27, "октиліон"),
    (1e30, "нонільйон"),
    (1e33, "дециліон"),
    (1e36, "ундеціліон"),
    (1e39, "дуодециліон"),
    (1e42, "тредециліон"),
    (1e45, "кваттордециліон"),
    (1e48, "квіндециліон"),
    (1e51, "сексдециліон"),
    (1e54, "септендециліон"),
    (1e57, "октодециліон"),
    (1e60, "новемдециліон"),
    (1e63, "вігінтильйон"),
    (1e66, "унвігінтільйон"),
    (1e69, "дуовігінтильйон"),
    (1e72, "тревігінтильйон"),
    (1e75, "кватторвігінтільйон"),
    (1e78, "квінвігінтильйон"),
    (1e81, "секснвігінтіліон"),
    (1e84, "септенвігінтильйон"),
    (1e87, "октовігінтиліон"),
    (1e90, "новемвігінтільйон"),
    (1e93, "тригінтильйон"),
])


_LONG_SCALE_UK = OrderedDict([
    (1e3, "тисяча"),
    (1e6, "мільйон"),
    (1e9, "мільярд"),
    (1e12, "більйон"),
    (1e15, "біліард"),
    (1e18, "трильйон"),
    (1e21, "трильярд"),
    (1e24, "квадрилліон"),
    (1e27, "квадрільярд"),
    (1e30, "квінтиліон"),
    (1e33, "квінтільярд"),
    (1e36, "секстильйон"),
    (1e39, "секстильярд"),
    (1e42, "септилліон"),
    (1e45, "септільярд"),
    (1e48, "октиліон"),
    (1e51, "октільярд"),
    (1e54, "нонільйон"),
    (1e57, "нонільярд"),
    (1e60, "дециліон"),
    (1e63, "дециліард"),
    (1e66, "ундеціліон"),
    (1e72, "дуодециліон"),
    (1e78, "тредециліон"),
    (1e84, "кваттордециліон"),
    (1e90, "квіндециліон"),
    (1e96, "сексдециліон"),
    (1e102, "септендециліон"),
    (1e108, "октодециліон"),
    (1e114, "новемдециліон"),
    (1e120, "вігінтильйон"),
])


_ORDINAL_BASE_UK = {
    1: "перший",
    2: "другий",
    3: "третій",
    4: "четвертий",
    5: "п'ятий",
    6: "шостий",
    7: "сьомий",
    8: "восьмий",
    9: "дев'ятий",
    10: "десятий",
    11: "одинадцятий",
    12: "дванадцятий",
    13: "тринадцятий",
    14: "чотирнадцятий",
    15: "п'ятнадцятий",
    16: "шістнадцятий",
    17: "сімнадцятий",
    18: "вісімнадцятий",
    19: "дев'ятнадцятий",
    20: "двадцятий",
    30: "тридцятий",
    40: "сороковий",
    50: "п'ятдесятий",
    60: "шістдесятий",
    70: "сімдесятий",
    80: "вісімдесятий",
    90: "дев'яностий",
    1e2: "сотий",
    2e2: "двохсотий",
    3e2: "трьохсотий",
    4e2: "чотирисотий",
    5e2: "п'ятисотий",
    6e2: "шістсотий",
    7e2: "семисотий",
    8e2: "восьмисотий",
    9e2: "дев'ятисотий",
    1e3: "тисячний"
}


_SHORT_ORDINAL_UK = {
    1e6: "мільйон",
    1e9: "мільярд",
    1e18: "трильйон",
    1e15: "квадрилліон",
    1e18: "квінтильйон",
    1e21: "секстильйон",
    1e24: "септилліон",
    1e27: "октиліон",
    1e30: "нонільйон",
    1e33: "дециліон",
    1e36: "ундеціліон",
    1e39: "дуодециліон",
    1e42: "тредециліон",
    1e45: "кваттордециліон",
    1e48: "квіндециліон",
    1e51: "сексдециліон",
    1e54: "септендециліон",
    1e57: "октодециліон",
    1e60: "новемдециліон",
    1e63: "вігінтильйон"
}
_SHORT_ORDINAL_UK.update(_ORDINAL_BASE_UK)


_LONG_ORDINAL_UK = {
    1e6: "мільйон",
    1e9: "мільярд",
    1e12: "більйон",
    1e15: "біліард",
    1e18: "трильйон",
    1e21: "трильярд",
    1e24: "квадрилліон",
    1e27: "квадрильярд",
    1e30: "квінтиліон",
    1e33: "квінтільярд",
    1e36: "секстильйон",
    1e39: "секстильярд",
    1e42: "септилліон",
    1e45: "септільярд",
    1e48: "октиліон",
    1e51: "октільярд",
    1e54: "нонільйон",
    1e57: "нонільярд",
    1e60: "дециліон",
    1e63: "дециліард",
    1e66: "ундеціліон",
    1e72: "дуодециліон",
    1e78: "тредециліон",
    1e84: "кваттордециліон",
    1e90: "квіндециліон",
    1e96: "сексдециліон",
    1e102: "септендециліон",
    1e108: "октодециліон",
    1e114: "новемдециліон",
    1e120: "вігінтильйон"
}
_LONG_ORDINAL_UK.update(_ORDINAL_BASE_UK)

# hours
HOURS_UK = {
     1: 'перша',
     2: 'друга',
     3: 'третя',
     4: 'четверта',
     5: "п'ята",
     6: 'шоста',
     7: 'сьома',
     8: 'восьма',
     9: "дев'ята",
     10: 'десята',
     11: 'одинадцята',
     12: 'дванадцята'
     }
# Months

_MONTHS_CONVERSION = {
    0: "january",
    1: "february",
    2: "march",
    3: "april",
    4: "may",
    5: "june",
    6: "july",
    7: "august",
    8: "september",
    9: "october",
    10: "november",
    11: "december"
}

_MONTHS_UK = ["січень", "лютий", "березень", "квітень", "травень", "червень",
             "липень", "серпень", "вересень", "жовтень", "листопад",
             "грудень"]

# Time
_TIME_UNITS_CONVERSION = {
    "мікросекунд": "microseconds",
    "мілісекунд": "milliseconds",
    "секунда": "seconds",
    "секунди": "seconds",
    "секунд": "seconds",
    "секунду": "seconds",
    "хвилина": "minutes",
    "хвилини": "minutes",
    "хвилин": "minutes",
    "хвилину": "minutes",
    "година": "hours",
    "годин": "hours",
    "години": "hours",
    "годину": "hours",
    "годинами": "hours",
    "годиною": "hours",
    "днів": "days",
    "день": "days",
    "дні": "days",
    "дня": "days",
    "тиждень": "weeks",
    "тижня": "weeks",
    "тижні": "weeks",
    "тижнів": "weeks"
}
