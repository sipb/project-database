#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import jinja2


def add_project(arguments):
    # import pickle as pkl
    # with open('results.pkl', 'wb') as pf:
    #     pkl.dump(arguments, pf)
    pass


def render_result_page(arguments):
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        autoescape=True
    )
    result = ''
    result += 'Content-type: text/html\n\n'
    result += jenv.get_template('performaddprojectsuccess.html').render(
        name=arguments['name'].value,
        description=arguments['description'].value,
        status=arguments['status'].value,
        links=arguments['links'].value,
        comm_channels=arguments['comm_channels'].value,
        contacts=arguments['contacts'].value,
        role_names=[arguments['role_name_0'].value, arguments['role_name_1'].value],
        role_descriptions=[arguments['role_description_0'].value, arguments['role_description_1'].value],
        role_prereqs=[arguments['role_prereqs_0'].value, arguments['role_prereqs_1'].value]
    ).encode('utf-8')
    return result


def main():
    arguments = cgi.FieldStorage()
    add_project(arguments)
    page = render_result_page(arguments)
    print(page)


if __name__ == '__main__':
    main()
