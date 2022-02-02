import re

from .util import sort_keys, format_value, format_pair, format_block
class Context:
    """
    Represents a simple key/value store for configuration properties.

    A context is created from a stack of dictionaries, in which upper
    dictionaries override lower ones. The actual overriding is done
    during the stack flattening proces.

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

    def __init__(self, mapping, system={}):
        self.system_props = system
        self.mapping = mapping

    def replace(self, orig):
        if orig is None:
            return ""
        if type(orig) != str:
            return str(orig)
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
            subs = '' if subs is None else str(subs)
            rewritten = head + subs + tail
        return rewritten

    def get_value(self, key):
        value = self.system_props.get(key)
        if value is not None:
            return value
        return self.mapping.get(key, None)
    
    def get(self, key):
        return self.replace(self.get_value(key))
    
    def require(self, key):
        value = self.system_props.get(key)
        if value is not None:
            return value
        try:
            return self.mapping[key]
        except KeyError:
            raise Exception("Variable '" + key + "' is not defined.") from None

    def keys(self):
        keys = set(self.system_props.keys()).copy()
        keys.update(self.mapping.keys())
        return keys

    def __str__(self):
        s = ''
        for k in sort_keys(self.keys()):
            raw = self.get_value(k)
            if type(raw) is not str:
                s += format_pair(k, raw, '') + '\n'
                continue
            final = self.get(k)
            s += format_pair(k, raw, '')
            if raw == final:
                s += '\n'
            elif '\n' in final:
                s += ' (' + format_block(final, '') + ')\n'
            else:
                s += ' (' + format_value(final, '') + ')\n'
        return s
