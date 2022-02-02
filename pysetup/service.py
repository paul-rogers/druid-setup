import os
from os import path
from .jvm import jvmCodec
from .codec import mainCodec, fileCodec
from .props import propertiesCodec
from . import consts
from .util import merge

class ResourceDefn:

    def __init__(self, key, codec, file_name):
        self.key = key
        self.codec = codec
        self.file_name = file_name

class ServiceDefn:

    def __init__(self, dir_path, resources):
        self.dir_path = dir_path
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
    
    def load_base(self, conf_dir):
        config = {}
        for resource in self.resources():
            file_path = path.join(conf_dir, resource.file_name)
            if not path.isfile(file_path):
                continue
            config[resource.key] = resource.codec.read(file_path)
        return config

    def build_config(self, dest_dir, final_config):
        os.makedirs(dest_dir)
        for resource in self.resources():
            config = final_config.get(resource.key, None)
            if config is None:
                continue
            resource.codec.write(
                path.join(dest_dir, resource.file_name),
                config)
    
    def build_data(self, context):
        pass
 
class ZkServiceDefn(ServiceDefn):

    def __init__(self):
        ServiceDefn.__init__(self,
            '$' + consts.ZK_CONFIG_DIR_KEY,
            [jvmResource, zkResource, log4jResource])
    
    def build_data(self, context):
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

resources = {
    'jvm': jvmResource,
    'properties': runtimeResource,
    'log4j': log4jResource,
    'main': mainResource
}

def druidService(name):
    return ServiceDefn(
        '$' + consts.DRUID_CONFIG_DIR_KEY + '/' + name,
        [jvmResource, runtimeResource, mainResource])

services = {
    consts.HISTORICAL_SERVICE: druidService(consts.HISTORICAL_SERVICE),
    consts.BROKER_SERVICE: druidService(consts.BROKER_SERVICE),
    consts.ROUTER_SERVICE: druidService(consts.ROUTER_SERVICE),
    consts.OVERLORD_SERVICE: druidService(consts.OVERLORD_SERVICE),
    consts.MASTER_SERVICE: druidService(consts.MASTER_SERVICE),
    consts.INDEXER_SERVICE: druidService(consts.INDEXER_SERVICE),
    consts.PEON_SERVICE: druidService(consts.PEON_SERVICE),
    consts.MIDDLE_MANAGER_SERVICE: druidService(consts.MIDDLE_MANAGER_SERVICE),
    consts.COMMON_SERVICE: ServiceDefn(
        '$druidConfDir/' + consts.COMMON_DIR,
        [jvmResource, commonResource, log4jResource]),
    consts.ZK_SERVICE: ZkServiceDefn()
    }

class Services:

    def __init__(self, context):
        self.services = services.copy()
        self.context = context
        self.config = {}
        self.extns = {}

    def build_custom_service(self, key, config):
        if self.services.get(key, None) != None:
            raise Exception("Custom service {} is already defined".format(key))
        self.extns[key] = config
        custom_resources = []
        for k in config.keys():
            resource = resources.get(k, None)
            if resource is None:
                raise Exception(
                    "Custom service {} refers to a non-existent resource {}".format(
                        key, k))
            custom_resources.append(resource)
        if len(custom_resources) == 0:
            raise Exception("Custom service {} has no resources defined".format(key))
        self.services[key] = ServiceDefn('$' + consts.DRUID_CONFIG_DIR_KEY + '/' + key, custom_resources)

    def load(self, zk_dir, service_dir):
        self.load_zk(zk_dir)
        self.load_druid_services(service_dir)
        self.expand_extn_services()
        return self.config

    def load_zk(self, zk_dir):
        """
        ZK is not within the named config directory: it is in
        ${druidHome}/conf/zk
        """
        if not path.isdir(zk_dir):
            raise Exception("No ZK found: " + zk_dir)
        service = self.services[consts.ZK_SERVICE]
        config = service.load_base(zk_dir)
        if len(config) == 0:
            print("Warning: ZK config dir is empty:", zk_dir)
            return
        self.config[consts.ZK_SERVICE] = config
    
    def load_druid_services(self, service_dir):
       for f in os.listdir(service_dir):
            full_path = path.join(service_dir, f)
            if f == consts.USER_CLASSPATH_DIR:
                # TODO
                continue
            if f == consts.COMMON_DIR:
                key = consts.COMMON_SERVICE
                service = self.services[key]
            else:
                service = self.services.get(f, None)
                if service is None:
                    continue
                key = f
                if key in self.extns:
                    print(
                        "Warning: service {} is defined as an extension, but exists in {} - base ignored"
                        .format(key, service_dir))
            config = service.load_base(full_path)
            if len(config) == 0:
                continue
            self.config[key] = config

    def expand_extn_services(self):
        for extn_key, extn in self.extns.items():
            self.expand_extn_service(extn_key, extn)
    
    def expand_extn_service(self, extn_key, extn):
        extn_config = {}
        self.config[extn_key] = extn_config
        for config_key, config in extn.items():
            base = config.get(consts.COPY_KEY, None)
            if base is not None:
                base_service = self.config.get(base, None)
                if base_service is None:
                    raise Exception(
                        "Custom service {} refers to non-existent base {}".format(
                        extn_key, base))
                base_config = base_service.get(config_key, None)
                if base_config is None:
                    raise Exception(
                        "Custom service {} copies {} from {}, but {} does not exist".format(
                        extn_key, config_key, base, config_key))
                custom_config = base_config.copy()
            else:
                custom_config = {}
            defn_config = config.get(consts.CONFIG_KEY, None)
            if defn_config is not None:
                merge(custom_config, defn_config)
            extn_config[config_key] = custom_config        

    def build(self, services, final_config):
        for key in services:
            try:
                defn = self.services[key]
            except KeyError:
                raise Exception("Unknown service {}".format(key)) from None
            config = final_config.get(key, None)
            if config is None:
                continue
            config_dir = self.context.replace(defn.dir_path)
            defn.build_config(config_dir, config)
