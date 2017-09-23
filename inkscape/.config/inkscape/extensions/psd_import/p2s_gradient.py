# Copyright (c) 2012 Stuart Pernsteiner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from lxml import etree
import math

from .p2s_util import *


def compute_gradient_points(bounds, angle, scale):
    """Find the (x1,y1) and (x2,y2) to use for a gradient overlay with the
    given angle and scale, on a layer with the given bounds.
    """
    top    = bounds['top']
    left   = bounds['left']
    bottom = bounds['bottom']
    right  = bounds['right']

    theta = angle * math.pi / 180
    dx = math.cos(theta)
    dy = -math.sin(theta)

    fx = (right - left) / 2 / dx if dx != 0 else float('inf')
    fy = (bottom - top) / 2 / dy if dy != 0 else float('inf')

    f = min(abs(fx), abs(fy)) * scale

    mid_x = (right + left) / 2
    mid_y = (bottom + top) / 2

    p1 = {
        'x': mid_x - dx * f,
        'y': mid_y - dy * f,
    }
    p2 = {
        'x': mid_x + dx * f,
        'y': mid_y + dy * f,
    }
    return (p1, p2)

def compute_gradient_offset(bounds, offset):
    assert offset['Hrzn']['units'] == '#Prc'
    assert offset['Vrtc']['units'] == '#Prc'

    width = bounds['right'] - bounds['left']
    height = bounds['bottom'] - bounds['top']
    offset_x = width * (offset['Hrzn']['value'] / 100.0)
    offset_y = height * (offset['Vrtc']['value'] / 100.0)

    return (offset_x, offset_y)

def construct_gradient(gradient, bounds, base_color=None):
    """Construct an <svg:linearGradient> for the given gradient on a layer with
    the given bounds.
    """
    assert gradient['Algn'] == True

    d_angl = gradient['Angl']
    assert d_angl['units'] == '#Ang'
    angle = d_angl['value']

    assert gradient['Opct']['units'] == '#Prc'
    assert gradient['Opct']['value'] == 100 or base_color is not None

    d_clrs = gradient['Grad']['Clrs']
    d_trns = gradient['Grad']['Trns']
    stops = construct_gradient_stops(d_clrs, d_trns, base_color, gradient['Opct']['value'])

    assert gradient['Md  ']['type'] == 'BlnM'
    assert gradient['Md  ']['enum'] == 'Nrml'

    if gradient['Rvrs'] == True:
        stops.reverse()
        for stop in stops:
            offset = float(stop.get('offset'))
            stop.set('offset', '%f' % (1 - offset))

    d_scl = gradient['Scl ']
    assert d_scl['units'] == '#Prc'
    scale = d_scl['value'] / 100.0

    assert gradient['Type']['type'] == 'GrdT'

    if gradient['Type']['enum'] == 'Lnr ':
        p1, p2 = compute_gradient_points(bounds, angle, scale)
        offset_x, offset_y = compute_gradient_offset(bounds, gradient['Ofst'])

        p1['x'] += offset_x
        p1['y'] += offset_y
        p2['x'] += offset_x
        p2['y'] += offset_y

        item = etree.Element('{%s}linearGradient' % NS_SVG)
        item.set('x1', '%f' % p1['x'])
        item.set('y1', '%f' % p1['y'])
        item.set('x2', '%f' % p2['x'])
        item.set('y2', '%f' % p2['y'])
        item.set('gradientUnits', 'userSpaceOnUse')
        item.extend(stops)
    elif gradient['Type']['enum'] == 'Rdl ':
        p1, p2 = compute_gradient_points(bounds, angle, scale)
        offset_x, offset_y = compute_gradient_offset(bounds, gradient['Ofst'])

        center = {
            'x': (p1['x'] + p2['x']) / 2 + offset_x,
            'y': (p1['y'] + p2['y']) / 2 + offset_y,
        }

        dx = center['x'] - p1['x']
        dy = center['y'] - p1['y']
        dist = math.sqrt(dx * dx + dy * dy)

        item = etree.Element('{%s}radialGradient' % NS_SVG)
        item.set('cx', '%f' % center['x'])
        item.set('cy', '%f' % center['y'])
        item.set('r', '%f' % dist)
        item.set('gradientUnits', 'userSpaceOnUse')
        item.extend(stops)
    else:
        assert False, 'unknown gradient type %s' % gradient['Type']['enum']

    return item

def construct_gradient_stops(d_clrs, d_trns, base_color, global_opacity):
    """Build <svg:stop>s for each stop in the gradient."""

    d_clrs = sorted(d_clrs, key=lambda x: x['Lctn'])
    d_trns = sorted(d_trns, key=lambda x: x['Lctn'])

    lctn_map = {}
    for d_clrs_item in d_clrs:
        lctn_map[d_clrs_item['Lctn']] = { 'Clrs': d_clrs_item }
    for d_trns_item in d_trns:
        lctn = d_trns_item['Lctn']
        entry = lctn_map.get(lctn, {})
        entry['Trns'] = d_trns_item
        lctn_map[lctn] = entry

    def blend_with_base_color(color,opacity):
        if base_color is None:
            return (color,opacity)

        opacity *= global_opacity / 100.0
        c1 = opacity
        c2 = 1 - opacity

        r = color['Rd  '] * c1 + base_color['Rd  '] * c2
        g = color['Grn '] * c1 + base_color['Grn '] * c2
        b = color['Bl  '] * c1 + base_color['Bl  '] * c2
        a = 1

        return ({
            'Rd  ': r,
            'Grn ': g,
            'Bl  ': b,
        }, a)

    def color_at_lctn(lctn):
        if lctn in lctn_map and 'Clrs' in lctn_map[lctn]:
            # There is a Clrs item for this location.
            return lctn_map[lctn]['Clrs']['Clr ']

        # There is no entry for this location, so we need to interpolate.
        if lctn < d_clrs[0]['Lctn']:
            return d_clrs[0]['Clr ']
        if lctn >= d_clrs[-1]['Lctn']:
            return d_clrs[-1]['Clr ']

        for i in xrange(1, len(d_clrs)):
            if lctn < d_clrs[i]['Lctn']:
                a = d_clrs[i - 1]['Clr ']
                b = d_clrs[i]['Clr ']

                length = float(d_clrs[i]['Lctn'] - d_clrs[i - 1]['Lctn'])
                aw = (lctn - d_clrs[i - 1]['Lctn']) / length
                bw = (d_clrs[i]['Lctn'] - lctn) / length

                return dict((k, aw * a[k] + bw * b[k])
                        for k in ['Rd  ', 'Grn ', 'Bl  '])

        assert False, 'unreachable code'

    def opacity_at_lctn(lctn):
        if lctn in lctn_map and 'Trns' in lctn_map[lctn]:
            # There is a Trns item for this location.
            return lctn_map[lctn]['Trns']['Opct']['value'] / 100.0

        # There is no entry for this location, so we need to interpolate.
        if lctn < d_trns[0]['Lctn']:
            return d_trns[0]['Opct']['value'] / 100.0
        if lctn >= d_trns[-1]['Lctn']:
            return d_trns[-1]['Opct']['value'] / 100.0

        for i in xrange(1, len(d_trns)):
            if lctn < d_trns[i]['Lctn']:
                a = d_trns[i - 1]['Opct']['value'] / 100.0
                b = d_trns[i]['Opct']['value'] / 100.0

                length = float(d_trns[i]['Lctn'] - d_trns[i - 1]['Lctn'])
                # The weight is 1 - dist / length, where 'dist' is the distance
                # from 'lctn' to the control point, and 'length' is the
                # distance between control points.
                aw = 1 - (lctn - d_trns[i - 1]['Lctn']) / length
                bw = 1 - (d_trns[i]['Lctn'] - lctn) / length

                return aw * a + bw * b

        assert False, 'unreachable code'


    lctns = sorted(lctn_map.keys())
    min_lctn = lctns[0]
    max_lctn = lctns[-1]

    def lctn_to_pos(lctn):
        # Convert a PSD descriptor 'Lctn' value to an <svg:stop> 'pos' value.
        return (lctn - min_lctn) / float(max_lctn - min_lctn)

    stops = []

    for lctn in lctns:
        color = color_at_lctn(lctn)
        opacity = opacity_at_lctn(lctn)
        color, opacity = blend_with_base_color(color,opacity)

        pos = lctn_to_pos(lctn)

        stop = etree.Element('{%s}stop' % NS_SVG)
        stop.set('offset', '%f' % pos)
        stop.set('stop-color', parse_color(color))
        stop.set('stop-opacity', '%f' % opacity)
        stops.append(stop)

    return stops
