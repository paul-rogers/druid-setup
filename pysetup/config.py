from .context import Context
from .util import sort_keys, format_pair
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
        return Context(sys_context, self.merge())

class FinalConfig:

    def __init__(self, config):
        self.config = config

    def get(self, key):
        if type(key) == str:
            key = split_key(key)
        value, found = search(self.config, key)
        return value if found else None

    def get_value(self, key, context):
        value = self.get(key)
        return context.replace(value)

    def get_config(self, key):
        value = self.get(key)
        if value is None:
            return value
        if type(value) is not dict:
            raise Exception("Value of key is not a dict: " + key)
        return FinalConfig(value)

    def __str__(self):
        s = ''
        for k in sort_keys(self.config):
            s += format_pair(k, self.config[k], '') + '\n'
        return s
        
def split_key(key):
    return key.split('.')
   
def search(config, key):
    if len(key) == 0:
        return config
    value = config.get(key[0])
    if value is None:
        return (None, False)
    elif value is TOMBSTONE:
        return (None, True)
    elif type(value) is dict:
        return search(value, key[1:])
    elif len(key) == 1:
        return (value, True)
    else:
        return (None, False)

def merge(merged, overlay):
    for k, v in overlay.items():
        if v is TOMBSTONE:
            merged.pop(k, None)
            continue
        existing = merged.get(k, None)
        if existing is None:
            if type(existing) is dict:
                merged[k] = existing.copy()
            else:
                merged[k] = v            
        else:
            if type(existing) == dict:
                merge(existing, v)
            else:
                merged[k] = v

def resolve(value, context):
    if value is None:
        return None
    if type(value) is str:
        return context.replace(value)
    if type(value) is not dict:
        return value
    resolved = {}
    for k, v in value.items():
        resolved[k] = resolve(v, context)
    return resolved
