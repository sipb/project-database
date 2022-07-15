#!/usr/bin/env python

import unittest

import sys
sys.path.insert(0, '..')

import os
os.environ['PROJECTS_DATABASE_MODE'] = 'test'
import creds
assert creds.mode == 'test'

import authutils


class Test_get_kerberos(unittest.TestCase):
    def setUp(self):
        self.initial_email = os.getenv('SSL_CLIENT_S_DN_Email')

    def tearDown(self):
        if self.initial_email is None:
            try:
                os.environ.pop('SSL_CLIENT_S_DN_Email')
            except KeyError:
                pass
        else:
            os.environ['SSL_CLIENT_S_DN_Email'] = self.initial_email

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


if __name__ == '__main__':
    unittest.main()
