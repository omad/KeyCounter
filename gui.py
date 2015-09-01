import sys
from PyQt4 import QtGui, QtCore
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import urllib
from datetime import datetime
from sys import platform as _platform

if _platform == "darwin":
    from Foundation import NSObject, NSLog
    from Cocoa import NSEvent, NSKeyDownMask, NSKeyDown
    import string
elif _platform == "win32":
    import pyHook

class KeyCounter(QtCore.QObject):
    '''
    Create an object that counts global keyboard presses

    The current count can be accessed at `keyCount`
    '''
    def __init__(self):
        super(KeyCounter, self).__init__()
        self.keyCount = 0
        if _platform == "win32":
            self.setupKeyCounterWin()
        elif _platform == "darwin":
            self.setupKeyCounterMac()

    def setupKeyCounterMac(self):
        mask = NSKeyDownMask
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, self.macCountKey)
        NSEvent.addLocalMonitorForEventsMatchingMask_handler_(mask, self.macCountKey)

    def macCountKey(self, event):
        eventCharAscii = ord(event._.characters)
        if eventCharAscii > 32 and eventCharAscii < 127:
            self.keyCount += 1

    def countKey(self, event):
        '''
        Increment the keyCount variable if an ascii key was pressed
        '''
        if event.Ascii > 32 and event.Ascii < 127:
            self.keyCount += 1
        return True # Don't block key handling

    def setupKeyCounterWin(self):
        '''
        Setup the hook for monitoring global key presses
        '''
        hm = pyHook.HookManager()
        # watch for all keyboard events
        hm.KeyDown = self.countKey
        # set the hook
        hm.HookKeyboard()


class KeyCounterGui(QtGui.QWidget):
    '''
    Provide a GUI displaying the number of recorded keyboard Presses

    Will include some controls for saving to files or uploading online
    '''

    def __init__(self):
        super(KeyCounterGui, self).__init__()
        self.keyCounter = KeyCounter()
        self.initUI()


    def initUI(self):

        label = QtGui.QLabel('Characters Pressed')

        self.counter = QtGui.QLabel()

        saveButton = QtGui.QPushButton('Save')
        saveButton.clicked.connect(self.saveToFile)

        resetButton = QtGui.QPushButton('Reset')
        resetButton.clicked.connect(self.resetCounter)

        postButton = QtGui.QPushButton('Post to Google')
        postButton.clicked.connect(self.postCount)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(label, 1, 0)
        grid.addWidget(self.counter, 1, 1)
        grid.addWidget(resetButton, 2, 0)
        grid.addWidget(saveButton, 2, 1)
        grid.addWidget(postButton, 3, 0)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateCounter)
        self.timer.start(1000)

        self.setLayout(grid)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Keystroke Counter')
        self.setWindowIcon(QtGui.QIcon('web.png'))

        self.show()

    def updateCounter(self):
        keyCount = self.keyCounter.keyCount
        self.counter.setText(str(keyCount))

    def saveToFile(self):
        with open('count.txt', 'a') as f:
            keyCount = self.keyCounter.keyCount
            f.write('%s, %s' % (datetime.now(), keyCount))

    def resetCounter(self):
        self.keyCounter.keyCount = 0

    def postCount(self):
        keyCount = self.keyCounter.keyCount
        postCountToGoogleForm(keyCount)


#Remote Google Form logs post
def postCountToGoogleForm(keyCount):
    url="https://docs.google.com/forms/d/1KVMkL76ju93IFI6ieCoY8_HyYl9tYjCeRAw_I7nRX7s/formResponse" #Specify Google Form URL here
    klog={'entry_566766994':keyCount} #Specify the Field Name here
    try:
        dataenc = urllib.urlencode(klog)
        req = urllib2.Request(url,dataenc)
        response = urllib2.urlopen(req)
    except Exception as e:
        print(e)
    return True

def main():
    app = QtGui.QApplication(sys.argv)
    ex = KeyCounterGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


## NOTES
# https://gist.github.com/ljos/3019549 for OS X support
# Check out QSystemTrayIcon (see https://github.com/Svenito/EasyTimer/blob/master/timer.py)
# and https://docs.python.org/2/library/configparser.html
# and http://zetcode.com/gui/pyqt4/eventsandsignals/ for a quick very basic reference
# and