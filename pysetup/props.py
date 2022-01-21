import re
from .codec import tombstone, Value
from . import consts

comment = '([^"#]*)(?:#|//)(.*)'

class ConfigValue(Value):

    def __init__(self, value, comments=None):
        Value.__init__(self, value)
        self.comments = comments

    def write(self, key, out):
        if self.comments is not None and len(self.comments) > 0:
            for line in self.comments:
                out.write("# {}\n".format(line))
        if self.value is not None:
            out.write("{}={}\n".format(key, self.value))

class PropsParser:

    def __init__(self):
        self.props = {}
        self.comment = []

    def parse(self, file_path):
        with open(file_path) as f:
            for line in f:
                self.parse_line(line)
        return self.props

    def parse_line(self, line):
        line = line.strip()
        if len(line) == 0:
            self.comment.append(line)
            return
        m = re.fullmatch(comment, line)
        if m is not None:
            line = m.group(1).strip()
            tail = m.group(2).strip()
            if len(tail) > 0:
                self.comment.append(tail)

        if len(line) == 0:
            return
        posn = line.find('=')
        if posn == -1:
            print("Bad properties line: " + line)
            return
        key = line[0:posn]
        self.props[key] = ConfigValue(line[posn+1:], self.comment)
        self.comment = []

class PropertiesCodec:

    def read(self, file_path) -> dict:
        return PropsParser().parse(file_path)

    def write(self, config, file_path):
        with open(file_path, 'w') as f:
            for k, v in config.items():
                if type(v) == ConfigValue:
                    v.write(k, f)
                else:
                    f.write("{}={}\n".format(k, v))

    def encode(self, config):
        encoded = {}
        for k, v in config.items():
            if v == consts.NULL_VALUE:
                encoded[k] = tombstone
            else:
                encoded[k] = ConfigValue(v)
        return encoded

propertiesCodec = PropertiesCodec()