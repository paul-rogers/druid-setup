import os
from os import path
import datetime

from .template import Template
from .builder import ConfigBuilder
from .config import ConfigStack
from .service import Service
from . import consts

class Model:

    def __init__(self):
        pass
    
    def load(self, template):
        self.template_name = template
        self.templates = [Template(template)]
        self.expand_includes(self.templates[0])
        self.context_stack = ConfigStack()
        self.config_stack = ConfigStack()
        self.build_system_context()
        self.build_root_context()
        self.build_context()
        self.verify_target()
        self.load_base_config()
        self.build_default_config()
        self.build_user_config()
        self.resolve_config()
    
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

    def build_system_context(self):
        self.system_context = {
            consts.TEMPLATE_KEY: self.template_name,
            consts.TEMPLATE_PATH_KEY: self.templates[0].file_path,
            consts.TODAY_KEY: datetime.datetime.today().isoformat(),
        }

    def build_root_context(self):
        root_context = {
            consts.DATA_DIR_KEY: '$target/var',
            consts.ZK_DATA_DIR_KEY: '$dataDir/zk',
            consts.README_KEY: consts.DEFAULT_README,
            consts.DISCLAIMER_KEY: consts.DISCLAIMER
        }
        self.context_stack.add(root_context)

    def build_context(self):
        self.walk_includes(
            lambda template: self.context_stack.add(template.context())
        )
        self.context = self.context_stack.to_context(self.system_context)

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

    def verify_target(self):
        self.target = self.context.get(consts.TARGET_KEY)
        if self.target is None:
            raise Exception("'" + consts.TARGET_KEY + "' is not set.")
        if not path.isdir(self.target):
            return
        if path.isfile(path.join(self.target, consts.GENERATED_FILE)):
            return
        raise Exception('Target exists, but was not generated: ' + self.target)
    
    def load_base_config(self):
        self.verify_druid()
        config_dir = self.context.get(consts.BASE_CONFIG_KEY)
        if config_dir is None or len(config_dir) == 0:
            print("Warning: no base config set.")
            return
        self.verify_base()
        self.services = {}
        self.load_zk()
        self.load_druid_services()
        self.build_service_config()

    def verify_druid(self):
        self.druid_home = self.context.get(consts.DRUID_HOME_KEY)
        if self.druid_home is None:
            raise Exception("'" + consts.DRUID_HOME_KEY + "' is not set.")
        if not path.isdir(self.druid_home):
            raise Exception("Druid home does not exist: " + self.druid_home)
        if path.isfile(path.join(self.druid_home, 'README')):
            self.distro_type = consts.APACHE_DISTRO
            self.system_context[consts.DISTRO_KEY] = self.distro_type
            return
        if path.isfile(path.join(self.druid_home, 'build.name')):
            self.distro_type = consts.IMPLY_DISTRO
            self.system_context[consts.DISTRO_KEY] = self.distro_type
            return
        raise Exception("Druid home is not a Druid distro?: " + self.druid_home)

    def verify_base(self):
        base_config = self.context.get(consts.BASE_CONFIG_KEY)
        if base_config is None:
            return
        search_path = ['', 'conf', 'conf/druid', 'conf/druid/single-server', 'conf/druid/cluster']
        for p in search_path:
            guess = self.druid_home
            if len(p) > 0:
                guess = path.join(guess, p)
            guess = path.join(guess, base_config)
            if path.isdir(guess) and path.isdir(path.join(guess, consts.COMMON_DIR)):
                self.base_config = guess
                self.system_context[consts.BASE_CONFIG_PATH_KEY] = self.base_config
                return
        raise Exception('Base config not found: ' + base_config)
        
    def load_zk(self):
        """
        ZK is not within the named config directory: it is in
        ${druidHome}/conf/zk
        """
        self.zk_dir = path.join(self.druid_home, 'conf', 'zk')
        if not path.isdir(self.zk_dir):
            raise Exception("No zK found: " + self.zk_dir)
        service = Service(consts.ZK_SERVICE)
        service.load_base(self.zk_dir)
        self.services[consts.ZK_SERVICE] = service
        self.system_context[consts.BASE_ZK_DIR_KEY] = self.zk_dir
    
    def load_druid_services(self):
       for f in os.listdir(self.base_config):
            full_path = path.join(self.base_config, f)
            if f == consts.USER_CLASSPATH_DIR:
                # TODO
                continue
            if f == consts.COMMON_DIR:
                service = Service(consts.COMMON_SERVICE)
            else:
                service = Service(f)
            service.load_base(full_path)
            self.services[f] = service

    def build_service_config(self):
        config = {}
        for service in self.services.values():
            config[service.name] = service.base_config
        self.config_stack.add(config)

    def build_default_config(self):
        self.default_config = {
            consts.ZK_SERVICE: {
                consts.PROPERTIES_KEY: {
                    'dataDir': '$dataDir/zk'
                }
            },
            consts.COMMON_SERVICE: {
                consts.PROPERTIES_KEY: {
                    'druid.indexer.logs.directory': '$dataDir/druid/indexing-logs',
                    'druid.storage.storageDirectory': '$dataDir/druid/segments'
                }
            },
            consts.BROKER_SERVICE: {
                consts.PROPERTIES_KEY: {
                    'druid.processing.tmpDir': '$dataDir/druid/processing'
                }
            },
            consts.MASTER_SERVICE: {
                consts.PROPERTIES_KEY: {
                    'derby.stream.error.file': '$dataDir/druid/derby.log'
                }
            },
            consts.HISTORICAL_SERVICE: {
                consts.JVM_KEY: {
                    consts.PROPERTIES_KEY: {
                        'java.io.tmpdir': '$dataDir/tmp'
                    }
                },
                consts.PROPERTIES_KEY: {
                    'druid.processing.tmpDir': '$dataDir/druid/processing',
                    'druid.segmentCache.locations': [{
                        "path":"$dataDir/druid/segment-cache",
                        "maxSize":"300g"}]
                }
            },
            consts.MIDDLE_MANAGER_SERVICE: {
                consts.JVM_KEY: {
                    consts.PROPERTIES_KEY: {
                        'java.io.tmpdir': '$dataDir/tmp'
                    }
                },
                consts.PROPERTIES_KEY: {
                    'druid.indexer.task.hadoopWorkingPath': '$dataDir/druid/hadoop-tmp',
                }
            },
            consts.ROUTER_SERVICE: {
                consts.JVM_KEY: {
                    consts.PROPERTIES_KEY: {
                        'java.io.tmpdir': '$dataDir/tmp'
                    }
                }
            }
        }
        self.config_stack.add(self.default_config)

    def build_user_config(self):
        self.walk_includes(
            lambda template: self.config_stack.add(template.services())
        )

    def resolve_config(self):
        self.final_config = self.config_stack.resolve(self.context)
    
    def build(self):
        builder = ConfigBuilder(self)
        builder.build()

    def print_config(self):
        print("Context:")
        print(str(self.context))

    def print_model(self):
        print("Model:")
        print(str(self.final_config))

