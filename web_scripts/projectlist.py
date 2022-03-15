#!/usr/bin/python

import db


def render_project_list(project_list):
    print('Content-type: text/html\n')
    print('<html>')
    print('Received %d project(s)' % len(project_list))
    for key in project_list[0].keys():
        print(key)
    print('</html>')


def main():
    project_list = db.list_dict_convert(db.get_all_projects())
    render_project_list(project_list)


if __name__ == '__main__':
    main()
