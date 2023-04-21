#!/usr/bin/env python3

import struct
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


def write_header(data, level, wbits):
    cmf = CompressionMethod.DEFLATE | ((wbits - 8) << 4)

    fdict = 0
    # TODO: adjust according to level (this is just what zlib sets it to)
    flevel = CompressionLevel.FASTEST
    flg = (fdict << 5) | (flevel << 6)
    checknum = (cmf << 8) | flg
    # TODO: Do common implementations set fcheck to 0 if the modulus is 0?
    # Us setting it to 31 is correct, but could be unconventional.
    FCHECKBITS = 2**5 - 1
    fcheck = FCHECKBITS - (checknum % FCHECKBITS)
    flg |= fcheck

    data.extend(struct.pack("!BB", cmf, flg))


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

    data = bytearray()
    write_header(data, level, wbits)
    # TODO: write compressed data
    # TODO: write checksum
    return data


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
        b_written = f_out.write(compress(data, Z_NO_COMPRESSION))
        print(f"wrote {b_written} bytes to {path_out}")


if __name__ == "__main__":
    exit(main())
