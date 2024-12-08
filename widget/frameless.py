



from main import *







from ctypes.wintypes import MSG, RECT
import win32api
import win32con
import win32gui















class Titlebar(QWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("titlebar")

		self.startDrag = False
		self.iconScale = 2.5





		btns = QHBoxLayout(contentsMargins=QMargins(PARAM["margin"],0,0,0), spacing=0)
		iconWidth = 15

		(icon := QLabel()).setPixmap(QApplication.windowIcon().pixmap(iconWidth, iconWidth))
		icon.setStyleSheet("padding: 0")
		btns.addWidget(icon)
		btns.addStretch()




		for btn, paint, func in [(QPushButton(), p, f) for p, f in [(self.paintMin, self.parent().showMinimized), (self.paintMax, self.mouseDoubleClickEvent), (self.paintClose, self.parent().close)]]:
			# button height as titlebar height
			btn.setFixedSize(44, PARAM["titleHeight"])
			btn.paintEvent = lambda e, btn=btn, paint=paint: paint(e, btn)

			btn.clicked.connect(lambda _, btn=btn, func=func: (func(), btn.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, False)))
			btns.addWidget(btn)



		self.setLayout(btns)
   





	def mouseDoubleClickEvent(self, e=False):
		if not e or e.buttons() == Qt.MouseButton.LeftButton:
			self.startDrag = False
			self.parent().showNormal() if self.parent().isMaximized() else self.parent().showMaximized()




	def mousePressEvent(self, e):
		self.startDrag = not self.parent().isMaximized() and e.buttons() == Qt.MouseButton.LeftButton

	def mouseMoveEvent(self, e):
		if self.startDrag:
			self.parent().windowHandle().startSystemMove()
			self.startDrag = False









	def paintMin(self, e, btn):
		p = QPainter(btn)
		rect = btn.rect()

		if btn.underMouse():
			p.save()
			p.fillRect(rect, QColor(COLOR["selected"]))
			p.setPen(QColor(COLOR["border"]))
			p.drawLine(rect.bottomLeft(), rect.bottomRight())
			p.restore()


		center = rect.center().y()
		width = int(rect.width() / self.iconScale)
		p.drawLine(QPoint(rect.left() + width, center), QPoint(rect.right() - width, center))
		p.end()








	def paintMax(self, e, btn):
		p = QPainter(btn)
		rect = btn.rect()
		background = COLOR["selected" if btn.underMouse() else "background"]
		p.fillRect(rect, QColor(background))
		p.save()
		p.setPen(QColor(COLOR["border"]))
		p.drawLine(rect.bottomLeft(), rect.bottomRight())
		p.restore()



		width = int(rect.width() / self.iconScale)
		norm = max = QRect(0,0, (width := (rect.right() - width) - (rect.left() + width)), width)
		norm.moveCenter(rect.center())



		adj = 2 if (isMax := self.parent().isMaximized()) else 0
		if isMax:
			p.drawRect(max.adjusted(adj,0,0,-adj))
			p.setBrush(QBrush(QColor(background), Qt.BrushStyle.SolidPattern))

		p.drawRect(norm.adjusted(0,adj,-adj,0))
		p.end()












	def paintClose(self, e, btn):
		p = QPainter(btn)
		rect = btn.rect().toRectF()

		if btn.underMouse():
			p.save()
			p.fillRect(rect, QColor(COLOR["selected"]))
			p.setPen(QColor(COLOR["border"]))
			p.drawLine(QPointF(0, rect.height() - 1), QPointF(rect.width(), rect.height() - 1))
			p.restore()




		width = rect.width() / self.iconScale
		bound = QRectF(0,0, (width := (rect.right() - width) - (rect.left() + width)), width)
		bound.moveCenter(rect.center())

		


		drawX = lambda: (p.drawLine(bound.topLeft(), bound.bottomRight()), p.drawLine(bound.topRight(), bound.bottomLeft()))
		drawX()

		# 60 alpha
		p.setPen(QPen(QColor(*p.pen().color().getRgb()[:-1], 60), 2))
		bound.adjust(1,1,-1,-1)
		drawX()
		p.end()


































class NCCALCSIZE_PARAMS(ctypes.Structure):
	_fields_ = [("rgrc", RECT * 3)]


class MARGINS(ctypes.Structure):
	_fields_ = [
		("cxLeftWidth",     ctypes.c_int),
		("cxRightWidth",    ctypes.c_int),
		("cyTopHeight",     ctypes.c_int),
		("cyBottomHeight",  ctypes.c_int),
	]





class Frameless(QWidget): 
	def __init__(self):
		super().__init__()
		self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinMaxButtonsHint)


		id = int(self.winId())
		win32gui.SetWindowLong(id, win32con.GWL_STYLE, win32gui.GetWindowLong(id, win32con.GWL_STYLE) | win32con.WS_CAPTION | win32con.WS_THICKFRAME)

		ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(id, ctypes.byref(MARGINS(-1,-1,-1,-1)))



		self.isMax = False
		self.prevGeom = self.geometry()
		self.isMaximized = lambda: self.isMax
	
		self.screen().virtualGeometryChanged.connect(lambda: self.setGeometry(self.screen().availableGeometry()) if self.isMax else None)





	def showMaximized(self):
		self.prevGeom = self.geometry()
		self.setGeometry(self.screen().availableGeometry())
		self.isMax = True

	def showNormal(self):
		self.setGeometry(self.prevGeom)
		self.isMax = False
		





	def nativeEvent(self, eType, msg):
		msg = MSG.from_address(msg.__int__())
		if msg.message == win32con.WM_NCHITTEST:
			pos = QCursor.pos()
			x, y = pos.x() - self.x(), pos.y() - self.y()
			w, h = self.width(), self.height()


			border = 5 if not self.isMaximized() else 0
			left = x < border
			right = x > w - border
			top = y < border
			bottom = y > h - border
			if left and top:
				return True, win32con.HTTOPLEFT
			elif right and bottom:
				return True, win32con.HTBOTTOMRIGHT
			elif right and top:
				return True, win32con.HTTOPRIGHT
			elif left and bottom:
				return True, win32con.HTBOTTOMLEFT
			elif top:
				return True, win32con.HTTOP
			elif bottom:
				return True, win32con.HTBOTTOM
			elif left:
				return True, win32con.HTLEFT
			elif right:
				return True, win32con.HTRIGHT




		elif msg.message == win32con.WM_NCCALCSIZE:	
			if msg.wParam:
				rect = ctypes.cast(msg.lParam, ctypes.POINTER(NCCALCSIZE_PARAMS)).contents.rgrc[0]
				rect.bottom += 1
			return True, 0


		return False, 0

