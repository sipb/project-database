#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi

import authutils
import db
import formutils
import strutils
import templateutils
import valutils

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()


def format_approve_project(project_id):
    """Format the approve project interface.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = templateutils.get_jenv()
    is_valid, status_messages = valutils.validate_project_id(project_id)
    user = authutils.get_kerberos()
    can_approve = authutils.can_edit(user)
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)

    project_info = db.get_all_info_for_project(project_id)

    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('approveproject.html').render(
        user=user,
        is_valid=is_valid,
        validation_status=(
            strutils.html_listify(status_messages) if not is_valid else ''
        ),
        can_approve=can_approve,
        help_address='useful-help-email-for-projects-db [at] mit [dot] edu',
        authlink=authlink,
        project_info=project_info,
        project_id=project_id,
        deauthlink=deauthlink,
        can_add=can_add,
        operation='Submit'
    ).encode('utf-8')
    return result


def main():
    """Display the edit project interface.
    """
    arguments = cgi.FieldStorage()
    project_id = formutils.safe_cgi_field_get(arguments, 'project_id')

    page = format_approve_project(project_id)
    print(page)


if __name__ == '__main__':
    main()
