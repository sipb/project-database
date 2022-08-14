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

def format_faq():
    """Format FAQ template into an HTML page.
    
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
    can_approve = authutils.can_approve(user)

    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('faq.html').render(
        user=user,
        user_email=user_email,
        authlink=authlink,
        deauthlink=deauthlink,
        can_add=can_add,
        can_approve=can_approve
    ).encode('utf-8')
    return result


def main():
    """Display the edit project interface.
    """
    page = format_faq()
    print(page)


if __name__ == '__main__':
    main()
