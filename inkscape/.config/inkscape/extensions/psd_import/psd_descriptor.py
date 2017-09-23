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

class PSDDescriptorReaderMixin(object):
    def read_descriptor(self):
        name = self.read_psd_unicode(2)
        class_id = self.read_descriptor_id()

        item_count = self.read_int(4)

        result = {}

        for i in xrange(item_count):
            key = self.read_descriptor_id()
            item_type = self.read_raw(4)

            result[key] = self.read_descriptor_item(item_type)

        return result

    def read_descriptor_id(self):
        id_length = self.read_int(4)
        if id_length != 0:
            return self.read_raw(id_length)
        else:
            return self.read_raw(4)

    def read_descriptor_item(self, item_type):
        func = 'read_di_%s' % item_type.strip()
        assert hasattr(self, func), \
                "don't know how to read descriptor item %s" % item_type
        return getattr(self, func)()


    def read_di_Objc(self):
        return self.read_descriptor()

    def read_di_doub(self):
        return self.read_double()

    def read_di_UntF(self):
        units = self.read_raw(4)
        value = self.read_double()
        return {'units': units, 'value': value}

    def read_di_bool(self):
        return self.read_int(1) != 0

    def read_di_enum(self):
        type = self.read_descriptor_id()
        enum = self.read_descriptor_id()
        return {
            'type': type,
            'enum': enum,
        }

    def read_di_TEXT(self):
        return self.read_psd_unicode(2)

    def read_di_VlLs(self):
        count = self.read_int(4)
        results = []
        for i in xrange(count):
            item_type = self.read_raw(4)
            results.append(self.read_descriptor_item(item_type))
        return results

    def read_di_long(self):
        return self.read_int(4)
