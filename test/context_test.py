import unittest
from pysetup.context import Context

expected_fmt = \
'''c: 10
d: foo
e: " bar "
f: """
  | two
  | lines
  """
'''
class TestContext(unittest.TestCase):

    def test_empty_context(self):
        c = Context({}, {})
        self.assertIsNone(c.get_value('foo'))
        self.assertEqual('', c.get('foo'))
        try:
            self.require('foo')
            self.fail()
        except Exception:
            # Expected
            pass
        self.assertEqual(0, len(c.keys()))

    def test_vars(self):
        c = Context({}, {
            'prop1': 'a', 
            'prop2': 'd', 
            'prop3': '${x}', 
            'prop4': '${prop1}', 
            'prop5': '${prop2}', 
            'prop6': '$prop1', 
            'x': 10})

        self.assertEqual('a', c.get('prop1'))
        self.assertEqual('d', c.get('prop2'))
        self.assertEqual('10', c.get('prop3'))
        self.assertEqual('a', c.get('prop4'))
        self.assertEqual('d', c.get('prop5'))
        self.assertEqual('a', c.get('prop6'))
        self.assertEqual('10', c.get('x'))
        self.assertEqual(10, c.get_value('x'))

        self.assertEqual('prop2: d, combo: aandd/a', c.replace("prop2: $prop2, combo: ${prop4}and$prop5/$prop6"))

        self.assertEqual('${x}', c.get_value('prop3'))

        self.assertEqual(7, len(c.keys()))

    def test_indirection(self):
        c = Context({}, {'foo': 'bar', 'bar': 'mumble'})
        self.assertEqual('mumble', c.replace('$$foo'))

    def test_non_string(self):
        c = Context({}, {'p1': None, 'p2': 10})
        self.assertEqual('', c.replace('$p1'))
        self.assertEqual('10', c.replace('$p2'))
        self.assertEqual('a//b/10/c', c.replace('a/$p1/b/$p2/c'))

    def test_system(self):
        sys_props = {}
        c = Context(sys_props, {'p1': 'foo', 'p2': '$sys', 'p3': '$p1'})
        self.assertEqual('foo', c.get('p1'))
        self.assertEqual('foo', c.get('p3'))

        sys_props['p1'] = 'bar'
        sys_props['sys'] = 'x'
        self.assertEqual('bar', c.get('p1'))
        self.assertEqual('x', c.get('p2'))
        self.assertEqual('bar', c.get('p3'))

    def test_to_str(self):
        d = {'c': 10, 'd': 'foo', 'e': ' bar ', 'f': 'two\nlines'}
        c = Context({}, d)
        self.assertEqual(expected_fmt, str(c))

if __name__ == '__main__':
    unittest.main()