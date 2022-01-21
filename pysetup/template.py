import yaml
from os import path
from .group import ConfigGroup
from . import consts

prop_names = [
    consts.DRUID_HOME_KEY,
    consts.TARGET_KEY,
    consts.BASE_CONFIG_KEY,
    consts.DATA_DIR_KEY,
    consts.CONFIG_DIR_KEY,
]

class Template:

    def __init__(self, file_path):
        self.file_path = file_path
        self.path = path.expanduser(file_path)
        self.path = path.realpath(self.path)
        self.dir = path.dirname(file_path)
        self.dependencies = []
        self.config = {}

        with open(self.path) as f:
            self.raw = yaml.load(f, Loader=yaml.Loader)

        self.gather_context()
        self.gather_services()

    def gather_context(self):
        context = self.raw.get(consts.CONTEXT_KEY, None)
        context = {} if context is None else context
        if context is None:
            context = {}
        for k in prop_names:
            v = self.raw.get(k, None)
            if v is not None:
                context[k] = v
        self.config[consts.CONTEXT_KEY] = context

    def gather_services(self):
        services = self.raw.get(consts.SERVICES_KEY, None)
        if services is not None and len(services) > 0:
            self.config[consts.SERVICES_KEY] = services

    def includes(self):
        try:
            includes = self.raw[consts.INCLUDE_KEY]
        except KeyError:
            return []
        if type(includes) is str:
            includes = [includes]
        resolved = []
        for f in includes:
            if len(f) == 0:
                continue
            if f[0] in ['/', '~', '$']:
                resolved.append(f)
            else:
                resolved.append(path.join(self.dir, f))
        return resolved

    def context(self):
        return self.config.get(consts.CONTEXT_KEY, None)

    def services(self):
        return self.config.get(consts.SERVICES_KEY, None)

    def add_dependency(self, include):
        self.dependencies.add(include)
        self.main_group.parents.add(include.main_group)
        self.context_group.parents.add(include.context_group)
