#!/usr/bin/python
from schema import *


##############################################################
## Database Operations
##############################################################

# General Purpose

def db_add(x):
    '''
    Add an object defined by the Schema to the database
    and commits the change
    '''
    session.add(x)
    session.commit()
    
def list_dict_convert(query_res_lst):
    '''
    Given a list which contains query results from SQLalchemy,
    return a list of their Python dictionary representation
    
    Source: https://stackoverflow.com/questions/1958219/how-to-convert-sqlalchemy-row-object-to-a-python-dict
    '''
    return [r.__dict__ for r in query_res_lst]

def check_object_params(dict,req_params):
    '''
    Check if a given dictionary has all of the keys defined in req_params (lst)
    '''
    res = True
    for param in req_params:
        if param not in dict:
            res = False
    return res

# DB specific

def get_all_projects():
    '''Get metadata all of projects in database'''
    return session.query(Projects).all()

def get_project_info(model,project_id):
    '''
    Given an SQL class model (e.g. ContactEmail, Roles, Links, etc.), query that table
    for all entries associated with project_id and return the result in the form of 
    list of dictionaries
    
    Useful for building higher-level queries
    '''
    sql_result = session.query(model).filter_by(project_id=project_id).all()
    return list_dict_convert(sql_result)

## Shorthand functions to get all table entries associated with a project ID `id`
get_project = lambda id: get_project_info(Projects,id) # Return maximum 1 result
get_contacts = lambda id: get_project_info(ContactEmails,id)
get_roles = lambda id: get_project_info(Roles,id)
get_links = lambda id: get_project_info(Links,id)
get_comm = lambda id: get_project_info(CommChannels, id)

def get_project_id(name):
    '''
    Get the ID of a project with `name`, if it exists
    Otherwise returns None
    '''
    project = session.query(Projects).filter_by(name=name).one_or_none()
    if project:
        return project.project_id
    return None


def get_all_info_for_project(project_id):
    """Get all of the information for a specific project.

    Parameters
    ----------
    project_id : str or int
        The project ID to get information for.

    Returns
    -------
    project_info : dict
        The information on the specified project.
    """
    # May want to figure out a way to remove redundancy with
    # get_all_project_info...
    project_info = get_project(project_id)[0]
    project_info['links'] = [
        link['link'] for link in get_links(project_id)
    ]
    project_info['comm_channels'] = [
        channel['commchannel'] for channel in get_comm(project_id)
    ]
    project_info['roles'] = get_roles(project_id)
    project_info['contacts'] = get_contacts(project_id)

    return project_info


def get_all_project_info():
    """Get the information for all projects.

    Returns
    -------
    project_list : list of dict
        List of all projects.
    """
    project_list = list_dict_convert(get_all_projects())
    # There's probably a way to do this with joins...
    for project in project_list:
        project_id = project['project_id']
        project['links'] = [
            link['link'] for link in get_links(project_id)
        ]
        project['comm_channels'] = [
            channel['commchannel'] for channel in get_comm(project_id)
        ]
        project['roles'] = get_roles(project_id)
        project['contacts'] = get_contacts(project_id)
        
    return project_list


# Adding entry to each table

def add_project_metadata(args):
    '''
    Add a project with provided metadata to the database
    
    Requires: 
        - args to have keys of 'name', 'status', 'description' with valid types
        - status is either 'active' or 'inactive'
    Returns: project_id associated with newly created project, None if project already exists or invalid arguments
    '''
    try:
        args_lst = ['name','status','description']
        assert check_object_params(args,args_lst)
        assert args['status'] in ['active','inactive']
    except AssertionError:
        return None
    
    # Check if project already exists
    exists = True if get_project_id(args['name']) else False
    if exists:
        return None

    project = Projects()
    project.name = args['name']
    project.status = args['status']
    project.description = args['description']
    db_add(project)
    return get_project_id(args['name'])
    
def add_project_contacts(project_name, args):
    '''
    Add a list of emails associated with a project to the database
    
    Requires: 
        - args to be list of dictionaries with keys 'type','email' 
        - key 'type' is either 'primary' or 'secondary'
    Returns: 
        - None if no project with that name or invalid arguments, otherwise 
        returns list of all emails associated with project in DB
    '''
    try:
        args_lst = ['type','email']
        for dict in args:
            assert check_object_params(dict,args_lst)
            assert dict['type'] in ['primary','secondary']
    except AssertionError:
        return None
    
    # Get project ID
    project_id = get_project_id(project_name)
    if not project_id:
        return None
    
    for entry in args:
        contact = ContactEmails()
        contact.project_id = project_id
        contact.type = entry['type']
        contact.email = entry['email']
        db_add(contact)
    return get_contacts(project_id)

def add_project_roles(project_name, args):
    '''
    Add a list of roles associated with a project to the database
    
    Requires: 
        - args to be list of dictionaries with keys 'role','description', and (optional) 'prereq' 
    Returns: 
        - None if no project with that name or invalid arguments, otherwise 
        returns list of all roles associated with project in DB
    '''
    try:
        args_lst = ['role','description'] # 'prereq' optional 
        for dict in args:
            assert check_object_params(dict,args_lst)
    except AssertionError:
        return None
    
    # Get project ID
    project_id = get_project_id(project_name)
    if not project_id:
        return None
    
    for entry in args:
        role = Roles()
        role.project_id = project_id
        role.role = entry['role']
        role.description = entry['description']
        if 'prereq' in entry:
            role.prereq = entry['prereq']
        db_add(role)
    return get_roles(project_id)

def add_project_links(project_name, args):
    '''
    Add a list of website links associated with a project to the database
    
    Requires: 
        - args to be list of dictionaries with keys 'link'
    Returns: 
        - None if no project with that name or invalid arguments, otherwise 
        returns list of all links associated with project in DB
    '''
    try:
        args_lst = ['link'] 
        for dict in args:
            assert check_object_params(dict,args_lst)
    except AssertionError:
        return None
    
    # Get project ID
    project_id = get_project_id(project_name)
    if not project_id:
        return None
    
    for entry in args:
        link = Links()
        link.project_id = project_id
        link.link = entry['link']
        db_add(link)
    return get_links(project_id)

def add_project_comms(project_name, args):
    '''
    Add a list of communication channels associated with a project to the database
    CommChannels can be text description rather than just HTML links
    
    Requires: 
        - args to be list of dictionaries with keys 'commchannel'
    Returns: 
        - None if no project with that name or invalid arguments, otherwise 
        returns list of all communication channels associated with project in DB
    '''
    try:
        args_lst = ['commchannel'] 
        for dict in args:
            assert check_object_params(dict,args_lst)
    except AssertionError:
        return None
    
    # Get project ID
    project_id = get_project_id(project_name)
    if not project_id:
        return None
    
    for entry in args:
        comm = CommChannels()
        comm.project_id = project_id
        comm.commchannel = entry['commchannel']
        db_add(comm)
    return get_comm(project_id)

######################################################################
###### Testing Code 
######################################################################

## Example usage
# project = {
#         "name":"SIPB Minecraft",
#         "status":"active",
#         "description":"Virtual MIT in a Minecraft server!"
#         }
# add_project(project)

# print(get_all_projects())
# pj1 = {
#     'name':'test1',
#     'status':'active',
#     'description':'that is all folks'
# }
# print(add_project_metadata(pj1))
# print(get_project_id('test1'))
# print(get_all_projects())

# contacts1 =[
#     {
#         'type':'primary',
#         'email':'huydai@mit.edu',
#     },
#     {
#         'type':'secondary',
#         'email':'ec-discuss@mit.edu'
#     }
# ]
#print(add_project_contacts('test1',contacts1))

# project_id = get_project_id('test1')
# print(get_contacts(project_id))

# roles1 = [
#     {
#         'role':'Support Tech',
#         'description':'get familiar with MIT\'s and SIPB\'s computing infrastructure by helping answer user questions and approve user requests.'
#         # missing prereq
#     },
#     {
#         'role':'Support Tech',
#         'description':"help design, implement, test, and review SIPB's cluster management software.",
#         'prereq':'previous programming experience in any statically typed language, knowledge of Python and Go or ability to independently learn them, 6.033-level understanding of computer systems, experience with Git, experience with Linux'
#     }
# ]
# #print(add_project_roles('test1',roles1))

# links1 = [
#     {'link':'https://sipb.mit.edu/'},
#     {'link':'https://hwops.mit.edu/'}
# ]
# #print(add_project_links('test1',links1))

# comms1 = [
#     {'commchannel':'sipb-hwops@mit.edu'},
# ]
# #print(add_project_comms('test1',comms1))


# print("Done")


    
    

    