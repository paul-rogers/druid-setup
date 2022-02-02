from os import path
import datetime, shutil, os

from .template import TemplateSet
from .config import ConfigStack
from .service import Services
from .finder import ConfigFinder
from . import consts, builtins

class Model:

    def __init__(self, template):
        self.templates = TemplateSet(template)
        self.config_stack = ConfigStack()
    
    def load(self):
        self.templates.load()
        self.build_system_context()
        self.build_context()
        self.verify_target()
        self.build_metadata()
        self.services = Services(self.context)
        self.define_extensions()
        self.load_base()
        self.build_default_config()
        self.build_user_config()
        self.resolve_config()
    
    def build_system_context(self):
        self.system_context = {
            consts.TEMPLATE_KEY: self.templates.root_template,
            consts.TEMPLATE_PATH_KEY: self.templates.templates[0].file_path,
            consts.TODAY_KEY: datetime.datetime.today().isoformat(),
        }

    def build_context(self):
        context_stack = ConfigStack()
        context_stack.add(builtins.root_context)
        self.templates.walk_includes(
            lambda template: context_stack.add(template.context())
        )
        self.context = context_stack.to_context(self.system_context)

    def verify_target(self):
        self.target = self.context.get(consts.TARGET_KEY)
        if self.target is None:
            raise Exception("'" + consts.TARGET_KEY + "' is not set.")
        if not path.isdir(self.target):
            return
        if path.isfile(path.join(self.target, consts.GENERATED_FILE)):
            return
        raise Exception('Target exists, but was not generated: ' + self.target)

    def build_metadata(self):
        metadata_stack = ConfigStack()
        self.templates.walk_includes(
            lambda template: metadata_stack.add(template.metadata())
        )
        self.metadata = metadata_stack.resolve(self.context).config

    def define_extensions(self):
        extns = self.metadata.get(consts.CUSTOM_KEY, None)
        if extns is None:
            return
        for key, defn in extns.items():
            self.services.build_custom_service(key, defn)
    
    def load_base(self):
        if self.find_base():
            self.load_base_config()

    def find_base(self):
        self.finder = ConfigFinder(self.context)
        if not self.finder.find():
            return False
        self.druid_home = self.finder.druid_home
        self.system_context[consts.DISTRO_KEY] = self.finder.distro
        self.system_context[consts.BASE_CONFIG_PATH_KEY] = self.finder.service_dir
        self.system_context[consts.BASE_ZK_DIR_KEY] = self.finder.zk_dir
        return True

    def load_base_config(self):
        config = self.services.load(self.finder.zk_dir, self.finder.service_dir)
        self.config_stack.add(config)

    def build_default_config(self):
        self.config_stack.add(builtins.default_config)

    def build_user_config(self):
        self.templates.walk_includes(
            lambda template: self.config_stack.add(template.services())
        )

    def resolve_config(self):
        self.final_config = self.config_stack.resolve(self.context)
        service_list = self.final_config.get_value(consts.SERVICES_KEY)
        loaded = [key for key in self.services.config.keys()]
        if service_list is None:
            self.selected_services = set(loaded)
        elif len(service_list) > 0 and service_list[0] == '+':
            self.selected_services = set(service_list[1:])
            self.selected_services += set(loaded)
        else:
            self.selected_services = set(loaded)
        excludes = self.final_config.get_value(consts.EXCLUDE_KEY)
        if excludes is not None:
            self.selected_services -= set(excludes)        
   
    def build(self):
        self.remove_old()
        self.create_new()
        self.build_readme()
        self.services.build(self.selected_services, self.final_config.config)

    def remove_old(self):
        if not path.exists(self.target):
            return
        if not path.isdir(self.target):
            raise Exception("Target exists and is not a directory: " + self.target)
        if not path.isfile(path.join(self.target, consts.GENERATED_FILE)):
            raise Exception("Target exists but was not generated: " + self.target)
        shutil.rmtree(self.target)

    def create_new(self):
        os.makedirs(self.target)
        if not path.isdir(self.target):
            raise Exception("Could not create target: " + self.target)
        disclaimer = self.context.get(consts.DISCLAIMER_KEY)
        if disclaimer is None:
            disclaimer = consts.DISCLAIMER
        with open(path.join(self.target, consts.GENERATED_FILE), 'w') as f:
            f.write(disclaimer.strip())
            f.write('\n')

    def build_readme(self):
        label = self.context.get(consts.README_KEY)
        if label is None:
            return
        with open(path.join(self.target, consts.README_FILE), 'w') as f:
            f.write(label.strip())
            f.write('\n')

    def print_context(self):
        print("Context:")
        print(str(self.context))

    def print_config(self):
        print("Model:")
        print(str(self.final_config))
