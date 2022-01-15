import re
from .codec import Value, tombstone
from . import consts

prop_pattern = '-D([^=]+)=(.*)'
jvm_prop_pattern = '-([^=]+)=(.*)'
arg_patterns = [
    '-(Xm.)(.*)',
    '-(.*)()'
]

arg_key = "Xm."

class SystemProperty(Value):

    def __init__(self, value):
        Value.__init__(self, value)

    def write(self, key, out):
        out.write("-D{}={}\n".format(key, self.value))

class JvmProperty(Value):

    def __init__(self, value):
        Value.__init__(self, value)

    def write(self, key, out):
        out.write("-{}={}\n".format(key, self.value))

class JvmArgument(Value):

    def __init__(self, value):
        Value.__init__(self, value)

    def write(self, key, out):
        if self.value is None or len(self.value) == 0:
            out.write("-{}\n".format(key))
        else:
            out.write("-{}{}\n".format(key, self.value))

class JvmCodec:

    def read(self, file_path):
        config = {
            consts.PROPERTIES_KEY: {},
            consts.JVM_ARGS_KEY: {}
        }
        with open(file_path) as f:
            for line in f:
                self.parse_arg(line, config)
        return config
    
    def parse_arg(self, line, config):
        line = line.strip()
        if len(line) == 0 or line.startswith('#'):
            return
        m = re.fullmatch(prop_pattern, line)
        if m is not None:
            config[consts.PROPERTIES_KEY][m.group(1)] = SystemProperty(m.group(2))
            return
        m = re.fullmatch(jvm_prop_pattern, line)
        args = config[consts.JVM_ARGS_KEY]
        if m is not None:
            args[m.group(1)] = JvmProperty(m.group(2))
            return
        for p in arg_patterns:
            m = re.fullmatch(p, line)
            if m is None:
                continue
            args[m.group(1)] = JvmArgument(m.group(2))
            return
        print("Did not match jvm.config line:", line)

    def write(self, config, file_path):
        with open(file_path, 'w') as f:
            self.write_set(f, config[consts.JVM_ARGS_KEY])
            self.write_set(f, config[consts.PROPERTIES_KEY])
    
    def write_set(self, out, config):
        for k, v in config.items():
            if v is not None:
                v.write(k, out)

    def encode(self, config):
        encoded = {}
        self.encode_args(encoded, config.get(consts.JVM_ARGS_KEY))
        self.encode_props(encoded, config.get(consts.PROPERTIES_KEY))
        return encoded
    
    def encode_args(self, encoded, config):
        if config is None:
            return
        for k, v in config.items():
            v = v.strip()
            if v == consts.NULL_VALUE:
                value = tombstone
            elif len(v) == 0:
                value = JvmArgument(v)
            elif re.fullMatch(arg_key, k) is not None:
                value = JvmArgument(v)
            else:
                value = SystemProperty(v)
            encoded[k] = value
    
    def encode_props(self, encoded, config):
        if config is None:
            return
        for k, v, in config.items():
            if v == consts.NULL_VALUE:
                encoded[k] = tombstone
            else:
                encoded[k] = SystemProperty(v)

jvmCodec = JvmCodec()