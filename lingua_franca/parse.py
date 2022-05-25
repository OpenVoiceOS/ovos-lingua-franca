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

from lingua_franca.internal import populate_localized_function_dict, \
    get_active_langs, localized_function, UnsupportedLanguageError, \
    resolve_resource_file, FunctionNotLocalizedError
from lingua_franca.util import match_one, MatchStrategy, fuzzy_match

_REGISTERED_FUNCTIONS = ("extract_numbers",
                         "extract_number",
                         "extract_duration",
                         "extract_datetime",
                         "extract_langcode",
                         "normalize",
                         "get_gender",
                         "is_fractional",
                         "extract_currencycode",
                         "extract_countrycode",
                         "is_ordinal")

populate_localized_function_dict("parse", langs=get_active_langs())


@localized_function(run_own_code_on=[UnsupportedLanguageError, FunctionNotLocalizedError])
def extract_currencycode(text, lang=""):
    # this method tries to be lang agnostic and use mainly fuzzy matching
    # it should be considered a fallback for unimplemented languages
    # dedicated per language implementations wanted!

    # match lang
    l, s = extract_langcode(text, lang=lang)

    # match country data
    resource_file = resolve_resource_file("countries.json")
    with open(resource_file) as f:
        countries = json.load(f)
        best_score = 0
        best_currency = None

        for c in countries:
            if not c["ISO4217-currency_alphabetic_code"]:
                continue
            k = f"official_name_{lang.split('-')[0]}"
            if k in c:
                name = c[k]
            else:
                name = c["official_name_en"]

            # match currency name + country name + country lang
            currency_score = fuzzy_match(text, c["ISO4217-currency_name"], strategy=MatchStrategy.TOKEN_SET_RATIO)
            country_score = fuzzy_match(text, name, strategy=MatchStrategy.TOKEN_SET_RATIO)
            lang_score = 0
            if l in c.get("Language", "").lower():
                # bonus if language is spoken in this country
                lang_score = s * 0.6
                # bonus if country code is part of language code
                if c['ISO3166-1-Alpha-2'].lower() in l:
                    lang_score = s

            score = max([currency_score, country_score]) * 0.8 + 0.2 * lang_score

            if score > best_score:
                best_score = score
                best_currency = c["ISO4217-currency_alphabetic_code"]

    # special corner cases
    if best_score < 0.55:
        # european union
        if "euro" in text.lower() or "€" in text:
            return "EUR", 0.5

    return best_currency, best_score


@localized_function(run_own_code_on=[UnsupportedLanguageError, FunctionNotLocalizedError])
def extract_langcode(text, lang=""):
    resource_file = resolve_resource_file(f"text/{lang}/langs.json") or \
                    resolve_resource_file("text/en-us/langs.json")
    with open(resource_file) as f:
        LANGUAGES = {v: k for k, v in json.load(f).items()}

    best_lang, best_score = match_one(text, LANGUAGES, strategy=MatchStrategy.TOKEN_SET_RATIO)

    # match country names
    if best_score < 0.7:
        resource_file = resolve_resource_file("countries.json")
        with open(resource_file) as f:
            countries = json.load(f)
            for c in countries:
                if "Language" not in c:
                    continue
                k = f"official_name_{lang.split('-')[0]}"
                if k in c:
                    name = c[k]
                else:
                    name = c["official_name_en"]
                score = fuzzy_match(text, name, strategy=MatchStrategy.TOKEN_SET_RATIO)
                if score >= best_score:
                    best_lang, best_score = c["Language"].lower(), score

    return best_lang, best_score


@localized_function(run_own_code_on=[UnsupportedLanguageError, FunctionNotLocalizedError])
def extract_countrycode(text, iso3=False, lang=""):

    resource_file = resolve_resource_file("countries.json")
    with open(resource_file) as f:
        countries = json.load(f)
        best_score = 0
        best_country = None

        for c in countries:
            # if text is a langcode, return parent country
            l = c.get("Language", "").lower()
            if not l:
                lang_score = 0
            elif l == f'{c["ISO3166-1-Alpha-2"]}-{c["ISO3166-1-Alpha-2"]}'.lower() and l in text:
                lang_score = 1.0
            else:
                lang_score = fuzzy_match(text, l, strategy=MatchStrategy.TOKEN_SET_RATIO) * 0.8
                if c["ISO3166-1-Alpha-2"].lower() in l:
                    lang_score += 0.05

            # match country name to text
            k = f"official_name_{lang.split('-')[0]}"
            if k in c:
                name = c[k]
            else:
                name = c["official_name_en"]

            name_score = fuzzy_match(text, name, strategy=MatchStrategy.TOKEN_SET_RATIO)

            if name_score < 0.7 <= lang_score:
                score = lang_score
            elif lang_score < 0.7 <= name_score:
                score = name_score
            else:
                score = 0.5 * name_score + 0.5 * lang_score

            if score >= best_score:
                if iso3:
                    best_country, best_score = c["ISO3166-1-Alpha-3"], score
                else:
                    best_country, best_score = c["ISO3166-1-Alpha-2"], score

    return best_country, best_score


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
