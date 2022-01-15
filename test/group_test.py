import unittest
from pysetup.group import ConfigGroup, ConfigStack
from pysetup.codec import Value
from pysetup.context import Context

class TestConfigGroup(unittest.TestCase):

    def test_empty_group(self):
        g = ConfigGroup(None)
        self.assertTrue(g.is_empty())
        g = ConfigGroup({})
        self.assertTrue(g.is_empty())
        child = ConfigGroup({})
        g = ConfigGroup({'top': child})
        g.prune()
        self.assertTrue(g.is_empty())
        g = ConfigGroup({'foo': Value('bar')})
        g.prune()
        self.assertFalse(g.is_empty())

    def test_nested_group(self):
        g = ConfigGroup({
            'value': Value('$foo'),
            'dict': {'dict-value': Value('$bar')},
            'group': ConfigGroup({'group-value': Value('$mumble')})
            })
        c = Context()
        c.add({'foo': 'a', 'bar': 'b', 'mumble': 'c'})
        g.resolve(c)
        self.assertEqual('a', g.get('value').value)
        self.assertEqual('b', g.get('dict')['dict-value'].value)
        self.assertEqual('c', g.get('group').get('group-value').value)

    def test_empty_stack(self):
        s = ConfigStack()
        context = Context()
        s.resolve(context)
        self.assertTrue(s.resolved().is_empty())

        child = ConfigGroup({})
        g = ConfigGroup({'top': child})
        s = ConfigStack()
        s.add(child)
        self.assertEqual(0, len(s.groups))
        s.resolve(context)
        self.assertTrue(s.resolved().is_empty())

        self.assertIsNone(s.get('foo'))

    def test_single_level(self):
        s = ConfigStack()
        g1 = ConfigGroup({'a': Value('1'), 'b': Value('2')})
        s.add(g1)
        c = Context()
        s.resolve(c)
        r = s.resolved()
        self.assertEqual(2, len(r.merged()))
        self.assertEqual('1', s.get('a').value)
        self.assertEqual('2', s.get('b').value)

    def test_two_levels(self):
        s = ConfigStack()
        g1 = ConfigGroup({'a': Value('1'), 'b': Value('2')})
        s.add(g1)
        g2 = ConfigGroup({'a': Value('3'), 'c': Value('4')})
        s.add(g2)
        c = Context()
        s.resolve(c)
        r = s.resolved()
        self.assertEqual(3, len(r.merged()))
        self.assertEqual('3', s.get('a').value)
        self.assertEqual('2', s.get('b').value)
        self.assertEqual('4', s.get('c').value)

    def test_resolve(self):
        s = ConfigStack()
        g1 = ConfigGroup({'a': Value('$foo'), 'b': Value('$foo/$bar')})
        s.add(g1)
        g2 = ConfigGroup({'a': Value('$bar'), 'c': Value('$foo$bar')})
        s.add(g2)
        c = Context()
        c.add({'foo': 'x', 'bar': 'y'})
        s.resolve(c)
        r = s.resolved()
        self.assertEqual(3, len(r.resolved()))
        self.assertEquals('y', s.get('a').value)
        self.assertEquals('x/y', s.get('b').value)
        self.assertEquals('xy', s.get('c').value)

if __name__ == '__main__':
    unittest.main()