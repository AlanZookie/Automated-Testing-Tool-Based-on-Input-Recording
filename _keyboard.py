from __future__ import print_function as _print_function


import re as _re
import itertools as _itertools
import collections as _collections
from threading import Thread as _Thread, Lock as _Lock
import time as _time

_time.monotonic = getattr(_time, 'monotonic', None) or _time.time

_is_str = lambda x: isinstance(x, str)
_is_number = lambda x: isinstance(x, int)
import queue as _queue
from threading import Event as _UninterruptibleEvent
_is_list = lambda x: isinstance(x, (list, tuple))

# Just a dynamic object to store attributes for the closures.
class _State(object): pass

# The "Event" class from `threading` ignores signals when waiting and is
# impossible to interrupt with Ctrl+C. So we rewrite `wait` to wait in small,
# interruptible intervals.
class _Event(_UninterruptibleEvent):
    def wait(self):
        while True:
            if _UninterruptibleEvent.wait(self, 0.5):
                break

import platform as _platform
import _winkeyboard as _os_keyboard
_os_keyboard.init()
_time.sleep(0.1)
from _keyboard_event import KEY_DOWN, KEY_UP, KeyboardEvent
from _generic import GenericListener as _GenericListener
from _canonical_names import all_modifiers, sided_modifiers, normalize_name

_modifier_scan_codes = set()
def is_modifier(key):
    """
    Returns True if `key` is a scan code or name of a modifier key.
    """
    if _is_str(key):
        return key in all_modifiers
    else:
        if not _modifier_scan_codes:
            scan_codes = (key_to_scan_codes(name, False) for name in all_modifiers) 
            _modifier_scan_codes.update(*scan_codes)
        return key in _modifier_scan_codes

_pressed_events_lock = _Lock()
_pressed_events = {}
_physically_pressed_keys = _pressed_events
_logically_pressed_keys = {}
class _KeyboardListener(_GenericListener):
    transition_table = {
        #Current state of the modifier, per `modifier_states`.
        #|
        #|             Type of event that triggered this modifier update.
        #|             |
        #|             |         Type of key that triggered this modifier update.
        #|             |         |
        #|             |         |            Should we send a fake key press?
        #|             |         |            |
        #|             |         |     =>     |       Accept the event?
        #|             |         |            |       |
        #|             |         |            |       |      Next state.
        #v             v         v            v       v      v
        ('free',       KEY_UP,   'modifier'): (False, True,  'free'),
        ('free',       KEY_DOWN, 'modifier'): (False, False, 'pending'),
        ('pending',    KEY_UP,   'modifier'): (True,  True,  'free'),
        ('pending',    KEY_DOWN, 'modifier'): (False, True,  'allowed'),
        ('suppressed', KEY_UP,   'modifier'): (False, False, 'free'),
        ('suppressed', KEY_DOWN, 'modifier'): (False, False, 'suppressed'),
        ('allowed',    KEY_UP,   'modifier'): (False, True,  'free'),
        ('allowed',    KEY_DOWN, 'modifier'): (False, True,  'allowed'),

        ('free',       KEY_UP,   'hotkey'):   (False, None,  'free'),
        ('free',       KEY_DOWN, 'hotkey'):   (False, None,  'free'),
        ('pending',    KEY_UP,   'hotkey'):   (False, None,  'suppressed'),
        ('pending',    KEY_DOWN, 'hotkey'):   (False, None,  'suppressed'),
        ('suppressed', KEY_UP,   'hotkey'):   (False, None,  'suppressed'),
        ('suppressed', KEY_DOWN, 'hotkey'):   (False, None,  'suppressed'),
        ('allowed',    KEY_UP,   'hotkey'):   (False, None,  'allowed'),
        ('allowed',    KEY_DOWN, 'hotkey'):   (False, None,  'allowed'),

        ('free',       KEY_UP,   'other'):    (False, True,  'free'),
        ('free',       KEY_DOWN, 'other'):    (False, True,  'free'),
        ('pending',    KEY_UP,   'other'):    (True,  True,  'allowed'),
        ('pending',    KEY_DOWN, 'other'):    (True,  True,  'allowed'),
        # Necessary when hotkeys are removed after beign triggered, such as
        # TestKeyboard.test_add_hotkey_multistep_suppress_modifier.
        ('suppressed', KEY_UP,   'other'):    (False, False, 'allowed'),
        ('suppressed', KEY_DOWN, 'other'):    (True,  True,  'allowed'),
        ('allowed',    KEY_UP,   'other'):    (False, True,  'allowed'),
        ('allowed',    KEY_DOWN, 'other'):    (False, True,  'allowed'),
    }

    def init(self):
        _os_keyboard.init()

        self.active_modifiers = set()
        self.blocking_hooks = []
        self.blocking_keys = _collections.defaultdict(list)
        self.nonblocking_keys = _collections.defaultdict(list)
        self.blocking_hotkeys = _collections.defaultdict(list)
        self.nonblocking_hotkeys = _collections.defaultdict(list)
        self.filtered_modifiers = _collections.Counter()
        self.is_replaying = False

        # Supporting hotkey suppression is harder than it looks. See
        # https://github.com/boppreh/keyboard/issues/22
        self.modifier_states = {} # "alt" -> "allowed"

    def pre_process_event(self, event):
        for key_hook in self.nonblocking_keys[event.scan_code]:
            key_hook(event)

        with _pressed_events_lock:
            hotkey = tuple(sorted(_pressed_events))
        for callback in self.nonblocking_hotkeys[hotkey]:
            callback(event)

        return event.scan_code or (event.name and event.name != 'unknown')

    def direct_callback(self, event):
        """
        This function is called for every OS keyboard event and decides if the
        event should be blocked or not, and passes a copy of the event to
        other, non-blocking, listeners.

        There are two ways to block events: remapped keys, which translate
        events by suppressing and re-emitting; and blocked hotkeys, which
        suppress specific hotkeys.
        """
        # Pass through all fake key events, don't even report to other handlers.
        if self.is_replaying:
            return True

        if not all(hook(event) for hook in self.blocking_hooks):
            return False

        event_type = event.event_type
        scan_code = event.scan_code

        # Update tables of currently pressed keys and modifiers.
        with _pressed_events_lock:
            if event_type == KEY_DOWN:
                if is_modifier(scan_code): self.active_modifiers.add(scan_code)
                _pressed_events[scan_code] = event
            hotkey = tuple(sorted(_pressed_events))
            if event_type == KEY_UP:
                self.active_modifiers.discard(scan_code)
                if scan_code in _pressed_events: del _pressed_events[scan_code]

        # Mappings based on individual keys instead of hotkeys.
        for key_hook in self.blocking_keys[scan_code]:
            if not key_hook(event):
                return False

        # Default accept.
        accept = True

        if self.blocking_hotkeys:
            if self.filtered_modifiers[scan_code]:
                origin = 'modifier'
                modifiers_to_update = set([scan_code])
            else:
                modifiers_to_update = self.active_modifiers
                if is_modifier(scan_code):
                    modifiers_to_update = modifiers_to_update | {scan_code}
                callback_results = [callback(event) for callback in self.blocking_hotkeys[hotkey]]
                if callback_results:
                    accept = all(callback_results)
                    origin = 'hotkey'
                else:
                    origin = 'other'

            for key in sorted(modifiers_to_update):
                transition_tuple = (self.modifier_states.get(key, 'free'), event_type, origin)
                should_press, new_accept, new_state = self.transition_table[transition_tuple]
                if should_press: press(key)
                if new_accept is not None: accept = new_accept
                self.modifier_states[key] = new_state

        if accept:
            if event_type == KEY_DOWN:
                _logically_pressed_keys[scan_code] = event
            elif event_type == KEY_UP and scan_code in _logically_pressed_keys:
                del _logically_pressed_keys[scan_code]

        # Queue for handlers that won't block the event.
        self.queue.put(event)

        return accept

    def listen(self):
        _os_keyboard.listen(self.direct_callback)

_listener = _KeyboardListener()

def key_to_scan_codes(key, error_if_missing=True):
    if _is_number(key):
        return (key,)
    elif _is_list(key):
        return sum((key_to_scan_codes(i) for i in key), ())
    elif not _is_str(key):
        raise ValueError('Unexpected key type ' + str(type(key)) + ', value (' + repr(key) + ')')

    normalized = normalize_name(key)
    if normalized in sided_modifiers:
        left_scan_codes = key_to_scan_codes('left ' + normalized, False)
        right_scan_codes = key_to_scan_codes('right ' + normalized, False)
        return left_scan_codes + tuple(c for c in right_scan_codes if c not in left_scan_codes)

    try:
        # Put items in ordered dict to remove duplicates.
        t = tuple(_collections.OrderedDict((scan_code, True) for scan_code, modifier in _os_keyboard.map_name(normalized)))
        e = None
    except (KeyError, ValueError) as exception:
        t = ()
        e = exception

    if not t and error_if_missing:
        raise ValueError('Key {} is not mapped to any known key.'.format(repr(key)), e)
    else:
        return t

def parse_hotkey(hotkey):
    if _is_number(hotkey) or len(hotkey) == 1:
        scan_codes = key_to_scan_codes(hotkey)
        step = (scan_codes,)
        steps = (step,)
        return steps
    elif _is_list(hotkey):
        if not any(map(_is_list, hotkey)):
            step = tuple(key_to_scan_codes(k) for k in hotkey)
            steps = (step,)
            return steps
        return hotkey

    steps = []
    for step in _re.split(r',\s?', hotkey):
        keys = _re.split(r'\s?\+\s?', step)
        steps.append(tuple(key_to_scan_codes(key) for key in keys))
    return tuple(steps)

def send(hotkey, do_press=True, do_release=True):
    _listener.is_replaying = True

    parsed = parse_hotkey(hotkey)
    for step in parsed:
        if do_press:
            for scan_codes in step:
                _os_keyboard.press(scan_codes[0])

        if do_release:
            for scan_codes in reversed(step):
                _os_keyboard.release(scan_codes[0])

    _listener.is_replaying = False

press_and_release = send

def press(hotkey):
    send(hotkey, True, False)

def release(hotkey):
    send(hotkey, False, True)

def hook(callback):
    _listener.add_handler(callback)
    return callback


def unhook(remove):
    _listener.remove_handler(remove)
unhook_key = unhook





