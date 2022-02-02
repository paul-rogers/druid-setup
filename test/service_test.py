import unittest, tempfile, filecmp, os, shutil
from os import path

from pysetup import service, consts, builtins
from pysetup.context import Context
from pysetup.config import ConfigStack

class TestService(unittest.TestCase):

    def test_zk_service(self):
        defn = service.services[consts.ZK_SERVICE]
        self.assertIsInstance(defn, service.ZkServiceDefn)
        source = "data/conf/zk"
        config = defn.load_base(source)

        with tempfile.TemporaryDirectory() as tempdir:

            config_dir = path.join(tempdir, "zk")
            defn.build_config(config_dir, config)

            common = os.listdir('data/expected/zk')
            match, mismatch, errors = filecmp.cmpfiles('data/expected/zk', config_dir, common, shallow=False)
            self.assertEqual(3, len(match))
            self.assertEqual(0, len(mismatch))
            self.assertEqual(0, len(errors))

    def test_load_build_services(self):
        with tempfile.TemporaryDirectory() as tempdir:
            vars = builtins.root_context.copy()
            vars.update({
                consts.TARGET_KEY: tempdir,
                consts.README_KEY: 'howdy',
                consts.DATA_DIR_KEY: "/my-path",
                consts.DRUID_HOME_KEY: 'data/conf'
                })
            c = Context(vars)
            s = service.Services(c)
            conf = path.join('data', 'conf')
            zk_dir = path.join(conf, 'zk')
            service_dir = path.join(conf, 'druid')
            config = s.load(zk_dir, service_dir)
            self.assertEqual(3, len(config))
            self.assertTrue(consts.ZK_SERVICE in config)
            self.assertEqual(3, len(config[consts.ZK_SERVICE]))
            self.assertTrue(consts.COMMON_SERVICE in config)
            self.assertEqual(2, len(config[consts.COMMON_SERVICE]))
            self.assertTrue(consts.BROKER_SERVICE in config)
            self.assertEqual(3, len(config[consts.BROKER_SERVICE]))

            s.build(config)
            self.verify_dir(path.join('data', 'expected'), path.join(tempdir, 'conf'))

    def verify_dir(self, dir1, dir2):
        if not path.isdir(dir1):
            self.fail("Missing directory: " + dir1)
        if not path.isdir(dir2):
            self.fail("Missing directory: " + dir2)
        for f in os.listdir(dir1):
            f1 = path.join(dir1, f)
            f2 = path.join(dir2, f)
            if path.isdir(f1):
                self.verify_dir(f1, f2)
            elif not path.isfile(f2):
                self.fail("Missing file: " + f2)
            else:
                self.assertTrue(filecmp.cmp(f1, f2, False), f1)

    def test_custom_service(self):
        c = Context({consts.DRUID_CONFIG_DIR_KEY: 'out'})
        s = service.Services(c)
        s.build_custom_service('extn', {
            'jvm': { 'config': { 'args': {'Xmx': '20G' }}},
            'main': { 'config': { 'main': 'org.bozotron.Main'}}
        })
        extn = s.services.get('extn', None)
        self.assertIsNotNone(extn)
        self.assertEqual('$' + consts.DRUID_CONFIG_DIR_KEY + '/extn', extn.dir_path)
        self.assertEqual(2, len(extn.config))
        self.assertIn('jvm', extn.config)
        self.assertIn('main', extn.config)
        s.expand_extn_services()
        self.assertIn('extn', s.config)
        self.assertIn('jvm', s.config['extn'])
        jvm = s.config['extn']['jvm']
        self.assertEqual(1, len(jvm))
        self.assertIn('args', jvm)
        self.assertIn('Xmx', jvm['args'])
        self.assertIn('main', s.config['extn'])
        main = s.config['extn']['main']
        self.assertEqual(1, len(main))

    def test_copy_resource(self):
        c = Context({})
        s = service.Services(c)
        conf = path.join('data', 'conf')
        zk_dir = path.join(conf, 'zk')
        service_dir = path.join(conf, 'druid')
        s.load(zk_dir, service_dir)
        s.build_custom_service('extn', {
            'jvm': { 'copy': 'broker', 'config': { 'args': {'Xmx': '20G' } } },
            'main': { 'main': 'org.bozotron.Main'}
        })
        s.expand_extn_services()
        jvm = s.config['extn']['jvm']
        self.assertEqual(2, len(jvm))
        self.assertEqual(6, len(jvm['args']))
        self.assertEqual('20G', jvm['args']['Xmx'])

if __name__ == '__main__':
    unittest.main()