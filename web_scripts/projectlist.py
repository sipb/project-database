#!/usr/bin/python

import db


def render_project_list(project_list):
    print('Content-type: text/html\n')
    print('<html>\n')
    print('Received %d project(s)\n' % len(project_list))
    for key, value in project_list[0].items():
        print('%s: %s\n' % (key, value))
    print('</html>')


def main():
    project_list = db.list_dict_convert(db.get_all_projects())
    render_project_list(project_list)


if __name__ == '__main__':
    main()
