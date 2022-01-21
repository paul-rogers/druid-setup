import unittest

from pysetup.template import Template

class TestTemplate(unittest.TestCase):

    def test_load(self):
        t = Template('data/templates/main.yaml')

        self.assertEqual(t.context(), {
            'target': '$home/apps/example',
            'configDir': '$targetDir/config',
            # Main props override context
            'dataDir': '$home/data/example',
            'baseConfig': 'micro-quickstart',
            'heapMem': '2G',
            'directMem': '1G'
            })
        self.assertEqual(t.services(), {
            'historical': {
                'runtime': {'foo': 'bar'},
                'jvm': {'foo': None}
                }
            })
        self.assertEqual(t.includes(), [
            'data/templates/base.yaml',
            '/tmp/std.yaml'
            ])

if __name__ == '__main__':
    unittest.main()