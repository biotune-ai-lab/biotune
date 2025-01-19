import openslide
import PIL.Image


def read_slide(img, coords=(0, 0), dim=(512, 512), level=1):
    slide = openslide.open_slide(img)
    width, height = slide.dimensions
    image = slide.read_region(coords, level, dim)

    return image


def read_img(img):
    return PIL.Image.open(img)
