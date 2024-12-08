



from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import sys
import ctypes
import os
import json
import math
import sass
import subprocess
import time
import threading

from datetime import datetime, timedelta
from fontTools import ttLib

























class FontGatherer(QThread):
	finished = pyqtSignal(dict, str)
	fontIndexed = pyqtSignal(str, int)

	def __init__(self, path, filePaths=[]):
		super().__init__()
		self.path = path
		self.filePaths = filePaths



	def run(self):
		startTime = time.perf_counter()
		rawFont = QRawFont()
		systemFonts = QFontDatabase.families()
		fontData = {}
		total = 0
		parent = os.path.basename(self.path)



		if not self.filePaths:
			self.filePaths = [os.path.join(root, f) for root, _, files in os.walk(self.path) for f in files]

		for path in self.filePaths:
			suffix = os.path.splitext(os.path.basename(path))[1].lower()
			if suffix in (".ttf", ".otf"):
				try:
					# skip variable fonts
					if "fvar" not in (ttFont := ttLib.TTFont(path)):
						nameTable = ttFont["name"]
						if (family := nameTable.getDebugName(1)) == "false" or \
						(fullName := nameTable.getDebugName(4)) == "false" or \
						(typeface := nameTable.getDebugName(16) or family) == "false":
							continue


						if family not in systemFonts:
							with open(path, "rb") as f:
								rawFont.loadFromData(fontBytes := f.read(), 0, QFont.HintingPreference.PreferNoHinting)

							# if the font family name exceeds 30 characters, qt may not recognize the font
							QFontDatabase.addApplicationFont(path) if len(family) < 30 else QFontDatabase.addApplicationFontFromData(fontBytes)




						weight = ttFont["OS/2"].usWeightClass
						style = rawFont.style()

						if typeface not in fontData:
							fontData[typeface] = {"family": family, "fullName": fullName, "weight": weight, "path": path, "style": style, "type": set(), "fontFamily": {}, "folderPath": self.path}


						fontData[typeface]["type"].add(suffix)
						fontData[typeface]["fontFamily"][fullName] = {"family": family, "weight": weight, "path": path, "style": style}



						if abs(400 - weight) <= abs(400 - fontData[typeface]["weight"]):
							# if style == QFont.Style.StyleNormal and not any(s in fullName.lower() for s in ("round", "slant")):
							if style == QFont.Style.StyleNormal:
								fontData[typeface].update(family=family, fullName=fullName, weight=weight, path=path, style=style)




						ttFont.close()
						total += 1
						self.fontIndexed.emit(parent, total)
				except Exception as e:
					print(e)
	


		self.finished.emit(fontData, self.path)
		print(f"{time.perf_counter() - startTime:.6f}")

















from conf import *
from widget.controls import *
from widget.widgets import *
from widget.font_window import *
from widget.sidebar import *

if (isWin := elem["platform"] == "win32"):
	from widget.frameless import *



































class Main(Frameless if isWin else QWidget):
	fontSizeChanged = pyqtSignal()
	threadFinished = pyqtSignal(dict, str)

	def __init__(self):
		super().__init__()
		elem["main"] = self
		self.setObjectName("main")

		Tooltip(self)
		Toast(self)

		QFontDatabase.addApplicationFont(f"resource/{PARAM['iconsName']}.ttf")
		self.updateStylesheet()



		layout = QVBoxLayout(contentsMargins=QMargins(), spacing=0)
		layout.addWidget(Controls())

		mainArea = QHBoxLayout(contentsMargins=QMargins(), spacing=0)
		mainArea.addWidget(Sidebar())

		fontWindow = elem["mainStack"] = QStackedWidget()
		fontWindow.addWidget(ScrollArea())
		mainArea.addWidget(fontWindow)

		layout.addLayout(mainArea)
		
	

		if isWin:
			wrap = QVBoxLayout(contentsMargins=QMargins(), spacing=0)
			wrap.addWidget(Titlebar(self))
			wrap.addLayout(layout)
			layout = wrap


		self.setLayout(layout)
		self.setAppGeometry()




		self.threadQueue = []
		self.currentThread = None

		for i in PREFS["folders"]:
			self.queueThread(i)






	
		for seq, func in [
		(QKeySequence.StandardKey.ZoomIn, self.scaleInterface),
		("Ctrl+=", self.scaleInterface),
		(QKeySequence.StandardKey.ZoomOut, lambda: self.scaleInterface(zoomOut=True)),
		(QKeySequence.StandardKey.Find, elem["search"].setFocus),
		]:
			QShortcut(seq, self, autoRepeat=False).activated.connect(func)















	def queueThread(self, path):
		fontThread = FontGatherer(path)
		fontThread.finished.connect(lambda data, path: (
			self.populate(data), 
			self.processThreads(), 
			self.threadFinished.emit(data, path),
			elem["mainStack"].currentWidget().update()
			))
		fontThread.fontIndexed.connect(lambda parent, n: elem["toast"].notify(f"Found {n} fonts in {parent}"))

		self.threadQueue.append(fontThread)
		if self.currentThread is None:
			self.processThreads()



	def processThreads(self):
		if self.currentThread:
			self.currentThread.wait()
			self.currentThread = None

		if self.threadQueue:
			self.currentThread = self.threadQueue.pop(0)
			self.currentThread.start()


	def populate(self, data):
		for n, i in enumerate(data.items()):
			elem["mainStack"].widget(0).addWidget(FontRow(i, isLast=n==len(data) - 1))











	def setAppGeometry(self):
		geom = DATA.get("appGeometry", {})

		if geom.get("rect"):
			self.setGeometry(QRect(*geom["rect"]))
		else:
			screenGeom = self.screen().availableGeometry()
			appGeom = QRect(QPoint(), screenGeom.size() / 1.5)
			appGeom.moveCenter(screenGeom.center())
			self.setGeometry(appGeom)

		if geom.get("max"):
			self.showMaximized()





	def scaleInterface(self, zoomOut=False):
		PREFS["fontSize"] = max(12, min(PREFS["fontSize"] + (1 if not zoomOut else -1), 40))
		self.updateStylesheet()









	def updateStylesheet(self):
		PARAM["margin"] = int(PREFS["fontSize"] * SC_FACTOR["margin"])

		# init relative colors
		for base, key, val in [
			("foreground", "mid", 120), 
			("background", "selected", 30), 
			("foreground", "selected-inverted", 100), 
			("background", "background-selection", 30),
			]:
			(color := QColor(COLOR[base])).setHsv(color.hue(), color.saturation() ,(v := color.value()) + (val if v <= 255 - val else -val))
			COLOR[key] = color.name()





		values = [
			(PREFS, "fontSize"),
			(PARAM, "iconsName"),
			(PARAM, "margin"),
			(PREFS, "font"),

			(COLOR, "foreground"),
			(COLOR, "border"),
			(COLOR, "background"),
			(COLOR, "background-selection"),

			(COLOR, "mid"),
			(COLOR, "selected"),
			(COLOR, "selected-inverted"),

		]

		with open("resource/style.css", "r") as f:
			css = f.read()
			for dictName, key in values:
				css = css.replace(f"{{{key}}}", str(dictName[key]))
			app.setStyleSheet(sass.compile(string=css, output_style="compressed"))

		self.fontSizeChanged.emit()












	def closeEvent(self, e):
		DATA["appGeometry"] = {"rect": self.geometry().getRect() if not self.isMaximized() else DATA.get("appGeometry", {}).get("rect"), "max": self.isMaximized()}


		DATA.update(PREFS)
		DATA.update({k: v for k, v in COLOR.items() if k not in ("mid", "selected", "selected-inverted", "background-selection")})
		self.saveData()


	def saveData(self):
		with open("data.json", "w") as f:
			json.dump(DATA, f)






































if __name__ == "__main__":
	app = QApplication([])
	elem["app"] = app

	setFontConf()
	app.setWindowIcon(QIcon("resource/logo.ico"))
	app.setEffectEnabled(Qt.UIEffect.UI_AnimateMenu, False)


	if isWin:
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("fontview")



	main = Main()
	main.show()
	sys.exit(app.exec())