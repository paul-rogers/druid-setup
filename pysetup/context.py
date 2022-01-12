import re

class Context:

    def __init__(self, root, user):
        self.root_context = root
        self.user_context = user
    
    def replace(self, orig, local_context={}):
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
            subs = None
            try:
                subs = local_context[var]
            except KeyError:
                try:
                    subs = self.user_context[var]
                except KeyError:
                    try:
                        subs = self.root_context[var]
                    except KeyError:
                        raise Exception("Cannot find value for variable {} in '{}'".format(var, orig))
            rewritten = head + str(subs) + tail
        return rewritten
