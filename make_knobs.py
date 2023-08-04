#!/usr/bin/env python3

# make_knobs.py
#
# written by: Oliver Cordes 2023-08-04
# changed by: Oliver Cordes 2023-08-04


"""
This script creates a animation stripe from a single template
svg-file. The stripe is then a list of individual knobs which
can be cut out by the displaying program. There are a few
parameters which can be set in a toml config file.
"""


from PILSVG import SVG
from PIL import Image, ImageDraw

import os, sys, inspect

import numpy as np
import toml

from animation_slide import AnimationSlide
  

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

def retrieve_name(var):
        """
        Gets the name of var. Does it from the out most frame inner-wards.
        :param var: variable to get name from.
        :return: string
        """
        for fi in reversed(inspect.stack()):
            names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
            if len(names) > 0:
                return names[0]

def get_config(d, name):
    table = retrieve_name(d)
    if name in d:
        return d[name]
    else:
        print(f'Required variable \'{name}\' not found in table \'{table}\'!')
        sys.exit(0)

    
def create_knobs(config):
    #print(config)

    # read SVG file as a base
    main = get_config(config, 'main')
    marker = get_config(config, 'marker')
    
    svg = SVG(get_config(main, 'knob_file'))

    # convert into PIL image
    knob = svg.im()

    # size of the template image
    size = get_config(main, 'resize')

    nr_images = get_config(marker, 'nr_positions')

    anim = AnimationSlide(size, nr_images)

    angles = np.linspace(get_config(marker, 'start_pos'), get_config(marker, 'end_pos'), nr_images)

    if get_config(main, 'ring'):
        pass
    else:
        scale_color = None

    for i, angle in enumerate(angles):
        img = create_knob_image(knob, angle, get_config(marker, 'color'), size, scale_color=scale_color)
        anim.draw(i, img)

    anim.save(get_config(main, 'output'))
    #anim.show()


# main program

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    print(f'Need at least a toml configuration file for a proper working!')
    sys.exit(0)

with open(filename, 'r') as f:
   config = toml.load(f)

create_knobs(config)

sys.exit(0)