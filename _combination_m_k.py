import _mouse as mouse
import _keyboard as keyboard
import time
from _mouse_event import ButtonEvent, MoveEvent, WheelEvent, LEFT, RIGHT, MIDDLE, X, X2, UP, DOWN, DOUBLE
from _keyboard_event import KEY_DOWN, KEY_UP, KeyboardEvent
import _winmouse as _os_mouse



def record(events):
    mouse.hook(events.append)
    keyboard.hook(events.append)
    return events

def stopRecording(events):
    mouse.unhook(events.append)
    keyboard.unhook(events.append)
    return events

def delayMicrosecond(t):    # 微秒级延时函数
    start,end=0,0           # 声明变量
    start=time.time()       # 记录开始时间
    t=(t-3)/1000000     # 将输入t的单位转换为秒，-3是时间补偿
    while end-start<t:  # 循环至时间差值大于或等于设定值时
        end=time.time()     # 记录结束时间

def play(events, scale=1, speed_factor=1.0):
    last_time = None
    for event in events:
        if speed_factor > 0 and last_time is not None:
            delay = ((event.time - last_time)*1000000) / speed_factor
            delayMicrosecond(delay)
        last_time = event.time

        if isinstance(event, MoveEvent):
            _os_mouse.move_to(event.x, event.y, scale)
        elif isinstance(event, ButtonEvent):
            if event.event_type == UP:
                _os_mouse.release(event.button)
            else:
                _os_mouse.press(event.button)
        elif isinstance(event, WheelEvent):
            _os_mouse.wheel(event.delta)
        elif isinstance(event, KeyboardEvent): 
            key = event.scan_code or event.name
            keyboard.press(key) if event.event_type == KEY_DOWN else keyboard.release(key)



