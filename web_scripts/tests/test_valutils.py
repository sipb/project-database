#!/usr/bin/env python

# testutils MUST be imported first to set up test configuration and module
# paths properly!
import testutils

import unittest

import valutils


class Test_all_unique(unittest.TestCase):
    def test_unique_ignore_case(self):
        vals = ['alpha', 'bravo', 'charlie']
        result = valutils.all_unique(vals, ignore_case=True)
        self.assertTrue(result)

    def test_unique_with_case(self):
        vals = ['alpha', 'ALPHA', 'bravo', 'charlie']
        result = valutils.all_unique(vals, ignore_case=False)
        self.assertTrue(result)

    def test_nonunique_ignore_case(self):
        vals = ['alpha', 'ALPHA', 'bravo', 'charlie']
        result = valutils.all_unique(vals, ignore_case=True)
        self.assertFalse(result)

    def test_nonunique_with_case(self):
        vals = ['alpha', 'bravo', 'bravo', 'charlie']
        result = valutils.all_unique(vals, ignore_case=False)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
