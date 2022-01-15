import unittest
import tempfile
import filecmp
from os import path
from pysetup import consts
from pysetup.props import propertiesCodec

class TestPropertiesCodec(unittest.TestCase):

    def test_properties_codec(self):
        self.assertIsNotNone(propertiesCodec)
        source = 'data/runtime.properties'
        config = propertiesCodec.read(source)
        self.assertEquals(11, len(config))

        with tempfile.TemporaryDirectory() as tempdir:
            dest = path.join(tempdir, "out-runtime.properties")
            propertiesCodec.write(config, dest)
            expected = 'data/out-runtime.properties'
            self.assertTrue(filecmp.cmp(dest, expected))

if __name__ == '__main__':
    unittest.main()