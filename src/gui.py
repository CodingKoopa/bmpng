#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

import os
import tkinter
from tkinter import Label, filedialog, ttk

from bmp import Bmp

dirname = os.path.dirname(__file__)


class Display(ttk.Frame):
    def __init__(self, container, file):
        super().__init__(container)
        if file.header.valid:
            Label(text="it's valid!").grid(row=0, column=0, padx=10, pady=3, sticky="w")
        else:
            Label(text="invalid bitmap").grid(
                row=0, column=0, padx=10, pady=3, sticky="w"
            )
            pass
        Label(text=f"file size = {file.header.size} bytes").grid(
            row=1, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"pixel array starting address = {file.header.offset}").grid(
            row=2, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"width = {file.dib.width} pixels").grid(
            row=3, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"height = {file.dib.height} pixels").grid(
            row=4, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"color planes = {file.dib.planes} ").grid(
            row=5, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"bits per pixel = {file.dib.bpp}").grid(
            row=6, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"compression method = {file.dib.compression}").grid(
            row=7, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"image size = {file.dib.img_size} bytes").grid(
            row=8, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"horizontal resolution = {file.dib.h_res} ppm").grid(
            row=9, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"vertical resolution = {file.dib.v_res} ppm").grid(
            row=10, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"colors in palatte = {file.dib.palette}").grid(
            row=11, column=0, padx=10, pady=3, sticky="w"
        )
        Label(text=f"imporant colors = {file.dib.important_colors}").grid(
            row=12, column=0, padx=10, pady=3, sticky="w"
        )


class StartPage(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.chomp = tkinter.PhotoImage(
            file=os.path.join(dirname, "data/assets/chompchomp-small.png")
        )
        open_button = ttk.Button(
            self,
            image=self.chomp,
            text="feed me bitmaps",
            compound=tkinter.RIGHT,
            command=lambda: self.select_file(container),
        )
        open_button.pack(expand=True)
        self.pack(expand=True)

    def select_file(self, container):
        filetypes = (("bitmap image", "*.bmp"), ("all files", "*.*"))
        filename = filedialog.askopenfilename(
            title="bmp plz",
            initialdir=os.path.join(dirname, "../sample"),
            filetypes=filetypes,
        )
        if filename != "":
            bmp = Bmp(filename)
            self.pack_forget()
            display = Display(container=container, file=bmp)
            display.tkraise()
            # message = "File size is " + str(bmp.getSize()) + " bytes"
            # showinfo(title='file info', message=message)


class Gui(tkinter.Tk):
    def __init__(self):
        super().__init__()

        if "nt" == os.name:
            self.iconbitmap(os.path.join(dirname, "data/assets/icon.ico"))
        else:
            self.iconbitmap("@" + os.path.join(dirname, "data/assets/icon.xbm"))
        self.title("bitmap decoder")
        window_width = int(self.winfo_screenwidth() / 4)
        window_height = int(self.winfo_screenheight() / 2)
        window_x = int(self.winfo_screenwidth() / 16)
        window_y = int(self.winfo_screenheight() / 16)
        self.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
        StartPage(self)


if __name__ == "__main__":
    gui = Gui()
    gui.mainloop()
