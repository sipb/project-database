#!/usr/bin/python
# -*- coding: utf-8 -*-

import jinja2

import db


def format_project_list(project_list):
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=True
    )
    result = u''
    result += 'Content-type: text/html\n'
    result += jenv.get_template('projectlist.html').render(
        project_list=project_list
    ).encode('utf-8')
    return result


def obfuscate_email(email):
    return email.replace('@', ' [at] ').replace('.', ' [dot] ')


def get_project_table():
    project_list = db.list_dict_convert(db.get_all_projects())
    for project in project_list:
        project_id = project['project_id']
        project['links'] = [
            link['link'] for link in db.get_links(project_id)
        ]
        project['comm_channels'] = [
            obfuscate_email(channel['commchannel'])
            for channel in db.get_comm(project_id)
        ]
        project['roles'] = db.get_roles(project_id)
        project['contacts'] = db.get_contacts(project_id)
        for contact in project['contacts']:
            contact['email'] = obfuscate_email(contact['email'])
    return project_list


def main():
    project_list = get_project_table()
    page = format_project_list(project_list)
    print(page)


if __name__ == '__main__':
    main()
