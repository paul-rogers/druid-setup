import re
from . import consts

class GroupStack:

    def __init__(self, base):
        self.stack = [base]
        self.expanded = None

    def resolve(self, context):
        for i in range(self.length):
            self.merge_group(i)
        self.top().expand(context)

    def top(self):
        return self.stack[-1]

    def merge_group(self, index):
        group = self.stack[index]
        if group._merged is not None:
            return
        if index == 0:
            group._merged = group.config
            return
        group.merge(self.stack[index + 1])

    def get(self, key, context):
        return context.get(key, self.top()._resolved)

class ConfigGroup:

    def __init__(self, config):
        self.config = config
        self._merged = None
        self._expanded = None

    def merge(self, parent):
        self._merged = parent.copy()
        merge_recursive(self._merged, self.config)

    def expand(self, context):
        self._expanded = resolve_recursive(self._merged, self._merged, context)

class JvmGroup(ConfigGroup):

    def __init__(self, config):
        ConfigGroup.__init__(self, config)

    def expand(self, context) :
        self._expanded = resolve_recursive(self._merged, None, context)

class PropertiesGroup(ConfigGroup):

    def __init__(self, config):
        ConfigGroup.__init__(self, config)

    def expand(self, context):
        props = self._merged[consts.PROPERTIES_KEY]
        self._expanded = {
            consts.COMMENTS_KEY: self._merged[consts.COMMENTS_KEY],
            consts.PROPERTIES_KEY: resolve_recursive(props, context, props)
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

def resolve_recursive(config, context, local):
    resolved = {}
    for k, v in config.items():
        if v is None:
            continue
        if type(v) == dict:
            resolved[k] = resolve_recursive(v, context, local)
        else:
            resolved[k] = context.replace(v, local)
    return resolved    
