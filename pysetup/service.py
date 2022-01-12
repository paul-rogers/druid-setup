from os import path
from .jvm import JvmCodec
from .group import ConfigGroup, PropertiesGroup, JvmGroup
from .codec import MainCodec, FileCodec
from .props import PropertiesCodec

class Service:

    def __init__(self, name):
        self.name = name

    def load_base(self, conf_dir):
        raise NotImplementedError

class DruidService(Service):

    def __init__(self, name):
        Service.__init__(self, name)

    def load_base(self, service_dir):
        self.jvm = JvmGroup(JvmCodec().read(path.join(service_dir, 'jvm.config')))
        self.properties = PropertiesGroup(PropertiesCodec().read(path.join(service_dir, 'runtime.properties')))
        self.main = ConfigGroup(MainCodec().read(path.join(service_dir, 'main.config')))

class CommonService(Service):

    def __init__(self):
        Service.__init__(self, "_common")

    def load_base(self, service_dir):
        self.properties = PropertiesGroup(PropertiesCodec().read(path.join(service_dir, 'common.runtime.properties')))
        self.log4j = ConfigGroup(FileCodec().read(path.join(service_dir, 'log4j2.xml')))

class ZkService(Service):

    def __init__(self):
        Service.__init__(self, "zk")

    def load_base(self, conf_dir):
        pass