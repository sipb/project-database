#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

import cgi

import formutils
import performutils
import strutils
import valutils

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()


def add_project(project_info):
    """Add the given project to the database.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.

    Returns
    -------
    project_id : int
        The project_id (primary key) for the newly-added project.
    """
    # TODO: this needs to be implemented!
    return -1


def main():
    """Respond to an add project request, displaying the appropriate status
    message.
    """
    arguments = cgi.FieldStorage()
    project_info = formutils.args_to_dict(arguments)
    is_ok, status_messages = valutils.validate_add_project(project_info)

    if is_ok:
        try:
            project_id = add_project(project_info)
            project_info['project_id'] = project_id
        except Exception:
            is_ok = False
            status = ''
            status += 'add_project failed with the following exception:\n'
            status += traceback.format_exc()
            status_messages = [status]

    if is_ok:
        page = performutils.format_success_page(project_info, 'Add Project')
    else:
        page = performutils.format_failure_page(
            strutils.html_listify(status_messages), 'Add Project'
        )

    print(page)


if __name__ == '__main__':
    main()
