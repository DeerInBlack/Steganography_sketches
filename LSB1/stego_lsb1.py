from PIL import Image, ImageDraw
from os import path
import _json


def binary(integer, length=-1):
    """
    Returns bit sequence of binary representation of 'integer' value extended
    with '0' in front to 'length'.
    :param integer: integer value
    :param length: length of bit sequence; '-1' - extend to byte
    :return: bit sequence string
    """
    b = f"{integer:b}"
    ext = 0
    if length == -1:
        ext = (len(b) // 8 + 1 if len(b) % 8 != 0 else 0) * 8
    elif length >= 0:
        ext = length
    b = b.rjust(ext, '0')
    return b


def embed(message_bs, im_path, sparseness=10, greed=2, mod_ch='B'):
    """
    Embeds bit sequence in 'PNG' or 'JPEG' image ('RGB' and 'RGBA' modes only)
    using LSB method and saves it as new image. Also embeds the length of
    given message for not to pluck out useless bit.
    Raises ValueError if image has inappropriate format or mode. Save new image
    in the directory of given image.
    :param message_bs: string with bit sequence to embed
    :param im_path: path to image; raises FileNotFoundError,
    PIL.UnidentifiedImageError if it hasn't been found or open respectively
    :param sparseness: gap between overwritten pixels in both directions
    :param greed: number of overwritten bits (0 - *max_bits_for_channel* else
    raises ValueError)
    :param mod_ch: one or more channels to overwrite, e.g.'R', 'GRB', 'RGBA';
    !order and repetitions affect!
    raises ValueError if there's no such channel
    :return: tuple: (name of stego image, not embedded bits)
    """
    with Image.open(im_path) as image:
        im_format = image.format
        im_mode = image.mode

        for ch in mod_ch:
            if ch not in im_mode:
                raise ValueError("Invalid channel")
        if (im_format != "PNG" and im_format != "JPEG") \
                or (im_mode != 'RGB' and im_mode != 'RGBA'):
            raise ValueError("Not supported format or mode")

        pix = image.load()

        if greed < 0 or greed > len(binary(pix[0, 0][0])):
            raise ValueError("Invalid greed value")

        draw = ImageDraw.Draw(image)
        width, height = image.size

        max_len = (width // sparseness) * \
                  (height // sparseness) * greed * len(mod_ch)
        message_len = len(message_bs)
        max_len_bin = binary(max_len, 0)
        if max_len <= message_len:
            len_info = max_len_bin
        else:
            len_info = binary(message_len, len(max_len_bin))
        message_bs = len_info + message_bs
        if message_len % 3 > 0:
            message_len = len(message_bs)
            message_bs = message_bs.ljust(message_len +
                                          (greed - message_len % greed), '0')

        end_of_message = False
        for x in range(0, width, sparseness):
            for y in range(0, height, sparseness):
                channels = list(pix[x, y])
                for ch in mod_ch.upper():
                    if not message_bs:
                        end_of_message = True
                        break
                    i = im_mode.index(ch)
                    val = binary(channels[i])
                    val = val[:len(val) - greed] + message_bs[:greed]
                    channels[i] = int(val, 2)
                    message_bs = message_bs[greed:]
                draw.point((x, y), tuple(channels))
            if end_of_message:
                break
        new_title = path.splitext(im_path)[0] + "_corrupted.png"
        image.save(new_title, "PNG")
        return new_title, message_bs


def pluck_out(im_path, sparseness=10, greed=2, mod_ch='B'):
    """
    Plucks out sequence of bits of length embedded with the message from PNG
    image ('RGB' and 'RGBA' modes only).
    Raises ValueError if image has inappropriate format or mode.
    :param im_path: path to image; raises FileNotFoundError,
    PIL.UnidentifiedImageError if it hasn't been found or open respectively
    :param sparseness: gap between overwritten pixels in both directions
    :param greed: number of overwritten bits (0 - *max_bits_for_channel* else
    raises ValueError)
    :param mod_ch: one or more channels to overwrite, e.g.'R', 'GRB', 'RGBA';
    !order and repetitions affect!
    raises ValueError if there's no such channel
    :return: sequence of bits
    """
    with Image.open(im_path) as image:
        im_format = image.format
        im_mode = image.mode

        for ch in mod_ch:
            if ch not in im_mode:
                raise ValueError("Invalid channel")

        if im_format != "PNG" or (im_mode != 'RGB' and im_mode != 'RGBA'):
            raise ValueError("Not supported format or mode")

        message_bs = ""
        pix = image.load()

        if greed < 0 or greed > len(binary(pix[0, 0][0])):
            raise ValueError("Invalid greed value")

        width, height = image.size
        max_bits = (width // sparseness) * \
                   (height // sparseness) * greed * len(mod_ch)
        len_info_len = len(binary(max_bits, 0))
        message_len = len_info_len

        info_read = False
        end_of_message = False
        for x in range(0, width, sparseness):
            for y in range(0, height, sparseness):
                if not info_read and len(message_bs) >= len_info_len:
                    message_len = int(message_bs[:len_info_len], 2)
                    message_bs = message_bs[len_info_len:]
                    info_read = True
                channels = list(pix[x, y])
                for ch in mod_ch.upper():
                    if len(message_bs) >= message_len:
                        message_bs = message_bs[:message_len]
                        end_of_message = True
                        break
                    i = im_mode.index(ch)
                    val = binary(channels[i])
                    message_bs += val[len(val) - greed:]
            if end_of_message:
                break
        return message_bs
