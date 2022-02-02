import unittest

from pysetup.template import Template

class TestTemplate(unittest.TestCase):

    def test_load(self):
        t = Template('data/templates/main.yaml')

        print(t.context())
        self.assertEqual(t.context(), {
            'druidHome': '/tmp/apache-druid-0.12',
            # Main props override context
            'target': '$home/apps/example',
            'configDir': '$targetDir/config',
            'baseConfig': 'micro-quickstart',
            'dataDir': '$home/data/example',
            'heapMem': '2G',
            'directMem': '1G'
            })
        md = t.metadata()
        self.assertEqual(3, len(md))
        self.assertTrue('custom' in md)
        self.assertTrue('services' in md)
        self.assertTrue('exclude' in md)
        self.assertEqual(t.services(), {
            'historical': {
                'runtime': {'foo': 'bar'},
                'jvm': {'foo': None}
            },
            'whizbang': {
                'properties': {
                    'foo.bar' : 'mumble'
                }
            }})
        self.assertEqual(t.includes(), [
            'data/templates/base.yaml',
            '/tmp/std.yaml'
            ])

if __name__ == '__main__':
    unittest.main()