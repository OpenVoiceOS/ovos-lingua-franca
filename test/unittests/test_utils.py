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
from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.util.colors import Color, ColorOutOfSpace


def setUpModule():
    load_language("en")
    set_default_lang('en-us')


def tearDownModule():
    unload_language("en")


class TestColorObject(unittest.TestCase):

    def test_color(self):
        black = Color()
        self.assertEqual(black, Color("black"))

        # NOTE constructor takes the exact web name
        try:
            color = Color("dark green")
        except ValueError:
            color = Color("DarkGreen")

        self.assertEqual(color, color.from_description("dark green"))
        self.assertEqual(color.web, "DarkGreen")
        self.assertEqual(color.name, "Dark Green")

        white = Color.from_description("white")
        self.assertEqual(white, Color.from_rgb(255, 255, 255))

        # color without a defined name
        color = Color.from_rgb(0, 120, 240)
        self.assertTrue(color.name is None)
        # modify
        color.set_saturation(0.3)
        color.set_luminance(0.7)
        desc = "bright blue-ish gray color"
        self.assertEqual(color.get_description("en"), desc)
        self.assertEqual(color.rgb255, (155, 178, 201))

        # special color -> fuzzy from description
        color = Color.from_description("NNNNNNNNNNNNNNNNNN")
        self.assertTrue(isinstance(color, ColorOutOfSpace))
        self.assertNotEqual(color.name, "black")
        self.assertEqual(color.name, color.hex)
        self.assertEqual(color.get_description(), "Black")

        # colors created from description wont match both ways
        aprox_color = Color.from_description(desc)
        self.assertTrue(isinstance(aprox_color, ColorOutOfSpace))
        self.assertEqual(aprox_color.get_description("en"), desc)
        self.assertNotEqual(aprox_color.rgb255, color.rgb255)
        self.assertEqual(aprox_color.rgb255, (159, 160, 197))


if __name__ == "__main__":
    unittest.main()
