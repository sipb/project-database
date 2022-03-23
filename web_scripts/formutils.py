def safe_cgi_field_get(arguments, field, default=''):
    """Get a field from CGI arguments, with failback for absent fields.

    Parameters
    ----------
    arguments : cgi.FieldStorage
        The data from the form.
    field : str
        The field to get.
    default : str, optional
        The value to use when a field is not present. Default is the empty
        string.

    Returns
    -------
    value : str
        The field value.
    """
    return arguments[field].value if field in arguments else default
