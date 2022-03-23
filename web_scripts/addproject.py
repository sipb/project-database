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
    # NOTE: the original HWOPS code sets the argument to "not user" (i.e., only
    # add the authentication port if there isn't a user). But, this doesn't
    # seem to work for me when running from my scripts account.
    authlink = authutils.get_auth_url(True)
    can_add = authutils.can_add(user)
    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('addproject.html').render(
        user=user,
        can_add=can_add,
        # TODO: what is the contact email for projects-db maintainers?
        help_address='useful-help-email-for-projects-db [at] mit [dot] edu',
        authlink=authlink
    ).encode('utf-8')
    return result


def main():
    """Display the add project interface.
    """
    page = format_add_project()
    print(page)


if __name__ == '__main__':
    main()
