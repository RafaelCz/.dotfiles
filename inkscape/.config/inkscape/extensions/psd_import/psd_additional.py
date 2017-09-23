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
from .binaryreader import BinaryReader
from .psd_primitive import PSDPrimitiveReaderMixin
from .psd_descriptor import PSDDescriptorReaderMixin


IGNORED_KEYS = set([
    'clbl',     # blend clipping elements
    'fxrp',     # reference point
    'infx',     # blend interior elements
    'knko',     # knockout setting
    'lclr',     # sheet color setting
    'lnsr',     # layer name source setting
    'lspf',     # protected setting
    'lyid',     # layer id
    'lyvr',     # layer version
    'shmd',     # metadata setting
])

class PSDAdditionalLayerInfoReaderMixin(object):
    def read_additional_layer_info(self, data):
        assert self.read_raw(4) in ('8BIM', '8B64')
        key = self.read_raw(4)

        func = 'read_ali_%s' % key
        if hasattr(self, func):
            data[key] = getattr(self, func)()
        elif key in IGNORED_KEYS:
            self.skip_section()
        else:
            if 'unknown' not in data:
                data['unknown'] = set()
            data['unknown'].add(key)
            self.skip_section()


    def read_ali_luni(self):
        # layer unicode name
        end_pos = self.read_section_end()
        return self.read_psd_unicode()

    def read_ali_lsct(self):
        # section divider type
        end_pos = self.read_section_end()
        result = {'type': self.read_int(4)}
        self.skip_to(end_pos)
        return result

    # lsdk: undocumented, seems to be the same as lsct
    read_ali_lsdk = read_ali_lsct

    def read_ali_vmsk(self):
        # vector mask
        end_pos = self.read_section_end()
        assert self.read_int(4) == 3

        result = {}
        result['flags'] = self.read_uint(4)

        path_records = []
        # Each path record is 26 bytes long.  There may be padding at the end,
        # to make it a multiple of 4 bytes in total.
        while end_pos - self.pos >= 26:
            path_records.append(self.read_path_record())

        result['path_records'] = path_records

        self.skip_to(end_pos)
        return result

    read_ali_vsms = read_ali_vmsk

    def read_ali_vscg(self):
        # vector stroke data
        end_pos = self.read_section_end()
        key = self.read_raw(4)
        assert self.read_int(4) == 16
        desc = self.read_descriptor()
        self.skip_to(end_pos)
        return {key: desc}

    def read_ali_vstk(self):
        # vector stroke info?
        # The 'vstk' type is undocumented, but it seems to be the same format
        # as SoCo (but with different descriptor contents).
        end_pos = self.read_section_end()

        assert self.read_int(4) == 16
        desc = self.read_descriptor()

        # The descriptor is padded to a multiple of 4 bytes.
        self.skip_to(end_pos)
        return desc

    def read_ali_SoCo(self):
        # solid color
        end_pos = self.read_section_end()
        assert self.read_int(4) == 16
        desc = self.read_descriptor()
        self.skip_to(end_pos)
        return desc

    def read_ali_lfx2(self):
        # layer effects 2
        end_pos = self.read_section_end()
        assert self.read_int(4) == 0
        assert self.read_int(4) == 16
        desc = self.read_descriptor()
        self.skip_to(end_pos)
        return desc


    def read_ali_Txt2(self):
        # text engine data

        # We want to ignore this, but it seems we can't use skip_section like
        # normal because the section length needs to be rounded up to the
        # nearest multiple of 2.
        self.skip_section(alignment=2)


    def read_path_record(self):
        result = {}
        record_type = self.read_int(2)

        if record_type == 0 or record_type == 3:
            result['type'] = 'subpath_start'
            result['mode'] = 'closed' if record_type < 3 else 'open'
            result['knot_count'] = self.read_int(2)
            result['combine_mode'] = self.read_int(2)
            self.skip(20)
        elif record_type in (1, 2, 4, 5):
            result['type'] = 'knot'
            result['mode'] = 'closed' if record_type < 3 else 'open'
            result['linked'] = record_type in (1, 4)
            result['control_back'] = self.read_point()
            result['control_anchor'] = self.read_point()
            result['control_front'] = self.read_point()
        elif record_type == 6:
            result['type'] = 'path_fill_rule'
            self.skip(24)
        elif record_type == 7:
            result['type'] = 'clipboard'
            result['top'] = self.read_fixed()
            result['left'] = self.read_fixed()
            result['bottom'] = self.read_fixed()
            result['right'] = self.read_fixed()
            result['resolution'] = self.read_fixed()
            self.skip(4)
        elif record_type == 8:
            result['type'] = 'initial_fill_rule'
            result['value'] = self.read_int(2)
            self.skip(22)

        return result
