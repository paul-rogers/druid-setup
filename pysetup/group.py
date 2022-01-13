import re
from . import consts

class ConfigGroup:

    def __init__(self, config):
        self.config = config
        self.parent = None
        self._merged = None
        self._resolved = None

    def merged(self) -> dict:
        if self._merged is None:
            if self.parent is None:
                self._merged = self.config
            else:
                self._merged = self.merge(self.parent.merged())
        return self._merged

    def resolve(self, context):
        self._resolved = self.expand(self.merged(), context)

    def merge(self, parent):
        return merge_recursive(parent, self.config)

    def expand(self, config, context):
        return resolve_recursive(config, context)

    def resolved(self):
        return self._resolved

class JvmGroup(ConfigGroup):

    def __init__(self, config):
        ConfigGroup.__init__(self, config)

    def expand(self, config, context) :
        return resolve_recursive(self._merged, context)

class PropertiesGroup(ConfigGroup):

    def __init__(self, config):
        ConfigGroup.__init__(self, config)

    def expand(self, config, context):
        props = config[consts.PROPERTIES_KEY]
        return {
            consts.COMMENTS_KEY: config[consts.COMMENTS_KEY],
            consts.PROPERTIES_KEY: resolve_recursive(props, context)
        }
 
def merge_recursive(base, config) -> dict:
    merged = base.copy()
    for k, v in config.items():
        if v is None:
            del merged[k]
        elif type(v) == dict:
            try:
                merged[k] = merge_recursive(merged[k], v)
            except:
                merged[k] = v
        else:
            merged[k] = v
    return merged

def resolve_recursive(config, context):
    resolved = {}
    for k, v in config.items():
        if v is None:
            continue
        if type(v) == dict:
            resolved[k] = resolve_recursive(v, context)
        else:
            resolved[k] = context.replace(v)
    return resolved    
