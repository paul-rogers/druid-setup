import unittest
import tempfile

from pysetup.config2 import ConfigStack
from pysetup.context import Context

class TestService(unittest.TestCase):

    def test_empty(self):
        s = ConfigStack()
        self.assertIsNone(s.get('foo'))
        result = s.flatten()
        self.assertEqual(0, len(result))
        c = Context()
        resolved = s.resolve(c)
        self.assertEquals(0, len(resolved.config))

if __name__ == '__main__':
    unittest.main()