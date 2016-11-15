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
image_out_path = args.image_path + '.ste'

with open(args.text_path, 'r') as f:
    text = "".join(f.readlines())


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
        char = chr(int(b[i:i+8], 2))
        chars.append(char)
    return "".join(chars)



print(string_to_bits(text))
print(bits_to_string(string_to_bits(text)))
