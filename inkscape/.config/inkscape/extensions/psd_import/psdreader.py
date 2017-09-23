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
import sys

from .binaryreader import BinaryReader
from .psd_additional import PSDAdditionalLayerInfoReaderMixin
from .psd_descriptor import PSDDescriptorReaderMixin
from .psd_primitive import PSDPrimitiveReaderMixin


def dump_hex(buf):
    for i in xrange(0,len(buf),16):
        chunk = buf[i:i+16]
        hex_bytes = ' '.join(map(lambda x: '%02x' % ord(x), chunk))
        ascii_chars = ''.join(map(lambda x: '.' if ord(x) < 32 or ord(x) >= 128
            else x, chunk))
        sys.stderr.write(hex_bytes + '   ' + ascii_chars + '\n')
    sys.stderr.write('---\n')

class PSDReader(BinaryReader,
        PSDPrimitiveReaderMixin,
        PSDDescriptorReaderMixin,
        PSDAdditionalLayerInfoReaderMixin):
    def __init__(self, stream):
        super(PSDReader, self).__init__(stream)

    def dump(self, count=128):
        dump_hex(self.read_raw(count))
        self.skip(-count)

    def read_psd(self):
        try:
            self.psd = {}
            self.read_header()
            self.read_color_mode_data()
            self.read_image_resources()
            self.read_layer_and_mask_info()
            return self.psd
        except AssertionError:
            sys.stderr.write('Assertion failed on data:\n')
            self.dump()
            raise

    def read_header(self):
        assert self.read_raw(4) == '8BPS'   # signature
        assert self.read_int(2) == 1    # version
        assert self.read_int(2) == 0    # reserved, MBZ
        assert self.read_int(4) == 0    # reserved, MBZ
        channel_count = self.read_int(2)
        image_height = self.read_int(4)
        image_width = self.read_int(4)
        channel_depth = self.read_int(2)
        color_mode = self.read_int(2)

        self.psd['bounds'] = {
            'top': 0,
            'left': 0,
            'bottom': image_height,
            'right': image_width,
        }
        self.psd['dimensions'] = {
            'width': image_width,
            'height': image_height,
        }

    def read_color_mode_data(self):
        self.skip_section()

    def read_image_resources(self):
        self.skip_section()

    def read_layer_and_mask_info(self):
        end_pos = self.read_section_end()

        self.read_layer_info()
        self.read_global_layer_mask_info()

        # skip remaining additional layer info sections
        data = {}
        while self.pos < end_pos:
            self.read_additional_layer_info(data)
        self.psd['extra'] = data

        self.skip_to(end_pos)

    def read_layer_info(self):
        end_pos = self.read_section_end()

        # layer_count might be negative, in which case there are
        # abs(layer_count) actual layers.
        layer_count = abs(self.read_int(2))

        self.psd['layers'] = \
                [self.read_layer_record() for _ in xrange(layer_count)]

        # Skip all channel image data
        self.skip_to(end_pos)

    def read_layer_record(self):
        layer = {}

        layer['bounds'] = {
            'top':    self.read_int(4),
            'left':   self.read_int(4),
            'bottom': self.read_int(4),
            'right':  self.read_int(4),
        }

        channel_count = self.read_uint(2)

        layer['channels'] = []
        for i in xrange(channel_count):
            channel = {
                'id': self.read_int(2),
                'length': self.read_int(4),
            }
            layer['channels'].append(channel)

        assert self.read_raw(4) == '8BIM'
        blend_mode = self.read_raw(4)
        layer['opacity'] = self.read_uint(1)
        layer['clipping'] = self.read_uint(1)
        layer['flags'] = self.read_uint(1)
        self.skip(1)

        # Extra layer data section

        # The spec says there are five fields here, but it only lists three of
        # them.  It seems there are actually four, with the last (undocumented)
        # one being a list of "additional layer info" structures.
        end_pos = self.read_section_end()

        self.skip_section() # mask data
        self.skip_section() # blend data

        layer['name'] = self.read_psd_string()

        layer['extra'] = {}
        while self.pos < end_pos:
            self.read_additional_layer_info(layer['extra'])

        return layer

    def read_global_layer_mask_info(self):
        self.skip_section()
