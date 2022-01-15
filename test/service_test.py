import unittest
import tempfile
import filecmp
from os import path

from pysetup import service, consts
from pysetup.context import Context

class TestService(unittest.TestCase):

    def test_zk_service(self):
        s = service.Service(consts.ZK_SERVICE, service.services[consts.ZK_SERVICE])
        defn = s.defn
        self.assertIs(service.ZkServiceDefn, defn)
        self.assertIsInstance(defn, service.ZkServiceDefn)
        source = "data/conf/druid/zk"
        s.load_base(source)

        overlay_conf = {
            consts.PROPERTIES_KEY: {
                'dataDir': '$dataDir/zk'
                }
            }
        s.apply_config(overlay_conf)

        with tempfile.TemporaryDirectory() as tempdir:

            # Use fixed path to write config
            data_dir = path.join(tempdir, "zk-data")
            c = Context()
            c.add({consts.DATA_DIR_KEY: "/my-path/"})
            s.resolve(c)

            config_dir = path.join(tempdir, "zk")
            s.build_config(config_dir, c)

            match, mismatch, errors = filecmp.cmpfiles('data/expected/zk', config_dir, shallow=False)
            self.assertEquals(3, len(match))
            self.assertEqual(0, len(mismatch))
            self.assertEqual(0, len(errors))

            # Cheat a bit. Change the path to test data dir
            data_dir = path.join(tempdir, "zk-data")
            c = Context()
            c.add({consts.DATA_DIR_KEY: data_dir})
            s.build_data(c)
            self.assertTrue(path.isdir(data_dir))

if __name__ == '__main__':
    unittest.main()