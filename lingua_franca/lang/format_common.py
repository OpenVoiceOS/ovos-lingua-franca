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
import enum


class PluralCategory(str, enum.Enum):
    """
    plural category for the specified amount. Category can be one of
    the categories specified by Unicode CLDR Plural Rules.

    For more details:
    http://cldr.unicode.org/index/cldr-spec/plural-rules
    https://unicode-org.github.io/cldr-staging/charts/37/supplemental/language_plural_rules.html

    """
    CARDINAL = "cardinal"
    ORDINAL = "ordinal"
    RANGE = "range"


class PluralAmount(str, enum.Enum):
    """
    For more details:
    http://cldr.unicode.org/index/cldr-spec/plural-rules
    https://unicode-org.github.io/cldr-staging/charts/37/supplemental/language_plural_rules.html
    """
    ZERO = "zero"
    ONE = "one"
    TWO = "two"
    FEW = "few"
    MANY = "many"
    OTHER = "other"


def convert_to_mixed_fraction(number, denominators=range(1, 21)):
    """
    Convert floats to components of a mixed fraction representation

    Returns the closest fractional representation using the
    provided denominators.  For example, 4.500002 would become
    the whole number 4, the numerator 1 and the denominator 2

    Args:
        number (float): number for convert
        denominators (iter of ints): denominators to use, default [1 .. 20]
    Returns:
        whole, numerator, denominator (int): Integers of the mixed fraction
    """
    int_number = int(number)
    if int_number == number:
        return int_number, 0, 1  # whole number, no fraction

    frac_number = abs(number - int_number)
    if not denominators:
        denominators = range(1, 21)

    for denominator in denominators:
        numerator = abs(frac_number) * denominator
        if abs(numerator - round(numerator)) < 0.01:  # 0.01 accuracy
            break
    else:
        return None

    return int_number, int(round(numerator)), denominator
