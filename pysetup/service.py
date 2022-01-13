from os import path
import os, shutil
from .jvm import JvmCodec
from .group import ConfigGroup, PropertiesGroup, JvmGroup
from .codec import MainCodec, FileCodec
from .props import PropertiesCodec
from . import consts

class Service:

    def __init__(self, name):
        self.name = name

    def load_base(self, conf_dir):
        raise NotImplementedError()

    def build(self, target_dir, context):
        raise NotImplementedError()

class DruidService(Service):

    def __init__(self, name):
        Service.__init__(self, name)

    def load_base(self, service_dir):
        self.jvm = JvmGroup(JvmCodec().read(path.join(service_dir, consts.JVM_CONFIG_FILE)))
        self.properties = PropertiesGroup(PropertiesCodec().read(path.join(service_dir, consts.RUNTIME_PROPERTIES_FILE)))
        self.main = ConfigGroup(MainCodec().read(path.join(service_dir, consts.MAIN_CONFIG_FILE)))

class CommonService(Service):

    def __init__(self):
        Service.__init__(self, consts.COMMON_DIR)

    def load_base(self, service_dir):
        self.properties = PropertiesGroup(PropertiesCodec().read(path.join(service_dir, consts.COMMON_PROPERTIES_FILE)))
        self.log4j = ConfigGroup(FileCodec().read(path.join(service_dir, consts.LOG4J_FILE)))

class ZkService(Service):
    """
    Represents the ZooKeeper service.
    """

    def __init__(self):
        Service.__init__(self, consts.ZK_SERVICE)
        self.user_jvm = None
        self.user_config = None

    def load_base(self, service_dir):
        self.source_dir = service_dir
        self.base_jvm = JvmGroup(JvmCodec().read(path.join(service_dir, consts.JVM_CONFIG_FILE)))
        self.base_config = ConfigGroup(PropertiesCodec().read(path.join(service_dir, consts.ZOO_CFG_FILE)))

    def override_config(self, label, group):
        if label == consts.JVM_KEY:
            self.user_jvm = group
            self.user_jvm.parents.add(self.base_jvm)
        elif label == consts.PROPERTIES_KEY:
            self.user_config = group
            self.user_config.parents.add(self.base_config)
        else:
            raise Exception("Unsupported ZK key: " + label)

    def build(self, dest_dir, context):
        os.makedirs(dest_dir)
        zk_data_dir = context.get(consts.ZK_DATA_DIR_KEY)
        os.makedirs(zk_data_dir)
        self.write_jvm_config(dest_dir, context)
        self.write_zoo_cfg(dest_dir, context)
 
        for f in os.listdir(self.source_dir):
            if f == consts.ZOO_CFG_FILE or f == consts.JVM_CONFIG_FILE:
                continue
            source_path = path.join(self.source_dir, f)
            dest_path = path.join(dest_dir, f)
            shutil.copyfile(source_path, dest_path)

    def write_jvm_config(self, dest_dir, context):
        group = self.base_config if self.user_config is None else self.user_config
        JvmCodec().write(
            path.join(dest_dir, consts.ZOO_CFG_FILE),
            group.resolve(self.context))

    def write_zoo_cfg(self, dest_dir, context):
        group = self.base_jvm if self.user_jvm is None else self.user_jvm
        PropertiesCodec().write(
            path.join(dest_dir, consts.ZOO_CFG_FILE),
            group.resolve(self.context))
