import shutil

class ConfigBuilder:

    def __init__(self, model):
        self.model = model
        self.target = model.target

    def build(self):
        self.remove_old()
        self.build_label()
        self.build_zk()
        self.build_services()
    
    def remove_old(self):
        pass

    def build_label(self):
        pass

    def build_zk(self):
        pass

    def build_services(self):
        pass
