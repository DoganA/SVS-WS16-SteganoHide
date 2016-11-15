# http://python-pillow.org
from PIL import Image

import argparse

parser = argparse.ArgumentParser()
mode = parser.add_mutually_exclusive_group()
mode.add_argument('-d', help='encrypt', action='store_true')
mode.add_argument('-e', help='decrypt', action='store_true')
parser.add_argument('-m', help='MAC key')
parser.add_argument('-k', help='crypto key')
parser.add_argument('text_path', nargs='?')
parser.add_argument('image_path', nargs=1)
args = parser.parse_args()


def string_to_bits(s):
    """
    Converts a String of text into a String of bits (padded to 8 bit per char)
    :param s: String
    :return: String, bits
    """
    bits = []
    for c in s:
        bin_t = bin(ord(c))[2:]  # remove 0b header
        bits.append(bin_t.zfill(8))  # pad to 8 bit
    return "".join(bits)


def bits_to_string(b):
    """
    Converts a String of bits (8 bits per char) into a String of text
    :param s: bit-String
    :return: Text
    """
    chars = []
    for i in range(0, len(b), 8):
        char = chr(int(b[i:i + 8], 2))
        chars.append(char)
    return "".join(chars)


def clear_lowest_bits_of_image(img):
    """
    Sets the least important bits of an image to 0
    :param img: Image to change
    :return: new changed image
    """
    image_pixelmap = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            r, g, b = image_pixelmap[x, y]
            r -= r % 2
            g -= g % 2
            b -= b % 2
            image_pixelmap[x, y] = r, g, b
    return img.copy()


def write_bits_to_image(bits, img):
    """
    Writes a String of bits to the least important bits of an image
    :param bits:
    :param img:
    :return:
    """
    img = clear_lowest_bits_of_image(img)
    if len(bits) > (img.size[0] * img.size[1]) * 3:
        print("Got more text than pixels, message will get cropped!")
    image_pixels = img.load()
    for pixel_index in range(0, img.size[0] * img.size[1]):
        x = pixel_index % img.size[1]
        y = int(pixel_index / img.size[1])
        bit_triple = bits[pixel_index * 3: pixel_index * 3 + 3]
        if len(bit_triple) == 0:
            break  # break if no text bits left
        bit_triple = bit_triple.ljust(3, "0")  # pad 0 to the right if less than 3 bits
        r, g, b = image_pixels[x, y]
        r += int(bit_triple[0])
        g += int(bit_triple[1])
        b += int(bit_triple[2])
        image_pixels[x, y] = r, g, b
    return img


""" MAIN """
if not args.e and not args.d:
    image = Image.open(args.image_path[0])
    image_out_path = args.image_path[0] + '.ste'
    with open(args.text_path, 'r') as f:
        text = "".join(f.readlines())
    text_bits = string_to_bits(text)
    image_out = write_bits_to_image(text_bits, image)
    image_out.save(image_out_path, 'BMP')
