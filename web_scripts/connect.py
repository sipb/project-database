from webbrowser import get
import sqlalchemy as db
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import creds

DATABASE_NAME = "huydai+project-database"
SQL_URL = "mysql://%s:%s@sql.mit.edu/%s" % (creds.user,creds.password,DATABASE_NAME)

## Initialization Steps

SQLBase = db.ext.declarative.declarative_base()
sqlengine = db.create_engine(SQL_URL)
SQLBase.metadata.bind = sqlengine
session = db.orm.sessionmaker(bind=sqlengine)() #main object used for queries

class Projects(SQLBase):
    __tablename__ = "projects"
    project_id = db.Column(db.Integer(), nullable=False, primary_key=True, autoincrement=True)
    status = db.Column(db.String(50), nullable=False) # Can be "active" or "inactive"
    name = db.Column(db.String(50), nullable=False)
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

def get_or_create(session, model, **kwargs):
    '''
    Get a table, if it exists, otherwise create it
    
    Function taken from: https://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create
    '''
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
        
print(session)   
SQLBase.metadata.create_all(sqlengine)


    
    

    
    

    


