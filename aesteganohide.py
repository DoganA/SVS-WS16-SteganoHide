# http://python-pillow.org
import hashlib

from PIL import Image

import argparse

parser = argparse.ArgumentParser()
mode = parser.add_mutually_exclusive_group()
mode.add_argument('-d', help='encrypt', action='store_true')
mode.add_argument('-e', help='decrypt', action='store_true')
parser.add_argument('-m', help='MAC key', required=True)
parser.add_argument('-k', help='crypto key', required=True)
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
    Sets the least significant bits of an image to 0
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
    Writes a String of bits to the least significant bits of an image
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


def read_bits_from_image(img):
    """
    Reads a String of bits from the least significant bits of an image
    :param img: Image to read from
    :return:
    """
    # img = clear_lowest_bits_of_image(img)
    # if len(bits) > (img.size[0] * img.size[1]) * 3:
    #     print("Got more text than pixels, message will get cropped!")
    bits = []
    image_pixels = img.load()
    for pixel_index in range(0, img.size[0] * img.size[1]):
        x = pixel_index % img.size[1]
        y = int(pixel_index / img.size[1])
        r, g, b = image_pixels[x, y]
        bits.append(r % 2)
        bits.append(g % 2)
        bits.append(b % 2)
    bits = [str(x) for x in bits]
    return ''.join(bits)


def generate_hmac_sha256(key, text):
    """
    Generates a sha256 hmac for given text and key
    :param key: String, key
    :param text: String, text
    :return: String, hmac
    """
    key_hash = hashlib.sha256(key.encode('utf-8')).hexdigest()
    x = key_hash+text
    print(x)
    return hashlib.sha256(x.encode('utf-8')).hexdigest()
    pass  # TODO IMPLEMENT ME


def check_hmac_sha256(hmac, key, text):
    """
    Checks whether hmac, key and text combination is correct or not
    :param hmac: hmac to check
    :param key: key
    :param text: text
    :return: True if correct, False if not valid
    """
    return generate_hmac_sha256(key, text) == hmac


""" MAIN """

if args.e:
    # Encryption mode
    with open(args.text_path, 'r') as f:
        text = "".join(f.readlines())
    print(generate_hmac_sha256(args.m, text))