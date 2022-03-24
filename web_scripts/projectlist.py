#!/usr/bin/env python
# -*- coding: utf-8 -*-

import authutils
import db
import strutils
import templateutils

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()


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
    jenv = templateutils.get_jenv()
    user = authutils.get_kerberos()
    project_list = authutils.enrich_project_list_with_permissions(
        user, project_list
    )
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)
    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('projectlist.html').render(
        project_list=project_list,
        user=user,
        authlink=authlink,
        deauthlink=deauthlink,
        can_add=can_add
    ).encode('utf-8')
    return result


def main():
    """Display the info for all projects.
    """
    project_list = db.get_all_project_info()
    project_list = strutils.obfuscate_project_info_dicts(project_list)
    project_list = strutils.make_project_info_dicts_links_absolute(
        project_list
    )
    page = format_project_list(project_list)
    print(page)


if __name__ == '__main__':
    main()
