
# TODO
# - infinite wait
# - mouse.on_move
version = '0.7.1'

import time as _time
import _winmouse as _os_mouse
from _mouse_event import ButtonEvent, MoveEvent, WheelEvent, LEFT, RIGHT, MIDDLE, X, X2, UP, DOWN, DOUBLE
from _generic import GenericListener as _GenericListener

_pressed_events = set()
class _MouseListener(_GenericListener):
    def init(self):
        _os_mouse.init()
    def pre_process_event(self, event):
        if isinstance(event, ButtonEvent):
            if event.event_type in (UP, DOUBLE):
                _pressed_events.discard(event.button)
            else:
                _pressed_events.add(event.button)
        return True

    def listen(self):
        _os_mouse.listen(self.queue)

_listener = _MouseListener()


def hook(callback):
    """
    Installs a global listener on all available mouses, invoking `callback`
    each time it is moved, a key status changes or the wheel is spun. A mouse
    event is passed as argument, with type either `mouse.ButtonEvent`,
    `mouse.WheelEvent` or `mouse.MoveEvent`.

    Returns the given callback for easier development.
    """
    _listener.add_handler(callback)
    return callback

def unhook(callback):
    """
    Removes a previously installed hook.
    """
    _listener.remove_handler(callback)




