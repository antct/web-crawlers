from PIL import Image, ImageFilter
import random
import argparse
import os


nrow, ncol, uw, uh, path = 4, 8, 200, 200, './images'
backend = Image.new('RGBA', (ncol*uw, nrow*uh))
files = os.listdir('{}'.format(path))
random.shuffle(files)

for x in range(nrow):
    for y in range(ncol):
        file = files[ncol * x + y]
        t = Image.open("{}\\{}".format(path, file)).resize((uw, uh), Image.ANTIALIAS)
        backend.paste(t, (y * uw, x * uh))
backend = backend.filter(ImageFilter.ModeFilter(5)).filter(ImageFilter.GaussianBlur)
frontend = Image.open("{}\\{}".format(path, '0.jpg')).resize((uw*ncol, uh*nrow), Image.ANTIALIAS)
final = Image.blend(backend.convert('RGBA'), frontend.convert('RGBA'), 0.7)
final.rotate(0)
final.save("mix.png")
