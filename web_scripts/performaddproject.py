#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import jinja2


def add_project(arguments):
    # import pickle as pkl
    # with open('results.pkl', 'wb') as pf:
    #     pkl.dump(arguments, pf)
    pass


def render_result_page():
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        autoescape=True
    )
    result = ''
    result += 'Content-type: text/html\n\n'
    result += '<!DOCTYPE html>\n<html lang="en">\n<head>\n<title>success?</title>\n</head>\n<body>\n<p>hello</p>\n</body>\n</html>\n'
    # result += jenv.get_template('projectlist.html').render().encode('utf-8')
    return result


def main():
    arguments = cgi.FieldStorage()
    add_project(arguments)
    page = render_result_page()
    print(page)


if __name__ == '__main__':
    main()
