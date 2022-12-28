import re
from colorsys import rgb_to_yiq, yiq_to_rgb, rgb_to_hls, hls_to_rgb, \
    rgb_to_hsv, hsv_to_rgb

from colour import Color as _Color
from webcolors import name_to_rgb, rgb_to_name, \
    hex_to_rgb

from lingua_franca.internal import get_default_lang


def hsv_to_name(h, s, v):
    rgb = hsv_to_rgb(h, s, v)
    return rgb_to_name(rgb)


def name_to_hsv(name):
    r, g, b = name_to_rgb(name)
    return rgb_to_hsv(r, g, b)


def hex_to_hsv(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    h, s, v = rgb_to_hsv(r, g, b)
    return h, s, v


class UnrecognizedColorName(ValueError):
    """ No color defined with this name """


class Color(_Color):
    """ A well defined Color, just the way computers love colors"""

    @property
    def name(self):
        if self.web != self.hex:
            # Split camel case string
            regex = '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)'
            matches = re.finditer(regex, self.web)
            return ' '.join([m.group(0) for m in matches])
        return None

    @staticmethod
    def from_description(text, lang=None):
        from lingua_franca.parse import get_color
        lang = lang or get_default_lang()
        return get_color(text, lang)

    @property
    def main_color(self):
        """
        reduce to 1 color of the following:
        - grey
        - black
        - white
        - orange
        - yellow
        - green
        - cyan
        - blue
        - violet
        - red
        """
        if self.saturation <= 0.3:
            return Color("grey")
        if self.luminance <= 0.15:
            return Color("black")
        elif self.luminance >= 0.85:
            return Color("white")

        thresh = 0.5
        orange = 0.10
        yellow = 0.16
        green = 0.33
        cyan = 0.5
        blue = 0.66
        violet = 0.83

        if orange - thresh <= self.hue <= orange + thresh:
            return Color("orange")
        elif yellow - thresh <= self.hue <= yellow + thresh:
            return Color("yellow")
        elif green - thresh <= self.hue <= green + thresh:
            return Color("green")
        elif cyan - thresh <= self.hue <= cyan + thresh:
            return Color("cyan")
        elif blue - thresh <= self.hue <= blue + thresh:
            return Color("blue")
        elif violet - thresh <= self.hue <= violet + thresh:
            return Color("violet")
        else:
            return Color("red")

    def get_description(self, lang=None):
        from lingua_franca.format import describe_color
        lang = lang or get_default_lang()
        return describe_color(self, lang)

    #### HEX ####
    @staticmethod
    def from_hex(hex_value):
        return Color(hex_value)

    #### RGB ####
    @property
    def rgb255(self):
        return (int(self.red * 255),
                int(self.green * 255),
                int(self.blue * 255))

    def rgb_percent(self):
        return self.rgb

    @staticmethod
    def from_rgb(r, g, b):
        return Color(rgb=(r / 255, g / 255, b / 255))

    @staticmethod
    def from_rgb_percent(r, g, b):
        if isinstance(r, str) or isinstance(g, str) or isinstance(b, str):
            r = float(r.replace("%", ""))
            g = float(g.replace("%", ""))
            b = float(b.replace("%", ""))
        return Color(rgb=(r, g, b))

    #### HSV ####
    @staticmethod
    def from_hsv(h, s, v):
        r, g, b = hsv_to_rgb(h, s, v)
        return Color.from_rgb(r, g, b)

    @property
    def hsv(self):
        return rgb_to_hsv(self.red, self.green, self.blue)

    #### HLS ####
    @staticmethod
    def from_hls(h, l, s):
        r, g, b = hls_to_rgb(h, l, s)
        return Color.from_rgb(r, g, b)

    @property
    def hls(self):
        return rgb_to_hls(self.red, self.green, self.blue)

    #### YIQ ####
    @staticmethod
    def from_yiq(y, i, q):
        r, g, b = yiq_to_rgb(y, i, q)
        return Color.from_rgb(r, g, b)

    @property
    def yiq(self):
        return rgb_to_yiq(self.red, self.green, self.blue)

    def __str__(self):
        return self.hex_l


class ColorOutOfSpace(Color):
    """ Some Human described this color, but humans suck at this"""

    @property
    def name(self):
        # H.P. Lovecraft - https://www.youtube.com/watch?v=4liRxrDzS5I
        # return "The Color Out of Space"
        return self.hex
