from _mouse_event import ButtonEvent, MoveEvent, WheelEvent, LEFT, RIGHT, MIDDLE, X, X2, UP, DOWN, DOUBLE
from _keyboard_event import KEY_DOWN, KEY_UP, KeyboardEvent
import _mouse as mouse
import _keyboard as keyboard
import _winmouse as _os_mouse
import pyautogui
import cv2
import time
import pytesseract
from PIL import Image
import threading
from collections import namedtuple
WordJudge = namedtuple('WordJudge',['judge', 'time'])
ImageJudge = namedtuple('ImageJudge',['judge', 'time'])

def delayMicrosecond(t):    # 微秒级延时函数
    if t < 1000000:
        start,end=0,0           # 声明变量
        start=time.time()       # 记录开始时间
        t=(t-3)/1000000     # 将输入t的单位转换为秒，-3是时间补偿
        while end-start<t:  # 循环至时间差值大于或等于设定值时
            end=time.time()     # 记录结束时间
    else:
        time.sleep(1)


def locateScreen_label(event, image_name, confi=0.6, gray=False):
    state = 1
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        pos = pyautogui.locateOnScreen(image_name, confidence=confi, grayscale=gray)
        ti = time.time()
        if pos != None and state == 1:
            event.append(ImageJudge(True, ti))
            state = 2
        elif pos == None and state == 2:
            event.append(ImageJudge(False, ti))
            state = 1



def wordRetrieve_label(event, word, x, y, width, height):
    tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract'
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    state = 1
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        text = pytesseract.image_to_string(screenshot, lang='chi_sim')
        ti = time.time()
        if word in text and state == 1:
            event.append(WordJudge(True, ti))
            state = 2
        elif word not in text and state == 2:
            event.append(WordJudge(False, ti))
            state = 1


def locateScreen(image_name, state, confi=0.3, gray=False):
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        pos = pyautogui.locateOnScreen(image_name, confidence=confi, grayscale=gray)
        if pos != None and state == 1:
            state = 2
        elif pos == None and state == 2:
            state = 1


def wordRetrieve(word, state, x, y, width, height):
    tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract'
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        text = pytesseract.image_to_string(screenshot, lang='chi_sim')
        if word in text and state == 1:
            state = 2
        elif word not in text and state == 2:
            state = 1


def play_Game(events, image, word, x, y, width, height, scale=1):
    last_time = None
    state = 1

    for event in events:
        if last_time is not None:
            delay = (event.time - last_time) * 1000000
            delayMicrosecond(delay)
        last_time = event.time

        if isinstance(event, ImageJudge):
            if event.judge == True:
                t_image = threading.Thread(target=wordRetrieve, args=(state, image,))
                t_image.start()
            elif event.judge == False:
                while state == 2:
                    wait = time.time()
                t_image.do_run = False
            # wait_time = time.time()
            # while (event.map_name != state["map"]["name"]):
            #     count = time.time()
            #     if count - wait_time > 10:
            #         break
            # continue
        elif isinstance(event, WordJudge):
            if event.judge == True:
                t_word = threading.Thread(target=locateScreen, args=(state, word, state, x, y, width, height,))
                t_word.start()
            elif event.judge == False:
                while state == 2:
                    wait = time.time()
                t_word.do_run = False
            # wait_time = time.time()
            # while (event.Enum != state["gamestate"]["name"]):
            #     count = time.time()
            #     if count - wait_time > 10:
            #         break
            # continue
        elif isinstance(event, MoveEvent):
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

