#!/usr/bin/env python
# -*- coding: utf-8 -*-

import authutils
import templateutils


def format_add_project():
    """Format the add project interface.

    Returns
    -------
    result : str
        The HTML to display.
    """
    jenv = templateutils.get_jenv()
    user = authutils.get_kerberos()
    authlink = authutils.get_auth_url(True)
    deauthlink = authutils.get_auth_url(False)
    can_add = authutils.can_add(user)
    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('addproject.html').render(
        user=user,
        can_add=can_add,
        # TODO: what is the contact email for projects-db maintainers?
        help_address='useful-help-email-for-projects-db [at] mit [dot] edu',
        authlink=authlink,
        deauthlink=deauthlink,
        operation='Create project'
    ).encode('utf-8')
    return result


def main():
    """Display the add project interface.
    """
    page = format_add_project()
    print(page)


if __name__ == '__main__':
    main()
