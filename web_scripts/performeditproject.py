#!/usr/bin/env python
# -*- coding: utf-8 -*-

import performutils

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()


def main():
    performutils.edit_confirm_main('Edit')


if __name__ == '__main__':
    main()
