import unittest
import json
from app import create_app, db


class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""
