# http://python-pillow.org
from PIL import Image

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-e')  # TODO describe me
parser.add_argument('-d')  # TODO describe me
parser.add_argument('-m')  # TODO describe me
parser.add_argument('-k')  # TODO describe me
parser.add_argument('text_path')
parser.add_argument('image_path')
args = parser.parse_args()
image = Image.open(args.image_path)
image_pixels = image.load()
image_out_path = args.image_path + '.ste'


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


"""set lowest bit of all pixels to 0"""
for x in range(image.size[0]):
    for y in range(image.size[1]):
        r, g, b = image_pixels[x, y]
        r -= r % 2
        g -= g % 2
        b -= b % 2
        image_pixels[x, y] = r, g, b

"""hide text in lowest bits"""
with open(args.text_path, 'r') as f:
    text = "".join(f.readlines())

text_bits = string_to_bits(text)

if len(text_bits) > (image.size[0] * image.size[1]) * 3:
    print("Got more text than pixels, message will get cropped!")

for pixel_index in range(0, image.size[0] * image.size[1]):
    x = pixel_index % image.size[1]
    y = int(pixel_index / image.size[1])
    bit_triple = text_bits[pixel_index * 3: pixel_index * 3 + 3]
    if len(bit_triple) == 0:
        break  # break if no text bits left
    bit_triple = bit_triple.ljust(3, "0")  # pad 0 to the right if less than 3 bits
    r, g, b = image_pixels[x, y]
    r += int(bit_triple[0])
    g += int(bit_triple[1])
    b += int(bit_triple[2])
    image_pixels[x, y] = r, g, b

image.save(image_out_path, 'BMP')
