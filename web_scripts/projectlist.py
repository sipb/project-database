#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi

import authutils
import db
import formutils
import strutils
import templateutils

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()


def format_project_list(project_list, filter_method, contact_email):
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
    jenv = templateutils.get_jenv()
    user = authutils.get_kerberos()
    user_email = authutils.get_email()
    project_list = authutils.enrich_project_list_with_permissions(
        user, project_list
    )
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)

    if filter_method == 'all':
        title = 'SIPB Project List'
    elif filter_method == 'active':
        title = 'SIPB Active Project List'
    elif filter_method == 'inactive':
        title = 'SIPB Inactive Project List'
    elif filter_method == 'contact':
        title = 'SIPB Projects for Which %s Is a Contact' % contact_email
    else:
        raise ValueError('Unknown filter method!')

    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('projectlist.html').render(
        project_list=project_list,
        user=user,
        user_email=user_email,
        authlink=authlink,
        deauthlink=deauthlink,
        can_add=can_add,
        title=title
    ).encode('utf-8')
    return result


def main():
    """Display the info for all projects.
    """
    arguments = cgi.FieldStorage()
    filter_method = formutils.safe_cgi_field_get(
        arguments, 'filter_by', default='all'
    )

    if filter_method == 'contact':
        contact_email = formutils.safe_cgi_field_get(
            arguments, 'email', default=''
        )
    else:
        contact_email = None

    project_list = db.get_all_project_info(
        filter_method=filter_method, contact_email=contact_email
    )
    # project_list = strutils.make_project_info_dicts_links_absolute(
    #     project_list
    # )
    page = format_project_list(project_list, filter_method, contact_email)
    print(page)


if __name__ == '__main__':
    main()
