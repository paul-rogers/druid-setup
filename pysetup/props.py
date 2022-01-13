import re
from . import consts

comment = '([^"#]*)(?:#|//)(.*)'

class PropsParser:

    def __init__(self):
        self.props = {
            consts.COMMENTS_KEY: {},
            consts.PROPERTIES_KEY: {}
        }
        self.comment = []

    def parse(self, file_path):
        with open(file_path) as f:
            for line in f:
                self.parse_line(line)
        return self.props

    def parse_line(self, line):
        line = line.strip()
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
        self.props[consts.PROPERTIES_KEY][key] = line[posn+1:]
        if len(self.comment) > 0:
            self.props[consts.COMMENTS_KEY][key] = self.comment
            self.comment = []

class PropertiesCodec:

    def read(self, file_path) -> dict:
        return PropsParser().parse(file_path)

    def write(self, config, file_path):
        with open(file_path, 'w') as f:
            for k, v in config[consts.PROPERTIES_KEY].items():
                try:
                    f.write('\n')
                    comments = config[consts.COMMENTS_KEY][k]
                    for line in comments:
                        f.write("# {}\n".format(line))
                except KeyError:
                    pass
                if v is None:
                    continue
                f.write("{}={}\n".format(k, v))
