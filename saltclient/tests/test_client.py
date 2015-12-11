import unittest
from saltclient import SaltClient


class TestSaltClient(unittest.TestCase):
    def setUp(self):
        self.salt = SaltClient('http://example.com:8080', 'user', 'pass')

    def test_hello(self):
        self.assertEqual(1+1, 2)
