#!/usr/bin/python

import db


def render_project_list(project_list):
    print('Content-type: text/html\n')
    print('<html>')
    print('Received %d project(s)' % len(project_list))
    print('</html>')


def main():
    project_list = db.list_dict_convert(db.get_all_projects())
    render_project_list(project_list)


if __name__ == '__main__':
    main()
