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
from lingua_franca.util import match_one, fuzzy_match, MatchStrategy
from lingua_franca.lang.parse_common import match_yes_or_no
from difflib import SequenceMatcher
from warnings import warn
from lingua_franca.time import now_local
from lingua_franca.internal import populate_localized_function_dict, \
    get_active_langs, get_full_lang_code, get_primary_lang_code, \
    get_default_lang, localized_function, _raise_unsupported_language, UnsupportedLanguageError,\
    resolve_resource_file, FunctionNotLocalizedError
import unicodedata
from lingua_franca.lang.parse_common import DurationResolution
from lingua_franca.location import Hemisphere, get_active_hemisphere, \
    get_active_location, get_active_location_code

import dateparser
from dateparser.search import search_dates


_REGISTERED_FUNCTIONS = ("extract_numbers",
                         "extract_number",
                         "extract_duration",
                         "extract_datetime",
                         "extract_langcode",
                         "normalize",
                         "get_gender",
                         "yes_or_no",
                         "is_fractional",
                         "is_ordinal")

populate_localized_function_dict("parse", langs=get_active_langs())


@localized_function(run_own_code_on=[FunctionNotLocalizedError])
def yes_or_no(text, lang=""):
    text = normalize(text, lang=lang, remove_articles=True).lower()
    return match_yes_or_no(text, lang)


@localized_function(run_own_code_on=[UnsupportedLanguageError, FunctionNotLocalizedError])
def extract_langcode(text, lang=""):
    resource_file = resolve_resource_file(f"text/{lang}/langs.json") or \
                    resolve_resource_file("text/en-us/langs.json")
    with open(resource_file) as f:
        LANGUAGES = {v: k for k, v in json.load(f).items()}
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


def extract_calendar_duration(text, lang="", replace_token=""):
    """
    Equivalent to extract_duration with

        resolution=DurationResolution.RELATIVEDELTA_FALLBACK

     Args:
        text (str): string containing a duration
        lang (str): the BCP-47 code for the language to use, None uses default
        replace_token (str): string to replace consumed words with

    Returns:
        (relativedelta, str):
                    A tuple containing the duration and the remaining text
                    not consumed in the parsing. The first value will
                    be None if no duration is found. The text returned
                    will have whitespace stripped from the ends.

    """
    return extract_duration(text, lang,
                            DurationResolution.RELATIVEDELTA_FALLBACK,
                            replace_token)

@localized_function()
def extract_duration(text, lang='',
                     resolution=DurationResolution.TIMEDELTA,
                     replace_token=""):
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
        resolution (DurationResolution): format to return extracted duration on
        replace_token (str): string to replace consumed words with

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
    # hard-parse, fallback to dateparser
    # this brings "free support" for many languages
    print("No dates found, falling back to strict parser")
    _dates = search_dates(text, languages=[lang_code],
                          settings={'RELATIVE_BASE': anchorDate,
                                    'STRICT_PARSING': True})
    if _dates is not None:
        # return first datetime only
        # TODO extract_datetimes
        # TODO extract_datetime_range
        date_str, extracted_date = _dates[0]
        remainder = text.replace(date_str, "")
        return extracted_date, remainder

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


@localized_function()
def extract_date(text, anchor_date=None, lang="", location=None):
    """
    Extracts date information from a sentence.  Parses many of the
    common ways that humans express dates, including relative dates
    like "5 days from today", "tomorrow', and "Tuesday".

    Vague terminology are given arbitrary values, accounting for
    geographic location, like:
        - summer = XXX
        - spring = XXX
        - winter = XXX

    Args:
        text (str): the text to be interpreted
        anchor_date (:obj:`datetime`, optional): the date to be used for
            relative dating (for example, what does "tomorrow" mean?).
            Defaults to the current local date/time.
        lang (str): the BCP-47 code for the language to use, None uses default
        location (str, float, float): ISO code, lat, lon of reference
            location, used for holidays and seasons

    Returns:
        [:obj:`date`, :obj:`str`]: 'date' is the extracted date
            as a date object in the user's local timezone.
            'leftover_string' is the original phrase with all date
            related keywords stripped out. See examples for further
            clarification

            Returns 'None' if no date related text is found.

    Examples:

        >>> extract_date(
        ... "What is the weather like the day after tomorrow?",
        ... date(2017, 06, 30)
        ... )
        [datetime.date(2017, 7, 2), 'what is weather like']

        >>> extract_date(
        ... "Set up an appointment 2 weeks from Sunday",
        ... date(2016, 02, 19)
        ... )
        [datetime.datetime(2016, 3, 6), 'set up appointment']

        >>> extract_date(
        ... "Set up an appointment",
        ... date(2016, 02, 19)
        ... )
        None
    """

    lang_code = get_primary_lang_code(lang)

    if not anchor_date:
        anchor_date = now_local()

    if location is not None:
        code, lat, lon = location
    else:
        code = get_active_location_code()
        lat, lon = get_active_location()

    if lat < 0:
        hemisphere = Hemisphere.SOUTH
    else:
        hemisphere = Hemisphere.NORTH

    if lang_code == "en":
        extracted_date = extract_date_en(text, anchor_date,
                                         hemisphere=hemisphere,
                                         location_code=code)
    else:
        extracted_date = None
        # TODO: extract_date for other languages
        _log_unsupported_language(lang_code, ['en'])

    if extracted_date is None:
        # hard-parse, fallback to dateparser
        # this brings "free support" for many languages
        print("No dates found, falling back to strict parser")
        _dates = search_dates(text, languages=[lang_code],
                              settings={'RELATIVE_BASE': anchor_date,
                                        'STRICT_PARSING': True})
        if _dates:
            # return first date only
            # TODO extract_dates
            # TODO extract_date_range
            date_str, extracted_datetime = _dates[0]
            remainder = text.replace(date_str, "")
            extracted_date = extracted_datetime.date()

    return extracted_date


@localized_function()
def extract_time(text, anchor_date=None, lang="", location=None):
    """
    Extracts date information from a sentence.  Parses many of the
    common ways that humans express dates, including relative dates
   "tomorrow morning', and "Tuesday evening".

    Vague terminology are given arbitrary values, accounting for
    geographic location (timezones), like:
        TODO

    Args:
        text (str): the text to be interpreted
        anchor_date (:obj:`datetime`, optional): the date to be used for
            relative dating (for example, what does "tomorrow" mean?).
            Defaults to the current local date/time.
        lang (str): the BCP-47 code for the language to use, None uses default
        location (str, float, float): ISO code, lat, lon of reference
            location, used for holidays and seasons

    Returns:
        [:obj:`time`, :obj:`str`]: 'time' is the extracted time
            as a time object in the user's local timezone or parsed timezone.
            'leftover_string' is the original phrase with all date
            related keywords stripped out. See examples for further
            clarification

            Returns 'None' if no time related text is found.

    Examples:

        TODO
    """

    lang_code = get_primary_lang_code(lang)

    if not anchor_date:
        anchor_date = now_local()

    if location is not None:
        code, lat, lon = location
    else:
        code = get_active_location_code()
        lat, lon = get_active_location()

    if True:  # TODO parsers per language
        extracted_time = None
        _log_unsupported_language(lang_code, [])

    if extracted_time is None:
        # hard-parse, fallback to dateparser
        # this brings "free support" for many languages
        print("No times found, falling back to strict parser")
        _dates = search_dates(text, languages=[lang_code],
                              settings={'RELATIVE_BASE': anchor_date})
        if len(_dates) > 0:
            date_str, extracted_datetime = _dates[0]
            remainder = text.replace(date_str, "")
            extracted_time = extracted_datetime.time()

    return extracted_time


@localized_function()
def get_named_dates(anchor_date=None, lang="", location=None):
    """
    returns dict of {"name": date} for named dates
     NOTE: Dates are set in anchor_date.year
     """
    if anchor_date:
        year = anchor_date.year
    else:
        year = now_local().year

    if location is not None:
        location_code, lat, lon = location
    else:
        location_code = get_active_location_code()

    lang_code = get_primary_lang_code(lang)

    if lang_code == "en":
        return get_named_dates_en(location_code, year)

    # TODO: get_named_dates for other languages
    _log_unsupported_language(lang_code, ['en'])

    return {}


@localized_function()
def get_named_eras(lang="", location=None):
    """ returns dict of {"era_name": date} for named eras
    NOTE: an era is simply a reference date
    """
    lang_code = get_primary_lang_code(lang)

    if location is not None:
        location_code, lat, lon = location
    else:
        location_code = get_active_location_code()

    if lang_code == "en":
        return get_named_eras_en(location_code)
    return {"anno domini": date(day=1, month=1, year=1)}
