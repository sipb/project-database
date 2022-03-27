import jinja2
from django.utils import html

import strutils


def linkify(text):
    """Convert the given input to an HTML link of the appropriate type.
    """
    if text.startswith('http://') or text.startswith('https://'):
        return '<a href="%s">%s</a>' % (text, text)
    elif strutils.isemail(text):
        return '<a href="mailto:%s">%s</a>' % (text, text)
    else:
        return text


def get_jenv():
    """Get the jinja environment.
    """
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        autoescape=True
    )
    jenv.filters['escapejs'] = html.escapejs
    jenv.filters['linkify'] = linkify
    return jenv
