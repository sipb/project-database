# Based on:
# https://github.com/sipb/hwops/blob/master/web_scripts/kerbparse.py
# https://github.com/sipb/hwops/blob/master/web_scripts/main.py
# https://github.com/sipb/hwops/blob/master/web_scripts/moira.py

import os

# import moira


def get_kerberos():
    """Get the kerberos of the user. Returns None if there is no user.

    Returns
    -------
    kerberos : str
        The kerberos (username only) for the user.
    """
    email = os.getenv('SSL_CLIENT_S_DN_Email')
    if (
        (email is None) or
        (not email.lower().endswith('@mit.edu')) or
        (email.count('@') != 1)
    ):
        return None
    else:
        return email[:email.index('@')]


def get_base_url(do_authenticate):
    """Get the base URL.

    Parameters
    ----------
    do_authenticate : bool
        Whether or not to add port 444 to trigger authentication.

    Returns
    -------
    url : str
        The base URL.
    """
    host = os.environ['HTTP_HOST'].split(':')[0]
    if do_authenticate:
        return 'https://%s:444' % host
    else:
        return 'https://%s' % host


def get_auth_url(do_authenticate):
    """Get the authentication URL.

    Parameters
    ----------
    do_authenticate : bool
        Whether or not to add port 444 to trigger authentication.

    Returns
    -------
    url : str
        The authentication URL.
    """
    return get_base_url(do_authenticate) + os.environ['REQUEST_URI']


def is_sipb(user):
    # TODO: scripts can't access moira anymore. What is an alternate way to
    # check if a user is in SIPB? Do we have a member database mirrored
    # somewhere?
    # return moira.has_access(user, 'sipb-office@mit.edu')
    return True


def can_add(user):
    """Determine whether the given user has add permission.

    Parameters
    ----------
    user : str
        The kerberos of the user.

    Returns
    -------
    can_add : bool
        Whether or not the user can add projects.
    """
    if not user:
        return False
    elif is_sipb(user):
        return True
    else:
        return False
