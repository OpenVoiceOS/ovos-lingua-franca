#
# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json

from quebra_frases import span_indexed_word_tokenize

from lingua_franca.internal import populate_localized_function_dict, \
    get_active_langs, localized_function, UnsupportedLanguageError, \
    resolve_resource_file, FunctionNotLocalizedError, get_full_lang_code
from lingua_franca.lang.parse_common import match_yes_or_no
from lingua_franca.util import match_one, fuzzy_match, MatchStrategy
from lingua_franca.util.colors import Color, ColorOutOfSpace

_REGISTERED_FUNCTIONS = ("extract_numbers",
                         "extract_number",
                         "extract_duration",
                         "extract_datetime",
                         "extract_langcode",
                         "normalize",
                         "get_gender",
                         "yes_or_no",
                         "is_fractional",
                         "extract_color_spans",
                         "get_color",
                         "is_ordinal")

populate_localized_function_dict("parse", langs=get_active_langs())


@localized_function(run_own_code_on=[FunctionNotLocalizedError])
def get_color(text, lang=''):
    """
        Given a color description, return a Color object

        Args:
            text (str): the string describing a color
            lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
        Returns:
            (list): list of tuples with detected color and span of the
                    color in parent utterance [(Color, (start_idx, end_idx))]
        """
    lang = get_full_lang_code(lang)
    resource_file = resolve_resource_file(f"text/{lang}/colors.json") or \
                    resolve_resource_file("text/webcolors.json")
    with open(resource_file) as f:
        COLORS = {v.lower(): k for k, v in json.load(f).items()}

    text = text.lower().strip()
    if text in COLORS:
        return Color.from_hex(COLORS[text])

    spans = extract_color_spans(text, lang)
    if spans:
        return spans[0][0]
    return ColorOutOfSpace()


@localized_function(run_own_code_on=[FunctionNotLocalizedError])
def extract_color_spans(text, lang=''):
    """
        This function tags colors in an utterance.
        Args:
            text (str): the string to extract colors from
            lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
        Returns:
            (list): list of tuples with detected color and span of the
                    color in parent utterance [(Color, (start_idx, end_idx))]
        """
    lang = get_full_lang_code(lang)
    resource_file = resolve_resource_file(f"text/{lang}/colors.json") or \
                    resolve_resource_file("text/webcolors.json")
    with open(resource_file) as f:
        COLORS = {v.lower(): k for k, v in json.load(f).items()}

    color_spans = []
    text = text.lower()
    spans = span_indexed_word_tokenize(text)

    for idx, (start, end, word) in enumerate(spans):
        next_span = spans[idx + 1] if idx + 1 < len(spans) else ()
        next_next_span = spans[idx + 2] if idx + 2 < len(spans) else ()
        word2 = word3 = ""
        if next_next_span:
            word3 = f"{word} {next_span[-1]} {next_next_span[-1]}"
        if next_span:
            word2 = f"{word} {next_span[-1]}"

        if next_span and next_next_span and word3 in COLORS:
            spans[idx + 1] = spans[idx + 2] = (-1, -1, "")
            end = next_next_span[1]
            color = Color.from_hex(COLORS[word3])
            color_spans.append((color, (start, end)))
        elif next_span and word2 in COLORS:
            spans[idx + 1] = (-1, -1, "")
            end = next_span[1]
            color = Color.from_hex(COLORS[word2])
            color_spans.append((color, (start, end)))
        elif word in COLORS:
            color = Color.from_hex(COLORS[word])
            color_spans.append((color, (start, end)))

    return color_spans


@localized_function(run_own_code_on=[FunctionNotLocalizedError])
def yes_or_no(text, lang=""):
    text = normalize(text, lang=lang, remove_articles=True).lower()
    return match_yes_or_no(text, lang)


# TODO - variant kwarg - ISO 639-2 vs ISO 639-1
@localized_function(run_own_code_on=[UnsupportedLanguageError, FunctionNotLocalizedError])
def extract_langcode(text, lang=""):
    lang = get_full_lang_code(lang)
    resource_file = resolve_resource_file(f"text/{lang}/langs.json") or \
                    resolve_resource_file("text/en-us/langs.json")
    LANGUAGES = {}
    with open(resource_file) as f:
        for k, v in json.load(f).items():
            if isinstance(v, str):
                v = [v]
            # list of spoken names for this language
            # multiple valid spellings may exist
            for l in v:
                LANGUAGES[l] = k
    return match_one(text, LANGUAGES, strategy=MatchStrategy.TOKEN_SET_RATIO)


@localized_function()
def extract_numbers(text, short_scale=True, ordinals=False, lang=''):
    """
        Takes in a string and extracts a list of numbers.

    Args:
        text (str): the string to extract a number from
        short_scale (bool): Use "short scale" or "long scale" for large
            numbers -- over a million.  The default is short scale, which
            is now common in most English speaking countries.
            See https://en.wikipedia.org/wiki/Names_of_large_numbers
        ordinals (bool): consider ordinal numbers, e.g. third=3 instead of 1/3
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
    Returns:
        list: list of extracted numbers as floats, or empty list if none found
    """


@localized_function()
def extract_number(text, short_scale=True, ordinals=False, lang=''):
    """Takes in a string and extracts a number.

    Args:
        text (str): the string to extract a number from
        short_scale (bool): Use "short scale" or "long scale" for large
            numbers -- over a million.  The default is short scale, which
            is now common in most English speaking countries.
            See https://en.wikipedia.org/wiki/Names_of_large_numbers
        ordinals (bool): consider ordinal numbers, e.g. third=3 instead of 1/3
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
    Returns:
        (int, float or False): The number extracted or False if the input
                               text contains no numbers
    """


@localized_function()
def extract_duration(text, lang=''):
    """ Convert an english phrase into a number of seconds

    Convert things like:

    * "10 minute"
    * "2 and a half hours"
    * "3 days 8 hours 10 minutes and 49 seconds"

    into an int, representing the total number of seconds.

    The words used in the duration will be consumed, and
    the remainder returned.

    As an example, "set a timer for 5 minutes" would return
    ``(300, "set a timer for")``.

    Args:
        text (str): string containing a duration
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.

    Returns:
        (timedelta, str):
                    A tuple containing the duration and the remaining text
                    not consumed in the parsing. The first value will
                    be None if no duration is found. The text returned
                    will have whitespace stripped from the ends.
    """


@localized_function()
def extract_datetime(text, anchorDate=None, lang='', default_time=None):
    """
    Extracts date and time information from a sentence.  Parses many of the
    common ways that humans express dates and times, including relative dates
    like "5 days from today", "tomorrow', and "Tuesday".

    Vague terminology are given arbitrary values, like:
        - morning = 8 AM
        - afternoon = 3 PM
        - evening = 7 PM

    If a time isn't supplied or implied, the function defaults to 12 AM

    Args:
        text (str): the text to be interpreted
        anchorDate (:obj:`datetime`, optional): the date to be used for
            relative dating (for example, what does "tomorrow" mean?).
            Defaults to the current local date/time.
        lang (str): the BCP-47 code for the language to use, None uses default
        default_time (datetime.time): time to use if none was found in
            the input string.

    Returns:
        [:obj:`datetime`, :obj:`str`]: 'datetime' is the extracted date
            as a datetime object in the local timezone.
            'leftover_string' is the original phrase with all date and time
            related keywords stripped out. See examples for further
            clarification

            Returns 'None' if no date or time related text is found.

    Examples:

        >>> extract_datetime(
        ... "What is the weather like the day after tomorrow?",
        ... datetime(2017, 6, 30, 00, 00)
        ... )
        [datetime.datetime(2017, 7, 2, 0, 0), 'what is weather like']

        >>> extract_datetime(
        ... "Set up an appointment 2 weeks from Sunday at 5 pm",
        ... datetime(2016, 2, 19, 00, 00)
        ... )
        [datetime.datetime(2016, 3, 6, 17, 0), 'set up appointment']

        >>> extract_datetime(
        ... "Set up an appointment",
        ... datetime(2016, 2, 19, 00, 00)
        ... )
        None
    """


@localized_function()
def normalize(text, lang='', remove_articles=True):
    """Prepare a string for parsing

    This function prepares the given text for parsing by making
    numbers consistent, getting rid of contractions, etc.

    Args:
        text (str): the string to normalize
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
        remove_articles (bool): whether to remove articles (like 'a', or
                                'the'). True by default.

    Returns:
        (str): The normalized string.
    """


@localized_function()
def get_gender(word, context="", lang=''):
    """ Guess the gender of a word

    Some languages assign genders to specific words.  This method will attempt
    to determine the gender, optionally using the provided context sentence.

    Args:
        word (str): The word to look up
        context (str, optional): String containing word, for context
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.

    Returns:
        str: The code "m" (male), "f" (female) or "n" (neutral) for the gender,
             or None if unknown/or unused in the given language.
    """


@localized_function()
def is_fractional(input_str, short_scale=True, lang=''):
    """
    This function takes the given text and checks if it is a fraction.
    Used by most of the number exractors.

    Will return False on phrases that *contain* a fraction. Only detects
    exact matches. To pull a fraction from a string, see extract_number()

    Args:
        input_str (str): the string to check if fractional
        short_scale (bool): use short scale if True, long scale if False
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction
    """


@localized_function()
def is_ordinal(input_str, lang=''):
    """
    This function takes the given text and checks if it is an ordinal number.

    Args:
        input_str (str): the string to check if ordinal
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
    Returns:
        (bool) or (float): False if not an ordinal, otherwise the number
        corresponding to the ordinal
    """
