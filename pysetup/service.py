from os import path
import os, shutil
from .jvm import jvmCodec
from .codec import mainCodec, fileCodec
from .props import propertiesCodec
from . import consts

class ResourceDefn:

    def __init__(self, key, codec, file_name):
        self.key = key
        self.codec = codec
        self.file_name = file_name

class ServiceDefn:

    def __init__(self, resources):
        self.config = {}
        for resource in resources:
            self.config[resource.key] = resource
    
    def has_key(self, key):
        self.config.get(key) is not None
    
    def codec_for(self, key):
        try:
            return self.config[key].codec
        except KeyError:
            return None

    def resources(self):
        return self.config.values()
    
    def keys(self):
        return self.config.keys()
    
    def build_data_dir(self, context):
        pass

class ZkServiceDefn(ServiceDefn):

    def __init__(self):
        ServiceDefn.__init__(self,
            [jvmResource, zkResource, log4jResource])
    
    def build_data_dir(self, context):
        zk_data_dir = context.get(consts.ZK_DATA_DIR_KEY)
        os.makedirs(zk_data_dir)

jvmResource = ResourceDefn(
    consts.JVM_KEY,
    jvmCodec,
    consts.JVM_CONFIG_FILE)

runtimeResource = ResourceDefn(
    consts.PROPERTIES_KEY,
    propertiesCodec,
    consts.RUNTIME_PROPERTIES_FILE)

commonResource = ResourceDefn(
    consts.PROPERTIES_KEY,
    propertiesCodec,
    consts.COMMON_PROPERTIES_FILE)

mainResource = ResourceDefn(
    consts.MAIN_KEY,
    mainCodec,
    consts.MAIN_CONFIG_FILE)

log4jResource = ResourceDefn(
    consts.LOG4J_KEY,
    fileCodec,
    consts.LOG4J_FILE)

zkResource = ResourceDefn(
    consts.PROPERTIES_KEY,
    propertiesCodec,
    consts.ZOO_CFG_FILE)

druidService = ServiceDefn([
    jvmResource,
    runtimeResource,
    mainResource])

services = {
    consts.HISTORICAL_SERVICE: druidService,
    consts.BROKER_SERVICE: druidService,
    consts.ROUTER_SERVICE: druidService,
    consts.OVERLORD_SERVICE: druidService,
    consts.MASTER_SERVICE: druidService,
    consts.INDEXER_SERVICE: druidService,
    consts.PEON_SERVICE: druidService,
    consts.MIDDLE_MANAGER_SERVICE: druidService,
    consts.COMMON_SERVICE: ServiceDefn([
        jvmResource,
        commonResource,
        log4jResource]),
    consts.ZK_SERVICE: ServiceDefn([
        jvmResource,
        zkResource,
        log4jResource])
    }

class Service:

    def __init__(self, name):
        self.name = name
        self.defn = services[name]
        self.base_config = {}

    def load_base(self, conf_dir):
        for resource in self.defn.resources():
            self.load_resource(conf_dir, resource)
    
    def load_resource(self, conf_dir, resource):
        file_path = path.join(conf_dir, resource.file_name)
        if not path.isfile(file_path):
            return
        self.base_config[resource.key] = resource.codec.read(file_path)

    def build_config(self, dest_dir, final_config):
        os.makedirs(dest_dir)
        for resource in self.defn.resources():
            config = final_config.get(resource.key)
            if config is None:
                continue
            resource.codec.write(config.resolved(),
                path.join(dest_dir, resource.file_name))
    
    def build_data(self, context):
        self.defn.build_data_dir(context)
