from os import path
import os, shutil
from .jvm import JvmCodec
from .group import ConfigGroup, PropertiesGroup, JvmGroup
from .codec import MainCodec, FileCodec
from .props import PropertiesCodec
from . import consts

class Service:

    def __init__(self, name, keys):
        self.name = name
        self.keys = keys
        self.base_config = {}
        self.overrides = []
        self.resolved = {}

    def load_base(self, conf_dir):
        raise NotImplementedError()

    def apply_config(self, config):
        raise NotImplementedError()

    def resolve(self, context):
        self.stitch()
        for v in self.resolved.values():
            v.resolve(context)

    def stitch(self):
        self.resolved = self.base_config.copy()
        for override in self.overrides:
            for key in self.keys:
                try:
                    group = override[key]
                    try:
                        group.parent = self.resolved[key]
                    except KeyError:
                        pass
                    self.resolved[key] = group
                except KeyError:
                    pass

    def build(self, target_dir, context):
        raise NotImplementedError()

class DruidService(Service):

    def __init__(self, name):
        Service.__init__(self, name, [
            consts.JVM_KEY,
            consts.PROPERTIES_KEY,
            consts.MAIN_KEY
        ])

    def load_base(self, service_dir):
        self.base_config = {
            consts.JVM_KEY: 
                JvmGroup(JvmCodec().read(path.join(service_dir, consts.JVM_CONFIG_FILE))),
            consts.PROPERTIES_KEY: 
                PropertiesGroup(PropertiesCodec().read(path.join(service_dir, consts.RUNTIME_PROPERTIES_FILE))),
            consts.MAIN_KEY:
                ConfigGroup(MainCodec().read(path.join(service_dir, consts.MAIN_CONFIG_FILE)))
        }


    def apply_config(self, defaults):
        pass
class CommonService(Service):

    def __init__(self):
        Service.__init__(self, consts.COMMON_DIR, [
            consts.PROPERTIES_KEY,
            consts.LOG4J_KEY
        ])

    def load_base(self, service_dir):
        self.base_config = {
            consts.PROPERTIES_KEY: 
                PropertiesGroup(PropertiesCodec().read(path.join(service_dir, consts.COMMON_PROPERTIES_FILE))),
            consts.LOG4J_KEY:
                ConfigGroup(FileCodec().read(path.join(service_dir, consts.LOG4J_FILE)))
        }

class ZkService(Service):
    """
    Represents the ZooKeeper service.
    """

    def __init__(self):
        Service.__init__(self, consts.ZK_SERVICE, [
            consts.JVM_KEY,
            consts.PROPERTIES_KEY
        ])

    def load_base(self, service_dir):
        self.source_dir = service_dir
        self.base_config = {
            consts.JVM_KEY: 
                JvmGroup(JvmCodec().read(path.join(service_dir, consts.JVM_CONFIG_FILE))),
            consts.PROPERTIES_KEY: 
                ConfigGroup(PropertiesCodec().read(path.join(service_dir, consts.ZOO_CFG_FILE)))
        }

    def apply_config(self, config):
        layer = {}
        try:
            layer[consts.JVM_KEY] = JvmGroup(config[consts.JVM_KEY])
        except KeyError:
            pass
        try:
            layer[consts.PROPERTIES_KEY] = ConfigGroup({
                consts.PROPERTIES_KEY: config[consts.PROPERTIES_KEY]})
        except KeyError:
            pass
        if len(layer) > 0:
            print("layer:", layer)
            self.overrides.append(layer)

    def build(self, dest_dir, context):
        os.makedirs(dest_dir)
        zk_data_dir = context.get(consts.ZK_DATA_DIR_KEY)
        os.makedirs(zk_data_dir)
        self.write_jvm_config(dest_dir)
        self.write_zoo_cfg(dest_dir)
 
        for f in os.listdir(self.source_dir):
            if f == consts.ZOO_CFG_FILE or f == consts.JVM_CONFIG_FILE:
                continue
            source_path = path.join(self.source_dir, f)
            dest_path = path.join(dest_dir, f)
            shutil.copyfile(source_path, dest_path)

    def write_jvm_config(self, dest_dir):
        try:
            JvmCodec().write(
                self.resolved[consts.JVM_KEY].resolved(),
                path.join(dest_dir, consts.ZOO_CFG_FILE))
        except KeyError:
            pass

    def write_zoo_cfg(self, dest_dir):
        try:
            PropertiesCodec().write(
                self.resolved[consts.PROPERTIES_KEY].resolved(),
                path.join(dest_dir, consts.ZOO_CFG_FILE))
        except KeyError:
            pass
