# http://python-pillow.org
from PIL import Image

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-e')   # TODO describe me
parser.add_argument('-d')   # TODO describe me
parser.add_argument('-m')   # TODO describe me
parser.add_argument('-k')   # TODO describe me
parser.add_argument('text_path')
parser.add_argument('image_path')

args = parser.parse_args()
