import shutil
import os
from os import path
from . import consts

class ConfigBuilder:

    def __init__(self, model):
        self.model = model
        self.target = model.target
        self.context = model.context

    def build(self):
        self.remove_old()
        self.create_new()
        self.build_readme()
        self.build_zk()
        self.build_services()
    
    def remove_old(self):
        if not path.isdir(self.target):
            if path.exists(self.target):
                raise Exception("Target exists and is not a directory: " + self.target)
            return
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
            f.write(disclaimer)
            f.write('\n')

    def build_readme(self):
        label = self.context.get(consts.README_KEY)
        if label is None:
            return
        with open(path.join(self.target, consts.README_FILE), 'w') as f:
            f.write(label.strip())
            f.write('\n')

    def build_zk(self):
        try:
            zk = self.model.services[consts.ZK_SERVICE]
        except KeyError:
            return
        zk_dir = path.join(self.target, consts.ZK_SERVICE)
        zk.build(zk_dir, self.context)

    def build_services(self):
        pass
