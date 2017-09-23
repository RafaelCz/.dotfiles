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

from .p2s_util import *

def psd_path_records_to_svg_path_data(records, bounds):
    def render_point(pt):
        x = bounds['left'] + pt['x'] * (bounds['right'] - bounds['left'])
        y = bounds['top'] + pt['y'] * (bounds['bottom'] - bounds['top'])
        return '%f,%f' % (x,y)

    render_points = lambda *pts: tuple(map(render_point, pts))

    d = ''
    results = []

    # Current subpath mode ('open' or 'closed')
    path_mode = None
    # Current subpath combine mode (1 = normal, 2 = subtract)
    combine_mode = None

    # The back-facing handle and anchor positions for the subpath's first knot
    first_back = None
    first_anchor = None
    # The front-facing handle position for the previous knot
    prev_front = None

    def finish_path():
        # Finish the current path and append its data to 'results'.
        if first_back is None:
            return

        if path_mode == 'closed':
            # Add a segment from the final anchor point to the initial one.
            extra_d = 'C %s %s %s Z' % render_points(
                    prev_front, first_back, first_anchor)
        else:
            extra_d = ''

        path = {}
        path['combine_mode'] = combine_mode
        path['data'] = d + extra_d
        results.append(path)

    for record in records:
        if record['type'] == 'subpath_start':
            # Finish the active subpath
            finish_path()

            # Reinitialize for the next subpath
            d = ''
            path_mode = record['mode']
            combine_mode = record['combine_mode']
            first_back = None
            first_anchor = None
            prev_front = None

        elif record['type'] == 'knot':
            if prev_front is None:
                # This is the first point of the path
                first_back = record['control_back']
                first_anchor = record['control_anchor']
                d += 'M %s ' % render_point(record['control_anchor'])
                prev_front = record['control_front']
            else:
                d += 'C %s %s %s ' % render_points(
                        prev_front,
                        record['control_back'],
                        record['control_anchor'])
                prev_front = record['control_front']

    # Finish the final subpath
    finish_path()

    return results

def build_path_from_data(path_data, invert, bounds):
    """Build a <svg:path> from the results of
    'psd_path_records_to_svg_path_data'.  Returns a <path> and possibly a
    <mask>, if one is necessary due to the presence of subtractive subpaths.
    """

    # Separate the data by combine_mode.
    positive_data = []
    negative_data = []
    positive_rule = None
    negative_rule = 'nonzero'   # This might change if 'invert' is set.

    for subpath in path_data:
        combine_mode = subpath['combine_mode']

        if combine_mode == -1:
            # -1 indicates that the current subpath is actually an extension of
            # the previous one.  The two should be treated as a single item for
            # rendering purposes.  If the two overlap, they are filled using
            # the 'evenodd' rule.
            #
            # We handle the case of a single multipart subpath with mode
            # 'combine' by switching the fill rule from 'nonzero' to 'evenodd'
            # when we see the extension.
            if positive_rule is None or (positive_rule == 'nonzero' and len(positive_data) == 1):
                positive_rule = 'evenodd'
            assert positive_rule == 'evenodd', \
                    "can't have multiple subpaths with mode 'combine' in a layer with a multi-part subpath"

            # Kind of a hack, but avoids duplicating code.
            combine_mode = 0

        if combine_mode == 1:
            assert len(negative_data) == 0, \
                    "can't have subpaths with mode 'combine' after subpaths with mode 'subtract'"

            if positive_rule is None:
                positive_rule = 'nonzero'
            assert positive_rule == 'nonzero', \
                    "can't mix subpaths with modes 'combine' and 'exclude overlap' in the same layer"

            positive_data.append(subpath['data'])
        elif combine_mode == 0:
            assert len(negative_data) == 0, \
                    "can't have subpaths with mode 'combine' after subpaths with mode 'subtract'"

            if positive_rule is None:
                positive_rule = 'evenodd'
            assert positive_rule == 'evenodd', \
                    "can't mix subpaths with modes 'combine' and 'exclude overlap' in the same layer"

            positive_data.append(subpath['data'])
        elif combine_mode == 2:
            negative_data.append(subpath['data'])
        else:
            assert False, "unknown subpath combining mode %d" % \
                    combine_mode

    if invert:
        positive_data, negative_data = negative_data, positive_data
        positive_rule, negative_rule = negative_rule, positive_rule

    # Build the mask if one is necessary.
    mask = None
    if len(negative_data) > 0:
        mask = etree.Element('{%s}mask' % NS_SVG)
        mask.set('id', next_id())
        
        group = etree.SubElement(mask, '{%s}g' % NS_SVG)

        box = etree.SubElement(group, '{%s}path' % NS_SVG)
        box.set('d', box_path_data(bounds))
        box.set('style', 'stroke:none; fill:white')

        path = etree.SubElement(group, '{%s}path' % NS_SVG)
        path.set('d', ' '.join(negative_data))
        path.set('style', 'stroke:none; fill:black')
        path.set('fill-rule', negative_rule)

    # Build the actual path.
    if len(positive_data) == 0:
        positive_data = [box_path_data(bounds)]
    path = etree.Element('{%s}path' % NS_SVG)
    path.set('d', ' '.join(positive_data))
    if positive_rule is not None:
        path.set('fill-rule', positive_rule)

    if mask is not None:
        path.set('mask', 'url(#%s)' % mask.get('id'))

    return path, mask

def construct_path(records, flags, bounds):
    if flags & 4 != 0:
        # Vector mask is disabled.
        data = []
    else:
        data = psd_path_records_to_svg_path_data(records,  bounds)

    return build_path_from_data(data, (flags & 1 != 0), bounds)
