import yaml
from os import path
from . import consts

context_keys = [
    consts.BASE_CONFIG_KEY,
    consts.DRUID_HOME_KEY,
    consts.TARGET_KEY,
]
metadata_keys = [
    consts.CUSTOM_KEY,
    consts.EXCLUDE_KEY,
    consts.SERVICES_KEY,
]

class TemplateSet:

    def __init__(self, root_template):
        self.root_template = root_template
        self.templates = [Template(self.root_template)]

    def load(self):
        self.expand_includes(self.templates[0])

    def expand_includes(self, template):
        for f in template.includes():
            include = None
            for t in self.templates:
                if f == t.file_path:
                    include = t
                    break
            if include is None:
                include = Template(f)
                self.templates.append(include)
                self.expand_includes(include)
            template.add_depenency(include)

    def walk_includes(self, fn):
        for include in self.templates:
            include.touched = False
        self.visit_template(self.templates[0], fn)
    
    def visit_template(self, template, fn):
        if template.touched:
            return
        template.touched = True
        for include in template.dependencies:
            self.visit_template(include, fn)
        fn(template)

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
            self.remainder = self.raw.copy()

        self.gather_context()
        self.gather_includes()
        self.gather_metadata()
        self.gather_services()

    def gather_context(self):
        self._context = self.remainder.pop(consts.CONTEXT_KEY, {})
        for k in context_keys:
            v = self.remainder.pop(k, None)
            if v is not None:
                self._context[k] = v

    def gather_includes(self):
        self._includes = self.remainder.pop(consts.INCLUDE_KEY, [])
        if type(self._includes) is str:
            self._includes = [self._includes]
        self.resolved_includes = []
        for f in self._includes:
            if len(f) == 0:
                continue
            if f[0] in ['/', '~', '$']:
                self.resolved_includes.append(f)
            else:
                self.resolved_includes.append(path.join(self.dir, f))

    def gather_metadata(self):
        self._metadata = {}
        for key in metadata_keys:
            value = self.remainder.pop(key, None)
            if not value is None:
                self._metadata[key] = value

    def gather_services(self):
        self._services = self.remainder

    def includes(self):
        return self.resolved_includes

    def metadata(self):
        return self._metadata

    def context(self):
        return self._context

    def services(self):
        return self._services

    def add_dependency(self, include):
        self.dependencies.add(include)
        self.main_group.parents.add(include.main_group)
        self.context_group.parents.add(include.context_group)
