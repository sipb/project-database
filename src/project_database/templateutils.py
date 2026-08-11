import json
import os

import jinja2

from . import strutils

TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../../templates"
)


def escapejs(value):
    """Escape a value for safe embedding inside a JavaScript string literal."""
    return json.dumps(str(value))[1:-1]


def get_jenv():
    """Get the jinja environment."""
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR), autoescape=True
    )
    jenv.filters["escapejs"] = escapejs
    jenv.filters["obfuscate_email"] = strutils.obfuscate_email
    return jenv
