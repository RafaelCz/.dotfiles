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
NS_SVG = 'http://www.w3.org/2000/svg'
NS_INK = 'http://www.inkscape.org/namespaces/inkscape'

_last_id = 0
def next_id():
    global _last_id
    _last_id += 1
    return '_%d' % _last_id

def parse_color(color_desc):
    r = int(color_desc['Rd  '])
    g = int(color_desc['Grn '])
    b = int(color_desc['Bl  '])
    return 'rgb(%d, %d, %d)' % (r,g,b)

def box_path_data(bounds):
    return 'M %(left)d,%(top)d %(right)d,%(top)d %(right)d,%(bottom)d ' \
            '%(left)d,%(bottom)d %(left)d,%(top)d Z' % bounds
