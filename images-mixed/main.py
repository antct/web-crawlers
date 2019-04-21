from PIL import Image, ImageFilter
import random
import argparse


class mixPhoto(object):
    row, col, uw, uh, width, height = 0, 0, 0, 0, 0, 0
    path = ""

    def __init__(self, row, col, uw, uh, imgpath):
        self.row = row
        self.col = col
        self.uw = uw
        self.uh = uh
        self.width = row*uw
        self.height = col*uh
        self.path = imgpath

    def read(self, address, width, height):
        img = Image.open("%s" % address)
        img = img.resize((width, height), Image.ANTIALIAS)
        return img

    def blend(self, img1, img2, factor=0.5):
        img1 = img1.convert('RGBA')
        img2 = img2.convert('RGBA')
        img = Image.blend(img1, img2, factor)
        # img.save("blend.png")
        return img

    def ranseq(self):
        seq = []
        border = self.row*self.col
        data = random.randint(1, border)
        for i in range(border):
            while data in seq:
                data = random.randint(1, border)
            seq.append(data)
        return seq

    def add(self):
        toImage = Image.new('RGBA', (self.width, self.height))
        seq = self.ranseq()
        for x in range(self.col):
            for y in range(self.row):
                name = r"%s\%s.jpg" % (self.path, (seq[self.row * x + y]))
                loadimage = self.read(name, self.uw, self.uh)
                toImage.paste(loadimage, (y * self.uw, x * self.uh))
        return toImage

    def mix(self):
        toImage = self.add()
        img = self.read(r"%s\0.jpg" % self.path, self.width, self.height)
        toImage_sm = toImage.filter(ImageFilter.ModeFilter(
            5)).filter(ImageFilter.GaussianBlur)
        final = self.blend(toImage_sm, img, 0.7)
        final.rotate(-3)
        final.save("mix.png")


parser = argparse.ArgumentParser()
parser.add_argument('row')
parser.add_argument('col')
parser.add_argument('uw')
parser.add_argument('uh')
parser.add_argument('file')
args = parser.parse_args()
row, col, uw, uh, file = int(args.row), int(
    args.col), int(args.uw), int(args.uh), args.file

img = mixPhoto(row, col, uw, uh, file)
img.mix()
