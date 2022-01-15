import unittest
import tempfile
import filecmp
from os import path
from pysetup import consts
from pysetup.jvm import jvmCodec

class TestJvmCodec(unittest.TestCase):

    def test_jvm_codec(self):
        self.assertIsNotNone(jvmCodec)
        source = 'data/jvm.config'
        config = jvmCodec.read(source)
        args = config[consts.JVM_ARGS_KEY]
        self.assertEqual(6, len(args))
        props = config[consts.PROPERTIES_KEY]
        self.assertEqual(4, len(props))

        with tempfile.TemporaryDirectory() as tempdir:
            dest = path.join(tempdir, "out-jvm.config")
            jvmCodec.write(config, dest)
            expected = 'data/out-jvm.config'
            self.assertTrue(filecmp.cmp(dest, expected))

if __name__ == '__main__':
    unittest.main()