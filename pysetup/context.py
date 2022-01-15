import re

class Context:
    """
    Represents a simple key/value store for configuration properties.

    A context is a stack of dictionaries, in which upper dictionaries
    override lower ones.

    The Context holds a set of values, typically strings. Values are not
    of the Value class because context values are not serialized.

    The Context provides for value lookup. More importantly, if provides
    for value subsitution: a value of "$foo" will be replace with the
    contents of the variable called "foo".

    Values are generally strings, but can also be other scalar types,
    such as numbers. Such values will be converted to strings when
    doing substitution.

    Syntax and semantic rules for replacment:

    * A variable runs from the "$" though the longest string of
      alpha-numeric characters, plus underscore. This "$foo_000/" contains
      a variable "foo_000".
    * The expression can include curley-brackets in the usual way:
      "${foo}_000/" replaces the variable "foo".
    * A string can have any number of variables:
      "$workDir/apache-druid-$version", say.
    * If the replacement variable itself has variables, then those
      variables are replaced first, and the resulting value replaced in
      the top string.
    * Variables can be defined anywhere in the stack, but replacement is
      always done with the top-most value. Thus, if level 0 defines
      "foo=$bar" and "bar=10", and the top level defines "bar=20", then
      requesting the value of "foo" will return 20.
    * It is possible to have indirection: "$$foo", which will first
      replace "$foo", then reparse the string, that if "foo=bar", the
      string becomes "$bar" and then that is replaced with the contents
      of "bar". This may not actually be usefull, but it works.

   Caveats
   -------
    * At present, there is no escape, but one should be added if this
      system is to be used to set the value of shell variables.
    * No error cheking is done for infinute recursion. A variable
      "foo=$foo" will loop forever.
    """

    def __init__(self):
        self.layers = []

    def add(self, layer):
        if layer is None or len(layer) == 0:
            return
        self.layers.append(layer)
    
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
        for layer in reversed(self.layers):
            try:
                return layer[key]
            except KeyError:
                pass
        return None
    
    def get(self, key):
        return self.replace(self.get_value(key))
    
    def require(self, key):
        value = self.get_value(key)
        if value is None:
            raise Exception("Variable " + key + " is not defined.")
        return value

    def keys(self):
        keys = set()
        for layer in self.layers:
            keys.update(layer.keys())
        return keys
        
