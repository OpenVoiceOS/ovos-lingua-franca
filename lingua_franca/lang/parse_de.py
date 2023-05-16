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

import re
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from lingua_franca.lang.parse_common import (
    ReplaceableNumber,
    Normalizer,
    Token,
    look_for_fractions,
    tokenize,
)
from lingua_franca.lang.common_data_de import (
    _STRING_NUM,
    _STRING_FRACTION,
    _STRING_LONG_ORDINAL,
    _STRING_LONG_SCALE,
    _MULTIPLIER,
    _NEGATIVES,
    _NUMBER_CONNECTORS,
    _COMMA,
    _ARTICLES
)
from lingua_franca.time import now_local, DAYS_IN_1_YEAR, DAYS_IN_1_MONTH
from lingua_franca.internal import resolve_resource_file



def _convert_words_to_numbers_de(text, short_scale=False,
                                 ordinals=False, fractions=True):
    """
    Convert words in a string into their equivalent numbers.
    Args:
        text str:
        short_scale boolean: True if short scale numberres should be used.
        ordinals boolean: True if ordinals (e.g. first, second, third) should
                          be parsed to their number values (1, 2, 3...)
    Returns:
        str
        The original text, with numbers subbed in where appropriate.
    """
    tokens = tokenize(text)
    numbers_to_replace = \
        _extract_numbers_with_text_de(tokens, short_scale, ordinals, fractions)
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


def _extract_numbers_with_text_de(tokens, short_scale=True,
                                  ordinals=False, fractions=True):
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
            _extract_number_with_text_de(tokens, short_scale,
                                         ordinals)

        if not to_replace:
            break

        if isinstance(to_replace.value, float) and not fractions:
            pass
        else:
            results.append(to_replace)

        tokens = [
            t if not
            to_replace.start_index <= t.index <= to_replace.end_index
            else
            Token(placeholder, t.index) for t in tokens
        ]
    results.sort(key=lambda n: n.start_index)
    return results


def _extract_number_with_text_de(tokens, short_scale=True,
                                 ordinals=False):
    """
    This function extracts a number from a list of Tokens.

    Args:
        tokens str: the string to normalize
        short_scale (bool): use short scale if True, long scale if False
        ordinals (bool): consider ordinal numbers
        fractional_numbers (bool): True if we should look for fractions and
                                   decimals.
    Returns:
        ReplaceableNumber

    """
    number, tokens = \
        _extract_number_with_text_de_helper(tokens, short_scale,
                                            ordinals)
    return ReplaceableNumber(number, tokens)


def _extract_number_with_text_de_helper(tokens,
                                        short_scale, ordinals):
    """
    Helper for _extract_number_with_text_de.

    Args:
        tokens [Token]:
        short_scale boolean:
        ordinals boolean:
        fractional_numbers boolean:
    Returns:
        int or float, [Tokens]
    """
    if ordinals:
        for token in tokens:
            ordinal = is_ordinal_de(token.word)
            if ordinal:
                return ordinal, [token]

    return _extract_real_number_with_text_de(tokens, short_scale)


def _extract_real_number_with_text_de(tokens, short_scale):
    """
    This is handling real numbers.

    Args:
        tokens [Token]:
        short_scale boolean:
    Returns:
        int or float, [Tokens]
        The value parsed, and tokens that it corresponds to.
    """
    number_words = []
    val = _val = _current_val = None
    _comma = False
    to_sum = []

    for idx, token in enumerate(tokens):

        _prev_val = _current_val
        _current_val = None

        word = token.word

        if word in _NUMBER_CONNECTORS and not number_words:
            continue
        if word in (_NEGATIVES | _NUMBER_CONNECTORS | _COMMA):
            number_words.append(token)
            if word in _COMMA:
                _comma = token
                _current_val = _val or _prev_val
            continue

        prev_word = tokens[idx - 1].word if idx > 0 else ""
        next_word = tokens[idx + 1].word if idx + 1 < len(tokens) else ""

        if word not in _STRING_LONG_SCALE and \
                word not in _STRING_NUM and \
                word not in _MULTIPLIER and \
                not is_numeric_de(word) and \
                not is_fractional_de(word):
            words_only = [token.word for token in number_words]
            if _val is not None:
                to_sum.append(_val)
            if to_sum:
                val = sum(to_sum)

            if number_words and (not all([w in _ARTICLES | _NEGATIVES
                                         | _NUMBER_CONNECTORS for w in words_only])
                                 or str(val) == number_words[-1].word):
                break
            else:
                number_words.clear()
                to_sum.clear()
                val = _val = _prev_val = None
            continue
        elif word not in _MULTIPLIER \
                and prev_word not in _MULTIPLIER \
                and prev_word not in _NUMBER_CONNECTORS \
                and prev_word not in _NEGATIVES \
                and prev_word not in _COMMA \
                and prev_word not in _STRING_LONG_SCALE \
                and prev_word not in _STRING_NUM \
                and not is_ordinal_de(word) \
                and not is_numeric_de(prev_word)  \
                and not is_fractional_de(prev_word):
            number_words = [token]
        else:
            number_words.append(token)

        # is this word already a number or a word of a number?
        _val = _current_val = is_number_de(word)

        # is this a negative number?
        if _current_val is not None and prev_word in _NEGATIVES:
            _val = 0 - _current_val
        
        # is the prev word a number and should we multiply it?
        if _prev_val is not None and ( word in _MULTIPLIER or \
            word in ("einer", "eines", "einem")):
            to_sum.append(_prev_val * _current_val or _current_val)
            _val = _current_val = None
        
        # fraction handling
        _fraction_val = is_fractional_de(word, short_scale=short_scale)
        if _fraction_val:
            if _prev_val is not None and prev_word != "eine" and \
                    word not in _STRING_FRACTION:   # zusammengesetzter Bruch
                _val = _prev_val + _fraction_val
                if prev_word not in _NUMBER_CONNECTORS and tokens[idx -1] not in number_words:
                    number_words.append(tokens[idx - 1])
            elif _prev_val is not None:
                _val = _prev_val * _fraction_val
                if tokens[idx -1] not in number_words:
                    number_words.append(tokens[idx - 1])
            else:
                _val = _fraction_val
            _current_val = _val
        
        # directly following numbers without relation
        if (is_numeric_de(prev_word) or prev_word in _STRING_NUM) \
                and not _fraction_val and not is_fractional_de(next_word) and not to_sum:
            val = _prev_val
            number_words.pop(-1)
            break

        # is this a spoken time ("drei viertel acht")
        if isinstance(_prev_val, float) and is_number_de(word) and not to_sum:
            if idx+1 < len(tokens):
                _, number = _extract_real_number_with_text_de([tokens[idx + 1]],
                                                              short_scale=short_scale)
            if not next_word or not number:
                val = f"{_val-1}:{int(60*_prev_val)}"
                break

        # spoken decimals
        if _current_val is not None and _comma:
            # to_sum = [ 1, 0.2, 0.04,...]
            to_sum.append(_current_val if _current_val >= 10 else (
                _current_val) / (10 ** (token.index - _comma.index)))
            _val = _current_val = None


        if _current_val is not None and next_word in (_NUMBER_CONNECTORS | _COMMA | {""}):
            to_sum.append(_val or _current_val)
            _val = _current_val = None

        
        if not next_word and number_words:
            val = sum(to_sum) or _val

    return val, number_words


def extract_duration_de(text):
    """
    Convert an german phrase into a number of seconds
    Convert things like:
        "10 Minuten"
        "3 Tage 8 Stunden 10 Minuten und 49 Sekunden"
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

    text = text.lower()
    # die time_unit values werden für timedelta() mit dem jeweiligen Wert überschrieben
    time_units = {
        'microseconds': 'mikrosekunden',
        'milliseconds': 'millisekunden',
        'seconds': 'sekunden',
        'minutes': 'minuten',
        'hours': 'stunden',
        'days': 'tage',
        'weeks': 'wochen'
    }

    # Einzahl und Mehrzahl
    pattern = r"(?:^|\s)(?P<value>\d+(?:[.,]?\d+)?\b)(?:\s+|\-)(?P<unit>{unit}[nes]?[sn]?\b)"

    text = _convert_words_to_numbers_de(text)

    for (unit_en, unit_de) in time_units.items():
        unit_pattern = pattern.format(
            unit=unit_de[:-1])  # remove 'n'/'e' from unit
        time_units[unit_en] = 0

        def repl(match):
            value = match.group("value").replace(",",".")
            time_units[unit_en] += float(value)
            return ''
        text = re.sub(unit_pattern, repl, text)

    text = text.strip()
    duration = timedelta(**time_units) if any(time_units.values()) else None

    return (duration, text)


def extract_datetime_de(text, anchorDate=None, default_time=None):
    def clean_string(s):
        """
            cleans the input string of unneeded punctuation
            and capitalization among other things.

            'am' is a preposition, so cannot currently be used
            for 12 hour date format
        """

        s = _convert_words_to_numbers_de(s)
        s = s.lower().replace('?', '').replace(' der ', ' ').replace(' den ', ' ')\
            .replace(' an ', ' ').replace(' am ', ' ').replace(' auf ', ' ')\
            .replace(' um ', ' ')
        wordList = s.split()

        for idx, word in enumerate(wordList):
            ordinal = _get_ordinal_index(word)
            if ordinal:
                wordList[idx] = ordinal

        return wordList

    def date_found():
        return found or \
            (
                datestr != "" or timeStr != "" or
                yearOffset != 0 or monthOffset != 0 or
                dayOffset is True or hrOffset != 0 or
                hrAbs or minOffset != 0 or
                minAbs or secOffset != 0
            )

    if text == "":
        return None

    anchorDate = anchorDate or now_local()
    found = False
    daySpecified = False
    dayOffset = False
    monthOffset = 0
    yearOffset = 0
    dateNow = anchorDate
    today = dateNow.strftime("%w")
    currentYear = dateNow.strftime("%Y")
    fromFlag = False
    datestr = ""
    hasYear = False
    timeQualifier = ""

    timeQualifiersList = ['früh', 'morgens', 'vormittag', 'vormittags',
                          'mittag', 'mittags', 'nachmittag', 'nachmittags',
                          'abend', 'abends', 'nacht', 'nachts', 'pm', 'p.m.']
    eveningQualifiers = ['nachmittag', 'nachmittags', 'abend', 'abends', 'nacht',
                        'nachts', 'pm', 'p.m.']
    markers = ['in', 'am', 'gegen', 'bis', 'für']
    days = ['montag', 'dienstag', 'mittwoch',
            'donnerstag', 'freitag', 'samstag', 'sonntag']
    months = ['januar', 'februar', 'märz', 'april', 'mai', 'juni',
              'juli', 'august', 'september', 'october', 'november',
              'dezember']
    monthsShort = ['jan', 'feb', 'mär', 'apr', 'mai', 'juni', 'juli', 'aug',
                   'sept', 'oct', 'nov', 'dez']

    validFollowups = days + months + monthsShort
    validFollowups.append("heute")
    validFollowups.append("morgen")
    validFollowups.append("nächste")
    validFollowups.append("nächster")
    validFollowups.append("nächstes")
    validFollowups.append("nächsten")
    validFollowups.append("nächstem")
    validFollowups.append("letzte")
    validFollowups.append("letzter")
    validFollowups.append("letztes")
    validFollowups.append("letzten")
    validFollowups.append("letztem")
    validFollowups.append("jetzt")

    words = clean_string(text)

    for idx, word in enumerate(words):
        if word == "":
            continue
        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""

        start = idx
        used = 0
        # save timequalifier for later
        if word in timeQualifiersList:
            timeQualifier = word
            # parse today, tomorrow, day after tomorrow
        elif word == "heute" and not fromFlag:
            dayOffset = 0
            used += 1
        elif word == "morgen" and not fromFlag and wordPrev != "am" and \
                wordPrev not in days:  # morgen means tomorrow if not "am
            # Morgen" and not [day of the week] morgen
            dayOffset = 1
            used += 1
        elif word == "übermorgen" and not fromFlag:
            dayOffset = 2
            used += 1
            # parse 5 days, 10 weeks, last week, next week
        elif word[:3] == "tag" and len(word) <= 5:
            num = is_number_de(wordPrev)
            if num:
                dayOffset += num
                start -= 1
                used = 2
        elif word[:5] == "woche" and len(word) <= 7 and not fromFlag:
            num = is_number_de(wordPrev)
            if num:
                dayOffset += num * 7
                start -= 1
                used = 2
            elif wordPrev[:6] == "nächst":
                dayOffset = 7
                start -= 1
                used = 2
            elif wordPrev[:5] == "letzt":
                dayOffset = -7
                start -= 1
                used = 2
                # parse 10 months, next month, last month
        elif word[:5] == "monat" and len(word) <= 7 and not fromFlag:
            num = is_number_de(wordPrev)
            if num:
                monthOffset = num
                start -= 1
                used = 2
            elif wordPrev[:6] == "nächst":
                monthOffset = 1
                start -= 1
                used = 2
            elif wordPrev[:5] == "letzt":
                monthOffset = -1
                start -= 1
                used = 2
                # parse 5 years, next year, last year
        elif word[:4] == "jahr" and len(word) <= 6 and not fromFlag:
            num = is_number_de(wordPrev)
            if num:
                yearOffset = num
                start -= 1
                used = 2
            elif wordPrev[:6] == "nächst":
                yearOffset = 1
                start -= 1
                used = 2
            elif wordPrev[:6] == "nächst":
                yearOffset = -1
                start -= 1
                used = 2
                # parse Monday, Tuesday, etc., and next Monday,
                # last Tuesday, etc.
        elif word in days and not fromFlag:
            d = days.index(word)
            dayOffset = (d + 1) - int(today)
            used = 1
            if dayOffset < 0:
                dayOffset += 7
            if wordNext == "morgen":  # morgen means morning if preceded by
                # the day of the week
                words[idx + 1] = "früh"
            if wordPrev[:6] == "nächst":
                dayOffset += 7
                used += 1
                start -= 1
            elif wordPrev[:5] == "letzt":
                dayOffset -= 7
                used += 1
                start -= 1
                # parse 15 of July, June 20th, Feb 18, 19 of February
        elif word in months or word in monthsShort and not fromFlag:
            try:
                m = months.index(word)
            except ValueError:
                m = monthsShort.index(word)
            used += 1
            datestr = months[m]
            if wordPrev and (wordPrev[0].isdigit() or
                             (wordPrev == "of" and wordPrevPrev[0].isdigit())):
                if wordPrev == "of" and wordPrevPrev[0].isdigit():
                    datestr += " " + words[idx - 2]
                    used += 1
                    start -= 1
                else:
                    datestr += " " + wordPrev
                start -= 1
                used += 1
                if wordNext and wordNext[0].isdigit():
                    datestr += " " + wordNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            elif wordNext and wordNext[0].isdigit():
                datestr += " " + wordNext
                used += 1
                if wordNextNext and wordNextNext[0].isdigit():
                    datestr += " " + wordNextNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False
        # parse 5 days from tomorrow, 10 weeks from next thursday,
        # 2 months from July

        if (
                word == "von" or word == "nach" or word == "ab") and wordNext \
                in validFollowups:
            used = 2
            fromFlag = True
            if wordNext == "morgen" and wordPrev != "am" and \
                    wordPrev not in days:  # morgen means tomorrow if not "am
                #  Morgen" and not [day of the week] morgen:
                dayOffset += 1
            elif wordNext in days:
                d = days.index(wordNext)
                tmpOffset = (d + 1) - int(today)
                used = 2
                if tmpOffset < 0:
                    tmpOffset += 7
                dayOffset += tmpOffset
            elif wordNextNext and wordNextNext in days:
                d = days.index(wordNextNext)
                tmpOffset = (d + 1) - int(today)
                used = 3
                if wordNext[:6] == "nächst":
                    tmpOffset += 7
                    used += 1
                    start -= 1
                elif wordNext[:5] == "letzt":
                    tmpOffset -= 7
                    used += 1
                    start -= 1
                dayOffset += tmpOffset
        if used > 0:
            if start - 1 > 0 and words[start - 1].startswith("diese"):
                start -= 1
                used += 1

            for i in range(0, used):
                words[i + start] = ""

            if start - 1 >= 0 and words[start - 1] in markers:
                words[start - 1] = ""
            found = True
            daySpecified = True

    # parse time
    timeStr = ""
    hrOffset = 0
    minOffset = 0
    secOffset = 0
    hrAbs = None
    minAbs = None

    for idx, word in enumerate(words):
        if word == "":
            continue

        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""
        wordNextNextNext = words[idx + 3] if idx + 3 < len(words) else ""
        wordNextNextNextNext = words[idx + 4] if idx + 4 < len(words) else ""

        # parse noon, midnight, morning, afternoon, evening
        used = 0
        if word[:6] == "mittag":
            hrAbs = 12
            used += 1
        elif word[:11] == "mitternacht":
            hrAbs = 0
            used += 1
        elif word == "morgens" or (
                wordPrev == "am" and word == "morgen") or word == "früh":
            if not hrAbs:
                hrAbs = 8
            used += 1
        elif word[:10] == "nachmittag":
            if not hrAbs:
                hrAbs = 15
            used += 1
        elif word[:5] == "abend":
            if not hrAbs:
                hrAbs = 19
            used += 1
            # parse half an hour, quarter hour
        elif word[:5] == "nacht":
            if not hrAbs:
                hrAbs = 23
            used += 1
        elif word[:6] == "stunde" and \
                (wordPrev in markers or wordPrevPrev in markers):
            factor = is_number_de(word) or 1
            minOffset = 60 * factor
            if wordPrevPrev in markers:
                words[idx - 2] = ""
            words[idx - 1] = ""
            used += 1
            hrAbs = -1
            minAbs = -1
            # parse 5:00 am, 12:00 p.m., etc
        elif word[0].isdigit():
            isTime = True
            strHH = ""
            strMM = ""
            timeQualifier = ""
            remainder = ""
            if ':' in word:
                # parse colons
                # "3:00 in the morning"
                stage = 0
                length = len(word)
                for i in range(length):
                    if stage == 0:
                        if word[i].isdigit():
                            strHH += word[i]
                        elif word[i] == ":":
                            stage = 1
                        else:
                            stage = 2
                            i -= 1
                    elif stage == 1:
                        if word[i].isdigit():
                            strMM += word[i]
                        else:
                            stage = 2
                            i -= 1
                    elif stage == 2:
                        remainder = word[i:].replace(".", "")
                        break
                if remainder == "":
                    nextWord = wordNext.replace(".", "")
                    if nextWord in eveningQualifiers:
                        used += 1
                        timeQualifier = "pm"
                    elif nextWord in timeQualifiersList:
                        used += 1
                        timeQualifier = "am"
            else:
                # try to parse # s without colons
                # 5 hours, 10 minutes etc.
                length = len(word)
                strNum = ""
                remainder = ""
                for i in range(length):
                    if word[i].isdigit():
                        strNum += word[i]
                    else:
                        remainder += word[i]

                if remainder == "":
                    timeQualifier = wordNext.replace(".", "").lstrip().rstrip()

                if (
                        remainder == "pm" or
                        wordNext == "pm" or
                        remainder == "p.m." or
                        wordNext == "p.m."):
                    strHH = strNum
                    timeQualifier = "pm"
                    used = 1
                elif (
                        remainder == "am" or
                        wordNext == "am" or
                        remainder == "a.m." or
                        wordNext == "a.m."):
                    strHH = strNum
                    timeQualifier = "am"
                    used = 1
                else:
                    if wordNext[:6] == "stunde" and len(wordNext) <= 7:
                        # "in 3 hours"
                        hrOffset = is_number_de(word) or 1 
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif wordNext[:6] == "minute" and len(wordNext) <= 7:
                        # "in 10 minutes"
                        minOffset = is_number_de(word) or 1
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif wordNext[:7] == "sekunde" and len(wordNext) <= 8:
                        # in 5 seconds
                        secOffset = is_number_de(word) or 1
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1

                    elif wordNext == "uhr":
                        strHH = word
                        used += 1
                        isTime = True
                        if wordNextNext in timeQualifiersList:
                            strMM = ""
                            if wordNextNext[:10] == "nachmittag":
                                used += 1
                                timeQualifier = "pm"
                            elif wordNextNext == "am" and wordNextNextNext == \
                                    "nachmittag":
                                used += 2
                                timeQualifier = "pm"
                            elif wordNextNext[:5] == "abend":
                                used += 1
                                timeQualifier = "pm"
                            elif wordNextNext == "am" and wordNextNextNext == \
                                    "abend":
                                used += 2
                                timeQualifier = "pm"
                            elif wordNextNext[:7] == "morgens":
                                used += 1
                                timeQualifier = "am"
                            elif wordNextNext == "am" and wordNextNextNext == \
                                    "morgen":
                                used += 2
                                timeQualifier = "am"
                            elif wordNextNext[:5] == "nacht":
                                used += 1
                                if 8 <= int(word) <= 12:
                                    timeQualifier = "pm"
                                else:
                                    timeQualifier = "am"

                        elif is_numeric_de(wordNextNext):
                            strMM = wordNextNext
                            used += 1
                            if wordNextNextNext == timeQualifier:
                                if wordNextNextNext[:10] == "nachmittag":
                                    used += 1
                                    timeQualifier = "pm"
                                elif wordNextNextNext == "am" and \
                                        wordNextNextNextNext == "nachmittag":
                                    used += 2
                                    timeQualifier = "pm"
                                elif wordNextNextNext[:5] == "abend":
                                    used += 1
                                    timeQualifier = "pm"
                                elif wordNextNextNext == "am" and \
                                        wordNextNextNextNext == "abend":
                                    used += 2
                                    timeQualifier = "pm"
                                elif wordNextNextNext[:7] == "morgens":
                                    used += 1
                                    timeQualifier = "am"
                                elif wordNextNextNext == "am" and \
                                        wordNextNextNextNext == "morgen":
                                    used += 2
                                    timeQualifier = "am"
                                elif wordNextNextNext == "nachts":
                                    used += 1
                                    if 8 <= int(word) <= 12:
                                        timeQualifier = "pm"
                                    else:
                                        timeQualifier = "am"

                    elif wordNext in timeQualifiersList:
                        strHH = word
                        strMM = 00
                        isTime = True
                        if wordNext[:10] == "nachmittag":
                            used += 1
                            timeQualifier = "pm"
                        elif wordNext == "am" and wordNextNext == "nachmittag":
                            used += 2
                            timeQualifier = "pm"
                        elif wordNext[:5] == "abend":
                            used += 1
                            timeQualifier = "pm"
                        elif wordNext == "am" and wordNextNext == "abend":
                            used += 2
                            timeQualifier = "pm"
                        elif wordNext[:7] == "morgens":
                            used += 1
                            timeQualifier = "am"
                        elif wordNext == "am" and wordNextNext == "morgen":
                            used += 2
                            timeQualifier = "am"
                        elif wordNext == "nachts":
                            used += 1
                            if 8 <= int(word) <= 12:
                                timeQualifier = "pm"
                            else:
                                timeQualifier = "am"

                # if timeQualifier != "":
                #     military = True
                # else:
                #     isTime = False

            strHH = int(strHH) if strHH else 0
            strMM = int(strMM) if strMM else 0
            if timeQualifier != "":
                if strHH <= 12 and timeQualifier == "pm" and not \
                    (strHH == 12 and any([q in words for q in ("pm", "p.m.")])):
                    if strHH == 12:
                        strHH = 0
                        dayOffset +=1
                    else:
                        strHH += 12
            if strHH > 24 or strMM > 59:
                isTime = False
                used = 0
            if isTime:
                hrAbs = strHH * 1
                minAbs = strMM * 1
                used += 1
        if used > 0:
            # removed parsed words from the sentence
            for i in range(used):
                words[idx + i] = ""

            if wordPrev == "Uhr":
                words[words.index(wordPrev)] = ""

            if wordPrev == "früh":
                hrOffset = -1
                words[idx - 1] = ""
                idx -= 1
            elif wordPrev == "spät":
                hrOffset = 1
                words[idx - 1] = ""
                idx -= 1
            if idx > 0 and wordPrev in markers:
                words[idx - 1] = ""
            if idx > 1 and wordPrevPrev in markers:
                words[idx - 2] = ""

            idx += used - 1
            found = True

    # check that we found a date
    if not date_found():
        return None

    if dayOffset is False:
        dayOffset = 0

    # perform date manipulation

    extractedDate = dateNow
    extractedDate = extractedDate.replace(microsecond=0,
                                          second=0,
                                          minute=0,
                                          hour=0)
    if datestr != "":
        en_months = ['january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november',
                     'december']
        en_monthsShort = ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july',
                          'aug',
                          'sept', 'oct', 'nov', 'dec']
        for idx, en_month in enumerate(en_months):
            datestr = datestr.replace(months[idx], en_month)
        for idx, en_month in enumerate(en_monthsShort):
            datestr = datestr.replace(monthsShort[idx], en_month)

        temp = datetime.strptime(datestr, "%B %d")
        if extractedDate.tzinfo:
            temp = temp.replace(tzinfo=extractedDate.tzinfo)

        if not hasYear:
            temp = temp.replace(year=extractedDate.year)
            if extractedDate < temp:
                extractedDate = extractedDate.replace(year=int(currentYear),
                                                      month=int(
                                                          temp.strftime(
                                                              "%m")),
                                                      day=int(temp.strftime(
                                                          "%d")))
            else:
                extractedDate = extractedDate.replace(
                    year=int(currentYear) + 1,
                    month=int(temp.strftime("%m")),
                    day=int(temp.strftime("%d")))
        else:
            extractedDate = extractedDate.replace(
                year=int(temp.strftime("%Y")),
                month=int(temp.strftime("%m")),
                day=int(temp.strftime("%d")))

    if timeStr != "":
        temp = datetime(timeStr)
        extractedDate = extractedDate.replace(hour=temp.strftime("%H"),
                                              minute=temp.strftime("%M"),
                                              second=temp.strftime("%S"))

    if yearOffset != 0:
        extractedDate = extractedDate + relativedelta(years=yearOffset)
    if monthOffset != 0:
        extractedDate = extractedDate + relativedelta(months=monthOffset)
    if dayOffset != 0:
        extractedDate = extractedDate + relativedelta(days=dayOffset)

    if hrAbs is None and minAbs is None and default_time:
        hrAbs = default_time.hour
        minAbs = default_time.minute

    if hrAbs != -1 and minAbs != -1:

        extractedDate = extractedDate + relativedelta(hours=hrAbs or 0,
                                                      minutes=minAbs or 0)
        if (hrAbs or minAbs) and datestr == "":
            if not daySpecified and dateNow > extractedDate:
                extractedDate = extractedDate + relativedelta(days=1)
    if hrOffset != 0:
        extractedDate = extractedDate + relativedelta(hours=hrOffset)
    if minOffset != 0:
        extractedDate = extractedDate + relativedelta(minutes=minOffset)
    if secOffset != 0:
        extractedDate = extractedDate + relativedelta(seconds=secOffset)
    for idx, word in enumerate(words):
        if words[idx] == "und" and words[idx - 1] == "" \
                and words[idx + 1] == "":
            words[idx] = ""

    resultStr = " ".join(words)
    resultStr = ' '.join(resultStr.split())

    return [extractedDate, resultStr]


def is_fractional_de(input_str, short_scale=False):
    """
    This function takes the given text and checks if it is a fraction.
    Args:
        input_str (str): the string to check if fractional
        short_scale (bool): use short scale if True, long scale if False
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction
    """
    # account for different numerators, e.g. zweidrittel

    input_str = input_str.lower()
    numerator = 1
    prev_number = 0
    denominator = False
    remainder = ""

    # first check if is a fraction containing a char (eg "2/3")
    _bucket = input_str.split('/')
    if look_for_fractions(_bucket):
        numerator = float(_bucket[0])
        denominator = float(_bucket[1])

    if not denominator:
        for fraction in sorted(_STRING_FRACTION.keys(),
                               key=lambda x: len(x),
                               reverse=True):
            if fraction in input_str and not denominator:
                denominator = _STRING_FRACTION.get(fraction)
                remainder = input_str.replace(fraction, "")
                break

        if remainder:
            if not _STRING_NUM.get(remainder, False):
                #acount for eineindrittel
                for numstring, number in _STRING_NUM.items():
                    if remainder.endswith(numstring):
                        prev_number = _STRING_NUM.get(
                            remainder.replace(numstring, "", 1), 0)
                        numerator = number
                        break
                else:
                    return False
            else:
                numerator = _STRING_NUM.get(remainder)

    if denominator:
        return prev_number + (numerator / denominator)
    else:
        return False


def is_ordinal_de(input_str):
    """
    This function takes the given text and checks if it is an ordinal number.
    Args:
        input_str (str): the string to check if ordinal
    Returns:
        (bool) or (float): False if not an ordinal, otherwise the number
        corresponding to the ordinal
    ordinals for 1, 3, 7 and 8 are irregular
    only works for ordinals corresponding to the numbers in _STRING_NUM
    """
    val = _STRING_LONG_ORDINAL.get(input_str.lower(), False)
    # account for numbered ordinals
    if not val and input_str.endswith('.') and is_numeric_de(input_str[:-1]):
        val = input_str
    return val


def _get_ordinal_index(input_str : str, type_: type = str):
    ord = is_ordinal_de(input_str)
    return type_(ord.replace(".","")) if ord else ord


def is_number_de(word: str):
        if is_numeric_de(word):
            if word.isdigit():
                return int(word)
            else:
                return float(word)
        elif word in _STRING_NUM:
            return _STRING_NUM.get(word)
        elif word in _STRING_LONG_SCALE:
            return _STRING_LONG_SCALE.get(word)
        
        return None

def is_numeric_de(input_str):
    """
    Takes in a string and tests to see if it is a number.

    Args:
        text (str): string to test if a number
    Returns:
        (bool): True if a number, else False
    """
    # da float("1.") = 1.0
    if input_str.endswith('.'):
        return False
    try:
        float(input_str)
        return True
    except ValueError:
        return False



def extract_numbers_de(text, short_scale=True, ordinals=False):
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
    results = _extract_numbers_with_text_de(tokenize(text),
                                            short_scale, ordinals)
    # note: ordinal values return in form of "1." (castable into float)
    values = [float(result.value) for result in results]
    for i, val in enumerate(values):
        if val.is_integer():
            values[i] = int(val)
    
    return values


def extract_number_de(text, short_scale=True, ordinals=False):
    """
    This function extracts a number from a text string

    Args:
        text (str): the string to normalize
        short_scale (bool): use short scale if True, long scale if False
        ordinals (bool): consider ordinal numbers
    Returns:
        (int) or (float) or False: The extracted number or False if no number
                                   was found

    """
    numbers = _extract_numbers_with_text_de(tokenize(text.lower()),
                                            short_scale, ordinals)
    # if query ordinals only consider ordinals
    if ordinals:
        numbers = list(filter(lambda x: isinstance(x.value, str) 
                                        and x.value.endswith("."),
                              numbers))

    number = numbers[0].value if numbers else None

    if number:
        number = float(number)
        if number.is_integer():
            number = int(number)

    return number


class GermanNormalizer(Normalizer):
    with open(resolve_resource_file("text/de-de/normalize.json")) as f:
        _default_config = json.load(f)


def normalize_de(text, remove_articles=True):
    return GermanNormalizer().normalize(text, remove_articles)
