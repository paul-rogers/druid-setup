import re

class ConfigKind:

    def __init__(self):
        pass

class ConfigGroup:

    def __init__(self, config):
        self.parents = []
        self.config = config
        self._merged = None

    def resolve(self, context) -> dict:
        merged = self.merge()
        return self._expand(merged, context)

    def merge(self) -> dict:
        if self._merged is None:
            self._merged = self._merge()
        return self._merged

    def _merge(self):
        return self._merge_parents()

    def _merge_parents(self) -> dict:
        resolved = {}
        for p in self.parents:
            merge_recursive(resolved, p._merge())
        merge_recursive(resolved, self.config)
        return resolved

    def _expand(self, resolved, context):
        return resolve_vars(resolved, context)

class JvmGroup(ConfigGroup):

    def __init__(self, config):
        ConfigGroup.__init__(self, config)

    def _expand(self, resolved, context) -> dict:
        resolve_vars(resolved['jvm'], context)
        resolve_vars(resolved['system'], context)
        return resolved

class PropertiesGroup(ConfigGroup):

    def __init__(self, config):
        ConfigGroup.__init__(self, config)

    def _expand(self, resolved, context) -> dict:
        resolved = self._merge_parents()
        resolve_vars(resolved['properties'], context)

def merge_recursive(dest, srce):
    for k, v in srce.items():
        if v is None:
            del dest[k]
        elif type(v) == dict:
            if len(v) > 0:
                try:
                    v_map = dest[k]
                    if v_map is None:
                        dest[k] = v
                    elif type(v_map) != dict:
                        print("Expected map for key " + k)
                    else:
                        merge_recursive(v_map, v)
                except KeyError:
                    dest[k] = v
        else:
            dest[k] = v

def resolve_vars(config, context):
    resolved = {}
    for k, v in config.items():
        resolved[k] = context.replace(v, config)
    return resolved
