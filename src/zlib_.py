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


class CompressionMethod(IntEnum):
    DEFLATE = 8
    RESERVED = 15


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
        fdict: bool = None
        flevel: CompressionLevel = None
        FMT = "!BB"

        def __init__(self, data=None, offset=0):
            if data is None:
                return
            cmf, flg = struct.unpack_from(self.FMT, data, offset)
            assert (flg | cmf << 8) % 31 == 0
            self.cm = CompressionMethod(cmf & 0b1111)
            cinfo = cmf >> 4 & 0b1111
            self.wbits = cinfo + 8
            self.fdict = flg >> 5 & 0b1
            self.flevel = CompressionLevel(flg >> 6 & 0b11)

        def __bytes__(self):
            cinfo = self.wbits - 8
            cmf = self.cm | cinfo << 4

            flg = self.fdict << 5 | self.flevel << 6
            # TODO: Do common implementations set fcheck to 0 if the modulus is 0?
            # Us setting it to 31 is correct, but could be unconventional.
            FCHECKBITS = 2**5 - 1
            fcheck = FCHECKBITS - (flg | cmf << 8) % FCHECKBITS
            flg |= fcheck

            return struct.pack(self.FMT, cmf, flg)

    header: Header = None
    compressed_data: bytes = None
    adler32: int = None

    def __init__(self, data=None, offset=0):
        if data is None:
            return
        self.header = self.Header(data, offset)
        offset += struct.calcsize(self.Header.FMT)
        self.compressed_data = data[offset:-4]
        self.adler32 = data[-4:]

    def __bytes__(self):
        data = bytearray()
        data += bytes(self.header)
        data += self.compressed_data
        data += struct.pack("!I", self.adler32)
        return bytes(data)

    def _setup_header(self, level, wbits):
        self.header = self.Header()
        self.header.cm = CompressionMethod.DEFLATE
        self.header.wbits = wbits
        # TODO: adjust according to level
        self.header.flevel = CompressionLevel.FASTEST
        self.header.fdict = False

    def _compress(self, uncompressed_data):
        import zlib

        # TODO
        self.compressed_data = uncompressed_data
        # TODO: compute this ourselves, remove zlib dep
        self.adler32 = zlib.adler32(uncompressed_data)

    def _decompress(self):
        # TODO return DECOMPRESSED data
        return self.compressed_data


def compress(data, /, level=Z_DEFAULT_COMPRESSION, wbits=MAX_WBITS):
    if level < Z_DEFAULT_COMPRESSION or level > Z_BEST_COMPRESSION:
        raise ValueError(f"invalid compression level {level}")
    if wbits < 9 or wbits > MAX_WBITS:
        raise ValueError(f"invalid window bits {wbits}")
    # TODO: implement compression
    if level != Z_NO_COMPRESSION:
        raise NotImplementedError()
    if level == Z_DEFAULT_COMPRESSION:
        level = 6

    zlib = Zlib()
    zlib._setup_header(level, wbits)
    zlib._compress(data)
    print(f"Created ZLIB container: {zlib}")
    return zlib


def decompress(data, /, wbits=MAX_WBITS):
    # TODO: support custom wbits (currently we take from the file)
    if wbits != 0:
        raise NotImplementedError()

    zlib = Zlib(data)
    print(f"Parsed ZLIB container: {zlib}")
    return zlib._decompress()


def main():
    import sys
    import zlib

    path_in = sys.argv[1]
    path_refout = "sample/output.reference.bin"
    path_out = "sample/output.bin"
    path_decout = "sample/outputdec.bin"
    path_dec2out = "sample/outputdec2.bin"

    with open(path_in, "rb") as f_in:
        data = f_in.read()
        print(f"read {len(data)} bytes from {path_in}")

    # Compression:

    with open(path_refout, "wb") as f_out:
        compressed_ref = zlib.compress(data, level=Z_NO_COMPRESSION)
        b_written = f_out.write(compressed_ref)
        print(f"wrote {b_written} bytes to {path_refout}")
    with open(path_out, "wb") as f_out:
        compressed_us = bytes(compress(data, Z_NO_COMPRESSION))
        b_written = f_out.write(compressed_us)
        print(f"wrote {b_written} bytes to {path_out}")

    # Decompression:

    with open(path_decout, "wb") as f_out:
        decompressed_us = decompress(compressed_ref, wbits=0)
        b_written = f_out.write(decompressed_us)
        print(f"wrote {b_written} bytes to {path_decout}")
    with open(path_dec2out, "wb") as f_out:
        decompressed_usthem = zlib.decompress(compressed_us, wbits=0)
        b_written = f_out.write(decompressed_usthem)
        print(f"wrote {b_written} bytes to {path_dec2out}")


if __name__ == "__main__":
    exit(main())
