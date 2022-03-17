#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jinja2

import db


def format_project_list(project_list):
    """Format a list of projects into an HTML page.

    Parameters
    ----------
    project_list : list of dict
        The projects to list.

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
    result += jenv.get_template('projectlist.html').render(
        project_list=project_list
    ).encode('utf-8')
    return result


def main():
    """Display the info for all projects.
    """
    project_list = db.get_all_project_info()
    page = format_project_list(project_list)
    print(page)


if __name__ == '__main__':
    main()
