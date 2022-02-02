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

def search(config, key):
    if len(key) == 0:
        return (config, True)
    value = config.get(key[0])
    if value is None:
        return (None, False)
    elif value is TOMBSTONE:
        return (None, True)
    elif type(value) is dict:
        return search(value, key[1:])
    elif len(key) == 1:
        return (value, True)
    else:
        return (None, False)

def merge(merged, overlay):
    for k, v in overlay.items():
        if v is TOMBSTONE:
            merged.pop(k, None)
            continue
        existing = merged.get(k, None)
        if existing is None:
            if type(existing) is dict:
                merged[k] = existing.copy()
            else:
                merged[k] = v            
        else:
            if type(existing) == dict:
                merge(existing, v)
            else:
                merged[k] = v

def resolve(value, context):
    if value is None:
        return None
    if type(value) is str:
        return context.replace(value)
    if type(value) is not dict:
        return value
    resolved = {}
    for k, v in value.items():
        resolved[k] = resolve(v, context)
    return resolved
