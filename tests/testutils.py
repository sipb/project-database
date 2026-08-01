# NOTE: when making a test script, `import testutils` should be the very first
# line in your test script. This ensures that the special handshake to put the
# database in test mode gets run before any other modules get imported.

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
    """Restore the given environment variable to the given value. If the value
    is None, the environment variable will be deleted.

    Parameters
    ----------
    key : str
        The name of the environment variable.
    value : str or None
        The value to set. Pass None to delete the variable.
    """
    if value is None:
        try:
            os.environ.pop(key)
        except KeyError:
            pass
    else:
        os.environ[key] = value


class EnvironmentOverrider(object):
    def __init__(
        self, keys=['SSL_CLIENT_S_DN_Email', 'HTTP_HOST', 'REQUEST_URI']
    ):
        """Context manager to allow specific environment variables to be
        overridden and restored.

        Parameters
        ----------
        keys : list of str, optional
            The keys to save/restore.
        """
        self.keys = keys

    def __enter__(self):
        self.initial_values = {key: os.getenv(key) for key in self.keys}
        return self

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        for key, value in self.initial_values.items():
            restore_env(key, value)


class DatabaseWiper(object):
    """Context manager which wipes the database on both entry and exit.
    """

    def drop_test_projects(self):
        """Empty all of the tables in the database.
        """
        assert creds.mode == 'test'

        # NOTE: this is done with .delete() rather than drop_all() because the
        # latter was found to be unacceptably slow. This method will need to be
        # updated if the schema ever changes.
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
        """Test fixture which enters into multiple context managers before each
        test (and exits each after each tests).

        Parameters
        ----------
        managers : list of ContextManager, optional
            The context managers to use. The managers are entered in the order
            provided, and exited in reverse order.
        """
        self.managers = kwargs.pop('managers', ())
        super(MultiManagerTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        for manager in self.managers:
            manager.__enter__()

    def tearDown(self):
        for manager in self.managers[::-1]:
            manager.__exit__()


class EnvironmentOverrideTestCase(MultiManagerTestCase):
    def __init__(self, *args, **kwargs):
        """Test fixture which permits overriding various environment variables.
        See the documentation for `EnvironmentOverrideTestCase` for details.
        """
        super(EnvironmentOverrideTestCase, self).__init__(
            *args, managers=[EnvironmentOverrider()], **kwargs
        )


class DatabasePopulatorMixin(unittest.TestCase):
    """Mix-in which populates the database with a couple of test projects.
    """

    def setUp(self):
        super(DatabasePopulatorMixin, self).setUp()

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
        self.initial_approvals = ['awaiting_approval', 'approved']
        for project_info, initial_approval in zip(
            self.project_info_list, self.initial_approvals
        ):
            project_info['project_id'] = db.add_project(
                project_info, 'creator', initial_approval=initial_approval
            )
            project_info['approval'] = initial_approval


class DatabaseWipeTestCase(DatabasePopulatorMixin, MultiManagerTestCase):
    def __init__(self, *args, **kwargs):
        """Test fixture which wipes the database before each test, populates it
        with test entries, then wipes it again after the test.
        """
        super(DatabaseWipeTestCase, self).__init__(
            *args, managers=[DatabaseWiper()], **kwargs
        )


class EnvironmentOverrideDatabaseWipeTestCase(
    DatabasePopulatorMixin, MultiManagerTestCase
):
    def __init__(self, *args, **kwargs):
        """Test fixture which performs the operations of both
        `EnvironmentOverrideTestCase` and `DatabaseWipeTestCase`.
        """
        super(EnvironmentOverrideDatabaseWipeTestCase, self).__init__(
            *args, managers=[EnvironmentOverrider(), DatabaseWiper()], **kwargs
        )
