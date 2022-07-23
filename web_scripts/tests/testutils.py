# Add the web_scripts directory to the path:
import sys
sys.path.insert(0, '..')

# Set the test mode flag:
import os
os.environ['PROJECTS_DATABASE_MODE'] = 'test'

# Ensure that we are actually in test mode:
import creds
assert creds.mode == 'test'

import unittest

import db
import schema


def restore_env(key, value):
    if value is None:
        try:
            os.environ.pop(key)
        except KeyError:
            pass
    else:
        os.environ[key] = value


class EnvironmentOverrider(object):
    def __enter__(self):
        self.initial_values = {
            key: os.getenv(key) for key in [
                'SSL_CLIENT_S_DN_Email',
                'HTTP_HOST',
                'REQUEST_URI'
            ]
        }
        return self

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        for key, value in self.initial_values.items():
            restore_env(key, value)


class DatabaseWiper(object):
    def drop_test_projects(self):
        assert creds.mode == 'test'

        schema.session.query(schema.ProjectsHistory).delete()
        schema.session.query(schema.ContactEmails).delete()
        schema.session.query(schema.ContactEmailsHistory).delete()
        schema.session.query(schema.Roles).delete()
        schema.session.query(schema.RolesHistory).delete()
        schema.session.query(schema.Links).delete()
        schema.session.query(schema.LinksHistory).delete()
        schema.session.query(schema.CommChannels).delete()
        schema.session.query(schema.CommChannelsHistory).delete()

        schema.session.query(schema.Projects).delete()

        schema.session.commit()

    def __enter__(self):
        self.drop_test_projects()
        return self

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        self.drop_test_projects()


class MultiManagerTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.managers = kwargs.pop('managers', ())
        super(MultiManagerTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        for manager in self.managers:
            manager.__enter__()

    def tearDown(self):
        for manager in self.managers:
            manager.__exit__()


class EnvironmentOverrideTestCase(MultiManagerTestCase):
    def __init__(self, *args, **kwargs):
        super(EnvironmentOverrideTestCase, self).__init__(
            *args, managers=[EnvironmentOverrider()], **kwargs
        )


class DatabasePopulatorMixin(object):
    def setUp(self):
        super(DatabaseWipeTestCase, self).setUp()

        self.project_info_list = [
            {
                'name': 'test1',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {'email': 'foo@mit.edu', 'type': 'primary', 'index': 0}
                ],
                'roles': []
            },
            {
                'name': 'test2',
                'description': 'some test description',
                'status': 'active',
                'links': [],
                'comm_channels': [],
                'contacts': [
                    {
                        'email': 'this_is_definitely_not_a_valid_kerb@mit.edu',
                        'type': 'primary',
                        'index': 0
                    }
                ],
                'roles': []
            }
        ]
        self.initial_approvals = ['approved', 'approved']
        for project_info, initial_approval in zip(
            self.project_info_list, self.initial_approvals
        ):
            project_info['project_id'] = db.add_project(
                project_info, 'creator', initial_approval=initial_approval
            )
            project_info['approval'] = initial_approval


class DatabaseWipeTestCase(MultiManagerTestCase, DatabasePopulatorMixin):
    def __init__(self, *args, **kwargs):
        super(DatabaseWipeTestCase, self).__init__(
            *args, managers=[DatabaseWiper()], **kwargs
        )


class EnvironmentOverrideDatabaseWipeTestCase(
    MultiManagerTestCase, DatabasePopulatorMixin
):
    def __init__(self, *args, **kwargs):
        super(EnvironmentOverrideDatabaseWipeTestCase, self).__init__(
            *args, managers=[EnvironmentOverrider(), DatabaseWiper()], **kwargs
        )
