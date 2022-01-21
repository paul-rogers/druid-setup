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

class MainCodec:

    def read(self, file_path):
        with open(file_path) as f:
            line = f.readline().strip()
            posn = line.find(' ')
            if posn == -1:
                main = line
                args = ''
            else:
                main = line[0:posn]
                args = line[posn+1:]
            return {'class': main, 'args': args}

    def write(self, file_path, config):
        with open(file_path, 'w') as f:
            f.write(config['class'])
            args = config.get('args', None)
            if args is not None and len(args) > 0:
                f.write(' ')
                f.write(args)
            f.write('\n')

class FileCodec:

    def read(self, file_path):
        with open(file_path) as f:
            lines = f.readlines()
            lines = [line.rstrip() for line in lines]
            return {'contents': lines}

    def write(self, file_path, config):
        with open(file_path, 'w') as f:
            f.write(config['contents'])

mainCodec = MainCodec()
fileCodec = FileCodec()