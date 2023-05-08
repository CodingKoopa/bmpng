#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from bmp import Bmp


def main_loop():
    filename = input("what file would you like to open? (type EXIT to close program) ")
    if filename.upper() == "EXIT":
        print("goodbye!")
        quit()
    bmp = Bmp(filename=filename)
    if bmp.header.valid:
        # output = open("output_test.bmp", "wb")
        # output.write(bytes(bmp))
        # output.close()
        print("it's valid!:3")
        print("size = " + str(bmp.header.size) + " bytes")
        print("pixel array starting address: " + str(bmp.header.offset))
        print("width = " + str(bmp.dib.width) + " pixels")
        print("height = " + str(bmp.dib.height) + " pixels")
        print("color planes = " + str(bmp.dib.planes))
        print("bits per pixel = " + str(bmp.dib.bpp))
        print("compression method = " + str(bmp.dib.compression))
        print("image size = " + str(bmp.dib.img_size) + " bytes")
        print("horizonal resolution = " + str(bmp.dib.h_res) + " ppm")
        print("vertical resolution = " + str(bmp.dib.v_res) + " ppm")
        print("colors in palette = " + str(bmp.dib.palette))
        print("important colors = " + str(bmp.dib.important_colors))
        while True:
            # NOTE: 1-indexed, may change later
            request = input(
                "what pixel do you want color info on? "
                + "please answer in the form x y (type EXIT to close program) "
            )
            if request.upper() == "EXIT":
                print("goodbye!")
                quit()
            tokens = request.split()
            if len(tokens) != 2:
                print("please input exactly two numbers")
            x = int(tokens[0])
            y = int(tokens[1])
            if x == 0 or y == 0:
                print("please use 1-indexing")
                continue
            if x > bmp.dib.width or y > bmp.dib.height:
                print("please give a pixel that is in range of the image")
                continue
            if x < 0 or y < 0:
                print("please no negatives :(")
                continue
            pixel = bmp.arr[x - 1][y - 1]
            red = pixel[0]
            green = pixel[1]
            blue = pixel[2]
            print(
                f"R = {red}, G = {green}, B = {blue}; hex code = "
                + hex(red)
                + hex(green).lstrip("0x")
                + hex(blue).lstrip("0x")
            )


if __name__ == "__main__":
    main_loop()
