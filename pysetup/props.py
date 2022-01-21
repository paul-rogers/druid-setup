import re, json
from . import consts

comment = '([^"#]*)(?:#|//)(.*)'

class ConfigValue:

    def __init__(self, value, comments=None):
        self.value = value
        self.comments = comments

    def write(self, key, out):
        if self.comments is not None and len(self.comments) > 0:
            for line in self.comments:
                out.write("# {}\n".format(line))
        if self.value is not None:
            write_value(key, self.value, out)

    def __str__(self):
        return str(self.value)

class JsonPropertyCodec:

    def parse(self, value):
        return json.loads(value)

    def format(self, value):
        return json.dumps(value)

json_property_codec = JsonPropertyCodec()

special_props = {
    'druid.extensions.loadList': json_property_codec,
    'druid.monitoring.monitors': json_property_codec,
    'druid.server.hiddenProperties': json_property_codec,
    'druid.segmentCache.locations': json_property_codec,
}

def parse_value(key, value):
    fmt = special_props.get(key, None)
    if fmt is None:
        return value
    return fmt.parse(value)

def format_value(key, value):
    fmt = special_props.get(key, None)
    if fmt is None:
        return value
    return fmt.format(value)

def write_value(key, value, out):
    out.write("{}={}\n".format(key, format_value(key, value)))

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
        value = line[posn+1:]
        fmt = special_props.get(key, None)
        if fmt is not None:
            value = fmt.parse(value)
        if len(self.comment) == 0:
            self.props[key] = value
        else:
            self.props[key] = ConfigValue(value, self.comment)
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
                    write_value(k, v, f)

propertiesCodec = PropertiesCodec()