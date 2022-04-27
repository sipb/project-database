#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi

import authutils
import db
import formutils
import templateutils

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()


def format_project_history(project_history):
    """Format a list of project revisions into an HTML page.

    Parameters
    ----------
    project_history : list of dict
        The project revisions to list.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = templateutils.get_jenv()
    user = authutils.get_kerberos()
    user_email = authutils.get_email()
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)

    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('projecthistory.html').render(
        project_history=project_history,
        user=user,
        user_email=user_email,
        authlink=authlink,
        deauthlink=deauthlink,
        can_add=can_add
    ).encode('utf-8')
    return result


def main():
    """Display the info for all project revisions.
    """
    arguments = cgi.FieldStorage()
    project_id = formutils.safe_cgi_field_get(
        arguments, 'project_id', default=None
    )
    # TODO: this should show a proper error page
    if project_id is None:
        raise RuntimeError('No project ID specified!')

    project_history = db.get_project_history(project_id)
    page = format_project_history(project_history)
    print(page)


if __name__ == '__main__':
    main()
