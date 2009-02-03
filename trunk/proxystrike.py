#!/usr/bin/python
#Covered by GPL V2.0
#Coded by Carlos del Ojo Elias (deepbit@gmail.com)

import sys
import time
import attacker
from crllr import *
from paConsole import ProixConsole


#iface="GUI"
#
#if '-c' in sys.argv:
#	iface="Console"
#
#try:
from PyQt4 import QtGui
from mainform import *
#except:
#	print "Unable to load PyQt4 Modules :S"
#	iface="Console"

#if iface=="GUI":
app = QtGui.QApplication(sys.argv)
window = QtGui.QMainWindow()
ui = Ui_MainWindow()
ui.setController(Controller())
ui.setupUi(window)

Proxynet.init("\.(jpg|png|gif|js|ico|bmp|zip|rar|pdf|css|t?gz)$")

window.show()
sys.exit(app.exec_())
#else:
#	pc=ProixConsole()
#	pc.run()
