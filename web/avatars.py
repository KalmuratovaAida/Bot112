from PIL import Image, ImageDraw, ImageFont
from random import randint
from io import BytesIO


def random_rgb():
    return randint(0, 255), randint(0, 255), randint(0, 255)


def interpolate(f_co, t_co, interval):
    det_co = [(t - f) / interval for f, t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]


class Avatar:
    def __init__(self, names: tuple, size: tuple = (256, 256)):
        self.initials = ''.join((name[0] for name in names))

        self.w = size[0]
        self.h = size[1]

        self.avatar = Image.new('RGB', size, color=0)
        self.draw = ImageDraw.Draw(self.avatar)
        self.fnt = ImageFont.truetype(font='arialbd.ttf', size=self.h // 3)
        self.generate()

    def generate(self):
        for i, color in enumerate(interpolate(random_rgb(), random_rgb(), 256 * 2)):
            self.draw.line([(i, 0), (0, i)], tuple(color), width=1)

        w, h = self.draw.textsize(self.initials, font=self.fnt)
        self.draw.text(((self.w / 2) - (w / 2), (self.h / 2) - (h / 2)), self.initials, font=self.fnt, align='center')

    def show(self):
        self.avatar.show()

    def get_bytes(self):
        buffer = BytesIO()
        self.avatar.save(buffer, 'JPEG')
        return buffer


if __name__ == '__main__':
    avatar = Avatar(names=('John', 'Doe'), size=(256, 256))
    print(avatar.get_bytes().getvalue())
    avatar.show()
