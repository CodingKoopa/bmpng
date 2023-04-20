# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later


def gui():
    from gui import Gui

    window = Gui()
    window.mainloop()
    return 0


def tui():
    import tui

    tui.main_loop()
    return 0


def cli():
    import argparse

    parser = argparse.ArgumentParser(
        prog="bmpng",
        description="Encode and decode PNG files",
    )
    subparsers = parser.add_subparsers(title="interfaces", dest="interface")
    parser_cli = subparsers.add_parser(
        "cli", help="use the command line interface (default)"
    )
    parser_tui = subparsers.add_parser("tui", help="use the text user interface")
    parser_gui = subparsers.add_parser("gui", help="use the graphical user interface")
    parser_gui.add_argument("-b", type=str, help="help for b")

    args = parser.parse_args()

    if args.interface == "gui":
        return gui()
    elif args.interface == "tui":
        return tui()

    print("CLI not implemented yet")
    return 0


if __name__ == "__main__":
    exit(cli())
