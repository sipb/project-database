import os

import sqlalchemy as db
import sqlalchemy.ext.declarative
import sqlalchemy.orm

MODE = os.environ.get("PROJECTS_DATABASE_MODE", "prod")
SQL_URL = "sqlite://" if MODE == "test" else "sqlite:///data/main.db"


##############################################################
# Setup Stages
##############################################################

# Initialization Steps
os.makedirs("data", exist_ok=True)
SQLBase = db.ext.declarative.declarative_base()
sqlengine = db.create_engine(SQL_URL)
SQLBase.metadata.bind = sqlengine
session = db.orm.sessionmaker(bind=sqlengine)()  # main object used for queries

# Implement schema
# SQLBase.metadata.create_all(sqlengine) # this is unnecessary?

# Strategy: Every table has a version which stores the current state, and a
# separate "history table" which contains the edit history. This is done to
# ensure that it is easy to make queries against the current state without
# having to understand the history tracking mechanism. To implement this, every
# table has a "Base" which is a mixin (i.e., it inherits from object, NOT
# SQLBase) and defines all columns. The main table then inherits from the
# "Base" mixin and SQLBase. The history table then inherits from the "Base"
# mixin, SQLBase, and the HistoryMixin which adds the columns needed for edit
# logging. (Columns which have different constraints in the main table vs. the
# history table must be defined in the subclasses.)


class HistoryMixin:
    author = db.orm.mapped_column(db.String(50), nullable=False)
    # action can be 'create', 'update', 'delete', 'same'
    action = db.orm.mapped_column(db.String(25), nullable=False)
    revision_id = db.orm.mapped_column(db.Integer(), nullable=False)
    timestamp = db.orm.mapped_column(
        db.TIMESTAMP, nullable=False, server_default=db.func.now()
    )

    @sqlalchemy.orm.validates("author")
    def validate_author(self, key, author):
        if len(author) > self.__table__.columns[key].type.length:
            raise ValueError(f'Value of "{author}" for key "author" is too long!')
        return author

    @sqlalchemy.orm.validates("action")
    def validate_action(self, key, action):
        if action not in ["create", "update", "delete", "same"]:
            raise ValueError(f'Value of "{action}" for key "action" is invalid!')
        return action


class ProjectsBase:
    # project_id and name must be defined in subclasses, as they have special
    # constraints which differ between the main table and the history table.

    description = db.orm.mapped_column(db.Text(), nullable=False)
    # status can be "active" or "inactive"
    status = db.orm.mapped_column(db.String(25), nullable=False)
    # approval can be "awaiting_approval" or "approved" or "rejected"
    approval = db.orm.mapped_column(db.String(25), nullable=False)
    # Kerb of user who registered the project:
    creator = db.orm.mapped_column(db.String(50), nullable=False)
    # Kerb of user who approved the project:
    approver = db.orm.mapped_column(db.String(50), nullable=True)
    # Comments from user who approved the project:
    approver_comments = db.orm.mapped_column(db.Text(), nullable=True)

    @sqlalchemy.orm.validates("status")
    def validate_status(self, key, status):
        if status not in ["active", "inactive"]:
            raise ValueError(f'Value of "{status}" for key "status" is invalid!')
        return status

    @sqlalchemy.orm.validates("approval")
    def validate_approval(self, key, approval):
        if approval not in ["awaiting_approval", "approved", "rejected"]:
            raise ValueError(f'Value of "{approval}" for key "approval" in invalid!')
        return approval

    @sqlalchemy.orm.validates("creator")
    def validate_creator(self, key, creator):
        if len(creator) > self.__table__.columns[key].type.length:
            raise ValueError(f'Value of "{creator}" for key "creator" is too long!')
        return creator

    @sqlalchemy.orm.validates("approver")
    def validate_approver(self, key, approver):
        if (approver is not None) and (
            len(approver) > self.__table__.columns[key].type.length
        ):
            raise ValueError(f'Value of "{approver}" for key "approver" is too long!')
        return approver

    @sqlalchemy.orm.validates("name")
    def validate_name(self, key, name):
        if len(name) > self.__table__.columns[key].type.length:
            raise ValueError(f'Value of "{name}" for key "name" is too long!')
        return name


class Projects(SQLBase, ProjectsBase):
    __tablename__ = "projects"
    project_id = db.orm.mapped_column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    name = db.orm.mapped_column(db.String(50), nullable=False, unique=True)


class ProjectsHistory(SQLBase, ProjectsBase, HistoryMixin):
    __tablename__ = "projectshistory"
    id = db.orm.mapped_column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    name = db.orm.mapped_column(db.String(50), nullable=False)

    # Foreign key constraint requires special handling.
    @sqlalchemy.ext.declarative.declared_attr
    def project_id(cls):
        return db.orm.mapped_column(
            db.Integer(), db.ForeignKey("projects.project_id"), nullable=False
        )


class ContactEmailsBase:
    id = db.orm.mapped_column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    # type can be either "primary" or "secondary". By convention, there should
    # be exactly one primary contact for each project.
    type = db.orm.mapped_column(db.String(25), nullable=False)
    email = db.orm.mapped_column(db.String(50), nullable=False)
    # index sets the order which contacts are listed in. By convention, the one
    # primary contact should have index 0.
    index = db.orm.mapped_column(db.Integer(), nullable=False)

    # Foreign key constraint requires special handling.
    @sqlalchemy.ext.declarative.declared_attr
    def project_id(cls):
        return db.orm.mapped_column(
            db.Integer(), db.ForeignKey("projects.project_id"), nullable=False
        )

    @sqlalchemy.orm.validates("type")
    def validate_type(self, key, type):
        if type not in ["primary", "secondary"]:
            raise ValueError(f'Value of "{type}" for key "type" is invalid!')
        return type

    @sqlalchemy.orm.validates("email")
    def validate_email(self, key, email):
        if len(email) > self.__table__.columns[key].type.length:
            raise ValueError(f'Value of "{email}" for key "email" is too long!')
        return email


class ContactEmails(SQLBase, ContactEmailsBase):
    __tablename__ = "contactemails"


class ContactEmailsHistory(SQLBase, ContactEmailsBase, HistoryMixin):
    __tablename__ = "contactemailshistory"


class RolesBase:
    id = sqlalchemy.Column(
        sqlalchemy.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    role = db.orm.mapped_column(db.String(50), nullable=False)
    description = db.orm.mapped_column(db.Text(), nullable=False)
    prereq = db.orm.mapped_column(db.Text(), nullable=True)
    # index sets the order which roles are listed in:
    index = db.orm.mapped_column(db.Integer(), nullable=False)

    # Foreign key constraint requires special handling.
    @sqlalchemy.ext.declarative.declared_attr
    def project_id(cls):
        return db.orm.mapped_column(
            db.Integer(), db.ForeignKey("projects.project_id"), nullable=False
        )

    @sqlalchemy.orm.validates("role")
    def validate_role(self, key, role):
        if len(role) > self.__table__.columns[key].type.length:
            raise ValueError(f'Value of "{role}" for key "role" is too long!')
        return role


class Roles(SQLBase, RolesBase):
    __tablename__ = "roles"


class RolesHistory(SQLBase, RolesBase, HistoryMixin):
    __tablename__ = "roleshistory"


class LinksBase:
    id = db.orm.mapped_column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    link = db.orm.mapped_column(db.Text(), nullable=False)
    # index sets the order which links are listed in:
    index = db.orm.mapped_column(db.Integer(), nullable=False)
    anchortext = db.orm.mapped_column(db.Text(), nullable=True)

    # Foreign key constraint requires special handling.
    @sqlalchemy.ext.declarative.declared_attr
    def project_id(cls):
        return db.orm.mapped_column(
            db.Integer(), db.ForeignKey("projects.project_id"), nullable=False
        )


class Links(SQLBase, LinksBase):
    __tablename__ = "links"


class LinksHistory(SQLBase, LinksBase, HistoryMixin):
    __tablename__ = "linkshistory"


class CommChannelsBase:
    id = db.orm.mapped_column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    commchannel = db.orm.mapped_column(db.Text(), nullable=False)
    # index sets the order which comm channels are listed in:
    index = db.orm.mapped_column(db.Integer(), nullable=False)

    # Foreign key constraint requires special handling.
    @sqlalchemy.ext.declarative.declared_attr
    def project_id(cls):
        return db.orm.mapped_column(
            db.Integer(), db.ForeignKey("projects.project_id"), nullable=False
        )


class CommChannels(SQLBase, CommChannelsBase):
    __tablename__ = "commchannels"


class CommChannelsHistory(SQLBase, CommChannelsBase, HistoryMixin):
    __tablename__ = "commchannelshistory"


class NewMemberSubmissions(SQLBase):
    # This table intentionally does NOT use the HistoryMixin pattern used by
    # Projects, etc. This is a single-pass review workflow (a new member
    # submits once, an approver reviews/responds once), not an iteratively
    # edited record that needs rollback support.
    __tablename__ = "newmembersubmissions"

    submission_id = db.orm.mapped_column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    # Kerb of the new member who submitted the form:
    kerberos = db.orm.mapped_column(db.String(50), nullable=False)
    email = db.orm.mapped_column(db.String(50), nullable=False)
    # Comma-separated list of selected interest tags (see
    # config.NEW_MEMBER_INTEREST_OPTIONS):
    interests = db.orm.mapped_column(db.Text(), nullable=False)
    interests_other = db.orm.mapped_column(db.Text(), nullable=True)
    # experience_level can be one of config.NEW_MEMBER_EXPERIENCE_LEVELS:
    experience_level = db.orm.mapped_column(db.String(25), nullable=False)
    experience_details = db.orm.mapped_column(db.Text(), nullable=True)
    comments = db.orm.mapped_column(db.Text(), nullable=True)
    # status can be "pending" or "reviewed":
    status = db.orm.mapped_column(db.String(25), nullable=False, default="pending")
    submitted_at = db.orm.mapped_column(
        db.TIMESTAMP, nullable=False, server_default=db.func.now()
    )
    # Kerb of the approver who reviewed the submission:
    reviewer = db.orm.mapped_column(db.String(50), nullable=True)
    reviewer_notes = db.orm.mapped_column(db.Text(), nullable=True)
    reviewed_at = db.orm.mapped_column(db.TIMESTAMP, nullable=True)

    @sqlalchemy.orm.validates("status")
    def validate_status(self, key, status):
        if status not in ["pending", "reviewed"]:
            raise ValueError(f'Value of "{status}" for key "status" is invalid!')
        return status

    @sqlalchemy.orm.validates("kerberos", "email", "reviewer")
    def validate_length(self, key, value):
        if (value is not None) and (
            len(value) > self.__table__.columns[key].type.length
        ):
            raise ValueError(f'Value of "{value}" for key "{key}" is too long!')
        return value


class NewMemberSuggestedProjects(SQLBase):
    __tablename__ = "newmembersuggestedprojects"

    id = db.orm.mapped_column(
        db.Integer(), nullable=False, primary_key=True, autoincrement=True
    )
    submission_id = db.orm.mapped_column(
        db.Integer(),
        db.ForeignKey("newmembersubmissions.submission_id"),
        nullable=False,
    )
    project_id = db.orm.mapped_column(
        db.Integer(), db.ForeignKey("projects.project_id"), nullable=False
    )


# Implement schema
SQLBase.metadata.create_all(sqlengine)

# Define data structure to help with history generation:
CLASS_TO_HISTORY_CLASS_MAP = {
    Projects: ProjectsHistory,
    ContactEmails: ContactEmailsHistory,
    Roles: RolesHistory,
    Links: LinksHistory,
    CommChannels: CommChannelsHistory,
}
