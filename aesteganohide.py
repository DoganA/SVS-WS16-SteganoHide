# http://python-pillow.org
import hashlib
import hmac

from PIL import Image
import argparse
import xtea

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
    return "".join(chars).rstrip(chr(0))  # remove trailing 0 characters since we don´t know where the message ends


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
    :return: String(hex), hmac
    """

    key_hash = hashlib.sha256(key.encode('utf-8')).digest()
    return hmac.new(key_hash, text.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()


def check_hmac_sha256(hmac, key, text):
    """
    Checks whether hmac, key and text combination is correct or not
    :param hmac: String(hex), hmac to check
    :param key: key
    :param text: text
    :return: True if correct, False if not valid
    """
    return generate_hmac_sha256(key, text) == hmac


def encrypt_xtea(key, bits):
    """
    Hashes the key and encrypts with XTEA
    :param key: String, key
    :param bits: String of bits
    :return: String of bits (encrypted)
    """
    key_hash = hashlib.sha256(key.encode('utf-8')).digest()[0:16]  # take first 128 bit of hash
    return xtea.encrypt(key_hash, bits)


def decrypt_xtea(key, bits):
    """
    Hashes the key and decrypts with XTEA
    :param key: String, key
    :param bits: String of bits
    :return: String of bits (decrypted)
    """
    key_hash = hashlib.sha256(key.encode('utf-8')).digest()[0:16]  # take first 128 bit of hash
    return xtea.decrypt(key_hash, bits)


""" MAIN """
key_hmac = args.m
key_xtea = args.k
image = Image.open(args.image_path[0])
image_out_path = args.image_path[0] + '.sae'

if args.e:
    with open(args.text_path, 'r') as f:
        text = "".join(f.readlines())
    generated_hmac = generate_hmac_sha256(key_hmac, text)
    assert check_hmac_sha256(generated_hmac, key_hmac, text)




    text_bits = string_to_bits(generated_hmac + text)
    encrypted_bits = encrypt_xtea(key_xtea, text_bits)
    print(encrypted_bits)
    print(bits_to_string(encrypted_bits))
    decrypted_bits = decrypt_xtea(key_xtea, encrypted_bits)
    print(decrypted_bits)
    print(bits_to_string(decrypted_bits))



    image_out = write_bits_to_image(encrypted_bits, image)
    image_out.save(image_out_path, 'BMP')

if args.d:
    bits = read_bits_from_image(image)
    """
    Since we store the hex value as part of the string, there are 8 bit for one hex char.
    That means the sha256 output 256 bit = 64 hex chars = 64*8 bit
    """
    extracted_hmac = bits_to_string(bits[0:512])
    extracted_text = bits_to_string(bits[512:])
    print("MAC CHECK: ", check_hmac_sha256(extracted_hmac, key_hmac, extracted_text))
    print(extracted_text)
