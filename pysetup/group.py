from .codec import tombstone, Value

class ConfigGroup(Value):

    def __init__(self, config):
        Value.__init__(self, None)
        self.config = {} if config is None else config
        self.parent = None
        self._merged = None
        self._resolved = None

    def merged(self) -> dict:
        if self._merged is None:
            if self.parent is None:
                self._merged = self.config
            else:
                self._merged = self.merge_dict(self.parent.merged(), self.config)
        return self._merged
    
    def merge_dict(self, base, overlay):
        merged = base.copy()
        for k, v in overlay.items():
            if v is tombstone or v is None:
                merged.pop(k, None)
                continue
            existing = merged.get(k, None)
            if existing is None:
                merged[k] = v            
            elif type(existing) == dict:
                merged[k] = self.merge_dict(existing, v)
            else:
                merged[k] = v.merge(merged[k])
        return merged

    def resolve(self, context):
        self._resolved = self.resolve_dict(self.merged(), context)
        return self
    
    def resolve_dict(self, values, context):
        resolved = {}
        for k, v in values.items():
            if v is None:
                continue
            if type(v) == dict:
                resolved[k] = self.resolve_dict(v, context)
            else:
                resolved[k] = v.resolve(context)
        return resolved

    def resolved(self):
        if self._resolved is None:
            raise Exception("Config group not resolved")
        return self._resolved

    def write(self, _, out):
        raise NotImplementedError()

    def prune(self):
        needs_prune = False
        for k, v in self.config.items():
            if type(v) != ConfigGroup:
                return
            if v.is_empty():
                needs_prune = True
                break
        if not needs_prune:
            return
        revised = {}
        for k, v in self.config.items():
            if not v.is_empty():
                revised[k] = v
        self.config = revised

    def is_empty(self):
        return len(self.config) == 0

    def get(self, key):
        return self._resolved.get(key, None)

class ConfigStack:

    def __init__(self):
        self.groups = []
        self._resolved = None

    def add(self, group):
        if group is None or group.is_empty():
            return
        if len(self.groups) > 0:
            top = self.groups[-1]
            if group.parent is None:
                group.parent = top
            elif group.parent is not top:
                raise Exception("Parents conflict")
        self.groups.append(group)

    def resolve(self, context):
        if len(self.groups) == 0:
            self._resolved = ConfigGroup({})
            self._resolved.resolve(context)
            return
        self._resolved = self.groups[-1]
        self._resolved.resolve(context)

    def resolved(self):
        if self._resolved is None:
            raise Exception("ConfigStack not resolved yet")
        return self._resolved
 
    def get(self, key):
        return self.resolved().get(key)
