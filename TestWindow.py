from ver_1 import Ui_MainWindow
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import *
import _combination_m_k as recordreplay
# import _crosshair as cross
import _imageAndworddetect as detect
import pickle
import os
import re
import threading

_events = []
_events_game = []
# state = {"map": {"name": None, "time": None},
#          "gamestate": {"name": None, "time": None},
#          "character": {"name": None, "time": None}}
t_image = None
t_word = None


class MyThreadRecord(QThread):
    # 创建一个信号，触发时传递当前时间给槽函数
    breakSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MyThreadRecord, self).__init__(parent)

    def run(self):
        self.breakSignal.emit("录制开始")
        global _events
        _events.clear()
        recordreplay.record(_events)




class MyThreadReplay(QThread):
    # 创建一个信号，触发时传递当前时间给槽函数
    breakSignal = pyqtSignal(str)
    breakSignal_2 = pyqtSignal(bool)
    file = None
    scale = None

    def __init__(self, parent=None):
        super(MyThreadReplay, self).__init__(parent)

    def run(self):
        replay_file = self.file
        screen_scale = self.scale
        if screen_scale == "":
            event_file = open(replay_file, 'rb')
            replay_events = pickle.load(event_file)
            msg = replay_file + "回放开始"
            self.breakSignal.emit(msg)
            recordreplay.play(replay_events)
            self.breakSignal_2.emit(True)
            self.breakSignal.emit("回放结束")
        else:
            try:
                screen_scale = float(screen_scale)
                event_file = open(replay_file, 'rb')
                replay_events = pickle.load(event_file)
                msg = replay_file+"回放开始"
                self.breakSignal.emit(msg)
                recordreplay.play(replay_events, screen_scale)
                self.breakSignal_2.emit(True)
                self.breakSignal.emit("回放结束")
            except Exception as e:
                self.breakSignal_2.emit(True)
                self.breakSignal.emit(str(e))





class MyThreadRecord_Game(QThread):
    # 创建一个信号，触发时传递当前时间给槽函数
    breakSignal = pyqtSignal(str)
    breakSignal_2 = pyqtSignal(bool)
    x = None
    y = None
    height = None
    width = None
    image = None
    word = None

    def __init__(self, parent=None):
        super(MyThreadRecord_Game, self).__init__(parent)

    def run(self):
        global _events_game
        global t_image
        global t_word

        t_image = None
        t_word = None
        _events_game.clear()

        if self.x == "":
            x = 0
        else:
            try:
                x = int(self.x)
            except Exception as e:
                self.breakSignal_2.emit(True)
                self.breakSignal.emit(str(e))
                return

        if self.y == "":
            y = 0
        else:
            try:
                y = int(self.y)
            except Exception as e:
                self.breakSignal_2.emit(True)
                self.breakSignal.emit(str(e))
                return

        if self.height == "":
            height = 0
        else:
            try:
                height = int(self.height)
            except Exception as e:
                self.breakSignal_2.emit(True)
                self.breakSignal.emit(str(e))
                return

        if self.width == "":
            width = 0
        else:
            try:
                width = int(self.width)
            except Exception as e:
                self.breakSignal_2.emit(True)
                self.breakSignal.emit(str(e))
                return

        try:
            self.breakSignal.emit("录制开始")
            if self.image != "":
                t_image = threading.Thread(target=detect.locateScreen_label, args=(_events_game, self.image,))
                t_image.start()
            if self.word != "":
                t_word = threading.Thread(target=detect.wordRetrieve_label, args=(_events_game, self.word, x, y, width, height,))
                t_word.start()
            recordreplay.record(_events_game)
        except Exception as e:
            self.breakSignal_2.emit(True)
            self.breakSignal.emit(str(e))





class MyThreadReplay_Game(QThread):
    # 创建一个信号，触发时传递当前时间给槽函数
    breakSignal = pyqtSignal(str)
    breakSignal_2 = pyqtSignal(bool)
    x = None
    y = None
    height = None
    width = None
    image = None
    word = None
    scale = None
    file = None

    def __init__(self, parent=None):
        super(MyThreadReplay_Game, self).__init__(parent)

    def run(self):
        if self.x == "":
            x = 0
        else:
            try:
                x = int(self.x)
            except Exception as e:
                self.breakSignal_2.emit(True)
                self.breakSignal.emit(str(e))
                return

        if self.y == "":
            y = 0
        else:
            try:
                y = int(self.y)
            except Exception as e:
                self.breakSignal_2.emit(True)
                self.breakSignal.emit(str(e))
                return

        if self.height == "":
            height = 0
        else:
            try:
                height = int(self.height)
            except Exception as e:
                self.breakSignal_2.emit(True)
                self.breakSignal.emit(str(e))
                return

        if self.width == "":
            width = 0
        else:
            try:
                width = int(self.width)
            except Exception as e:
                self.breakSignal_2.emit(True)
                self.breakSignal.emit(str(e))
                return
        replay_file = self.file
        event_file = open(replay_file, 'rb')
        replay_events = pickle.load(event_file)
        if self.scale == "":
            msg = replay_file + "回放开始"
            self.breakSignal.emit(msg)
            detect.play_Game(replay_events, self.image, self.word, x, y, width, height)
            self.breakSignal_2.emit(True)
            self.breakSignal.emit("回放结束")
        else:
            try:
                scale = float(self.scale)
                msg = replay_file + "回放开始"
                self.breakSignal.emit(msg)
                detect.play_Game(replay_events, self.image, self.word, x, y, width, height, scale)
                self.breakSignal_2.emit(True)
                self.breakSignal.emit("回放结束")
            except Exception as e:
                self.breakSignal_2.emit(True)
                self.breakSignal.emit(str(e))







class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.StartRecord)
        self.pushButton_2.clicked.connect(self.StopRecord)
        self.pushButton_3.clicked.connect(self.SaveRecord)
        self.pushButton_4.clicked.connect(self.Replay)
        self.pushButton_5.clicked.connect(self.StartRecord_Game)
        self.pushButton_6.clicked.connect(self.StopRecord_Game)
        self.pushButton_7.clicked.connect(self.SaveRecord_Game)
        self.pushButton_8.clicked.connect(self.Replay_Game)
        self.comboBox.addItems(self.getfile())
        self.comboBox_2.addItems(self.getfile_game())

    #done
    def StartRecord(self):
        self.pushButton.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.pushButton_5.setEnabled(False)
        self.pushButton_6.setEnabled(False)
        self.pushButton_7.setEnabled(False)
        self.pushButton_8.setEnabled(False)
        self.pushButton_9.setEnabled(False)
        self.pushButton_10.setEnabled(False)
        self.pushButton_11.setEnabled(False)
        self.Thread = MyThreadRecord()
        self.Thread.breakSignal.connect(self.textShowRecord)
        self.Thread.start()

    #done
    def StopRecord(self):
        global _events
        if len(_events) == 0:
            msg = "无录制"
            self.textShowRecord(msg)
        else:
            recordreplay.stopRecording(_events)
            msg = "录制结束"
            self.textShowRecord(msg)

            self.pushButton.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            self.pushButton_6.setEnabled(True)
            self.pushButton_7.setEnabled(True)
            self.pushButton_8.setEnabled(True)
            self.pushButton_9.setEnabled(True)
            self.pushButton_10.setEnabled(True)
            self.pushButton_11.setEnabled(True)


    #done
    def SaveRecord(self):
        global _events
        filename = self.lineEdit.text()

        if filename == "":
            self.textShowRecord("文件名不能为空")
        elif len(_events) == 0:
            self.textShowRecord("无录制操作")
        else:
            filename = filename + ".pickle"
            with open(filename, "wb") as f:
                pickle.dump(_events, f)
            msg = "录制操作文件" + filename + "已保存"
            self.textShowRecord(msg)
            _events.clear()
        self.comboBox.clear()
        self.comboBox.addItems(self.getfile())

    #done
    def textShowRecord(self, text):
        self.textBrowser.setText(text)

    #done
    def getfile(self):
        fileList = []
        file_dir = os.getcwd()

        for file in os.listdir(file_dir):
            ret = re.search("\.pickle", file)
            if ret != None:
                fileList.append(file)
        return fileList

    #done
    def Replay(self):
        self.setButtonEnabled(False)
        self.Thread = MyThreadReplay()
        self.Thread.breakSignal.connect(self.textShowReplay)
        self.Thread.breakSignal_2.connect(self.setButtonEnabled)
        self.Thread.file = self.comboBox.currentText()
        self.Thread.scale = self.lineEdit_3.text()
        self.Thread.start()

    #done
    def textShowReplay(self, text):
        self.textBrowser_2.setText(text)

    #done
    def setButtonEnabled(self, judge):
        self.pushButton.setEnabled(judge)
        self.pushButton_2.setEnabled(judge)
        self.pushButton_3.setEnabled(judge)
        self.pushButton_4.setEnabled(judge)
        self.pushButton_5.setEnabled(judge)
        self.pushButton_6.setEnabled(judge)
        self.pushButton_7.setEnabled(judge)
        self.pushButton_8.setEnabled(judge)
        self.pushButton_9.setEnabled(judge)
        self.pushButton_10.setEnabled(judge)
        self.pushButton_11.setEnabled(judge)

    def setButtonEnabled_Game(self, judge):
        self.pushButton.setEnabled(judge)
        self.pushButton_2.setEnabled(judge)
        self.pushButton_3.setEnabled(judge)
        self.pushButton_4.setEnabled(judge)
        self.pushButton_5.setEnabled(judge)
        self.pushButton_7.setEnabled(judge)
        self.pushButton_8.setEnabled(judge)
        self.pushButton_9.setEnabled(judge)
        self.pushButton_10.setEnabled(judge)
        self.pushButton_11.setEnabled(judge)


    def StartRecord_Game(self):
        self.setButtonEnabled_Game(False)
        self.Thread = MyThreadRecord_Game()
        self.Thread.x = self.lineEdit_10.text()
        self.Thread.y = self.lineEdit_11.text()
        self.Thread.height = self.lineEdit_12.text()
        self.Thread.width = self.lineEdit_13.text()
        self.Thread.image = self.lineEdit_14.text()
        self.Thread.word = self.lineEdit_15.text()
        self.Thread.breakSignal.connect(self.textShowRecord_Game)
        self.Thread.breakSignal_2.connect(self.setButtonEnabled_Game)
        self.Thread.start()


    def StopRecord_Game(self):
        global _events_game
        global t_image
        global t_word
        if len(_events_game) == 0:
            msg = "无录制"
            self.textShowRecord_Game(msg)
        else:
            if t_image != None:
                t_image.do_run = False
            if t_word != None:
                t_word.do_run = False
            recordreplay.stopRecording(_events_game)
            msg = "录制结束"
            self.textShowRecord_Game(msg)
            self.setButtonEnabled_Game(True)


    def SaveRecord_Game(self):
        global _events_game
        filename = self.lineEdit_2.text()

        if filename == "":
            self.textShowRecord_Game("文件名不能为空")
        elif len(_events_game) == 0:
            self.textShowRecord_Game("无录制操作")
        else:
            filename = filename + "_game.pickle"
            with open(filename, "wb") as f:
                pickle.dump(_events_game, f)
            msg = "录制操作文件" + filename + "已保存"
            self.textShowRecord_Game(msg)
            _events_game.clear()
        self.comboBox_2.clear()
        self.comboBox_2.addItems(self.getfile())

    def getfile_game(self):
        fileList = []
        file_dir = os.getcwd()

        for file in os.listdir(file_dir):
            ret = re.search("_game.pickle", file)
            if ret != None:
                fileList.append(file)
        return fileList

    def Replay_Game(self):
        self.setButtonEnabled(False)
        self.Thread = MyThreadReplay_Game()
        self.Thread.breakSignal.connect(self.textShowReplay_Game)
        self.Thread.breakSignal_2.connect(self.setButtonEnabled)
        self.Thread.scale = self.lineEdit_4.text()
        self.Thread.x = self.lineEdit_10.text()
        self.Thread.y = self.lineEdit_11.text()
        self.Thread.height = self.lineEdit_12.text()
        self.Thread.width = self.lineEdit_13.text()
        self.Thread.image = self.lineEdit_14.text()
        self.Thread.word = self.lineEdit_15.text()
        self.Thread.file = self.comboBox_2.currentText()
        self.Thread.start()


    def textShowRecord_Game(self, text):
        self.textBrowser_3.setText(text)


    def textShowReplay_Game(self, text):
        self.textBrowser_4.setText(text)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MyWindow()
    mainwindow.show()
    sys.exit(app.exec_())
input('please input any key to exit')