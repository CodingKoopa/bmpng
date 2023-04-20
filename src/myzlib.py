#!/usr/bin/env python3


def compress(data):
    pass


def main():
    import sys
    import zlib

    path_in = sys.argv[1]
    path_out = "sample/output.reference.bin"

    with open(path_in, "rb") as f_in:
        data = f_in.read()
        print(f"read {len(data)} bytes from {path_in}")
    with open(path_out, "wb") as f_out:
        b_written = f_out.write(zlib.compress(data))
        print(f"wrote {b_written} bytes to {path_out}")


if __name__ == "__main__":
    exit(main())
