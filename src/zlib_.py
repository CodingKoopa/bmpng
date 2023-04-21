#!/usr/bin/env python3

import struct
from dataclasses import dataclass
from enum import IntEnum

# zlib container RFC: https://www.rfc-editor.org/rfc/rfc1950

Z_NO_COMPRESSION = 0
Z_BEST_COMPRESSION = 9
Z_DEFAULT_COMPRESSION = -1

MIN_WBITS = 9
MAX_WBITS = 15


# Corresponds with CM.
class CompressionMethod(IntEnum):
    DEFLATE = 8
    RESERVED = 15


# Corresponds with FLEVEL.
class CompressionLevel(IntEnum):
    FASTEST = 0
    FAST = 1
    DEFAULT = 2
    SLOWEST = 3


@dataclass
class Zlib:
    @dataclass
    class Header:
        cm: CompressionMethod = None
        wbits: int = None
        flevel: CompressionLevel = None
        fdict: bool = None

        def __bytes__(self):
            cinfo = self.wbits - 8
            cmf = self.cm | cinfo << 4

            flg = (self.fdict << 5) | (self.flevel << 6)
            # TODO: Do common implementations set fcheck to 0 if the modulus is 0?
            # Us setting it to 31 is correct, but could be unconventional.
            FCHECKBITS = 2**5 - 1
            fcheck = FCHECKBITS - ((cmf << 8 | flg)) % FCHECKBITS
            flg |= fcheck

            return struct.pack("!BB", cmf, flg)

    header: Header = None
    compressed_data: bytes = None
    adler32: int = None

    def __bytes__(self):
        data = bytearray()
        data += bytes(self.header)
        data += self.compressed_data
        data += struct.pack("!I", self.adler32)
        return bytes(data)

    # Utilities for parsing a zlib container:

    @classmethod
    def from_data(data):
        # TODO: read header, store COMPRESSED data
        pass

    def decompress_data(self):
        # TODO return DECOMPRESSED data
        return self.compressed_data

    # Utilities for creating a zlib container:

    def setup_header(self, level, wbits):
        self.header = Zlib.Header()
        self.header.cm = CompressionMethod.DEFLATE
        self.header.wbits = wbits
        # TODO: adjust according to level
        self.header.flevel = CompressionLevel.FASTEST
        self.header.fdict = False

    def compress(self, uncompressed_data):
        # TODO
        self.compressed_data = uncompressed_data
        self.adler32 = 0


def compress(data, /, level=Z_DEFAULT_COMPRESSION, wbits=MAX_WBITS):
    if level < Z_DEFAULT_COMPRESSION or level > Z_BEST_COMPRESSION:
        raise ValueError(f"invalid compression level {level}")
    if wbits < 9 or wbits > MAX_WBITS:
        raise ValueError(f"invalid wbits {wbits}")
    # TODO: implement compression
    if level != Z_NO_COMPRESSION:
        raise NotImplementedError()
    if level == Z_DEFAULT_COMPRESSION:
        level = 6

    zlib = Zlib()
    zlib.setup_header(level, wbits)
    zlib.compress(data)

    return zlib


def main():
    import sys
    import zlib

    path_in = sys.argv[1]
    path_refout = "sample/output.reference.bin"
    path_out = "sample/output.bin"

    with open(path_in, "rb") as f_in:
        data = f_in.read()
        print(f"read {len(data)} bytes from {path_in}")
    with open(path_refout, "wb") as f_out:
        b_written = f_out.write(zlib.compress(data, level=Z_NO_COMPRESSION))
        print(f"wrote {b_written} bytes to {path_refout}")
    with open(path_out, "wb") as f_out:
        z = compress(data, Z_NO_COMPRESSION)
        b_written = f_out.write(bytes(z))
        print(f"wrote {b_written} bytes to {path_out}")


if __name__ == "__main__":
    exit(main())
