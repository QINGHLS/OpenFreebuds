import logging

import PIL.Image
from PIL import Image, ImageDraw

from openfreebuds import event_bus
from openfreebuds_applet.settings import SettingsStorage

ICON_SIZE = (24, 24)


def spawn_color_image(size, color):
    return Image.new("RGBA", size, color=color)


class BaseImages:
    transparent = Image.new("RGBA", ICON_SIZE, color="#00000000")

    light_missing = Image.new("RGBA", ICON_SIZE, color="#FFFFFF22")
    light_empty = Image.new("RGBA", ICON_SIZE, color="#FFFFFF44")
    light_full = Image.new("RGBA", ICON_SIZE, color="#FFFFFFFF")

    dark_missing = Image.new("RGBA", ICON_SIZE, color="#00000022")
    dark_empty = Image.new("RGBA", ICON_SIZE, color="#00000044")
    dark_full = Image.new("RGBA", ICON_SIZE, color="#000000FF")

    theme_missing = light_missing
    theme_full = light_full
    theme_empty = light_empty


def set_theme(theme_name="auto"):
    value = theme_name
    if theme_name == "auto":
        from openfreebuds_applet.platform_tools import is_dark_theme
        value = "dark" if is_dark_theme() else "light"

    if value == "dark":
        BaseImages.theme_missing = BaseImages.light_missing
        BaseImages.theme_full = BaseImages.light_full
        BaseImages.theme_empty = BaseImages.light_empty
    elif value == "light":
        BaseImages.theme_missing = BaseImages.dark_missing
        BaseImages.theme_full = BaseImages.dark_full
        BaseImages.theme_empty = BaseImages.dark_empty
    else:
        raise Exception("Unknown theme value: " + value)

    logging.getLogger("AppletIcons").debug("set theme=" + value)


def spawn_power_bg_mask(level: float):
    img = Image.new("RGBA", ICON_SIZE, color="#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, ICON_SIZE[0],
                    round(ICON_SIZE[1] * (1 - level))), fill="#000000")
    return img


# noinspection PyTypeChecker
def combine_mask(mask, foreground=None, background=None):
    mask = mask.convert("RGBA")
    mask_data = mask.getdata()
    fg_data = foreground.getdata()

    img_data = list()
    for a, mask_pixel in enumerate(mask_data):
        img_data.append((fg_data[a][0], fg_data[a][1], fg_data[a][2],
                         round((fg_data[a][3] / 255) * mask_pixel[0])))

    generated = Image.new("RGBA", mask.size)
    generated.putdata(img_data)

    out = Image.new("RGBA", mask.size)
    out.alpha_composite(background)
    out.alpha_composite(generated)

    return out


def _get_base_device():
    # Generate an image and draw a pattern
    image = Image.new('RGBA', ICON_SIZE, "#000000")
    dc = ImageDraw.Draw(image)
    dc.rectangle((0, 0, ICON_SIZE[0], ICON_SIZE[1]), fill="#FFFFFF")

    return image


def get_icon_offline():
    return combine_mask(_get_base_device(),
                        foreground=BaseImages.theme_missing,
                        background=BaseImages.transparent)


def get_icon_device(battery, noise_mode):
    icon = _get_base_device()

    power_bg = combine_mask(spawn_power_bg_mask(battery / 100),
                            foreground=BaseImages.theme_full,
                            background=BaseImages.theme_empty)
    return combine_mask(icon,
                        foreground=power_bg,
                        background=BaseImages.transparent)
