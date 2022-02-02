import unittest
import tempfile
import filecmp
from os import path
from pysetup.props import propertiesCodec
from pysetup.props import parse_value, format_value

class TestPropertiesCodec(unittest.TestCase):

    def test_properties_codec(self):
        self.assertIsNotNone(propertiesCodec)
        source = 'data/runtime.properties'
        config = propertiesCodec.read(source)
        self.assertEqual(11, len(config))

        with tempfile.TemporaryDirectory() as tempdir:
            dest = path.join(tempdir, "out-runtime.properties")
            propertiesCodec.write(dest, config)
            expected = 'data/out-runtime.properties'
            self.assertTrue(filecmp.cmp(dest, expected))

    def test_format_parser(self):
        key = 'druid.extensions.loadList'
        value = '["druid-hdfs-storage", "druid-kafka-indexing-service", "druid-datasketches"]'
        parsed = parse_value(key, value)
        self.assertIs(type(parsed), list)
        self.assertEqual(3, len(parsed))
        self.assertEqual("druid-hdfs-storage", parsed[0])

        fmt = format_value(key, parsed)
        self.assertEqual(value, fmt)

        self.assertEqual('bar', parse_value('foo', 'bar'))
        self.assertEqual('bar', format_value('foo', 'bar'))

if __name__ == '__main__':
    unittest.main()