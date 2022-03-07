#!/usr/bin/python
from webbrowser import get
import sqlalchemy as db
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import creds

DATABASE_NAME = "huydai+project-database"
SQL_URL = "mysql://%s:%s@sql.mit.edu/%s" % (creds.user,creds.password,DATABASE_NAME)


##############################################################
## Setup Stages
##############################################################

## Initialization Steps
SQLBase = db.ext.declarative.declarative_base()
sqlengine = db.create_engine(SQL_URL)
SQLBase.metadata.bind = sqlengine
session = db.orm.sessionmaker(bind=sqlengine)() #main object used for queries

## Implement schema
SQLBase.metadata.create_all(sqlengine)

class Projects(SQLBase):
    __tablename__ = "projects"
    project_id = db.Column(db.Integer(), nullable=False, primary_key=True, autoincrement=True)
    status = db.Column(db.String(50), nullable=False) # Can be "active" or "inactive"
    name = db.Column(db.String(50), nullable=False, primary_key=True)
    description = db.Column(db.Text(), nullable=False)
    
class ContactEmails(SQLBase):
    __tablename__ = "contactemails"
    id = sqlalchemy.Column(sqlalchemy.Integer(), nullable=False, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer(), nullable=False)
    type = db.Column(db.String(50), nullable=False) # Can be either "primary" or "secondary"
    email = db.Column(db.String(50), nullable=False)

class Roles(SQLBase):
    __tablename__ = "roles"
    id = sqlalchemy.Column(sqlalchemy.Integer(), nullable=False, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer(), nullable=False)
    role = db.Column(db.String(50),nullable=False)
    description = db.Column(db.Text(), nullable=False)
    prereq = db.Column(db.Text(), nullable=True)
    
class Links(SQLBase):
    __tablename__ = "links"
    id = sqlalchemy.Column(sqlalchemy.Integer(), nullable=False, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer(), nullable=False)
    link = db.Column(db.Text(), nullable=False)

class CommChannel(SQLBase):
    __tablename__ = "CommChannel"
    id = sqlalchemy.Column(sqlalchemy.Integer(), nullable=False, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer(), nullable=False)
    commchannel = db.Column(db.Text(), nullable=False)

## Database operations definitions

def db_add(x):
    '''Add object instance x to the database'''
    session.add(x)
    session.commit()

def get_all_projects():
    '''Get metadata all of projects in database'''
    return session.query(Projects).all()

def get_project_info(model,project_id):
    '''
    Given an SQL class model (e.g. ContactEmail, Roles, Links, etc.), query that table
    for all entries associated with project_id and return the result
    '''
    return session.query(model).filter_by(project_id=project_id).all()

get_project = lambda id: get_project_info(Projects,id) # Return maximum 1 result
get_contacts = lambda id: get_project_info(ContactEmails,id)
get_roles = lambda id: get_project_info(Roles,id)
get_links = lambda id: get_project_info(Links,id)
get_comm = lambda id: get_project_info(CommChannel, id)

def get_project_id(name):
    '''
    Get the ID of a project with `name`, if it exists
    Otherwise returns None
    '''
    project = session.query(Projects).filter_by(name=name).one_or_none()
    if project:
        return project.project_id
    return None

def check_object_params(dict,params_lst):
    '''Check if a given dictionary has all keys defined in params_lst'''
    res = True
    for param in params_lst:
        if param not in dict:
            res = False
    return res

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
    
## Test code
# print(get_all_projects())

# pj1 = {
#     'name':'test1',
#     'status':'active',
#     'description':'that is all folks'
# }
# print(add_project_metadata(pj1))
# print(get_project_id('test1'))
# print(get_all_projects())

# print("Done")


    
    

    


