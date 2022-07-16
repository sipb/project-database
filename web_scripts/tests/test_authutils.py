#!/usr/bin/env python

import sqlalchemy as sa
import unittest

import sys
sys.path.insert(0, '..')

import os
os.environ['PROJECTS_DATABASE_MODE'] = 'test'
import creds
assert creds.mode == 'test'

import authutils
import config
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
    TEST_PROJECT_NAME = '__test__'

    def drop_test_project(self):
        project_id = db.get_project_id(self.TEST_PROJECT_NAME)
        if project_id:
            sa.delete(schema.ContactEmailsHistory).where(
                schema.ContactEmailsHistory.project_id == project_id
            ).execute()
            sa.delete(schema.ContactEmails).where(
                schema.ContactEmails.project_id == project_id
            ).execute()
            sa.delete(schema.RolesHistory).where(
                schema.RolesHistory.project_id == project_id
            ).execute()
            sa.delete(schema.Roles).where(
                schema.Roles.project_id == project_id
            ).execute()
            sa.delete(schema.LinksHistory).where(
                schema.LinksHistory.project_id == project_id
            ).execute()
            sa.delete(schema.Links).where(
                schema.Links.project_id == project_id
            ).execute()
            sa.delete(schema.CommChannelsHistory).where(
                schema.CommChannelsHistory.project_id == project_id
            ).execute()
            sa.delete(schema.CommChannels).where(
                schema.CommChannels.project_id == project_id
            ).execute()
            sa.delete(schema.ProjectsHistory).where(
                schema.ProjectsHistory.project_id == project_id
            ).execute()
            sa.delete(schema.Projects).where(
                schema.Projects.project_id == project_id
            ).execute()

    def __enter__(self):
        self.drop_test_project()
        return self

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        self.drop_test_project()


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


class DatabaseWipeTestCase(MultiManagerTestCase):
    def __init__(self, *args, **kwargs):
        super(DatabaseWipeTestCase, self).__init__(
            *args, managers=[DatabaseWiper()], **kwargs
        )


class EnvironmentOverrideDatabaseWipeTestCase(MultiManagerTestCase):
    def __init__(self, *args, **kwargs):
        super(EnvironmentOverrideDatabaseWipeTestCase, self).__init__(
            *args, managers=[EnvironmentOverrider(), DatabaseWiper()], **kwargs
        )


class Test_get_kerberos(EnvironmentOverrideTestCase):
    def test_none(self):
        try:
            os.environ.pop('SSL_CLIENT_S_DN_Email')
        except KeyError:
            pass

        kerberos = authutils.get_kerberos()
        self.assertIsNone(kerberos)

    def test_base(self):
        true_kerberos = 'project_test'
        email = true_kerberos + '@mit.edu'
        os.environ['SSL_CLIENT_S_DN_Email'] = email

        kerberos = authutils.get_kerberos()
        self.assertEqual(kerberos, true_kerberos)

    def test_non_mit(self):
        email = 'project_test@foo.bar'
        os.environ['SSL_CLIENT_S_DN_Email'] = email

        kerberos = authutils.get_kerberos()
        self.assertIsNone(kerberos)

    def test_multiple_at(self):
        email = 'bad@@mit.edu'
        os.environ['SSL_CLIENT_S_DN_Email'] = email

        kerberos = authutils.get_kerberos()
        self.assertIsNone(kerberos)


class Test_get_email(EnvironmentOverrideTestCase):
    def test_none(self):
        try:
            os.environ.pop('SSL_CLIENT_S_DN_Email')
        except KeyError:
            pass

        email = authutils.get_email()
        self.assertIsNone(email)

    def test_base(self):
        true_kerberos = 'project_test'
        true_email = true_kerberos + '@mit.edu'
        os.environ['SSL_CLIENT_S_DN_Email'] = true_email

        email = authutils.get_email()
        self.assertEqual(email, true_email)

    def test_non_mit(self):
        true_email = 'project_test@foo.bar'
        os.environ['SSL_CLIENT_S_DN_Email'] = true_email

        email = authutils.get_email()
        self.assertIsNone(email)

    def test_multiple_at(self):
        true_email = 'bad@@mit.edu'
        os.environ['SSL_CLIENT_S_DN_Email'] = true_email

        email = authutils.get_email()
        self.assertIsNone(email)


class Test_get_base_url(EnvironmentOverrideTestCase):
    def test_with_auth(self):
        true_host = 'test.foo.bar:123'
        os.environ['HTTP_HOST'] = true_host

        host = authutils.get_base_url(True)
        self.assertEqual(host, 'https://test.foo.bar:444')

    def test_without_auth(self):
        true_host = 'test.foo.bar:123'
        os.environ['HTTP_HOST'] = true_host

        host = authutils.get_base_url(False)
        self.assertEqual(host, 'https://test.foo.bar')


class Test_get_auth_url(EnvironmentOverrideTestCase):
    def test_with_auth(self):
        true_host = 'test.foo.bar:123'
        os.environ['HTTP_HOST'] = true_host

        true_uri = '/baz.html'
        os.environ['REQUEST_URI'] = true_uri

        host = authutils.get_auth_url(True)
        self.assertEqual(host, 'https://test.foo.bar:444/baz.html')

    def test_without_auth(self):
        true_host = 'test.foo.bar:123'
        os.environ['HTTP_HOST'] = true_host

        true_uri = '/baz.html'
        os.environ['REQUEST_URI'] = true_uri

        host = authutils.get_auth_url(False)
        self.assertEqual(host, 'https://test.foo.bar/baz.html')


class Test_is_sipb(unittest.TestCase):
    def test_keyholder(self):
        result = authutils.is_sipb('markchil')
        self.assertTrue(result)

    def test_member(self):
        # rif was memberized in 1991, and this test will need to be revised
        # should they be elected a keyholder.
        result = authutils.is_sipb('rif')
        self.assertTrue(result)

    def test_nonmember(self):
        result = authutils.is_sipb('this_is_definitely_not_a_valid_kerb')
        self.assertFalse(result)


class Test_is_keyholder(unittest.TestCase):
    def test_keyholder(self):
        result = authutils.is_keyholder('markchil')
        self.assertTrue(result)

    def test_member(self):
        # rif was memberized in 1991, and this test will need to be revised
        # should they be elected a keyholder.
        result = authutils.is_keyholder('rif')
        self.assertFalse(result)

    def test_nonmember(self):
        result = authutils.is_keyholder('this_is_definitely_not_a_valid_kerb')
        self.assertFalse(result)


class Test_can_add(unittest.TestCase):
    def test_none(self):
        result = authutils.can_add(None)
        self.assertFalse(result)

    def test_member(self):
        # rif was memberized in 1991, and this test will need to be revised
        # should they be elected a keyholder.
        result = authutils.can_add('rif')
        self.assertTrue(result)

    def test_nonmember(self):
        result = authutils.can_add('this_is_definitely_not_a_valid_kerb')
        self.assertFalse(result)

    # NOTE: the non-SIPB admin or approver branches are not tested.


class Test_is_admin(unittest.TestCase):
    def test_none(self):
        result = authutils.is_admin(None)
        self.assertFalse(result)

    def test_nonadmin(self):
        result = authutils.is_admin('this_is_definitely_not_a_valid_kerb')
        self.assertFalse(result)

    def test_admin(self):
        if len(config.ADMIN_USERS) > 0:
            result = authutils.is_admin(config.ADMIN_USERS[0])
            self.assertTrue(result)


class Test_is_approver(unittest.TestCase):
    def test_none(self):
        result = authutils.is_approver(None)
        self.assertFalse(result)

    def test_nonadmin(self):
        result = authutils.is_approver('this_is_definitely_not_a_valid_kerb')
        self.assertFalse(result)

    def test_admin(self):
        if len(config.APPROVER_USERS) > 0:
            result = authutils.is_approver(config.APPROVER_USERS[0])
            self.assertTrue(result)


class Test_can_edit(EnvironmentOverrideTestCase):
    def test_none(self):
        result = authutils.can_edit(None, -1)
        self.assertFalse(result)

    def test_admin(self):
        if len(config.ADMIN_USERS) > 0:
            result = authutils.can_edit(config.ADMIN_USERS[0], -1)
            self.assertTrue(result)

    def test_approver(self):
        if len(config.APPROVER_USERS) > 0:
            result = authutils.can_edit(config.APPROVER_USERS[0], -1)
            self.assertTrue(result)

    def test_creator(self):
        with DatabaseWiper() as dw:
            kerberos = 'this_is_definitely_not_a_valid_kerb'
            email = kerberos + '@mit.edu'
            os.environ['SSL_CLIENT_S_DN_Email'] = email
            project_id = db.add_project(
                {
                    'name': dw.TEST_PROJECT_NAME,
                    'description': 'some test description',
                    'status': 'active',
                    'links': [],
                    'comm_channels': [],
                    'contacts': [
                        {'email': 'foo@mit.edu', 'type': 'primary', 'index': 0}
                    ],
                    'roles': []
                },
                kerberos
            )

            result = authutils.can_edit(kerberos, project_id)

        self.assertTrue(result)

    def test_contact(self):
        with DatabaseWiper() as dw:
            kerberos = 'this_is_definitely_not_a_valid_kerb'
            email = kerberos + '@mit.edu'
            os.environ['SSL_CLIENT_S_DN_Email'] = email
            project_id = db.add_project(
                {
                    'name': dw.TEST_PROJECT_NAME,
                    'description': 'some test description',
                    'status': 'active',
                    'links': [],
                    'comm_channels': [],
                    'contacts': [
                        {'email': email, 'type': 'primary', 'index': 0}
                    ],
                    'roles': []
                },
                'creator'
            )

            result = authutils.can_edit(kerberos, project_id)

        self.assertTrue(result)

    def test_non_contact(self):
        with DatabaseWiper() as dw:
            kerberos = 'this_is_definitely_not_a_valid_kerb'
            email = kerberos + '@mit.edu'
            os.environ['SSL_CLIENT_S_DN_Email'] = email
            project_id = db.add_project(
                {
                    'name': dw.TEST_PROJECT_NAME,
                    'description': 'some test description',
                    'status': 'active',
                    'links': [],
                    'comm_channels': [],
                    'contacts': [
                        {'email': 'foo@mit.edu', 'type': 'primary', 'index': 0}
                    ],
                    'roles': []
                },
                'creator'
            )

            result = authutils.can_edit(kerberos, project_id)

        self.assertFalse(result)


class Test_requires_approval(EnvironmentOverrideTestCase):
    def test_none(self):
        result = authutils.requires_approval(None)
        self.assertTrue(result)

    def test_admin(self):
        if len(config.ADMIN_USERS) > 0:
            result = authutils.requires_approval(config.ADMIN_USERS[0])
            self.assertFalse(result)

    def test_approver(self):
        if len(config.APPROVER_USERS) > 0:
            result = authutils.requires_approval(config.APPROVER_USERS[0])
            self.assertFalse(result)

    def test_keyholder(self):
        result = authutils.requires_approval('markchil')
        self.assertFalse(result)

    def test_non_keyholder(self):
        result = authutils.requires_approval(
            'this_is_definitely_not_a_valid_kerb'
        )
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
