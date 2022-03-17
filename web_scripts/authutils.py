# Based on:
# https://github.com/sipb/hwops/blob/master/web_scripts/kerbparse.py
# https://github.com/sipb/hwops/blob/master/web_scripts/main.py

import os


def get_kerberos():
    """Get the kerberos of the user. Returns None if there is no user.
    """
    email = os.getenv('SSL_CLIENT_S_DN_Email')
    if (
        (email is None) or
        (not email.lower().endswith('@mit.edu')) or
        (email.count('@') != 1)
    ):
        return None
    return email[:email.index('@')]


def get_base_url(do_authenticate):
    host = os.environ['HTTP_HOST'].split(':')[0]
    if do_authenticate:
        return 'https://%s:444' % host
    else:
        return 'https://%s' % host


def get_auth_url(do_authenticate):
    return (
        get_base_url(do_authenticate=do_authenticate) +
        os.environ['REQUEST_URI']
    )
