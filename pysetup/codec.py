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
            for line in config['contents']:
                f.write(line)
                f.write('\n')

mainCodec = MainCodec()
fileCodec = FileCodec()