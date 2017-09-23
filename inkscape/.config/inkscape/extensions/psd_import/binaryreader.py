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
import struct

INT_FORMATS = {1: 'b', 2: '>h', 4: '>i', 8: '>q'}
UINT_FORMATS = {1: 'B', 2: '>H', 4: '>I', 8: '>Q'}

class BinaryReader(object):
    def __init__(self, stream):
        self.stream = stream
        self.pos = 0


    def read_raw(self, size):
        """Read raw data as an 8-bit string."""
        self.pos += size
        return self.stream.read(size)

    def skip(self, size):
        """Skip forward (or backward, if 'size' is negative) in the stream."""
        self.pos += size
        self.stream.seek(size, 1)

    def skip_to(self, pos):
        """Skip to a specified position in the stream."""
        self.skip(pos - self.pos)

    def skip_padding(self, size, alignment):
        """Skip the padding bytes at the end of a structure that is 'size'
        bytes long and padded to the next multiple of 'alignment'.
        """
        if size % alignment == 0:
            return

        self.skip(alignment - size % alignment)


    def read_int(self, size):
        """Read a signed, big-endian integer of 'size' bytes.  'size' must be
        1, 2, 4, or 8.
        """
        assert size in INT_FORMATS
        buf = self.read_raw(size)
        result, = struct.unpack(INT_FORMATS[size], buf)
        return result

    def read_uint(self, size):
        """Read an unsigned, big-endian integer of 'size' bytes.  'size' must
        be 1, 2, 4, or 8.
        """
        assert size in UINT_FORMATS
        buf = self.read_raw(size)
        result, = struct.unpack(UINT_FORMATS[size], buf)
        return result

    def read_double(self):
        """Read a double (8 byte floating point number)."""
        buf = self.read_raw(8)
        result, = struct.unpack('>d', buf)
        return result
