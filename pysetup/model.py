import os
from os import path

from .service import CommonService, DruidService, ZkService
from .template import Template

class Model:

    def __init__(self):
        pass
    
    def load(self, template):
        self.template_name = template
        self.templates = [Template(template)]
        self.root_context = {}
        self.expand_includes(self.templates[0])
        self.root_context = {
            'template': template,
            'templatePath': self.templates[0].file_path
        }
        self.resolve_specs()
        self.verify()
        self.load_services()
    
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

    def resolve_specs(self):
        top = self.templates[0]
        self.context = top.context_group.resolve(self.root_context)
        self.specs = top.main_group.resolve(self.context)

    def verify(self):
        self.verify_druid()
        self.verify_target()
        self.verify_base()

    def verify_druid(self):
        try:
            self.druid_home = self.specs['druidHome']
            self.root_context['druidHome'] = self.druid_home
        except KeyError:
            raise Exception("'druidHome' is not set.")
        if not path.isdir(self.druid_home):
            raise Exception("Druid home does not exist: " + self.druid_home)
        if path.isfile(path.join(self.druid_home, 'README')):
            self.distro_type = 'apache'
            self.root_context['distro'] = self.distro_type
            return
        if path.isfile(path.join(self.druid_home, 'build.name')):
            self.distro_type = 'imply'
            self.root_context['distro'] = self.distro_type
            return
        raise Exception("Druid home is not a Druid distro?: " + self.druid_home)

    def verify_target(self):
        try:
            self.target = self.specs['target']
            self.root_context['target'] = self.target
        except KeyError:
            raise Exception("'target' is not set.")
        if not path.isdir(self.target):
            return
        if path.isfile('.generated"'):
            return
        raise Exception('Target exists, but was not generated: ' + self.target)
    
    def verify_base(self):
        try:
            base_config = self.specs['baseConfig']
            self.root_context['baseConfig'] = base_config
        except KeyError:
            raise Exception("'baseConfig' is not set.")
        search_path = ["", "conf", "conf/druid", "conf/druid/single-server", "conf/druid/cluster"]
        for p in search_path:
            guess = self.druid_home
            if len(p) > 0:
                guess = path.join(guess, p)
            guess = path.join(guess, base_config)
            if path.isdir(guess) and path.isdir(path.join(guess, 'druid', '_common')):
                self.base_config = guess
                self.root_context['baseConfigPath'] = self.base_config
                return
        raise Exception('Base config not found: ' + base_config)
        
    def load_services(self):
        self.services = []
        self.load_zk()
        self.load_druid_services()

    def load_zk(self):
        """
        ZK is not within the name config directory: it is in
        ${druidHome}/conf/zk
        """
        self.zk_dir = path.join(self.druid_home, 'conf', 'zk')
        if not os.isdir(self.zk_dir):
            raise Exception("No zK found: " + self.zk_dir)
        service = ZkService()
        service.load(self.zk_dir)
        self.services.append(service)
        self.root_context['zkDir'] = self.zk_dir
    
    def load_druid_services(self, conf_dir):
       for f in os.listdir(self.base_config):
            full_path = path.join(self.base_config, f)
            if f == 'user-classpath':
                # TODO
                continue
            if f == '_common':
                service = CommonService()
            else:
                service = DruidService(f)
            service.load_base(full_path)
            self.services.append(service)

