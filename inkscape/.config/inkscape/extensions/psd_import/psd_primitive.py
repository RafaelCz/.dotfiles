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

class PSDPrimitiveReaderMixin(object):
    def read_psd_unicode(self, alignment=4):
        """Read a PSD-format Unicode string."""
        length = self.read_int(4)
        string = u''.join(unichr(self.read_int(2)) for i in xrange(length))

        if alignment is not None:
            self.skip_padding(length * 2, alignment)

        return string

    def read_psd_string(self, alignment=4):
        """Read a PSD-format 8-bit string (called a "Pascal string" in the
        documentation).
        """
        length = self.read_int(1)
        string = self.read_raw(length)

        if alignment is not None:
            self.skip_padding(1 + length, alignment)
        return string

    def read_fixed(self):
        """Read a 32-bit fixed-point number, with 24 fractional bits."""
        return self.read_int(4) / float(1 << 24)

    def read_point(self):
        """Read a 2D point in fixed-point format."""
        y = self.read_fixed()
        x = self.read_fixed()
        return {'x': x, 'y': y}

    def skip_section(self, alignment=None):
        """Skip an entire section, by reading the 4-byte section length and
        skipping that many bytes.
        """
        length = self.read_uint(4)
        self.skip(length)
        if alignment is not None:
            self.skip_padding(length, alignment)

    def read_section_end(self):
        """Read a section length and compute the position of the end of the
        section.
        """
        length = self.read_uint(4)
        return self.pos + length
