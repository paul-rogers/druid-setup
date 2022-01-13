import yaml
from os import path
from .group import ConfigGroup
from . import consts

prop_names = [
    consts.DRUID_HOME_KEY,
    consts.TARGET_KEY,
    consts.BASE_CONFIG_KEY
]

def extract_props(source, keys):
    props = {}
    for k in keys:
        try:
            v = source[k]
            props[k] = v
        except KeyError:
            pass
    return props

class Template:

    def __init__(self, file_path):
        self.file_path = file_path
        self.path = path.expanduser(file_path)
        self.path = path.realpath(self.path)
        self.dir = path.dirname(self.path)
        self.dependencies = []

        with open(self.path) as f:
            self.raw = yaml.load(f, Loader=yaml.Loader)

        self.gather_props()

    def gather_props(self):
        props = extract_props(self.raw, prop_names)
        self.main_group = ConfigGroup(props)
        try:
            context = self.raw[consts.CONTEXT_KEY]
        except KeyError:
            context = {}
        self.context_group = ConfigGroup(context)

    def includes(self):
        try:
            includes = self.raw[consts.INCLUDE_KEY]
        except KeyError:
            return []
        return [path.join(self.dir, f) for f in includes]

    def add_dependency(self, include):
        self.dependencies.add(include)
        self.main_group.parents.add(include.main_group)
        self.context_group.parents.add(include.context_group)
