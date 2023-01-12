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
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from lingua_franca.lang.parse_common import is_numeric, look_for_fractions, \
    invert_dict, ReplaceableNumber, partition_list, tokenize, Token, Normalizer
from lingua_franca.lang.common_data_uk import _NUM_STRING_UK, \
    _LONG_ORDINAL_UK, _LONG_SCALE_UK, _SHORT_SCALE_UK, _SHORT_ORDINAL_UK, \
    _FRACTION_STRING_UK, _MONTHS_CONVERSION, _MONTHS_UK, _TIME_UNITS_CONVERSION, \
    _ORDINAL_BASE_UK, _PLURALS

import re
import json
from lingua_franca import resolve_resource_file
from lingua_franca.time import now_local


def generate_plurals_uk(originals):
    """
    Return a new set or dict containing the plural form of the original values,
    Generate different cases of values

    In English this means all with 's' appended to them.

    Args:
        originals set(str) or dict(str, any): values to pluralize

    Returns:
        set(str) or dict(str, any)

    """
    suffixes = ["а", "ах", "их", "ам", "ами", "ів",
                "ям", "ох", "и", "на", "ни", "і", "ні",
                "ий", "ний", 'ьох', 'ьома', 'ьом', 'ох',
                'ум', 'ма', 'ом']
    if isinstance(originals, dict):
        thousand = {"тисяч": 1000, "тисячі": 1000, "тисячу": 1000, "тисячах": 1000}
        hundred = {"сотня": 100, "сотні": 100, "сотень": 100}
        result_dict = {key + suffix: value for key, value in originals.items() for suffix in suffixes}
        result_dict.update(thousand)
        result_dict.update(hundred)
        return result_dict
    thousand = ["тисяч", "тисячі", "тисячу", "тисячах"]
    result_dict = {value + suffix for value in originals for suffix in suffixes}
    result_dict.update(thousand)
    return {value + suffix for value in originals for suffix in suffixes}


# negate next number (-2 = 0 - 2)
_NEGATIVES = {"мінус"}

# sum the next number (twenty two = 20 + 2)
_SUMS = {"двадцять", "20", "тридцять", "30", "сорок", "40", "п'ятдесят", "50",
         "шістдесят", "60", "сімдесят", "70", "вісімдесят", "80", "дев'яносто", "90",
         "сто", "100", "двісті", "200", "триста", "300", "чотириста", "400",
         "п'ятсот", "500", "шістсот", "600", "сімсот", "700", "вісімсот", "800",
         "дев'ятсот", "900"}

_MULTIPLIES_LONG_SCALE_UK = set(_LONG_SCALE_UK.values()) | \
                            generate_plurals_uk(_LONG_SCALE_UK.values())


_MULTIPLIES_SHORT_SCALE_UK = set(_SHORT_SCALE_UK.values()) | \
                             generate_plurals_uk(_SHORT_SCALE_UK.values())

# split sentence parse separately and sum ( 2 and a half = 2 + 0.5 )
_FRACTION_MARKER = {"і", "та", "з", " "}

# decimal marker ( 1 point 5 = 1 + 0.5)
_DECIMAL_MARKER = {"ціла", "цілих", "точка", "крапка", "кома"}

_STRING_NUM_UK = invert_dict(_NUM_STRING_UK)

_STRING_NUM_UK.update(generate_plurals_uk(_STRING_NUM_UK))
_STRING_NUM_UK.update(_PLURALS)
_STRING_NUM_UK.update({
    "трильйон": 1e18,
    "половина": 0.5, "половиною": 0.5, "половини": 0.5, "половин": 0.5, "половинами": 0.5, "пів": 0.5,
    "одна": 1, "одної": 1, "одній": 1, "одну": 1
})

_WORDS_NEXT_UK = [
    "майбутня", "майбутнє", "майбутній", "майбутньому", "майбутнім", "майбутньої", "майбутнього",
    "нова", "нове", "новий", "нового", "нової", "новим", "новою", "через",
    "наступна", "наступне", "наступний", "наступній", "наступному", "наступним",  "наступною",
]
_WORDS_PREV_UK = [
    "попередня", "попередній", "попереднім", "попередньої",
    "попередню", "попереднього", "попередне", "тому",
    "минула", "минулий", "минуле", "минулу", "минулого", "минулій", "минулому",
    "минулої", "минулою", "минулим",
    "та", "той", "ті", "те", "того",
]
_WORDS_CURRENT_UK = [
    "теперішній", "теперішня", "теперішні", "теперішній", "теперішньому",
    "теперішньою", "теперішнім", "теперішнього", "теперішньої",
    "дана", "даний", "дане", "даним", "даною", "даного", "даної", "даному", "даній",
    "поточний", "поточна", "поточні", "поточне", "поточного", "поточної",
    "поточному", "поточній", "поточним", "поточною",
    "нинішній", "нинішня", "нинішнє", "нинішньому", "нинішній",
    "нинішнього", "нинішньої", "нинішнім", "нинішньою",
    "цей", "ця", "це", "цим", "цією", "цьому", "цій"
]
_WORDS_NOW_UK = [
    "тепер",
    "зараз",
]
_WORDS_MORNING_UK = ["ранок", "зранку", "вранці", "ранку"]
_WORDS_DAY_UK = ["вдень", "опівдні"]
_WORDS_EVENING_UK = ["вечер", "ввечері", "увечері", "вечором"]
_WORDS_NIGHT_UK = ["ніч", "вночі"]

_STRING_SHORT_ORDINAL_UK = invert_dict(_SHORT_ORDINAL_UK)
_STRING_LONG_ORDINAL_UK = invert_dict(_LONG_ORDINAL_UK)


def _convert_words_to_numbers_uk(text, short_scale=True, ordinals=False):
    """
    Convert words in a string into their equivalent numbers.
    Args:
        text str:
        short_scale boolean: True if short scale numbers should be used.
        ordinals boolean: True if ordinals (e.g. first, second, third) should
                          be parsed to their number values (1, 2, 3...)

    Returns:
        str
        The original text, with numbers subbed in where appropriate.

    """
    text = text.lower()

    tokens = tokenize(text)
    numbers_to_replace = \
        _extract_numbers_with_text_uk(tokens, short_scale, ordinals)
    numbers_to_replace.sort(key=lambda number: number.start_index)

    results = []
    for token in tokens:
        if not numbers_to_replace or \
                token.index < numbers_to_replace[0].start_index:
            results.append(token.word)
        else:
            if numbers_to_replace and \
                    token.index == numbers_to_replace[0].start_index:
                results.append(str(numbers_to_replace[0].value))
            if numbers_to_replace and \
                    token.index == numbers_to_replace[0].end_index:
                numbers_to_replace.pop(0)
    return ' '.join(results)


def _extract_numbers_with_text_uk(tokens, short_scale=True,
                                  ordinals=False, fractional_numbers=True):
    """
    Extract all numbers from a list of Tokens, with the words that
    represent them.

    Args:
        [Token]: The tokens to parse.
        short_scale bool: True if short scale numbers should be used, False for
                          long scale. True by default.
        ordinals bool: True if ordinal words (first, second, third, etc) should
                       be parsed.
        fractional_numbers bool: True if we should look for fractions and
                                 decimals.

    Returns:
        [ReplaceableNumber]: A list of tuples, each containing a number and a
                         string.

    """
    placeholder = "<placeholder>"  # inserted to maintain correct indices
    results = []
    while True:
        to_replace = \
            _extract_number_with_text_uk(tokens, short_scale,
                                         ordinals, fractional_numbers)

        if not to_replace:
            break
        results.append(to_replace)
        tokens = [
            t if not
            to_replace.start_index <= t.index <= to_replace.end_index
            else
            Token(placeholder, t.index) for t in tokens
        ]
    results.sort(key=lambda n: n.start_index)
    return results


def _extract_number_with_text_uk(tokens, short_scale=True,
                                 ordinals=False, fractional_numbers=True):
    """
    This function extracts a number from a list of Tokens.

    Args:
        tokens str: the string to normalize
        short_scale (bool): use short scale if True, long scale if False
        ordinals (bool): consider ordinal numbers, third=3 instead of 1/3
        fractional_numbers (bool): True if we should look for fractions and
                                   decimals.
    Returns:
        ReplaceableNumber

    """
    number, tokens = \
        _extract_number_with_text_uk_helper(tokens, short_scale,
                                            ordinals, fractional_numbers)
    return ReplaceableNumber(number, tokens)


def _extract_number_with_text_uk_helper(tokens,
                                        short_scale=True, ordinals=False,
                                        fractional_numbers=True):
    """
    Helper for _extract_number_with_text_uk.

    This contains the real logic for parsing, but produces
    a result that needs a little cleaning (specific, it may
    contain leading articles that can be trimmed off).

    Args:
        tokens [Token]:
        short_scale boolean:
        ordinals boolean:
        fractional_numbers boolean:

    Returns:
        int or float, [Tokens]

    """
    if fractional_numbers:
        fraction, fraction_text = \
            _extract_fraction_with_text_uk(tokens, short_scale, ordinals)
        if fraction:
            return fraction, fraction_text

        decimal, decimal_text = \
            _extract_decimal_with_text_uk(tokens, short_scale, ordinals)
        if decimal:
            return decimal, decimal_text
    # special_number = [word for word in tokens if word ]
    # short_scale == False
    return _extract_whole_number_with_text_uk(tokens, short_scale, ordinals)


def _extract_fraction_with_text_uk(tokens, short_scale, ordinals):
    """
    Extract fraction numbers from a string.

    This function handles text such as '2 and 3/4'. Note that "one half" or
    similar will be parsed by the whole number function.

    Args:
        tokens [Token]: words and their indexes in the original string.
        short_scale boolean:
        ordinals boolean:

    Returns:
        (int or float, [Token])
        The value found, and the list of relevant tokens.
        (None, None) if no fraction value is found.

    """
    for c in _FRACTION_MARKER:
        partitions = partition_list(tokens, lambda t: t.word == c)

        if len(partitions) == 3:
            numbers1 = \
                _extract_numbers_with_text_uk(partitions[0], short_scale,
                                              ordinals, fractional_numbers=False)
            numbers2 = \
                _extract_numbers_with_text_uk(partitions[2], short_scale,
                                              ordinals, fractional_numbers=True)

            if not numbers1 or not numbers2:
                return None, None

            # ensure first is not a fraction and second is a fraction
            num1 = numbers1[-1]
            num2 = numbers2[0]
            if num1.value >= 1 and 0 < num2.value < 1:
                return num1.value + num2.value, \
                       num1.tokens + partitions[1] + num2.tokens

    return None, None


def _extract_decimal_with_text_uk(tokens, short_scale, ordinals):
    """
    Extract decimal numbers from a string.

    This function handles text such as '2 point 5'.

    Notes:
        While this is a helper for extract_number_xx, it also depends on
        extract_number_xx, to parse out the components of the decimal.

        This does not currently handle things like:
            number dot number number number

    Args:
        tokens [Token]: The text to parse.
        short_scale boolean:
        ordinals boolean:

    Returns:
        (float, [Token])
        The value found and relevant tokens.
        (None, None) if no decimal value is found.

    """
    for c in _DECIMAL_MARKER:
        partitions = partition_list(tokens, lambda t: t.word == c)

        if len(partitions) == 3:
            numbers1 = \
                _extract_numbers_with_text_uk(partitions[0], short_scale,
                                              ordinals, fractional_numbers=False)
            numbers2 = \
                _extract_numbers_with_text_uk(partitions[2], short_scale,
                                              ordinals, fractional_numbers=False)

            if not numbers1 or not numbers2:
                return None, None

            number = numbers1[-1]
            decimal = numbers2[0]

            # TODO handle number dot number number number
            if "." not in str(decimal.text):
                return number.value + float('0.' + str(decimal.value)), \
                       number.tokens + partitions[1] + decimal.tokens
    return None, None


def _extract_whole_number_with_text_uk(tokens, short_scale, ordinals):
    """
    Handle numbers not handled by the decimal or fraction functions. This is
    generally whole numbers. Note that phrases such as "one half" will be
    handled by this function, while "one and a half" are handled by the
    fraction function.

    Args:
        tokens [Token]:
        short_scale boolean:
        ordinals boolean:

    Returns:
        int or float, [Tokens]
        The value parsed, and tokens that it corresponds to.

    """
    number_token = [token for token in tokens if token.word.lower() in _MULTIPLIES_LONG_SCALE_UK]
    if number_token:
        short_scale = False
    multiplies, string_num_ordinal, string_num_scale = \
        _initialize_number_data(short_scale)
    number_words = []  # type: [Token]
    val = False
    prev_val = None
    next_val = None
    to_sum = []
    for idx, token in enumerate(tokens):
        current_val = None
        if next_val:
            next_val = None
            continue

        word = token.word
        if word in word in _NEGATIVES:
            number_words.append(token)
            continue

        prev_word = tokens[idx - 1].word if idx > 0 else ""
        prev_word = _text_uk_inflection_normalize(prev_word, 1)
        next_word = tokens[idx + 1].word if idx + 1 < len(tokens) else ""
        next_word = _text_uk_inflection_normalize(next_word, 1)

        # In Ukrainian (?) we do not use suffix (1st,2nd,..) but use point instead (1.,2.,..)
        if is_numeric(word[:-1]) and \
                (word.endswith(".")):
            # explicit ordinals, 1st, 2nd, 3rd, 4th.... Nth
            word = word[:-1]

        # Normalize Ukrainian inflection of numbers (один, одна, одно,...)
        if not ordinals:
            if word not in _STRING_NUM_UK:
                word = _text_uk_inflection_normalize(word, 1)

        if word not in string_num_scale and \
                word not in _STRING_NUM_UK and \
                word not in _SUMS and \
                word not in multiplies and \
                not (ordinals and word in string_num_ordinal) and \
                not is_numeric(word) and \
                not is_fractional_uk(word, word, short_scale=short_scale) and \
                not look_for_fractions(word.split('/')):
            words_only = [token.word for token in number_words]
            if number_words and not all([w in _NEGATIVES for w in words_only]):
                break
            else:
                number_words = []
                continue
        elif word not in multiplies \
                and prev_word not in multiplies \
                and prev_word not in _SUMS \
                and not (ordinals and prev_word in string_num_ordinal) \
                and prev_word not in _NEGATIVES:

            number_words = [token]
        elif prev_word in _SUMS and word in _SUMS :
            number_words = [token]
        else:
            number_words.append(token)
        # is this word already a number ?
        if is_numeric(word):
            if word.isdigit():  # doesn't work with decimals
                val = int(word)
            else:
                val = float(word)
            current_val = val

        # is this word the name of a number ?
        if word in _STRING_NUM_UK:
            val = _STRING_NUM_UK.get(word)
            current_val = val
        elif word in string_num_scale:
            val = string_num_scale.get(word)
            current_val = val
        elif ordinals and word in string_num_ordinal:
            val = string_num_ordinal[word]
            current_val = val
        # is the prev word an ordinal number and current word is one?
        # second one, third one
        if ordinals and prev_word in string_num_ordinal and val == 1:
            val = prev_val
        # is the prev word a number and should we sum it?
        # twenty two, fifty six
        if (prev_word in _SUMS and val and val < 10) \
                or (prev_word in _SUMS and val and val < 100 and prev_val >= 100) \
                or all([prev_word in multiplies, val < prev_val if prev_val else False]):
            val = prev_val + val

        # is the prev word a number and should we multiply it?
        multiplies.update({"тисячa", "тисячі", "тисячу", "тисячах", "тисячaми", "тисячею", "тисяч"})
        if word in multiplies:
            if not prev_val:
                prev_val = 1
            val = prev_val * val

        # пара сотень, три пари пива
        if prev_word in ['пара', 'пари', 'парою', 'парами'] and current_val != 1000.0:
            val = val * 2
        if prev_val in _STRING_NUM_UK.values() and current_val == 100:
            val = prev_val * current_val

        # half cup
        if val is False:
            val = is_fractional_uk(word, word, short_scale=short_scale)
            current_val = val

        # 2 fifths
        if not ordinals:
            next_val = is_fractional_uk(next_word, word, short_scale=short_scale)
            if next_val:
                if not val:
                    val = 1
                val = val * next_val
                number_words.append(tokens[idx + 1])
        if word in ['пара', 'пари', 'парою', 'парами']:
            if prev_val:
                val = val * prev_val
            else:
                val = 2
        # is this a negative number?
        if val and prev_word and prev_word in _NEGATIVES:
            val = 0 - val

        # let's make sure it isn't a fraction
        if not val:
            # look for fractions like "2/3"
            a_pieces = word.split('/')
            if look_for_fractions(a_pieces):
                val = float(a_pieces[0]) / float(a_pieces[1])
        else:
            # checking if word is digit in order not to substitute
            # existing calculated value
            new_word = re.sub(r'\.', '', word)
            if all([
                prev_word in _SUMS,
                word not in _SUMS,
                new_word.isdigit() is False,
                word not in multiplies,
                current_val >= 10
            ]):
                # Backtrack - we've got numbers we can't sum
                number_words.pop()
                val = prev_val
                break
            prev_val = val
            if word in multiplies and next_word not in multiplies:
                # handle long numbers
                # six hundred sixty six
                # two million five hundred thousand
                #
                # This logic is somewhat complex, and warrants
                # extensive documentation for the next coder's sake.
                #
                # The current word is a power of ten. `current_val` is
                # its integer value. `val` is our working sum
                # (above, when `current_val` is 1 million, `val` is
                # 2 million.)
                #
                # We have a dict `string_num_scale` containing [value, word]
                # pairs for "all" powers of ten: string_num_scale[10] == "ten.
                #
                # We need go over the rest of the tokens, looking for other
                # powers of ten. If we find one, we compare it with the current
                # value, to see if it's smaller than the current power of ten.
                #
                # Numbers which are not powers of ten will be passed over.
                #
                # If all the remaining powers of ten are smaller than our
                # current value, we can set the current value aside for later,
                # and begin extracting another portion of our final result.
                # For example, suppose we have the following string.
                # The current word is "million".`val` is 9000000.
                # `current_val` is 1000000.
                #
                #    "nine **million** nine *hundred* seven **thousand**
                #     six *hundred* fifty seven"
                #
                # Iterating over the rest of the string, the current
                # value is larger than all remaining powers of ten.
                #
                # The if statement passes, and nine million (9000000)
                # is appended to `to_sum`.
                #
                # The main variables are reset, and the main loop begins
                # assembling another number, which will also be appended
                # under the same conditions.
                #
                # By the end of the main loop, to_sum will be a list of each
                # "place" from 100 up: [9000000, 907000, 600]
                #
                # The final three digits will be added to the sum of that list
                # at the end of the main loop, to produce the extracted number:
                #
                #    sum([9000000, 907000, 600]) + 57
                # == 9,000,000 + 907,000 + 600 + 57
                # == 9,907,657
                #
                # >>> foo = "nine million nine hundred seven thousand six
                #            hundred fifty seven"
                # >>> extract_number(foo)
                # 9907657
                time_to_sum = True
                for other_token in tokens[idx + 1:]:
                    if other_token.word in multiplies:
                        if string_num_scale[other_token.word] >= current_val:
                            time_to_sum = False
                        else:
                            continue
                    if not time_to_sum:
                        break
                if time_to_sum:
                    to_sum.append(val)
                    val = 0
                    prev_val = 0

    if val is not None and to_sum:
        val += sum(to_sum)
    return val, number_words


def _initialize_number_data(short_scale):
    """
    Generate dictionaries of words to numbers, based on scale.

    This is a helper function for _extract_whole_number.

    Args:
        short_scale boolean:

    Returns:
        (set(str), dict(str, number), dict(str, number))
        multiplies, string_num_ordinal, string_num_scale

    """
    multiplies = _MULTIPLIES_SHORT_SCALE_UK if short_scale \
        else _MULTIPLIES_LONG_SCALE_UK

    string_num_ordinal_uk = _STRING_SHORT_ORDINAL_UK if short_scale \
        else _STRING_LONG_ORDINAL_UK

    string_num_scale_uk = _SHORT_SCALE_UK if short_scale else _LONG_SCALE_UK
    string_num_scale_uk = invert_dict(string_num_scale_uk)
    string_num_scale_uk.update(generate_plurals_uk(string_num_scale_uk))
    return multiplies, string_num_ordinal_uk, string_num_scale_uk


def extract_number_uk(text, short_scale=True, ordinals=False):
    """
    This function extracts a number from a text string,
    handles pronunciations in long scale and short scale

    https://en.wikipedia.org/wiki/Names_of_large_numbers

    Args:
        text (str): the string to normalize
        short_scale (bool): use short scale if True, long scale if False
        ordinals (bool): consider ordinal numbers, third=3 instead of 1/3
    Returns:
        (int) or (float) or False: The extracted number or False if no number
                                   was found

    """
    return _extract_number_with_text_uk(tokenize(text.lower()),
                                        short_scale, ordinals).value


def extract_duration_uk(text):
    """
    Convert an english phrase into a number of seconds

    Convert things like:
        "10 minute"
        "2 and a half hours"
        "3 days 8 hours 10 minutes and 49 seconds"
    into an int, representing the total number of seconds.

    The words used in the duration will be consumed, and
    the remainder returned.

    As an example, "set a timer for 5 minutes" would return
    (300, "set a timer for").

    Args:
        text (str): string containing a duration

    Returns:
        (timedelta, str):
                    A tuple containing the duration and the remaining text
                    not consumed in the parsing. The first value will
                    be None if no duration is found. The text returned
                    will have whitespace stripped from the ends.
    """
    if not text:
        return None

    # Ukrainian inflection for time: хвилина, хвилини, хвилин - safe to use хвилина as pattern
    # For day: день, дня, днів - short pattern not applicable, list all

    time_units = {
        'microseconds': 0,
        'milliseconds': 0,
        'seconds': 0,
        'minutes': 0,
        'hours': 0,
        'days': 0,
        'weeks': 0
    }

    pattern = r"(?P<value>\d+(?:\.?\d+)?)(?:\s+|\-){unit}(?:ів|я|и|ин|і|унд|ни|ну|ку|дні|у|днів)?"
    text = _convert_words_to_numbers_uk(text)

    for (unit_uk, unit_en) in _TIME_UNITS_CONVERSION.items():
        unit_pattern = pattern.format(unit=unit_uk)

        def repl(match):
            time_units[unit_en] += float(match.group(1))
            return ''
        text = re.sub(unit_pattern, repl, text)

    new_text = []
    tokens_in_result_text = text.split(' ')
    for token in tokens_in_result_text:
        if not token.isdigit():
            new_text.append(token)
    text = " ".join(new_text).strip()
    duration = timedelta(**time_units) if any(time_units.values()) else None

    return duration, text


def extract_datetime_uk(text, anchor_date=None, default_time=None):
    """ Convert a human date reference into an exact datetime

    Convert things like
        "today"
        "tomorrow afternoon"
        "next Tuesday at 4pm"
        "August 3rd"
    into a datetime.  If a reference date is not provided, the current
    local time is used.  Also consumes the words used to define the date
    returning the remaining string.  For example, the string
       "what is Tuesday's weather forecast"
    returns the date for the forthcoming Tuesday relative to the reference
    date and the remainder string
       "what is weather forecast".

    The "next" instance of a day or weekend is considered to be no earlier than
    48 hours in the future. On Friday, "next Monday" would be in 3 days.
    On Saturday, "next Monday" would be in 9 days.

    Args:
        text (str): string containing date words
        anchor_date (datetime): A reference date/time for "tommorrow", etc
        default_time (time): Time to set if no time was found in the string

    Returns:
        [datetime, str]: An array containing the datetime and the remaining
                         text not consumed in the parsing, or None if no
                         date or time related text was found.
    """

    def clean_string(s):
        # clean unneeded punctuation and capitalization among other things.
        # Normalize Ukrainian inflection
        s = s.lower().replace('?', '').replace('.', '').replace(',', '')
        s = s.replace("сьогодні вечером|сьогодні ввечері|вечором", "ввечері")
        s = s.replace("сьогодні вночі", "вночі")
        word_list = s.split()

        for idx, word in enumerate(word_list):
            ##########
            # Ukrainian Day Ordinals - we do not use 1st,2nd format
            #   instead we use full ordinal number names with specific format(suffix)
            #   Example: двадцять третього - 23
            count_ordinals = 0
            if word == "третього":
                count_ordinals = 3
            #   Example: тридцять першого - 31
            elif word.endswith("ого"):
                tmp = word[:-3]
                tmp += "ий"
                for nr, name in _ORDINAL_BASE_UK.items():
                    if name == tmp:
                        count_ordinals = nr
            #   Example: тридцять перше > 31
            elif word.endswith("є") or word.endswith("е"):
                tmp = word[:-1]
                tmp += "ий"
                for nr, name in _ORDINAL_BASE_UK.items():
                    if name == tmp:
                        count_ordinals = nr
            # If number is bigger than 19 check if next word is also ordinal
            #  and count them together
            if count_ordinals > 19:
                if word_list[idx + 1] == "третього":
                    count_ordinals += 3
                elif word_list[idx + 1].endswith("ого"):
                    tmp = word_list[idx + 1][:-3]
                    tmp += "ий"
                    for nr, name in _ORDINAL_BASE_UK.items():
                        if name == tmp and nr < 10:
                            # write only if sum makes acceptable count of days in month
                            if (count_ordinals + nr) <= 31:
                                count_ordinals += nr

            if count_ordinals > 0:
                word = str(count_ordinals)  # Write normalized value into word
            if count_ordinals > 20:
                # If counted number is greater than 20, clear next word so it is not used again
                word_list[idx + 1] = ""
            ##########
            # Remove inflection from Ukrainian months
            word_list[idx] = word
        return word_list

    def date_found():
        return found or \
               (
                       date_string != "" or
                       year_offset != 0 or month_offset != 0 or
                       day_offset is True or hr_offset != 0 or
                       hr_abs or min_offset != 0 or
                       min_abs or sec_offset != 0
               )

    if text == "":
        return None

    anchor_date = anchor_date or now_local()
    found = False
    day_specified = False
    day_offset = False
    month_offset = 0
    year_offset = 0
    today = anchor_date.strftime("%w")
    current_year = anchor_date.strftime("%Y")
    from_flag = False
    date_string = ""
    has_year = False
    time_qualifier = ""

    time_qualifiers_am = _WORDS_MORNING_UK
    time_qualifiers_pm = ['дня', 'вечора']
    time_qualifiers_pm.extend(_WORDS_DAY_UK)
    time_qualifiers_pm.extend(_WORDS_EVENING_UK)
    time_qualifiers_pm.extend(_WORDS_NIGHT_UK)
    time_qualifiers_list = set(time_qualifiers_am + time_qualifiers_pm)
    markers = ['на', 'у', 'в', 'о', 'до', 'це',
               'біля', 'цей', 'через', 'після', 'за', 'той']
    days = ["понеділок", "вівторок", "середа",
            "четвер", "п'ятниця", "субота", "неділя"]
    months = _MONTHS_UK
    recur_markers = days + ['вихідні', 'вікенд']
    months_short = ["січ", "лют", "бер", "квіт", "трав", "червень", "лип", "серп",
    "верес", "жовт", "листоп", "груд"]
    year_multiples = ["десятиліття", "століття", "тисячоліття", "тисячоліть", "століть",
                        "сторіччя", "сторіч"]

    words = clean_string(text)
    preposition = ""

    for idx, word in enumerate(words):
        if word == "":
            continue

        if word in markers:
            preposition = word

        word = _text_uk_inflection_normalize(word, 2)
        word_prev_prev = _text_uk_inflection_normalize(
            words[idx - 2], 2) if idx > 1 else ""
        word_prev = _text_uk_inflection_normalize(
            words[idx - 1], 2) if idx > 0 else ""
        word_next = _text_uk_inflection_normalize(
            words[idx + 1], 2) if idx + 1 < len(words) else ""
        word_next_next = _text_uk_inflection_normalize(
            words[idx + 2], 2) if idx + 2 < len(words) else ""

        # this isn't in clean string because I don't want to save back to words
        start = idx
        used = 0
        if word in _WORDS_NOW_UK and not date_string:
            result_str = " ".join(words[idx + 1:])
            result_str = ' '.join(result_str.split())
            extracted_date = anchor_date.replace(microsecond=0)
            return [extracted_date, result_str]
        elif word_next in year_multiples:
            multiplier = None
            if is_numeric(word):
                multiplier = extract_number_uk(word)
            multiplier = multiplier or 1
            multiplier = int(multiplier)
            used += 2
            if word_next == "десятиліття" or word_next == "декада":
                year_offset = multiplier * 10
            elif word_next == "століття" or word_next == "сторіччя":
                year_offset = multiplier * 100
            elif word_next in ["тисячоліття", "тисячоліть"]:
                year_offset = multiplier * 1000
            elif word_next in ["тисяча", "тисячі", "тисяч"]:
                year_offset = multiplier * 1000
        elif word in time_qualifiers_list and preposition != "через" and word_next != "тому":
            time_qualifier = word
        # parse today, tomorrow, day after tomorrow
        elif word == "сьогодні" and not from_flag:
            day_offset = 0
            used += 1
        elif word == "завтра" and not from_flag:
            day_offset = 1
            used += 1
        elif word == "післязавтра" and not from_flag:
            day_offset = 2
            used += 1
        elif word == "після" and word_next == "завтра" and not from_flag:
            day_offset = 2
            used += 2
        elif word == "позавчора" and not from_flag:
            day_offset = -2
            used += 1
        elif word == "вчора" and not from_flag:
            day_offset = -1
            used += 1
        elif (word in ["день", "дня",  "дні", "днів"] and
              word_next == "після" and
              word_next_next == "завтра" and
              not from_flag and
              (not word_prev or not word_prev[0].isdigit())):
            day_offset = 2
            used = 2
        elif word in ["день", "дня",  "дні", "днів"] and is_numeric(word_prev) and preposition == "через":
            if word_prev and word_prev[0].isdigit():
                day_offset += int(word_prev)
                start -= 1
                used = 2
        elif word in ["день", "дня",  "дні", "днів"] and is_numeric(word_prev) and word_next == "тому":
            if word_prev and word_prev[0].isdigit():
                day_offset += -int(word_prev)
                start -= 1
                used = 3
        elif word in ["день", "дня",  "дні", "днів"] and is_numeric(word_prev) and word_prev_prev == "на":
            if word_prev and word_prev[0].isdigit():
                day_offset += int(word_prev)
                start -= 1
                used = 2
        elif word == "сьогодні" and not from_flag and word_prev:
            if word_prev[0].isdigit():
                day_offset += int(word_prev) * 7
                start -= 1
                used = 2
            elif word_prev in _WORDS_NEXT_UK:
                day_offset = 7
                start -= 1
                used = 2
            elif word_prev in _WORDS_PREV_UK:
                day_offset = -7
                start -= 1
                used = 2
                # parse 10 months, next month, last month
        elif word == "тиждень" and not from_flag and preposition in ["через", "на"]:
            if word_prev[0].isdigit():
                day_offset = int(word_prev) * 7
                start -= 1
                used = 2
            elif word_prev in _WORDS_NEXT_UK:
                day_offset = 7
                start -= 1
                used = 2
            elif word_prev in _WORDS_PREV_UK:
                day_offset = -7
                start -= 1
                used = 2
        elif word == "місяць" and not from_flag and preposition in ["через", "на"]:
            if word_prev[0].isdigit():
                month_offset = int(word_prev)
                start -= 1
                used = 2
            elif word_prev in _WORDS_NEXT_UK:
                month_offset = 1
                start -= 1
                used = 2
            elif word_prev in _WORDS_PREV_UK:
                month_offset = -1
                start -= 1
                used = 2
        # parse 5 years, next year, last year
        elif word == "рік" and not from_flag and preposition in ["через", "на"]:
            if word_prev[0].isdigit():
                if word_prev_prev[0].isdigit():
                    year_offset = int(word_prev)*int(word_prev_prev)
                else:
                    year_offset = int(word_prev)
                start -= 1
                used = 2
            elif word_prev in _WORDS_NEXT_UK:
                year_offset = 1
                start -= 1
                used = 2
            elif word_prev in _WORDS_PREV_UK:
                year_offset = -1
                start -= 1
                used = 2
            elif word_prev == "через":
                year_offset = 1
                used = 1
        # parse Monday, Tuesday, etc., and next Monday,
        # last Tuesday, etc.
        elif word in days and not from_flag:
            d = days.index(word)
            day_offset = (d + 1) - int(today)
            used = 1
            if day_offset < 0:
                day_offset += 7
            if word_prev in _WORDS_NEXT_UK:
                if day_offset <= 2:
                    day_offset += 7
                used += 1
                start -= 1
            elif word_prev in _WORDS_PREV_UK:
                day_offset -= 7
                used += 1
                start -= 1
        elif word in months or word in months_short and not from_flag:
            try:
                m = months.index(word)
            except ValueError:
                m = months_short.index(word)
            used += 1
            # Convert Ukrainian months to english
            date_string = _MONTHS_CONVERSION.get(m)
            if word_prev and (word_prev[0].isdigit() or
                              (word_prev == " " and word_prev_prev[0].isdigit())):
                if word_prev == " " and word_prev_prev[0].isdigit():
                    date_string += " " + words[idx - 2]
                    used += 1
                    start -= 1
                else:
                    date_string += " " + word_prev
                start -= 1
                used += 1
                if word_next and word_next[0].isdigit():
                    date_string += " " + word_next
                    used += 1
                    has_year = True
                else:
                    has_year = False

            elif word_next and word_next[0].isdigit():
                date_string += " " + word_next
                used += 1
                if word_next_next and word_next_next[0].isdigit():
                    date_string += " " + word_next_next
                    used += 1
                    has_year = True
                else:
                    has_year = False

        # parse 5 days from tomorrow, 10 weeks from next thursday,
        # 2 months from July
        valid_followups = days + months + months_short
        valid_followups.append("сьогодні")
        valid_followups.append("завтра")
        valid_followups.append("післязавтра")
        valid_followups.append("вчора")
        valid_followups.append("позавчора")
        for followup in _WORDS_NEXT_UK:
            valid_followups.append(followup)
        for followup in _WORDS_PREV_UK:
            valid_followups.append(followup)
        for followup in _WORDS_CURRENT_UK:
            valid_followups.append(followup)
        for followup in _WORDS_NOW_UK:
            valid_followups.append(followup)
        if (word in ["до", "по", "з"]) and word_next in valid_followups:
            used = 2
            from_flag = True
            if word_next == "завтра":
                day_offset += 1
            elif word_next == "післязавтра":
                day_offset += 2
            elif word_next == "вчора":
                day_offset -= 1
            elif word_next == "позавчора":
                day_offset -= 2
            elif word_next in days:
                d = days.index(word_next)
                tmp_offset = (d + 1) - int(today)
                used = 2
                if tmp_offset < 0:
                    tmp_offset += 7
                day_offset += tmp_offset
            elif word_next_next and word_next_next in days:
                d = days.index(word_next_next)
                tmp_offset = (d + 1) - int(today)
                used = 3
                if word_next in _WORDS_NEXT_UK:
                    if day_offset <= 2:
                        tmp_offset += 7
                    used += 1
                    start -= 1
                elif word_next in _WORDS_PREV_UK:
                    tmp_offset -= 7
                    used += 1
                    start -= 1
                day_offset += tmp_offset
        if used > 0:
            if start - 1 > 0 and (words[start - 1] in _WORDS_CURRENT_UK):
                start -= 1
                used += 1

            for i in range(0, used):
                words[i + start] = ""

            if start - 1 >= 0 and words[start - 1] in markers:
                words[start - 1] = ""
            found = True
            day_specified = True

    # parse time
    hr_offset = 0
    min_offset = 0
    sec_offset = 0
    hr_abs = None
    min_abs = None
    military = False
    preposition = ""

    for idx, word in enumerate(words):
        if word == "":
            continue

        if word in markers:
            preposition = word
        word = _text_uk_inflection_normalize(word, 1)
        word_prev_prev = _text_uk_inflection_normalize(
            words[idx - 2], 2) if idx > 1 else ""
        word_prev = _text_uk_inflection_normalize(
            words[idx - 1], 2) if idx > 0 else ""
        word_next = _text_uk_inflection_normalize(
            words[idx + 1], 2) if idx + 1 < len(words) else ""
        word_next_next = _text_uk_inflection_normalize(
            words[idx + 2], 2) if idx + 2 < len(words) else ""

        # parse noon, midnight, morning, afternoon, evening
        used = 0
        if word == "опівдні":
            hr_abs = 12
            used += 1
        elif word == "північ":
            hr_abs = 0
            used += 1
        elif word in _STRING_NUM_UK:
            val = _STRING_NUM_UK.get(word)
        elif word in _WORDS_MORNING_UK:
            if hr_abs is None:
                hr_abs = 8
            used += 1
        elif word in _WORDS_DAY_UK:
            if hr_abs is None:
                hr_abs = 15
            used += 1
        elif word in _WORDS_EVENING_UK:
            if hr_abs is None:
                hr_abs = 19
            used += 1
            if word_next != "" and word_next[0].isdigit() and ":" in word_next:
                used -= 1
        elif word in _WORDS_NIGHT_UK:
            if hr_abs is None:
                hr_abs = 22
        # parse half an hour, quarter hour
        #  should be added different variations oh "hour forms"
        elif word in ["година", "годину", "години"] and \
                (word_prev in markers or word_prev_prev in markers):
            if word_prev in ["пів", "половина", "опів на", "опів"]:
                min_offset = 30
            elif word_prev == "чверть":
                min_offset = 15
            #parse in an hour
            elif word_prev == "через":
                hr_offset = 1
            else:
                hr_offset = 1
            if word_prev_prev in markers:
                words[idx - 2] = ""
                if word_prev_prev in _WORDS_CURRENT_UK:
                    day_specified = True
            words[idx - 1] = ""
            used += 1
            hr_abs = -1
            min_abs = -1
            # parse 5:00 am, 12:00 p.m., etc
        # parse in a minute
        elif word == "хвилину" and word_prev == "через":
            min_offset = 1
            words[idx - 1] = ""
            used += 1
        # parse in a second
        elif word == "секунду" and word_prev == "через":
            sec_offset = 1
            words[idx - 1] = ""
            used += 1
        elif word[0].isdigit():
            is_time = True
            str_hh = ""
            str_mm = ""
            remainder = ""
            word_next_next_next = words[idx + 3] \
                if idx + 3 < len(words) else ""
            if word_next in _WORDS_EVENING_UK or word_next in _WORDS_NIGHT_UK or word_next_next in _WORDS_EVENING_UK \
                    or word_next_next in _WORDS_NIGHT_UK or word_prev in _WORDS_EVENING_UK \
                    or word_prev in _WORDS_NIGHT_UK or word_prev_prev in _WORDS_EVENING_UK \
                    or word_prev_prev in _WORDS_NIGHT_UK or word_next_next_next in _WORDS_EVENING_UK \
                    or word_next_next_next in _WORDS_NIGHT_UK:
                remainder = "pm"
                used += 1
                if word_prev in _WORDS_EVENING_UK or word_prev in _WORDS_NIGHT_UK:
                    words[idx - 1] = ""
                if word_prev_prev in _WORDS_EVENING_UK or word_prev_prev in _WORDS_NIGHT_UK:
                    words[idx - 2] = ""
                if word_next_next in _WORDS_EVENING_UK or word_next_next in _WORDS_NIGHT_UK:
                    used += 1
                if word_next_next_next in _WORDS_EVENING_UK or word_next_next_next in _WORDS_NIGHT_UK:
                    used += 1

            if ':' in word:
                # parse colons
                # "3:00 in the morning"
                stage = 0
                length = len(word)
                for i in range(length):
                    if stage == 0:
                        if word[i].isdigit():
                            str_hh += word[i]
                        elif word[i] == ":":
                            stage = 1
                        else:
                            stage = 2
                            i -= 1
                    elif stage == 1:
                        if word[i].isdigit():
                            str_mm += word[i]
                        else:
                            stage = 2
                            i -= 1
                    elif stage == 2:
                        remainder = word[i:].replace(".", "")
                        break
                if remainder == "":
                    hour = ["година", "годині"]
                    next_word = word_next.replace(".", "")
                    if next_word in ["am", "pm", "ночі", "ранку", "дня", "вечора"]:
                        remainder = next_word
                        used += 1
                    # question with the case "година"
                    elif next_word in hour and word_next_next in ["am", "pm", "ночи", "утра", "дня", "вечера"]:
                        remainder = word_next_next
                        used += 2
                    elif word_next in _WORDS_MORNING_UK:
                        remainder = "am"
                        used += 2
                    elif word_next in _WORDS_DAY_UK:
                        remainder = "pm"
                        used += 2
                    elif word_next in _WORDS_EVENING_UK:
                        remainder = "pm"
                        used += 2
                    elif word_next == "цього" and word_next_next in _WORDS_MORNING_UK:
                        remainder = "am"
                        used = 2
                        day_specified = True
                    elif word_next == "на" and word_next_next in _WORDS_DAY_UK:
                        remainder = "pm"
                        used = 2
                        day_specified = True
                    elif word_next == "на" and word_next_next in _WORDS_EVENING_UK:
                        remainder = "pm"
                        used = 2
                        day_specified = True
                    elif word_next == "в" and word_next_next in _WORDS_NIGHT_UK:
                        if str_hh and int(str_hh) > 5:
                            remainder = "pm"
                        else:
                            remainder = "am"
                        used += 2
                    elif word_next == "о" and word_next_next in _WORDS_NIGHT_UK:
                        if str_hh and int(str_hh) > 5:
                            remainder = "pm"
                        else:
                            remainder = "am"
                        used += 2
                    elif hr_abs and hr_abs != -1:
                        if hr_abs >= 12:
                            remainder = "pm"
                        else:
                            remainder = "am"
                        used += 1
                    else:
                        if time_qualifier != "":
                            military = True
                            if str_hh and int(str_hh) <= 12 and \
                                    (time_qualifier in time_qualifiers_pm):
                                str_hh += str(int(str_hh) + 12)

            else:
                # try to parse numbers without colons
                # 5 hours, 10 minutes etc.
                length = len(word)
                str_num = ""
                remainder = ""
                for i in range(length):
                    if word[i].isdigit():
                        str_num += word[i]
                    else:
                        remainder += word[i]

                if remainder == "":
                    remainder = word_next.replace(".", "").lstrip().rstrip()
                if (
                        remainder == "pm" or
                        word_next == "pm" or
                        remainder == "p.m." or
                        word_next == "p.m." or
                        (remainder == "дня" and preposition != 'через') or
                        (word_next == "дня" and preposition != 'через') or
                        remainder == "вечора" or
                        word_next == "вечора"):
                    str_hh = str_num
                    remainder = "pm"
                    used = 1
                    if (
                            remainder == "pm" or
                            word_next == "pm" or
                            remainder == "p.m." or
                            word_next == "p.m." or
                            (remainder == "дня" and preposition != 'через') or
                            (word_next == "дня" and preposition != 'через') or
                            remainder == "вечора" or
                            word_next == "вечора"):
                        str_hh = str_num
                        remainder = "pm"
                        used = 1
                elif (
                        remainder == "am" or
                        word_next == "am" or
                        remainder == "a.m." or
                        word_next == "a.m." or
                        remainder == "ночі" or
                        word_next == "ночі" or
                        remainder == "ранку" or
                        word_next == "ранку"):
                    str_hh = str_num
                    remainder = "am"
                    used = 1
                elif (
                        remainder in recur_markers or
                        word_next in recur_markers or
                        word_next_next in recur_markers):
                    # Ex: "7 on mondays" or "3 this friday"
                    # Set str_hh so that is_time == True
                    # when am or pm is not specified
                    str_hh = str_num
                    used = 1
                else:
                    if int(str_num) > 100:
                        str_hh = str(int(str_num) // 100)
                        str_mm = str(int(str_num) % 100)
                        military = True
                        if word_next == "година":
                            used += 1
                    elif (
                            (word_next == "година" or word_next == "годину" or
                             remainder == "година") and
                            word[0] != '0' and
                            # (wordPrev != "в" and wordPrev != "на")
                            word_prev == "через"
                            and
                            (
                                    int(str_num) < 100 or
                                    int(str_num) > 2400
                            )):
                        # ignores military time
                        # "in 3 hours"
                        hr_offset = int(str_num)
                        used = 2
                        is_time = False
                        hr_abs = -1
                        min_abs = -1
                    elif word_next == "хвилина" or \
                            remainder == "хвилина":
                        # "in 10 minutes"
                        min_offset = int(str_num)
                        used = 2
                        is_time = False
                        hr_abs = -1
                        min_abs = -1
                    elif word_next == "секунда" \
                            or remainder == "секунда":
                        # in 5 seconds
                        sec_offset = int(str_num)
                        used = 2
                        is_time = False
                        hr_abs = -1
                        min_abs = -1
                    elif int(str_num) > 100:
                        # military time, eg. "3300 hours"
                        str_hh = str(int(str_num) // 100)
                        str_mm = str(int(str_num) % 100)
                        military = True
                        if word_next == "час" or \
                                remainder == "час":
                            used += 1
                    elif word_next and word_next[0].isdigit():
                        # military time, e.g. "04 38 hours"
                        str_hh = str_num
                        str_mm = word_next
                        military = True
                        used += 1
                        if (word_next_next == "година" or
                                remainder == "час"):
                            used += 1
                    elif (
                            word_next == "" or word_next == "година" or
                            (
                                    (word_next == "в" or word_next == "на") and
                                    (
                                            word_next_next == time_qualifier
                                    )
                            ) or word_next in _WORDS_EVENING_UK or
                            word_next_next in _WORDS_EVENING_UK):

                        str_hh = str_num
                        str_mm = "00"
                        if word_next == "година":
                            used += 1
                        if (word_next == "о" or word_next == "на"
                                or word_next_next == "о" or word_next_next == "на"):
                            used += (1 if (word_next ==
                                           "о" or word_next == "на") else 2)
                            word_next_next_next = words[idx + 3] \
                                if idx + 3 < len(words) else ""

                            if (word_next_next and
                                    (word_next_next in time_qualifier or
                                     word_next_next_next in time_qualifier)):
                                if (word_next_next in time_qualifiers_pm or
                                        word_next_next_next in time_qualifiers_pm):
                                    remainder = "pm"
                                    used += 1
                                if (word_next_next in time_qualifiers_am or
                                        word_next_next_next in time_qualifiers_am):
                                    remainder = "am"
                                    used += 1

                        if time_qualifier != "":
                            if time_qualifier in time_qualifiers_pm:
                                remainder = "pm"
                                used += 1

                            elif time_qualifier in time_qualifiers_am:
                                remainder = "am"
                                used += 1
                            else:
                                # TODO: Unsure if this is 100% accurate
                                used += 1
                                military = True
                        elif remainder == "година":
                            if word_next_next in ["ночі", "ранку"]:
                                remainder = "am"
                                used += 1
                            elif word_next_next in ["дня", "вечора"]:
                                remainder = "pm"
                                used += 1
                            else:
                                remainder = ""

                    else:
                        is_time = False
            hh = int(str_hh) if str_hh else 0
            mm = int(str_mm) if str_mm else 0
            hh = hh + 12 if remainder == "pm" and hh < 12 else hh
            hh = hh - 12 if remainder == "am" and hh >= 12 else hh
            if (not military and
                    remainder not in ['am', 'pm', 'година', 'хвилина', 'секунда'] and
                    ((not day_specified) or 0 <= day_offset < 1)):

                # ambiguous time, detect whether they mean this evening or
                # the next morning based on whether it has already passed
                if anchor_date.hour < hh or (anchor_date.hour == hh and
                                             anchor_date.minute < mm):
                    pass  # No modification needed
                elif anchor_date.hour < hh + 12:
                    hh += 12
                else:
                    # has passed, assume the next morning
                    day_offset += 1
            if time_qualifier in time_qualifiers_pm and hh < 12:
                hh += 12

            if hh > 24 or mm > 59:
                is_time = False
                used = 0
            if is_time:
                hr_abs = hh
                min_abs = mm
                used += 1

        if used > 0:
            # removed parsed words from the sentence
            for i in range(used):
                if idx + i >= len(words):
                    break
                words[idx + i] = ""

            # if wordPrev == "o" or wordPrev == "oh":
            #    words[words.index(wordPrev)] = ""

            if word_prev == "скоро":
                hr_offset = -1
                words[idx - 1] = ""
                idx -= 1
            elif word_prev == "пізніше":
                hr_offset = 1
                words[idx - 1] = ""
                idx -= 1
            if idx > 0 and word_prev in markers:
                words[idx - 1] = ""
                if word_prev in _WORDS_CURRENT_UK:
                    day_specified = True
            if idx > 1 and word_prev_prev in markers:
                words[idx - 2] = ""
                if word_prev_prev in _WORDS_CURRENT_UK:
                    day_specified = True

            idx += used - 1
            found = True
    # check that we found a date
    if not date_found():
        return None

    if day_offset is False:
        day_offset = 0

    # perform date manipulation

    extracted_date = anchor_date.replace(microsecond=0)
    if date_string != "":
        # date included an explicit date, e.g. "june 5" or "june 2, 2017"
        try:
            temp = datetime.strptime(date_string, "%B %d")
        except ValueError:
            # Try again, allowing the year
            temp = datetime.strptime(date_string, "%B %d %Y")
        extracted_date = extracted_date.replace(hour=0, minute=0, second=0)
        if not has_year:
            temp = temp.replace(year=extracted_date.year,
                                tzinfo=extracted_date.tzinfo)
            if extracted_date < temp:
                extracted_date = extracted_date.replace(
                    year=int(current_year),
                    month=int(temp.strftime("%m")),
                    day=int(temp.strftime("%d")),
                    tzinfo=extracted_date.tzinfo)
            else:
                extracted_date = extracted_date.replace(
                    year=int(current_year) + 1,
                    month=int(temp.strftime("%m")),
                    day=int(temp.strftime("%d")),
                    tzinfo=extracted_date.tzinfo)
        else:
            extracted_date = extracted_date.replace(
                year=int(temp.strftime("%Y")),
                month=int(temp.strftime("%m")),
                day=int(temp.strftime("%d")),
                tzinfo=extracted_date.tzinfo)
    else:
        # ignore the current HH:MM:SS if relative using days or greater
        if hr_offset == 0 and min_offset == 0 and sec_offset == 0:
            extracted_date = extracted_date.replace(hour=0, minute=0, second=0)

    if year_offset != 0:
        extracted_date = extracted_date + relativedelta(years=year_offset)
    if month_offset != 0:
        extracted_date = extracted_date + relativedelta(months=month_offset)
    if day_offset != 0:
        extracted_date = extracted_date + relativedelta(days=day_offset)
    if hr_abs != -1 and min_abs != -1:
        # If no time was supplied in the string set the time to default
        # time if it's available
        if hr_abs is None and min_abs is None and default_time is not None:
            hr_abs, min_abs = default_time.hour, default_time.minute
        else:
            hr_abs = hr_abs or 0
            min_abs = min_abs or 0

        extracted_date = extracted_date + relativedelta(hours=hr_abs,
                                                        minutes=min_abs)
        if (hr_abs != 0 or min_abs != 0) and date_string == "":
            if not day_specified and anchor_date > extracted_date:
                extracted_date = extracted_date + relativedelta(days=1)
    if hr_offset != 0:
        extracted_date = extracted_date + relativedelta(hours=hr_offset)
    if min_offset != 0:
        extracted_date = extracted_date + relativedelta(minutes=min_offset)
    if sec_offset != 0:
        extracted_date = extracted_date + relativedelta(seconds=sec_offset)
    for idx, word in enumerate(words):
        if words[idx] == "і" and \
                words[idx - 1] == "" and words[idx + 1] == "":
            words[idx] = ""

    result_str = " ".join(words)
    result_str = ' '.join(result_str.split())
    return [extracted_date, result_str]

# change logic here
def is_fractional_uk(input_str, word, short_scale=True):
    """
    This function takes the given text and checks if it is a fraction.

    Args:
        input_str (str): the string to check if fractional
        short_scale (bool): use short scale if True, long scale if False
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction

    """
    fractions = {"ціла": 1}
    # endings for creation different cases and plurals in different cases
    ending = ['ої', 'е', 'их', 'ою', 'і', 'ими', 'ій']
    for num in _FRACTION_STRING_UK.keys():  # Numbers from 2 to 1 hundred, more is not usually used in common speech
        if num > 1:
            fractions[str(_FRACTION_STRING_UK[num])] = num
            for end in ending:
                new_fraction_number = _FRACTION_STRING_UK[num][:-1]+end
                fractions[new_fraction_number] = num
    fractions.update({
        "половина": 2, "половиною": 2, "половини": 2, "половин": 2, "половинами": 2, "пів": 2,
        "шоста": 6,
        "третина": 1 / 3, "треть": 1 / 3, "треті": 3, "третьої": 3,
        "чверті": 4, "чверть": 0.25, "чвертю": 0.25
    })
    if input_str.lower() in fractions.keys():
        if word == input_str:
            return fractions[input_str.lower()]
        elif word not in _STRING_NUM_UK:
            return fractions[input_str.lower()]
        else:
            return 1.0 / fractions[input_str.lower()]
    return False


def extract_numbers_uk(text, short_scale=True, ordinals=False):
    """
        Takes in a string and extracts a list of numbers.

    Args:
        text (str): the string to extract a number from
        short_scale (bool): Use "short scale" or "long scale" for large
            numbers -- over a million.  The default is short scale, which
            is now common in most English speaking countries.
            See https://en.wikipedia.org/wiki/Names_of_large_numbers
        ordinals (bool): consider ordinal numbers, e.g. third=3 instead of 1/3
    Returns:
        list: list of extracted numbers as floats
    """
    results = _extract_numbers_with_text_uk(tokenize(text),
                                            short_scale, ordinals)
    #numbers_sum = sum([float(result.value) for result in results])
    return [float(result.value) for result in results]


class UkrainianNormalizer(Normalizer):
    with open(resolve_resource_file("text/uk-uk/normalize.json"), encoding='utf8') as f:
        _default_config = json.load(f)


def normalize_uk(text, remove_articles=True):
    """ Ukrainian string normalization """
    return UkrainianNormalizer().normalize(text, remove_articles)


def _text_uk_inflection_normalize(word, arg):
    """
    Ukrainian Inflection normalizer.

    This try to normalize known inflection. This function is called
    from multiple places, each one is defined with arg.

    Args:
        word [Word]
        arg [Int]

    Returns:
        word [Word]

    """


    if arg == 1:  # _extract_whole_number_with_text_uk
        if word in ["одна", "одним", "одно", "одною", "одного", "одної", "одному", "одній", "одного", "одну"]:
            return "один"
        return _plurals_normalizer(word)

    elif arg == 2:  # extract_datetime_uk
        if word in ["година", "години", "годин", "годину", "годин", "годинами"]:
            return "година"
        if word in ["хвилина", "хвилини", "хвилину", "хвилин", "хвилька"]:
            return "хвилина"
        if word in ["секунд", "секунди", "секундами", "секунду", "секунд", "сек"]:
            return "секунда"
        if word in ["днів", "дні", "днями", "дню", "днем", "днями"]:
            return "день"
        if word in ["тижні", "тижнів", "тижнями", "тиждень", "тижня"]:
            return "тиждень"
        if word in ["місяцем", "місяці", "місяця", "місяцях", "місяцем", "місяцями", "місяців"]:
            return "місяць"
        if word in ["року", "роки", "році", "роках", "роком", "роками", "років"]:
            return "рік"
        if word in _WORDS_MORNING_UK:
            return "вранці"
        if word in ["опівдні", "півдня"]:
            return "південь"
        if word in _WORDS_EVENING_UK:
            return "ввечері"
        if word in _WORDS_NIGHT_UK:
            return "ніч"
        if word in ["вікенд", "вихідних", "вихідними"]:
            return "вихідні"
        if word in ["столітті", "століттях", "століть"]:
            return "століття"
        if word in ["десятиліття", "десятиліть", "десятиліттях"]:
            return "десятиліття"
        if word in ["столітті", "століттях", "століть"]:
            return "століття"

        # Week days
        if word in ["понеділка", "понеділки"]:
            return "понеділок"
        if word in ["вівторка", "вівторки"]:
            return "вівторок"
        if word in ["середу", "середи"]:
            return "среда"
        if word in ["четверга"]:
            return "четвер"
        if word in ["п'ятницю", "п'ятниці"]:
            return "п'ятниця"
        if word in ["суботу", "суботи"]:
            return "субота"
        if word in ["неділю", "неділі"]:
            return "неділя"

        # Months
        if word in ["лютому", "лютого", "лютим"]:
            return "лютий"
        if word in ["листопада", "листопаді", "листопадом"]:
            return "листопад"
        tmp = ''
        if word[-3:] in ["ого", "ому"]:
            tmp = word[:-3] + "ень"
        elif word[-2:] in ["ні", "ня"]:
            tmp = word[:-2] + "ень"
        for name in _MONTHS_UK:
            if name == tmp:
                return name
    return word

def _plurals_normalizer(word):
    """
    Ukrainian Plurals normalizer.

    This function normalizes plural endings of numerals
    including different case variations.
    Uses _PLURALS dictionary with exceptions that can not
    be covered by rules.
    Args:
        word [Word]

    Returns:
        word [Word]

    """
    if word not in _STRING_NUM_UK:
        # checking for plurals 2-10
        for key, value in _PLURALS.items():
            if word == key:
                return _NUM_STRING_UK[value]

        # checking for plurals 11-19
        case_endings = ['надцяти', 'надцятим', 'надцятими',
                        'надцятьох', 'надцятьма', 'надцятьома', 'надцятьом']
        plural_case = ''.join([case for case in case_endings if case in word])
        if plural_case:
            if 'один' in word:
                return "одинадцять"
            word = word.replace(plural_case, '')+'надцять'
            return word

        # checking for plurals 20,30
        case_endings = ['дцяти', 'дцятим', 'дцятими',
                        'дцятьох', 'дцятьма', 'дцятьома', 'дцятьом']
        plural_case = ''.join([case for case in case_endings if case in word])
        if plural_case:
            word = word.replace(plural_case, '')+'дцять'
            return word

        # checking for plurals 50, 60, 70, 80
        case_endings = ['десятьох', 'десяти', 'десятьом',
                        'десятьма', 'десятьома']
        plural_case = ''.join([case for case in case_endings if case in word])
        if plural_case:
            word = word.replace(plural_case, '')+'десят'
            return word

        # checking for plurals 90, 100
        case_endings = ['стам', 'стами', 'стах',
                        'стами', 'ста', 'сот']
        plural_case = ''.join([case for case in case_endings if case in word])
        if plural_case:
            word = word.replace(plural_case, '')
            for key, value in _PLURALS.items():
                if word == key:
                    firs_part = _NUM_STRING_UK[value]
                    if value in [3, 4]:
                        word = firs_part+'ста'
                    elif value in [5, 6, 9]:
                        word = firs_part[:-1]+'сот'
                    elif value in [7, 8]:
                        word = firs_part+'сот'
                    return word
            return word
    return word


