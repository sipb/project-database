#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import jinja2

import authutils
import formutils
import strutils
import valutils

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()


def format_edit_project(project_id):
    """Format the edit project interface.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        autoescape=True
    )
    is_valid, status_messages = valutils.validate_project_id(project_id)
    user = authutils.get_kerberos()
    can_edit = authutils.can_edit(user, project_id)
    authlink = authutils.get_auth_url(True)

    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('editproject.html').render(
        user=user,
        is_valid=is_valid,
        validation_status=(
            strutils.html_listify(status_messages) if not is_valid else ''
        ),
        can_edit=can_edit,
        help_address='useful-help-email-for-projects-db [at] mit [dot] edu',
        authlink=authlink
    ).encode('utf-8')
    return result


def main():
    """Display the edit project interface.
    """
    arguments = cgi.FieldStorage()
    project_id = formutils.safe_cgi_field_get(arguments, 'project_id')

    page = format_edit_project(project_id)
    print(page)


if __name__ == '__main__':
    main()
