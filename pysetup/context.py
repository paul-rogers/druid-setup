import re

class Context:

    def __init__(self, root, user):
        self.root_context = root
        self.user_context = user
    
    def replace(self, orig, local_context={}):
        if orig is None:
            return orig
        if type(orig) != str:
            return orig
        rewritten = orig
        while True:
            m = re.search(r'\$\{([^\}]+)\}', rewritten)
            if m is None:
                m = re.search(r'\$(\w+)', rewritten)
            if m is None:
                break
            head = rewritten[0:m.start(0)]
            tail = rewritten[m.end(0):]
            var = m.group(1)
            subs = self.require(var)
            rewritten = head + str(subs) + tail
        return rewritten

    def get_value(self, key):
        try:
            return self.user_context[key]
        except KeyError:
            pass
        try:
            return self.root_context[key]
        except KeyError:
            return None
    
    def get(self, key):
        return self.replace(self.get_value(key))
    
    def require(self, key):
        value = self.get_value(key)
        if value is None:
            raise Exception("Variable " + key + " is not defined.")
        return value
        
