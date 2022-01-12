class Codec:

    def read(self, file_path):
        raise NotImplementedError

    def write(self, file_path, config):
        raise NotImplementedError

class MainCodec:

    def read(self, file_path):
        with open(file_path) as f:
            line = f.readline()
            return {'main': line}

    def write(self, file_path, config):
        with open(file_path, 'w') as f:
            f.write(config['main'])
            f.write('\n')

class FileCodec:

    def read(self, file_path):
        with open(file_path) as f:
            lines = f.readlines()
            return {'contents': lines}

    def write(self, file_path, config):
        with open(file_path, 'w') as f:
            f.write(config['contents'])
            