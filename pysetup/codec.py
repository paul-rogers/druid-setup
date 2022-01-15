class Value:

    def __init__(self, value):
        self.value = value

    def merge(self, parent):
        return self

    def resolve(self, context):
        if self.value is None:
            return self
        resolved = context.replace(self.value)
        if resolved == self.value:
            return self
        return type(self)(resolved)

    def __str__(self):
        return str(self.value)

class Tombstone(Value):

    def __init__(self):
        Value.__init__(self, None)

tombstone = Tombstone()

class Codec:

    def read(self, file_path):
        raise NotImplementedError()

    def write(self, file_path, config):
        raise NotImplementedError()
    
    def encode(self, config):
        raise NotImplementedError()

class MainCodec:

    def read(self, file_path):
        with open(file_path) as f:
            line = f.readline()
            return {'main': Value(line)}

    def write(self, file_path, config):
        with open(file_path, 'w') as f:
            f.write(config['main'].value)
            f.write('\n')

    def encode(self, config):
        encoded = {}
        v = config.get('main')
        if v is not None:
            encoded['main'] = Value(v)
        return encoded

class FileCodec:

    def read(self, file_path):
        with open(file_path) as f:
            lines = f.readlines()
            return {'contents': Value(lines)}

    def write(self, file_path, config):
        with open(file_path, 'w') as f:
            f.write(config['contents'].value)

    def encode(self, config):
        encoded = {}
        v = config.get('contents')
        if v is not None:
            encoded['contents'] = Value(v)
        return encoded

mainCodec = MainCodec()
fileCodec = FileCodec()