import unittest
from pysetup.context import Context

class TestContext(unittest.TestCase):

    def test_empty_context(self):
        c = Context()
        self.assertIsNone(c.get_value('foo'))
        self.assertIsNone(c.get('foo'))
        try:
            self.require('foo')
            self.fail()
        except Exception:
            # Expected
            pass
        self.assertEqual(0, len(c.keys()))

    def test_empty_layer(self):
        c = Context()
        c.add({})
        self.assertIsNone(c.get_value('foo'))
        self.assertIsNone(c.get('foo'))
        try:
            self.require('foo')
            self.fail()
        except Exception:
            # Expected
            pass
        self.assertEqual(0, len(c.keys()))

    def test_vars(self):
        c = Context()
        level1 = {'prop1': 'a', 'prop2': 'b', 'prop3': '${x}', 'prop4': '${prop1}', 'prop5': '${prop2}'}
        c.add(level1)
        level2 = {'prop2': 'c', 'prop6': '$prop1', 'x': 10}
        c.add(level2)
        level3 = {'prop2': 'd'}
        c.add(level3)

        self.assertEqual('a', c.get('prop1'))
        self.assertEqual('d', c.get('prop2'))
        self.assertEqual('10', c.get('prop3'))
        self.assertEqual('a', c.get('prop4'))
        self.assertEqual('d', c.get('prop5'))
        self.assertEqual('a', c.get('prop6'))
        self.assertEqual(10, c.get('x'))

        self.assertEqual('prop2: d, combo: aandd/a', c.replace("prop2: $prop2, combo: ${prop4}and$prop5/$prop6"))

        self.assertEqual('${x}', c.get_value('prop3'))

        self.assertEqual(7, len(c.keys()))

    def test_indirection(self):
        c = Context()
        c.add({'foo': 'bar', 'bar': 'mumble'})
        self.assertEqual('mumble', c.replace('$$foo'))

if __name__ == '__main__':
    unittest.main()