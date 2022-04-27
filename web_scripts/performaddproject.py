#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

import cgi

import authutils
import formutils
import performutils
import strutils
import valutils
import db

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()


def main():
    """Respond to an add project request, displaying the appropriate status
    message.
    """
    arguments = cgi.FieldStorage()
    project_info = formutils.args_to_dict(arguments)
    is_ok, status_messages = valutils.validate_add_project(project_info)

    if is_ok:
        try:
            project_id = db.add_project(project_info, authutils.get_kerberos())
            assert project_id != -1
            project_info['project_id'] = project_id
        except Exception:
            is_ok = False
            status = ''
            status += 'add_project failed with the following exception:\n'
            status += traceback.format_exc()
            status_messages = [status]

    if is_ok:
        page = performutils.format_success_page(project_id, 'Add Project')
    else:
        page = performutils.format_failure_page(
            strutils.html_listify(status_messages), 'Add Project'
        )

    print(page)


if __name__ == '__main__':
    main()
