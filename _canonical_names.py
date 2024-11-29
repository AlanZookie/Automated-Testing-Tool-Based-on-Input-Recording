from __future__ import unicode_literals

# try:
#     basestring
# except NameError:
basestring = str

# Defaults to Windows canonical names (platform-specific overrides below)
canonical_names = {
    'escape': 'esc',
    'return': 'enter',
    'del': 'delete',
    'control': 'ctrl',

    'left arrow': 'left',
    'up arrow': 'up',
    'down arrow': 'down',
    'right arrow': 'right',

    ' ': 'space',  # Prefer to spell out keys that would be hard to read.
    '\x1b': 'esc',
    '\x08': 'backspace',
    '\n': 'enter',
    '\t': 'tab',
    '\r': 'enter',

    'scrlk': 'scroll lock',
    'prtscn': 'print screen',
    'prnt scrn': 'print screen',
    'snapshot': 'print screen',
    'ins': 'insert',
    'pause break': 'pause',
    'ctrll lock': 'caps lock',
    'capslock': 'caps lock',
    'number lock': 'num lock',
    'numlock': 'num lock',
    'space bar': 'space',
    'spacebar': 'space',
    'linefeed': 'enter',
    'win': 'windows',

    # Mac keys
    'command': 'windows',
    'cmd': 'windows',
    'option': 'alt',

    'app': 'menu',
    'apps': 'menu',
    'application': 'menu',
    'applications': 'menu',

    'pagedown': 'page down',
    'pageup': 'page up',
    'pgdown': 'page down',
    'pgup': 'page up',

    'play/pause': 'play/pause media',

    'num multiply': '*',
    'num divide': '/',
    'num add': '+',
    'num plus': '+',
    'num minus': '-',
    'num sub': '-',
    'num enter': 'enter',
    'num 0': '0',
    'num 1': '1',
    'num 2': '2',
    'num 3': '3',
    'num 4': '4',
    'num 5': '5',
    'num 6': '6',
    'num 7': '7',
    'num 8': '8',
    'num 9': '9',

    'left win': 'left windows',
    'right win': 'right windows',
    'left control': 'left ctrl',
    'right control': 'right ctrl',
    'left menu': 'left alt',  # Windows...
    'altgr': 'alt gr',

}
sided_modifiers = {'ctrl', 'alt', 'shift', 'windows'}
all_modifiers = {'alt', 'alt gr', 'ctrl', 'shift', 'windows'} | set('left ' + n for n in sided_modifiers) | set(
    'right ' + n for n in sided_modifiers)


# Platform-specific canonical overrides


def normalize_name(name):
    """
    Given a key name (e.g. "LEFT CONTROL"), clean up the string and convert to
    the canonical representation (e.g. "left ctrl") if one is known.
    """
    if not name or not isinstance(name, basestring):
        raise ValueError('Can only normalize non-empty string names. Unexpected ' + repr(name))

    if len(name) > 1:
        name = name.lower()
    if name != '_' and '_' in name:
        name = name.replace('_', ' ')

    return canonical_names.get(name, name)
