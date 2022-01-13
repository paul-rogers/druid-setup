import re
from . import consts

prop_pattern = '-D([^=]+)=(.*)'

jvm_patterns = [
    '-(Xm.)(.*)',
    '-([^=]+)=(.*)',
    '-(.*)()'
]

header = '''
Generated by pysetup -- do not edit

'''

non_std_opts = 'Xm.'

class JvmCodec:

    def read(self, file_path):
        config = {
            consts.SYSTEM_KEY: {},
            consts.JVM_KEY: {}
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
            config[consts.SYSTEM_KEY][m.group(1)] = m.group(2)
            return
        for p in jvm_patterns:
            m = re.fullmatch(p, line)
            if m is None:
                continue
            config[consts.JVM_KEY][m.group(1)] = m.group(2)
            return
        print("Did not match line:", line)

    def write(self, config, file_path):
        with open(file_path, 'w') as f:
            f.write(header)
            for k, v in config[consts.JVM_KEY].items():
                if v is None:
                    continue
                if v is None or len(v) == 0:
                    f.write("-{}\n".format(k))
                    continue
                if re.fullmatch(non_std_opts, k):
                    f.write("-{}{}\n".format(k, v))
                    continue
                f.write("-{}={}\n".format(k, v))
            for k, v in config['system'].items():
                f.write("-D{}={}\n".format(k, v))
