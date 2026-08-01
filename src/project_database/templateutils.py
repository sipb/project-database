import jinja2
import strutils
from django.utils import html


def get_jenv():
    """Get the jinja environment."""
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"), autoescape=True
    )
    jenv.filters["escapejs"] = html.escapejs
    jenv.filters["obfuscate_email"] = strutils.obfuscate_email
    return jenv
