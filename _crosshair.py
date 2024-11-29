from _mouse_event import ButtonEvent, MoveEvent, WheelEvent, LEFT, RIGHT, MIDDLE, X, X2, UP, DOWN, DOUBLE
from _keyboard_event import KEY_DOWN, KEY_UP, KeyboardEvent
import _mouse as mouse
import _keyboard as keyboard
import _winmouse as _os_mouse
import requests
import json
import time
from collections import namedtuple
import threading

RotEvent = namedtuple('RotEvent',['pitch', 'yaw', 'roll', 'time'])
Map = namedtuple('Map', ['map_name', 'time'])
GameState = namedtuple('GameState', ['Enum', 'time'])
Character = namedtuple('Character', ['name', 'time'])




# #ch 42.186.78.39:18080
# #auto2 10.246.198.119:18080
# account = "#zhengyuxiang01"
# url = "http://{0}:18080/gm/exec_client_by_account".format(ip)



def getMapName(url, account):
    content = """
    return UE4.CppInterface.GetMapName(g_GameInstance)
    """

    data = {
        "cmd": content,
        "account": account
    }

    re = (requests.post(url, json.dumps(data))).json()
    result = json.loads(re['msg'])
    if result['ok'] == True:
        Map = result['res']
        return Map
    else:
        return False


def getGameState(url, account):
    content = """
    return UE4.CppInterface.GetMainGameState(g_GameInstance).GameplayState    
    """
    data = {
        "cmd": content,
        "account": account
    }

    re = (requests.post(url, json.dumps(data))).json()
    result = json.loads(re['msg'])
    if result['ok'] == True:
        GameState = result['res']
        return GameState
    else:
        return False
    # Waiting: 1            选边
    # FightingPrepare: 2    SelectHeroWnd
    # AllPrepared: 3,       进游戏读图界面
    # FightingPrepare: 4    倒计时准备
    # Fighting: 5           倒计时准备结束->最后一击
    # Ending: 6             最后一击+小局结算界面
    # HighlightReplay: 7    最后一击回放
    # ShowGameEnd: 8        大局结算界面


def getCharacterName(url, account):
    content = """
    local playerState = g_BattlePlayerController.PlayerState
    return DT_CharacterData[playerState.CharacterID].Name    
    """
    data = {
        "cmd": content,
        "account": account
    }

    re = (requests.post(url, json.dumps(data))).json()
    result = json.loads(re['msg'])
    if result['ok'] == True:
        current = result['res']
        character = current[2]
        return character
    else:
        return False


def getRot(url, account):
    # content_1 = """
    # local CurRot = UE4.UGameplayStatics.GetPlayerCharacter(g_GameInstance, 0):K2_GetActorRotation()
    # return {CurRot.Pitch, CurRot.Yaw, CurRot.Roll}
    # """ body only
    content = """
    local CurRot = UE4.UGameplayStatics.GetPlayerController(g_GameInstance, 0):GetControlRotation()
    return {CurRot.Pitch, CurRot.Yaw, CurRot.Roll} 
    """
    data = {
        "cmd": content,
        "account": account
    }

    t = time.time()
    re = (requests.post(url, json.dumps(data))).json()
    result = json.loads(re['msg'])
    if result['ok'] == True:
        rot = result['res']
        pitch = round(rot[0])
        yaw = round(rot[1])
        roll = round(rot[2])
        return RotEvent(pitch, yaw, roll, t)


def playRot(url, account, pitch, yaw, roll):
    content ="""
    local NormalRot = UE4.FRotator({0}, {1}, {2})
    g_BattlePlayerController:ClientSetRotation(NormalRot)
    """
    data = {
                    "cmd": content.format(pitch, yaw, roll),
                    "account": account
                }
    requests.post(url, json.dumps(data))


def GameState_Listener(url, account, state):
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        try:
            t1 = time.time()
            map = getMapName(url, account)
            if state["map"]["name"] != map and len(map) < 15:
                state["map"]["name"] = map
                state["map"]["time"] = t1
        except:
            continue

        try:
            t2 = time.time()
            gamestate = getGameState(url, account)
            if state["gamestate"]["name"] != gamestate:
                state["gamestate"]["name"] = gamestate
                state["gamestate"]["time"] = t2
        except:
            continue

        try:
            t3 = time.time()
            character = getCharacterName(url, account)
            if state["character"]["name"] != character:
                state["character"]["name"] = character
                state["character"]["time"] = t3
        except:
            continue
        time.sleep(0.1)


def record(event, state, url, account):
    map = None
    gamestate = None
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        if state["gamestate"]["name"] == 5:
            event.append(getRot(url, account))

        if map != state["map"]["name"]:
            event.append(Map(state["map"]["name"] ,state["map"]["time"]))
            map = state["map"]["name"]

        if map != "HallMap_N" and map != "TransitionLevel" and map != None and map != False and gamestate != state["gamestate"]["name"]:
            event.append(GameState(state["gamestate"]["name"] ,state["gamestate"]["time"]))
            gamestate = state["gamestate"]["name"]


def delayMicrosecond(t):    # 微秒级延时函数
    if t < 1000000:
        start,end=0,0           # 声明变量
        start=time.time()       # 记录开始时间
        t=(t-3)/1000000     # 将输入t的单位转换为秒，-3是时间补偿
        while end-start<t:  # 循环至时间差值大于或等于设定值时
            end=time.time()     # 记录结束时间
    else:
        time.sleep(1)



def play_Game(events, url, account, state):
    last_time = None

    for event in events:
        if last_time is not None:
            delay = (event.time - last_time) * 1000000
            delayMicrosecond(delay)
        last_time = event.time

        if isinstance(event, Map):
            wait_time = time.time()
            while (event.map_name != state["map"]["name"]):
                count = time.time()
                if count - wait_time > 10:
                    break
            continue
        elif isinstance(event, GameState):
            wait_time = time.time()
            while (event.Enum != state["gamestate"]["name"]):
                count = time.time()
                if count - wait_time > 10:
                    break
            continue
        elif isinstance(event, RotEvent):
            if state["gamestate"]["name"] == 5:
                pitch = event.pitch
                yaw = event.yaw
                roll = event.roll
                t = threading.Thread(target=playRot, args=(url, account, pitch, yaw, roll,))
                t.start()
        elif isinstance(event, MoveEvent):
            _os_mouse.move_to(event.x, event.y)
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