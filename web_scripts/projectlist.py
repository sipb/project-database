#!/usr/bin/python

import jinja2

import db


def render_project_list(project_list):
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=True
    )

    print('Content-type: text/html\n')
    print(
        jenv.get_template('projectlist.html').render(
            project_list=project_list
        ).encode('utf-8')
    )


def main():
    project_list = db.list_dict_convert(db.get_all_projects())
    render_project_list(project_list)


if __name__ == '__main__':
    main()
