from .context import Context
from .util import sort_keys, format_pair, search, resolve, merge
from .consts import TOMBSTONE


class ConfigStack:

    def __init__(self):
        self.stack = []

    def add(self, config):
        if config is None or len(config) == 0:
            return
        self.stack.append(config)

    def get(self, key):
        if type(key) == str:
            key = split_key(key)
        for layer in self.stack:
            value, found = search(layer, key)
            if found:
                return value
        return None

    def merge(self):
        merged = {}
        for layer in self.stack:
            merge(merged, layer)
        return merged

    def resolve(self, context):
        merged = self.merge()
        resolved = resolve(merged, context)
        return FinalConfig(resolved)

    def to_context(self, sys_context):
        return Context(self.merge(), sys_context)

class FinalConfig:

    def __init__(self, config):
        self.config = config

    def get_value(self, key):
        if type(key) == str:
            key = split_key(key)
        value, found = search(self.config, key)
        return value if found else None

    def get(self, key):
        if type(key) == str:
            key = key.split('.')
        value, found = search(self.config, key)
        if not found:
            raise Exception("Variable '" + '.'.join(key) + "' is not defined.")
        return value

    def __str__(self):
        s = ''
        for k in sort_keys(self.config):
            s += format_pair(k, self.config[k], '') + '\n'
        return s
        
def split_key(key):
    return key.split('.')
   
