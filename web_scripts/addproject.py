#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jinja2


def format_add_project():
    """Format the add project interface.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        autoescape=True
    )
    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('addproject.html').render(
        # TODO: Get user and permissions properly!
        user='markchil',
        can_add=True,
        help_address='dev [slash] null'
    ).encode('utf-8')
    return result


def main():
    """Display the add project interface.
    """
    page = format_add_project()
    print(page)


if __name__ == '__main__':
    main()
