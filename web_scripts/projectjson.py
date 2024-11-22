#!/usr/bin/env python
# -*- coding: utf-8 -*-

import db
import json
import templateutils

# TODO: May want to turn error listing off once stable?
import cgitb
cgitb.enable()

def main():
    """Display the info for all projects.
    """
    
    jenv = templateutils.get_jenv()
    all_projects_list = db.list_dict_convert(db.get_all_project_info('approved') ,remove_sql_ref=True)
    all_projects_json = json.dumps({"projects": all_projects_list})
    
    result = ''
    result += 'Content-type: application/json\n\n'
    result += all_projects_json
    print(result)


if __name__ == '__main__':
    main()
