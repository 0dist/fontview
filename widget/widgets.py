

from main import *





















class SizeGrip(QLabel):
	def __init__(self, parent):
		super().__init__()
		self.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.setObjectName("size-grip")
		self.setCursor(Qt.CursorShape.SizeFDiagCursor)

		self.parent = parent
		self.mousePressEvent = lambda e: setattr(self, "startPos", e.pos())


	def mouseMoveEvent(self, e):
		if e.buttons() == Qt.MouseButton.LeftButton:
			delta = e.pos() - self.startPos
			rect = self.parent.geometry()

			rect.setBottomRight(rect.bottomRight() + delta)
			self.parent.setGeometry(rect)
	






class FramelessDialog(QDialog):
	def __init__(self, parent, menu):
		super().__init__(parent)
		self.setObjectName("frameless-dialog")
		self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
		self.installEventFilter(self)


		self.destroyed.connect(lambda: (setattr(menu, "canHide", True), menu.activateWindow()))



		wrapLayout = QGridLayout(contentsMargins=QMargins(1,1,1,1))
		wrapLayout.addWidget(frame := QFrame(),0,0)
		frame.setObjectName("dialog-frame")


		self.layout = QVBoxLayout(contentsMargins=QMargins(), spacing=0)

		self.addWidget = lambda w: self.layout.addWidget(w)
		self.addLayout = lambda l: self.layout.addLayout(l)
		self.setResizable = lambda: wrapLayout.addWidget(SizeGrip(self), 0,0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)



		frame.setLayout(self.layout)
		self.setLayout(wrapLayout)






	def eventFilter(self, obj, e):
		if e.type() == QEvent.Type.WindowDeactivate:
			self.deleteLater()
		return False
































class ColorPicker(FramelessDialog):
	def __init__(self, parent, color, keys, btns, menu):
		super().__init__(parent, menu)
		self.keys = keys
		self.btns = btns



		colors = QHBoxLayout()
		colors.setSpacing(0)
		colors.setContentsMargins(QMargins())

		self.colorWindow = QWidget()
		self.colorWindow.setFixedSize(QSize(255,255))
		self.colorWindow.paintEvent = self.paintWindow
		self.colorWindow.mouseMoveEvent = self.mouseColor
		self.colorWindow.mousePressEvent = self.mouseColor
		self.colorWindow.mouseReleaseEvent = self.setNewColor



		self.hueRange = QWidget()
		self.hueRange.setFixedWidth(PREFS["fontSize"])
		self.hueRange.paintEvent = self.paintHues
		self.hueRange.mouseMoveEvent = self.mouseHues
		self.hueRange.mousePressEvent = self.mouseHues
		self.hueRange.mouseReleaseEvent = self.setNewColor


		colors.addWidget(self.colorWindow)
		colors.addWidget(self.hueRange)





		self.colorName = QLineEdit()
		self.colorName.setStyleSheet(f"padding: {PARAM['margin']}; border-top: 1px solid {COLOR['background']}")
		self.colorName.contextMenuEvent = lambda e: None
		self.colorName.textEdited.connect(lambda text: (self.initColor(c), self.setNewColor()) if (c := QColor(text)).isValid() else None)
		self.colorName.setObjectName("input")



		self.addLayout(colors)
		self.addWidget(self.colorName)

		self.initColor(color)
		self.moveWidget()
		self.show()











	def moveWidget(self):
		btn = self.btns[0]
		pos = btn.mapToGlobal(QPoint()) + QPoint(-1, btn.sizeHint().height())
		self.move(pos)


	def initColor(self, color):
		self.color = QColor(color)
		self.hue = max(self.color.hueF(), 0)
		# 255 fixed width
		self.posColor = QPoint(self.color.saturation(), 255 - self.color.value())

		self.hueRange.repaint()
		self.colorWindow.repaint()




	def setNewColor(self, e=False):
		for key, btn in zip(self.keys, self.btns):
			COLOR[key] = (color := self.color.name())
			btn.setStyleSheet(f"background-color: {color}; color: {QColor(*[255 - i for i in QColor(COLOR[key]).getRgb()[:-1]]).name()};")
		elem["main"].updateStylesheet()









	def mouseColor(self, e):
		rect = self.colorWindow.rect()
		self.posColor = QPoint(
			max(0, min(e.pos().x(), rect.width())), 
			max(0, min(e.pos().y(), rect.height())))
		self.colorWindow.repaint()


	def mouseHues(self, e):
		height = self.hueRange.rect().height()
		self.hue = max(0, min(e.pos().y(), height)) / height

		self.hueRange.repaint()
		self.colorWindow.repaint()








	def paintHues(self, e):
		p = QPainter(self.hueRange)
		height = (rect := self.hueRange.rect()).height()

		hue = QLinearGradient(0,0, 0,height)
		deg = 30
		hues = int(360 / deg)

		color = QColor()
		for i in range(hues + 1):
			color.setHsvF((deg * i) / 360, 1, 1)
			hue.setColorAt(i / hues, color)
		p.fillRect(rect, hue)




		p.setPen(QPen(QColor("black"), 2))
		y = max(0, min(self.hue * height, height - 2)) + 1
		p.drawLine(QPointF(0, y), QPointF(rect.width(), y))

		p.setPen(QPen(QColor(COLOR["background"])))
		p.drawLine(rect.topLeft(), rect.bottomLeft())
		p.end()











	def paintWindow(self, e):
		p = QPainter(self.colorWindow)
		p.setRenderHint(QPainter.RenderHint.Antialiasing)
		height = (rect := self.colorWindow.rect()).height()


		self.color.setHsvF(self.hue, 1, 1)
		horiz = QLinearGradient(0,0, rect.width(),0)
		horiz.setColorAt(0, QColor("white"))
		horiz.setColorAt(1, self.color)

		vert = QLinearGradient(0,0, 0,height)
		vert.setColorAt(0, QColor("transparent"))
		vert.setColorAt(1, QColor("black"))


		p.fillRect(rect, horiz)
		p.fillRect(rect, vert)



		self.color.setHsvF(self.hue, self.posColor.x() / rect.width(), (height - self.posColor.y()) / height)
		invert = QColor(*[255 - i for i in self.color.getRgb()[:-1]])
		p.setPen(QPen(invert, 2))
		p.drawEllipse(self.posColor, 5, 5)
		p.end()




		self.colorName.setStyleSheet(f"background-color: {self.color.name()}; color: {invert.name()}; padding: {PARAM['margin']}; border-top: 1px solid {COLOR['background']}")
		self.colorName.setText(self.color.name())



























class FontView(FramelessDialog):
	def __init__(self, parent, keys, btns, menu):
		super().__init__(parent, menu)
		self.setResizable()

		self.menu = menu
		


		self.keys = keys
		self.btns = btns


		self.fontList = QListWidget()
		self.fontList.setObjectName("font-list")
		self.fontList.setUniformItemSizes(True)
		self.fontList.setWordWrap(True)
		self.fontList.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.fontList.itemClicked.connect(self.setNewFont)
		self.fontList.itemActivated.connect(self.setNewFont)


		search = LineEdit(placeholder=f"Search fonts")
		search.textEdited.connect(self.searchFonts)
		search.setObjectName("search-font")


		self.addWidget(search)
		self.addWidget(self.fontList)


		self.setSizes()
		self.show()
		threading.Thread(target=self.populateFonts).start()








	def setSizes(self):
		btn = self.btns[0]
		pos = btn.mapToGlobal(QPoint()) + QPoint(-1, btn.sizeHint().height())
		size = QSize(PREFS["fontSize"], PREFS["fontSize"]) * SC_FACTOR["fontBoxSize"]
		self.setGeometry(QRect(pos, size))





	def populateFonts(self):
		for i in QFontDatabase.families(QFontDatabase.WritingSystem.Any):
			(item := QListWidgetItem(i)).setFont(QFont(i))
			self.fontList.addItem(item)


	def searchFonts(self, text):
		text = text.casefold()
		for i in range(self.fontList.count()):
			(item := self.fontList.item(i)).setHidden(text not in item.text().casefold())




	def setNewFont(self, item):
		if (font := item.text()) != PREFS[self.keys[0]]:
			for key, btn in zip(self.keys, self.btns):
				PREFS[key] = font
				btn.setText(font)

		elem["main"].updateStylesheet()
		self.menu.setSizes()
		self.setSizes()


































class ContextMenu(QMenu):
	def __init__(self, parent):
		super().__init__(parent)
		self.setWindowFlags(self.windowFlags() | Qt.WindowType.NoDropShadowWindowHint)
		self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)


		self.layout = QVBoxLayout(contentsMargins=QMargins(1,1,1,1), spacing=1)
		self.setLayout(self.layout)
	



	def addRow(self, text, func):
		(row := QPushButton(text)).clicked.connect(lambda: (self.close(), func()))
		self.layout.addWidget(row)


































class Toast(QLabel):
	def __init__(self, parent):
		super().__init__(parent, objectName="toast")
		elem["toast"] = self	
		parent.installEventFilter(self)



		self.moveToCorner = lambda: self.move(self.parent().width() - self.width() - PARAM["margin"], PARAM["margin"] + PARAM["titleHeight"] if elem["platform"] == "win32" else 0)
		self.mouseReleaseEvent = lambda _: self.hide()
		elem["main"].fontSizeChanged.connect(self.showEvent)

		self.hideTimer = QTimer()
		self.hideTimer.setInterval(1000)
		self.hideTimer.setSingleShot(True)
		self.hideTimer.timeout.connect(self.hide)
		self.hide()






	def eventFilter(self, obj, e):
		if self.isVisible() and e.type() == QEvent.Type.Resize:
			self.moveToCorner()
		return False

	def showEvent(self, e=False):
		self.adjustSize()
		self.eventFilter(False, QEvent(QEvent.Type.Resize))



	def notify(self, text):
		self.setText(text)
		self.adjustSize()
		self.moveToCorner()
		self.raise_()
		self.show()

		self.hideTimer.start()



















class Tooltip(QLabel):
	def __init__(self, parent=None):
		super().__init__(parent)
		elem["tooltip"] = self
		self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.ToolTip)
		self.setObjectName("tooltip")



		self.hideTimer = QTimer()
		self.hideTimer.setInterval(500)
		self.hideTimer.setSingleShot(True)
		self.hideTimer.timeout.connect(self.hide)



	


	def update(self, text, widget=False, isAbove=False, isFont=False, isTimed=True):
		dpi = elem["app"].primaryScreen().logicalDotsPerInch()
		self.setText(text if not isFont else f"{text}px / {round(text * 72 / dpi, 2)}pt")


		if widget:
			panelPos = widget.mapToGlobal(QPoint())
			self.move(QCursor.pos().x(), panelPos.y() - (self.height() if isAbove else -widget.height()))
		else:
			self.move(QCursor.pos() + QPoint(0,PREFS["fontSize"]))

		self.adjustSize()
		self.show() if self.isHidden() else None
		if isTimed:
			self.hideTimer.start()
		

























class LineEdit(QLineEdit):
	def __init__(self, parent=None, objectName=None, placeholder=None):
		super().__init__(parent, contextMenuPolicy=Qt.ContextMenuPolicy.NoContextMenu)
		if objectName:
			self.setObjectName(objectName)
		self.placeholder = placeholder



	def paintEvent(self, e):
		super().paintEvent(e)

		if not self.text() and self.placeholder:
			(p := QPainter(self)).setPen(QColor(COLOR["mid"]))
			p.drawText(self.rect().translated(2 + PARAM["margin"],0), Qt.AlignmentFlag.AlignVCenter, self.placeholder)
			p.end()




















class CompoundWidget(QPushButton):
	def __init__(self, widgets, checked=False, objectName=None, checkable=True, acceptDrops=False):
		super().__init__(checkable=checkable, checked=checked, objectName=objectName, acceptDrops=acceptDrops)
		self.layout = QHBoxLayout(self, contentsMargins=QMargins(0,0,0,1), spacing=0)

		
		for n, i in enumerate(widgets):
			if not n:
				i.setStyleSheet("padding-right: 0px")
				i.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
				if isinstance(i, QLabel):
					i.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
			self.layout.addWidget(i)








	def dragEnterEvent(self, e):
		if e.mimeData().property("fonts"):
			e.accept()
			self.setStyleSheet(f"background-color: {COLOR['selected']}")
		else:
			e.ignore()


	def dragLeaveEvent(self, e):
		super().dragLeaveEvent(e)
		self.setStyleSheet("")

		

	def dropEvent(self, e):
		fonts = [i.data["name"] for i in e.mimeData().property("fonts")]
		if self.text() == "favorites":
			PREFS["favorites"] = list(set(PREFS["favorites"] + fonts))
		else:
			PREFS["collections"][self.text()] = list(set(PREFS["collections"][self.text()] + fonts))

		self.updateCount()
		self.setStyleSheet("")




















class FloatingInput(QLineEdit):
	def __init__(self, parent, btn, widgetItem, key, objectName=None, replace=False, background=False, text=False):
		super().__init__(parent, objectName=objectName,contextMenuPolicy=Qt.ContextMenuPolicy.NoContextMenu)
		self.setStyleSheet("margin-right: 1px;")


		widgetItem.inEdit = True
		self.widgetItem = widgetItem
		self.btn = btn
		self.key = key
		self.replace = replace
		self.editingFinished.connect(self.changeItem)

		if background:
			self.setStyleSheet(f"background-color: {COLOR['selected' if parent.isChecked() else 'background']}")
		if text:
			self.setText(text)
			self.selectAll()



		parent.installEventFilter(self)
		self.focusOutEvent = lambda _: self.deleteLater()
		self.updateGeometry()
		elem["main"].fontSizeChanged.connect(self.updateGeometry)

		self.show()
		self.setFocus()






	def updateGeometry(self):
		self.setGeometry(self.btn.geometry())

	def eventFilter(self, obj, e):
		if e.type() == QEvent.Type.Resize:
			self.updateGeometry()
		return False


	def changeItem(self):
		layout = self.widgetItem.layout
		textCase = (text := self.text().replace("\n", "")[:150]).casefold()

		if textCase and not any(layout.itemAt(i).widget().text().casefold() == textCase for i in range(layout.count() - 1)) and textCase not in ["all", "favorites"]:
			if not self.replace:
				if "collection" not in self.key:
					PREFS[self.key].append(text)
				else:
					PREFS[self.key][text] = []

				self.deleteLater()
				layout.insertWidget(layout.count() - 1, self.widgetItem.userRow(text)),

			else:
				# preserve order
				PREFS[self.key] = {(text if k == self.btn.text() else k): v for k, v in PREFS[self.key].items()}
				self.btn.setText(text)
				self.deleteLater()




	

	def keyPressEvent(self, e):
		if e.key() == Qt.Key.Key_Escape:
			self.deleteLater()
			self.widgetItem.inEdit = False
		else:
			super().keyPressEvent(e)

















class DropdownMenu(QDialog):
	rowClicked = pyqtSignal(str)
	rowRemoved = pyqtSignal(str)

	def __init__(self, parent, btn, rows, current, customRows=[], fixedWidth=False, canAdd=False, userRows=[], keepOpen=False, key=None):
		super().__init__(parent, objectName="dropdown")
		self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
		self.installEventFilter(self)

		self.canAdd = canAdd
		self.current = current
		self.currentWidget = QWidget()
		self.btn = btn
		self.fixedWidth = fixedWidth
		self.keepOpen = keepOpen
		self.key = key

		self.inEdit = False
		self.canHide = True




		wrap = QVBoxLayout(contentsMargins=QMargins(1,1,1,1), spacing=1)
		self.scroll = QScrollArea(self)
		self.scroll.setWidgetResizable(True)
		self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


		container = QWidget()
		container.resizeEvent = lambda e: self.adjustSize()

		self.layout = QVBoxLayout(container, contentsMargins=QMargins(), spacing=1)
		self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
		self.scroll.setWidget(container)
		wrap.addWidget(self.scroll)





		if not customRows:
			for i in rows + userRows:
				self.layout.addWidget(r := self.row(i) if i not in userRows else self.userRow(i))
				if i in current:
					self.currentWidget = r
		else:
			for i in customRows:
				self.layout.addWidget(i)


		if canAdd:
			self.layout.addWidget(add := QPushButton(ICON["plus"], objectName="icon-row"))
			add.clicked.connect(lambda: FloatingInput(container, add, self, key=key, objectName="preview-input"))



		self.setLayout(wrap)
		self.setSizes()
		self.show()
		if len(current) == 1:
			self.scroll.ensureWidgetVisible(self.currentWidget,0,0)













	def setSizes(self):
		# adjust last button's height
		if self.canAdd:
			self.layout.itemAt(self.layout.count() - 1).widget().setFixedHeight(self.layout.itemAt(0).widget().sizeHint().height())

		btnGlobal = self.btn.mapToGlobal(QPoint())
		parentGlobal = self.btn.parent().mapToGlobal(QPoint())
		pos = QPoint(btnGlobal.x() - 1, parentGlobal.y() + self.btn.parent().height())

		self.adjustSize()
		self.move(pos)


		





	def adjustSize(self):
		super().adjustSize()
		self.inEdit = False
		# 8 visible rows, 9 border pixels
		maxHeight = self.layout.itemAt(0).widget().sizeHint().height() * 8 + 9
		container = self.scroll.widget()
		canScroll = maxHeight < (contentHeight := container.sizeHint().height())

		self.scroll.verticalScrollBar().setEnabled(canScroll)
		self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn if canScroll else Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.setFixedHeight(maxHeight if canScroll else contentHeight + 2)




		maxWidth = 0
		for i in range(self.layout.count() - (1 if self.canAdd else 0)):
			widget = self.layout.itemAt(i).widget()
			if callable(widget.layout):
				maxWidth = max(maxWidth, widget.sizeHint().width())
			else:
				totalWidth = 0
				for i in range(widget.layout.count()):
					totalWidth += widget.layout.itemAt(i).widget().sizeHint().width()
				maxWidth = max(maxWidth, totalWidth)


		scrollWidth = self.scroll.verticalScrollBar().sizeHint().width()
		prefWidth = maxWidth + ((scrollWidth + 2) if canScroll else 0)




		if self.fixedWidth or self.btn.width() > prefWidth:
			btnWidth = self.btn.width() + 1
			self.setFixedWidth(btnWidth)
			container.setFixedWidth(btnWidth - ((scrollWidth + 3) if canScroll else 0))
		else:
			self.setFixedWidth(maxWidth + (scrollWidth + 2 if canScroll else 1))
			container.setFixedWidth(maxWidth - 1)
			
		





	def row(self, text):
		(row := QPushButton(
			text, 
			checkable=True, 
			checked=text in self.current, 
			objectName="dropdown-row"
		)).clicked.connect(lambda: (self.rowClicked.emit(self.sender().text()), self.deleteLater() if not self.keepOpen else None))

		return row





	def userRow(self, text):
		delete = QPushButton(ICON["close"], objectName="icon-button")
		delete.clicked.connect(lambda: (
			self.layout.removeWidget(row), 
			row.deleteLater(), 
			self.adjustSize(),
			PREFS[self.key].remove(text) if text in PREFS[self.key] else None,
			self.rowRemoved.emit(text)
			))


		row = CompoundWidget([r := self.row(text), delete], checked=r.isChecked())
		r.clicked.connect(lambda: row.setChecked(r.isChecked()))
		row.setObjectName("compound-row")
		row.text = lambda: text
		return row






	def eventFilter(self, obj, e):
		if e.type() == QEvent.Type.KeyPress:
			if e.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Enter, Qt.Key.Key_Return) and self.inEdit:
				return True

		if e.type() == QEvent.Type.WindowDeactivate and self.canHide:
			self.deleteLater()
		return False






