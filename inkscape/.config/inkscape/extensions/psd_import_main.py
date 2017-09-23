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
#!/usr/bin/env python
from lxml import etree
import math
from pprint import pprint
import sys

from psd_import.psdreader import PSDReader

from psd_import.p2s_gradient import construct_gradient
from psd_import.p2s_path import construct_path
from psd_import.p2s_util import *



def process_psd(psd):
    svg = etree.Element('{%s}svg' % NS_SVG)
    svg.set('width', '%s' % psd['dimensions']['width'])
    svg.set('height', '%s' % psd['dimensions']['height'])

    group_stack = [svg]

    id_uses = {}
    def choose_id(s):
        if s in id_uses:
            result = u'%s_%d' % (s, id_uses[s])
            id_uses[s] += 1
        else:
            result = s
            id_uses[s] = 1
        return result

    for layer in psd['layers']:
        extra = layer['extra']

        if 'lsct' in extra:
            layer_type = extra['lsct']['type']
        elif 'lsdk' in extra:
            layer_type = extra['lsdk']['type']
        else:
            # 0 is the default
            layer_type = 0


        item = None
        extra_items = None

        if layer_type == 0:
            item, extra_items = process_shape_layer(layer, psd['bounds'])
        elif layer_type in (1,2):
            item = group_stack.pop()
            item.set('{%s}label' % NS_INK, extra['luni'])
            if 'vmsk' in extra:
                extra_items = apply_vector_mask_to_group(
                        item, extra['vmsk'], psd['bounds'])
            elif 'vsms' in extra:
                extra_items = apply_vector_mask_to_group(
                        item, extra['vsms'], psd['bounds'])
        elif layer_type == 3:
            # Don't add anything to the document until we see the end of the
            # group.
            group = etree.Element('{%s}g' % NS_SVG)
            group.set('{%s}groupmode' % NS_INK, 'layer')
            group_stack.append(group)
        else:
            assert False, 'bad layer type %d' % layer_type

        if item is not None:
            item.set('id', choose_id(extra['luni']))
            if layer['flags'] & 2 != 0:
                # layer is hidden
                item.set('display', 'none')
            if layer['opacity'] != 255:
                # TODO: For <g>s, we should set the opacity using a mask
                # instead.  <g opacity=...> sets the opacity for each element
                # of the group separately, so when two paths in the group
                # overlap, you can see both of them instead of just the topmost
                # one.
                item.set('opacity', '%f' % (layer['opacity'] / 255.0))

        if extra_items is not None:
            group_stack[-1].extend(extra_items)
        if item is not None:
            group_stack[-1].append(item)

    return svg


def process_shape_layer(layer, image_bounds):
    extra = layer['extra']

    color, color_extra = get_fill_for_layer(layer)
    if 'vmsk' in extra:
        path, path_extra = construct_path_from_vector_mask(extra['vmsk'],
                image_bounds)
    elif 'vsms' in extra:
        path, path_extra = construct_path_from_vector_mask(extra['vsms'],
                image_bounds)
    else:
        path, path_extra = None, []

    if color is not None and path is None:
        # For layers with fill but no vector mask, draw a box the size of the
        # image.
        path = construct_box_path(layer['bounds'])
    elif color is None:
        # Make it obvious that we couldn't find the right color.
        color = 'rgb(255, 0, 255)'

    if path is not None:
        path.set('style', 'stroke: none; fill: %s' % color)
        path.set('{%s}label' % NS_INK, extra['luni'])

    return path, path_extra + color_extra

def get_fill_for_layer(layer):
    extra = layer['extra']

    if 'lfx2' in extra \
            and extra['lfx2']['masterFXSwitch'] == True \
            and 'GrFl' in extra['lfx2'] \
            and extra['lfx2']['GrFl']['enab']:

        base_color = extra['SoCo']['Clr '] if 'SoCo' in extra else None
        gradient = construct_gradient(extra['lfx2']['GrFl'], layer['bounds'], base_color)
        gradient.set('id', next_id())

        return 'url(#%s)' % gradient.get('id'), [gradient]
    elif 'SoCo' in extra:
        return parse_color(extra['SoCo']['Clr ']), []
    elif 'vscg' in extra:
        if 'vstk' in extra and not extra['vstk']['fillEnabled']:
            return 'none', []

        d_vscg = extra['vscg']
        if 'SoCo' in d_vscg:
            return parse_color(d_vscg['SoCo']['Clr ']), []
        elif 'GrFl' in d_vscg:
            gradient = construct_gradient(d_vscg['GrFl'], layer['bounds'])
            gradient.set('id', next_id())

            return 'url(#%s)' % gradient.get('id'), [gradient]
        else:
            return None, []
    else:
        return None, []

def construct_path_from_vector_mask(vmsk, image_bounds):
    path, path_mask = construct_path(vmsk['path_records'], vmsk['flags'], image_bounds)
    if path_mask is None:
        path_extra = []
    else:
        path_extra = [path_mask]
    return path, path_extra

def apply_vector_mask_to_group(group, vmsk, image_bounds):
    path, path_mask = construct_path(vmsk['path_records'], vmsk['flags'], image_bounds)

    if path_mask is not None:
        # Use 'path' as a mask.
        path.set('style', 'stroke: none; fill: white')

        mask_id = next_id()
        mask = etree.Element('{%s}mask' % NS_SVG)
        mask.set('id', mask_id)
        mask.append(path)

        group.set('mask', 'url(#%s)' % mask_id)

        return [mask, path_mask]
    else:
        # Use 'path' as a clip path.
        clip_id = next_id()

        clip = etree.Element('{%s}clipPath' % NS_SVG)
        clip.set('id', clip_id)
        clip.append(path)

        group.set('clip-path', 'url(#%s)' % clip_id)

        return [clip]


def construct_box_path(bounds):
    data = box_path_data(bounds)
    path = etree.Element('{%s}path' % NS_SVG)
    path.set('d', data)
    return path



if __name__ == '__main__':
    if sys.argv[1] == '-d':
        filename = sys.argv[2]
        debug = True
    else:
        filename = sys.argv[1]
        debug = False

    with open(filename, 'rb') as f:
        psdr = PSDReader(f)
        psd = psdr.read_psd()

    if debug:
        pprint(psd)
        sys.exit(0)

    svg = process_psd(psd)
    print(etree.tostring(svg))
