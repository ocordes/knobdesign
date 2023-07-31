from PILSVG import SVG

from PIL import Image, ImageDraw

import numpy as np


from animation_slide import AnimationSlide
  
# colors
neon_green = '#7FFF00'
dark_green = '#107000'

def arc(draw, bbox, start, end, fill, width=1, segments=100):
    """
    Hack that looks similar to PIL's draw.arc(), but can specify a line width.
    """
    # radians
    start *= np.pi / 180
    end *= np.pi / 180

    # angle step
    da = (end - start) / segments

    # shift end points with half a segment angle
    start -= da / 2
    end -= da / 2

    # ellips radii
    rx = (bbox[2] - bbox[0]) / 2
    ry = (bbox[3] - bbox[1]) / 2

    # box centre
    cx = bbox[0] + rx
    cy = bbox[1] + ry

    # segment length
    l = (rx+ry) * da / 2.0

    for i in range(segments):

        # angle centre
        a = start + (i+0.5) * da

        # x,y centre
        x = cx + np.cos(a) * rx
        y = cy + np.sin(a) * ry

        # derivatives
        dx = -np.sin(a) * rx / (rx+ry)
        dy = np.cos(a) * ry / (rx+ry)

        draw.line([(x-dx*l,y-dy*l), (x+dx*l, y+dy*l)], fill=fill, width=width)



def rotate_polygon(points, angle, cx, cy):
    new_points = []
    cosang = np.cos(np.pi*angle/180.)
    sinang = np.sin(np.pi*angle/180.)
    for p in points:
        x = p[0]-cx
        y = p[1]-cy

        new_x = (x*cosang - y*sinang) + cx
        new_y = (x*sinang + y*cosang) + cy
        new_points.append((new_x, new_y))

    return new_points


def create_knob_image(knob, angle, color, resize, start_angle=-135, scale_color=None):

    size = knob.size

    # position of the led light 
    width = 6
    height = 25
    xm = size[0]//2
    y0 = 5

    cx = size[0]//2 - 1
    cy = size[1]//2 - 1

    # define the polygon points according the image and angle
    points = [(xm-width//2, y0), (xm+width//2, y0), (xm+width//2, y0+height), (xm-width//2, y0+height), (xm-width//2, y0)]
    points = rotate_polygon(points, angle, cx, cy)

    # need a copy of the knob
    knob = knob.copy()

    # draw led light
    _ = ImageDraw.Draw(knob).polygon(points, fill=color)
    shape = [(1,1),(size[0]-2,size[1]-2)]
    #_ = ImageDraw.Draw(knob).arc(shape, start = start_angle-90, end = angle-90, fill ="red")
    shape = [2,2,size[0]-3,size[1]-3]
    if scale_color is not None:
        arc(ImageDraw.Draw(knob), shape, start_angle-90, angle-90, scale_color,width=4)

    return knob.resize(resize)


    



# main program

# read SVG file as a base
svg = SVG('knob1_ring.svg')

# convert into PIL image
knob = svg.im()


nr_images = 50
#nr_images = 5

size = (knob.size[0]//4, knob.size[1]//4)
anim = AnimationSlide(size, nr_images)

angles = np.linspace(-135, 135, nr_images)


for i, angle in enumerate(angles):
    img = create_knob_image(knob, angle, neon_green, size, scale_color=dark_green)
    anim.draw(i, img)

anim.save('knobs1.png')
anim.show()