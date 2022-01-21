import re
from . import consts

prop_pattern = '-D([^=]+)=(.*)'
jvm_prop_pattern = '-([^=]+)=(.*)'
arg_patterns = [
    '-(Xm.)(.*)',
    '-(.*)()'
]

arg_key = "Xm."

arg_keys = {'Xms', 'Xmx'}

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
            config[consts.PROPERTIES_KEY][m.group(1)] = m.group(2)
            return
        m = re.fullmatch(jvm_prop_pattern, line)
        args = config[consts.JVM_ARGS_KEY]
        if m is not None:
            args[m.group(1)] = m.group(2)
            return
        for p in arg_patterns:
            m = re.fullmatch(p, line)
            if m is None:
                continue
            args[m.group(1)] = m.group(2)
            return
        print("Did not match jvm.config line:", line)

    def write(self, config, file_path):
        with open(file_path, 'w') as f:
            self.write_jvm_args(f, config)
            self.write_system_props(f, config)
    
    def write_jvm_args(self, out, config):
        args = config.get(consts.JVM_ARGS_KEY)
        if args is None:
            return
        for k, v in args.items():
            if v is None or len(v) == 0:
                out.write("-{}\n".format(k))
            elif k in arg_keys:
                out.write("-{}{}\n".format(k, v))
            else:
                out.write("-{}={}\n".format(k, v))

    def write_system_props(self, out, config):
        props = config.get(consts.PROPERTIES_KEY)
        if props is None:
            return
        for k, v in props.items():
            out.write("-D{}={}\n".format(k, v))

jvmCodec = JvmCodec()