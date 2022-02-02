from os import path
from . import consts

class ConfigFinder:

    def __init__(self, context):
        self.context = context
    
    def find(self):
        self.druid_home = self.context.get(consts.DRUID_HOME_KEY)
        base_config = self.context.get(consts.BASE_CONFIG_KEY)
        if base_config is None or len(base_config) == 0:
            print("Warning: no base config set.")
            return False
        self.verify_druid()
        self.find_base_dir(base_config)
        return True

    def verify_druid(self):
        if self.druid_home is None:
            raise Exception("'" + consts.DRUID_HOME_KEY + "' is not set.")
        if not path.isdir(self.druid_home):
            raise Exception("Druid home does not exist: " + self.druid_home)
        if path.basename(self.druid_home).find('-iap-') != -1:
            self.distro = consts.IMPLY_DISTRO
            return
        if path.isfile(path.join(self.druid_home, 'build.name')):
            self.distro = consts.IMPLY_DISTRO
            return
        if path.isfile(path.join(self.druid_home, 'README')):
            self.distro = consts.APACHE_DISTRO
            return
        raise Exception("Druid home is not a Druid distro?: " + self.druid_home)

    def find_base_dir(self, base_config):
        if base_config is None:
            return
        if self.find_simple_base(self.druid_home, base_config):
            return
        conf_dir = path.join(self.druid_home, consts.CONF_DIR)
        if self.find_simple_base(conf_dir, base_config):
            return
        if self.find_nested_base(conf_dir, 'single-server', base_config):
            return
        if self.find_nested_base(conf_dir, 'cluster', base_config):
            return
        raise Exception(
            "Cannot find config {} in Druid distribution {}".format(
                self.base_config, self.druid_home))

    def find_simple_base(self, base, base_config):
        guess = path.join(base, base_config)
        if not path.isdir(guess):
            return False
        self.zk_dir = path.join(guess, consts.ZK_SERVICE)
        self.service_dir = path.join(guess, consts.DRUID_DIR)
        return path.isDir(self.service_dir)

    def find_nested_base(self, base, group, base_config):
        guess = path.join(base, consts.DRUID_DIR, group, base_config)
        if not path.isdir(guess):
            return False
        self.zk_dir = path.join(base, consts.ZK_SERVICE)
        self.service_dir = guess
        return True
