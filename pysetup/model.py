import os
from os import path
import datetime

from pysetup.group import ConfigGroup

from .service import CommonService, DruidService, ZkService
from .template import Template
from .context import Context
from .builder import ConfigBuilder
from . import consts

class Model:

    def __init__(self):
        pass
    
    def load(self, template):
        self.template_name = template
        self.templates = [Template(template)]
        self.expand_includes(self.templates[0])
        self.build_context()
        self.build_default_config()
        self.verify()
        self.load_services()
        self.apply_service_defaults()
        self.apply_service_overrides()
        self.resolve_services()
    
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

    def build_context(self):
        self.root_context = {
            consts.TEMPLATE_KEY: self.template_name,
            consts.TEMPLATE_PATH_KEY: self.templates[0].file_path,
            consts.DATA_DIR_KEY: '$target/var',
            consts.ZK_DATA_DIR_KEY: '$dataDir/zk',
            consts.README_KEY: consts.DEFAULT_README,
            consts.TODAY_KEY: datetime.datetime.today().isoformat(),
            consts.DISCLAIMER_KEY: consts.DISCLAIMER
        }
        self.context = Context(self.root_context)
        self.walk_includes(
            lambda template: self.add_context(self.context, template))

    @staticmethod
    def add_context(context, template):
        context.add(template.context_props)
        context.add(template.kw_props)

    def build_default_config(self):
        self.default_config = {
            consts.ZK_SERVICE: {
                consts.PROPERTIES_KEY: {
                    'dataDir': '$dataDir/zk'
                }
            }
        }
    
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

    def verify(self):
        self.verify_druid()
        self.verify_target()
        self.verify_base()

    def verify_druid(self):
        try:
            self.druid_home = self.context.get(consts.DRUID_HOME_KEY)
            self.root_context[consts.DRUID_HOME_KEY] = self.druid_home
        except KeyError:
            raise Exception("'" + consts.DRUID_HOME_KEY + "' is not set.")
        if not path.isdir(self.druid_home):
            raise Exception("Druid home does not exist: " + self.druid_home)
        if path.isfile(path.join(self.druid_home, 'README')):
            self.distro_type = consts.APACHE_DISTRO
            self.root_context[consts.DISTRO_KEY] = self.distro_type
            return
        if path.isfile(path.join(self.druid_home, 'build.name')):
            self.distro_type = consts.IMPLY_DISTRO
            self.root_context[consts.DISTRO_KEY] = self.distro_type
            return
        raise Exception("Druid home is not a Druid distro?: " + self.druid_home)

    def verify_target(self):
        try:
            self.target = self.context.get(consts.TARGET_KEY)
            self.root_context[consts.TARGET_KEY] = self.target
        except KeyError:
            raise Exception("'" + consts.TARGET_KEY + "' is not set.")
        if not path.isdir(self.target):
            return
        if path.isfile(path.join(self.target, consts.GENERATED_FILE)):
            return
        raise Exception('Target exists, but was not generated: ' + self.target)
    
    def verify_base(self):
        try:
            base_config = self.context.get(consts.BASE_CONFIG_KEY)
            self.root_context[consts.BASE_CONFIG_KEY] = base_config
        except KeyError:
            raise Exception("'" + consts.BASE_CONFIG_KEY + "' is not set.")
        search_path = ['', 'conf', 'conf/druid', 'conf/druid/single-server', 'conf/druid/cluster']
        for p in search_path:
            guess = self.druid_home
            if len(p) > 0:
                guess = path.join(guess, p)
            guess = path.join(guess, base_config)
            if path.isdir(guess) and path.isdir(path.join(guess, consts.COMMON_DIR)):
                self.base_config = guess
                self.root_context[consts.BASE_CONFIG_PATH_KEY] = self.base_config
                return
        raise Exception('Base config not found: ' + base_config)
        
    def load_services(self):
        self.services = {}
        self.load_zk()
        self.load_druid_services()

    def load_zk(self):
        """
        ZK is not within the named config directory: it is in
        ${druidHome}/conf/zk
        """
        self.zk_dir = path.join(self.druid_home, 'conf', 'zk')
        if not path.isdir(self.zk_dir):
            raise Exception("No zK found: " + self.zk_dir)
        service = ZkService()
        service.load_base(self.zk_dir)
        self.services[consts.ZK_SERVICE] = service
        self.root_context[consts.BASE_ZK_DIR_KEY] = self.zk_dir
    
    def load_druid_services(self):
       for f in os.listdir(self.base_config):
            full_path = path.join(self.base_config, f)
            if f == consts.USER_CLASSPATH_DIR:
                # TODO
                continue
            if f == consts.COMMON_DIR:
                service = CommonService()
            else:
                service = DruidService(f)
            service.load_base(full_path)
            self.services[f] = service

    def resolve_services(self):
        for service in self.services.values():
            service.resolve(self.context)

    def apply_service_defaults(self):
        for key, service in self.services.items():
            try:
                service.apply_config(self.default_config[key])
            except KeyError:
                pass
    
    def apply_service_overrides(self):
        pass

    def build(self):
        builder = ConfigBuilder(self)
        builder.build()

    def print_config(self):
        print("Context:")
        for k in sort_keys(self.context.keys()):
            print_value(k, self.context.get_value(k))

def sort_keys(s):
    keys = [k for k in s]
    keys.sort()
    return keys

def print_value(k, v):
    if v is None:
        print('  {}: <unset>'.format(k))
        return
    if type(v) != str:
        print('  {}: {}'.format(k, v))
    if v.find('\n') != -1:
        print('  {}: """'.format(k))
        lines = v.strip().split('\n')
        for line in lines:
            print('    | {}'.format(line))
        print('    """')
        return
    if v != v.strip():
        print('  {}: "{}"'.format(k, v))
        return
    print('  {}: {}'.format(k, v))
