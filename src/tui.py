#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from bmp import Bmp


def main_loop():
    filename = input("what file would you like to open? (type EXIT to close program) ")
    if filename.upper() == "EXIT":
        print("goodbye!")
        quit()
    bmp = Bmp(filename)
    if bmp.valid:
        print("it's valid!:3")
        print("size = " + str(bmp.size) + " bytes")
        print("pixel array starting address: " + str(bmp.startingAddress))
        print("width = " + str(bmp.width) + " pixels")
        print("height = " + str(bmp.height) + " pixels")
        print("color planes = " + str(bmp.planes))
        print("bits per pixel = " + str(bmp.bpp))
        print("compression method = " + str(bmp.compression))
        print("image size = " + str(bmp.imgSize) + " bytes")
        print("horizonal resolution = " + str(bmp.horizontalRes) + " ppm")
        print("vertical resolution = " + str(bmp.verticalRes) + " ppm")
        print("colors in palette = " + str(bmp.palatte))
        print("important colors = " + str(bmp.importantColors))
        while True:
            # NOTE: 1-indexed, may change later
            request = input(
                "what pixel do you want color info on?"
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
            if x > bmp.width or y > bmp.height:
                print("please give a pixel that is in range of the image")
                continue
            if x < 0 or y < 0:
                print("please no negatives :(")
                continue
            pixel = bmp.arr[x-1][y-1]
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
