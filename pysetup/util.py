from .consts import TOMBSTONE

def sort_keys(s):
    keys = [k for k in s]
    keys.sort()
    return keys

def format_dict(value, prefix):
    s = '{\n'
    deeper = prefix + '  '
    for k in sort_keys(value.keys()):
        s += format_pair(k, value[k], deeper) + '\n'
    return s + prefix + '}'
   
def format_pair(key, value, prefix):
    return prefix + key + ': ' + format_value(value, prefix)

def format_value(value, prefix):
    if value is None or value is TOMBSTONE:
        return '<unset>'
    if type(value) is dict:
        return format_dict(value, prefix )
    if type(value) is list:
        return format_list(value, prefix)
    if type(value) is not str:
        return str(value)
    if '\n' in value:
        return format_block(value, prefix)
    if value != value.strip():
        return '"' + value + '"'
    return value

def format_block(value, prefix):
    lines = value.strip().split('\n')
    return format_list(lines, prefix)

def format_list(value, prefix):
    s = '"""\n'
    for line in value:
        s += '{}  | {}\n'.format(prefix, line)
    return s + prefix + '  """'
