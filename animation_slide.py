# animation_slide.py
#
# written by: Oliver Cordes 2023-07-31
# changed by: Oliver Cordes 2023-07-31

from PIL import Image

class AnimationSlide(object):
    def __init__(self, size, count):
        self._size = size
        self._image = Image.new('RGBA', (size[0]*count,size[1]))
        

    def draw(self, nr, image):
        pos = (self._size[0]*nr,0)
        self._image.paste(image, pos)


    def save(self, filename, type="PNG"):
        self._image.save(filename, type)


    def show(self):
        self._image.show()