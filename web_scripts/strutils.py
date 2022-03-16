def obfuscate_email(email):
    """Obfuscate an email address to mitigate simple spam bots.

    Parameters
    ----------
    email : str
        The raw email address.

    Returns
    -------
    email_obfuscated : str
        The obfuscated email address.
    """
    return email.replace('@', ' [at] ').replace('.', ' [dot] ')
