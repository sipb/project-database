#!/usr/bin/python

from turtle import update
from sqlalchemy import func
from schema import *


##############################################################
## Database Operations
##############################################################

# General Purpose Functions

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

## Get Functions

def get_all_projects():
    '''Get metadata all of projects in database'''
    return session.query(Projects).all()


def get_active_projects():
    """Get data for all active projects in the database.
    """
    return session.query(Projects).filter_by(status='active').all()


def get_inactive_projects():
    """Get data for all inactive projects in the database.
    """
    return session.query(Projects).filter_by(status='inactive').all()


def get_projects_for_contact(email):
    """Get all projects for which the given email is a contact.
    """
    return session.query(Projects).join(
        ContactEmails, Projects.project_id == ContactEmails.project_id
    ).filter(ContactEmails.email == email).all()


def get_project_info(model, project_id, raw_input=False):
    '''
    Given an SQL class model (e.g. ContactEmail, Roles, Links, etc.), query that table
    for all entries associated with project_id and return the result in the form of 
    list of dictionaries
    
    If `raw_input` is set to True, we will return the SQLobject instead. This allows
    for direct object modification
    
    Useful for building higher-level queries
    '''
    sql_result = session.query(model).filter_by(project_id=project_id).all()
    if raw_input:
        return sql_result
    else:
        return list_dict_convert(sql_result)

## Shorthand functions to get all table entries associated with a project ID `id` 
## If `get_raw` is set to True, return SQL object instead of dictionary.

get_project = lambda id, get_raw=False: get_project_info(Projects,id,get_raw) # Return maximum 1 result
get_contacts = lambda id, get_raw=False: get_project_info(ContactEmails,id,get_raw)
get_roles = lambda id, get_raw=False: get_project_info(Roles,id,get_raw)
get_links = lambda id, get_raw=False: get_project_info(Links,id,get_raw)
get_comm = lambda id, get_raw=False: get_project_info(CommChannels, id,get_raw)


def get_project_id(name):
    '''
    Get the ID of a project with `name`, if it exists
    Otherwise returns None
    '''
    return session.query(Projects.project_id).filter_by(name=name).scalar()


def get_project_name(project_id):
    """Get the name of the project with the given project_id, if it exists.
    Otherwise returns None.
    """
    return session.query(
        Projects.name
    ).filter_by(project_id=project_id).scalar()


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


def get_all_project_info(filter_method='all', contact_email=None):
    """Get the information for all projects.

    Parameters
    ----------
    filter_method : {'all', 'active', 'inactive'}, optional
        The filter to apply. Options are:
        * 'all' (default): return all projects
        * 'active': return all active projects
        * 'inactive': return all inactive projects
        * 'contact': return projects for which the given contact_email is in
            the contact list.
    contact_email : str, optional
        The contact email to filter on when filter_method is 'contact'.

    Returns
    -------
    project_list : list of dict
        List of all projects.
    """
    if filter_method == 'all':
        projects = get_all_projects()
    elif filter_method == 'active':
        projects = get_active_projects()
    elif filter_method == 'inactive':
        projects = get_inactive_projects()
    elif filter_method == 'contact':
        projects = get_projects_for_contact(contact_email)
    else:
        raise ValueError('Unknown status filter!')

    project_list = list_dict_convert(projects)
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

## Adding operations

def add_project_metadata(args):
    '''
    Add a project with provided metadata to the database
    
    Requires: 
        - args to have keys of 'name', 'status', 'description', and 'creator' with valid types
        - status is either 'active' or 'inactive'
        
    Returns: 
        - project_id associated with newly created project, None if project already exists or invalid arguments
    '''
    try:
        args_lst = ['name','status','description','creator']
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
    project.creator = args['creator']
    project.approval = 'awaiting_approval' # Projects are waiting to be approved by default
    db_add(project)
    return get_project_id(args['name'])
    
def add_project_contacts(project_id, args):
    '''
    Add a list of emails associated with a project to the database
    
    Requires: 
        - project_id to be a valid project ID in the Metadata table
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
    
    for entry in args:
        contact = ContactEmails()
        contact.project_id = project_id
        contact.type = entry['type']
        contact.email = entry['email']
        db_add(contact)
    return get_contacts(project_id)

def add_project_roles(project_id, args):
    '''
    Add a list of roles associated with a project to the database
    
    Requires: 
        - project_id to be a valid project ID in the Metadata table
        - args to be list of dictionaries with keys 'role','description', and (optional) 'prereq' 
        
    Returns: 
        - None if no project with that name or invalid arguments, otherwise returns list of all 
            roles associated with project in DB
    '''
    try:
        args_lst = ['role','description'] # 'prereq' optional 
        for dict in args:
            assert check_object_params(dict,args_lst)
    except AssertionError:
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

def add_project_links(project_id, args):
    '''
    Add a list of website links associated with a project to the database
    
    Requires: 
        - project_id to be a valid project ID in the Metadata table
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
    
    for entry in args:
        link = Links()
        link.project_id = project_id
        link.link = entry['link']
        db_add(link)
    return get_links(project_id)

def add_project_comms(project_id, args):
    '''
    Add a list of communication channels associated with a project to the database
    CommChannels can be text description rather than just HTML links
    
    Requires: 
        - project_id to be a valid project ID in the Metadata table
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
    
    for entry in args:
        comm = CommChannels()
        comm.project_id = project_id
        comm.commchannel = entry['commchannel']
        db_add(comm)
    return get_comm(project_id)

def add_project(project):
    """Add the given project to the database.

    Parameters
    ----------
    proj : dict
        The project info extracted from the form in performaddproject.html

    Returns
    -------
    project_id : int
        If success, return the project_id (primary key) for the newly-added project.
        Otherwise, return -1
    """
    project_id = get_project_id(project['name'])
    if project_id:
        return -1 #Project already exists
    
    metadata = {
        'name': project['name'],
        'description': project['description'],
        'status': project['status'],
        'creator': project['creator'],
    }
    project_id = add_project_metadata(metadata)
    add_project_links(project_id, project['links'])
    add_project_comms(project_id, project['comm_channels'])
    add_project_contacts(project_id, project['contacts'])
    add_project_roles(project_id, project['roles'])
    return project_id
    
## Update an existing project

def update_metadata(project_id, args):
    """Update the metadata entries for a project in the database.
    Only the name, description, and status can be changed.

    Parameters
    ----------
    project_id : int
        ID of the project we want to modify
    args : dict
        Keys are fields in the Projects table, and values fit the
        right type and correct value according to schema.
        
    Returns
    -------
    changed_fields : set
        Return the set of string fields which were changed for the project. 
        If no fields change, return empty dictionary.
    """
    allowed_fields = ['name','description','status']
    changed_fields = set()
    metadata = get_project(project_id,True)[0] # Returns SQL object
    
    for field in allowed_fields: # Only look for changes in the allowed fields
        if field in args and args[field] != getattr(metadata, field):
            changed_fields.add(field)
            setattr(metadata, field, args[field]) 
    session.commit()
    return changed_fields
    
def update_project(project_info, project_id):
    """Update the information for the given project in the database.

    Parameters
    ----------
    project_info : dict
        The project info extracted from the form.
    project_id : int or str
        The project ID for the existing project.
    """
    # TODO: this needs to be implemented!
    pass
    
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

# project_mod = {
#         "name":"SIPB Takes Over the World",
#         "status":"active",
#         "description":"April Fools"
# }
    
# print(update_metadata(1, project_mod))
    