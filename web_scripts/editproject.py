#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import jinja2
from django.utils import html

import authutils
import db
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
    jenv.filters['escapejs'] = html.escapejs
    is_valid, status_messages = valutils.validate_project_id(project_id)
    user = authutils.get_kerberos()
    can_edit = authutils.can_edit(user, project_id)
    authlink = authutils.get_auth_url(True)

    project_info = db.get_all_info_for_project(project_id)
    project_info = strutils.enrich_project_info_dict(project_info)

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
        authlink=authlink,
        project_info=project_info
    ).encode('utf-8')
    return result

    # TODO:
    # * Make form fields wider
    # * Handle escaped characters


def main():
    """Display the edit project interface.
    """
    arguments = cgi.FieldStorage()
    project_id = formutils.safe_cgi_field_get(arguments, 'project_id')

    page = format_edit_project(project_id)
    print(page)


if __name__ == '__main__':
    main()
