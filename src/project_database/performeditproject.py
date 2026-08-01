# TODO: May want to turn error listing off once stable?
import cgitb

import performutils

cgitb.enable()


def main():
    performutils.edit_confirm_main("Edit")


if __name__ == "__main__":
    main()
