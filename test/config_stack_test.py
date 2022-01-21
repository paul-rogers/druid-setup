import unittest

from pysetup.config2 import ConfigStack
from pysetup.context import Context
from pysetup.codec import tombstone

class TestService(unittest.TestCase):

    def test_empty(self):
        s = ConfigStack()
        self.assertIsNone(s.get('foo'))
        result = s.merge()
        self.assertEqual(0, len(result))
        c = Context({})
        resolved = s.resolve(c)
        self.assertEquals(0, len(resolved.config))
    
    def test_layers(self):
        s = ConfigStack()
        level1 = {'prop1': 'a', 'prop2': 'b', 'prop3': 'c'}
        s.add(level1)
        level2 = {'prop1': 'd', 'prop2': 'e', 'prop4': 'f'}
        s.add(level2)
        level3 = {'prop1': 'g'}
        s.add(level3)

        c = Context({})
        resolved = s.resolve(c)
        self.assertEqual('g', resolved.get('prop1'))
        self.assertEqual('e', resolved.get('prop2'))
        self.assertEqual('c', resolved.get('prop3'))
        self.assertEqual('f', resolved.get('prop4'))

    def test_as_context(self):
        s = ConfigStack()
        level1 = {'prop1': 'a', 'prop2': 'b', 'prop3': '${x}', 'prop4': '${prop1}', 'prop5': '${prop2}'}
        s.add(level1)
        level2 = {'prop2': 'c', 'prop6': '$prop1', 'x': 10}
        s.add(level2)
        level3 = {'prop2': 'd'}
        s.add(level3)

        c = s.to_context()
        self.assertEqual('a', c.get('prop1'))
        self.assertEqual('d', c.get('prop2'))
        self.assertEqual('10', c.get('prop3'))
        self.assertEqual('a', c.get('prop4'))
        self.assertEqual('d', c.get('prop5'))
        self.assertEqual('a', c.get('prop6'))
        self.assertEqual('10', c.get('x'))

        self.assertEqual('prop2: d, combo: aandd/a', c.replace("prop2: $prop2, combo: ${prop4}and$prop5/$prop6"))

        self.assertEqual('${x}', c.get_value('prop3'))

        self.assertEqual(7, len(c.keys()))

    def test_delete(self):
        s = ConfigStack()
        s.add({'p1': 'a', 'p2': 'b'})
        s.add({'p1': tombstone})
        s.add({'p1': 'c', 'p2': tombstone})

        result = s.merge()
        print(result)
        self.assertEqual(1, len(result))
        self.assertEqual('c', result['p1'])
        self.assertFalse('p2' in result)

    def test_non_string(self):
        s = ConfigStack()
        s.add({'p1': None, 'p2': 10})
        s.add({'p1': 10, 'p3': None})
        s.add({'p1': 'c'})

        result = s.merge()
        self.assertEquals(3, len(result))
        self.assertEqual('c', result['p1'])
        self.assertEqual(10, result['p2'])
        self.assertIsNone(result['p3'])

    def test_nested_map(self):
        s = ConfigStack()
        s.add({'t1': {'p1': 'a', 'p2': 'b'}})
        s.add({'t2': {'p1': 'c', 'p2': 'd'}})
        s.add({'t1': {'p1': 'e'}, 't2': {'p2': 'f'}})

        result = s.merge()
        self.assertEqual({'p1': 'e', 'p2': 'b'}, result['t1'])
        self.assertEqual({'p1': 'c', 'p2': 'f'}, result['t2'])

if __name__ == '__main__':
    unittest.main()