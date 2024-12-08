



from main import *












HEAD_TABLE = {
	"tableVersion",
	"fontRevision",
	"checkSumAdjustment",
	"magicNumber",
	"flags",
	"unitsPerEm",
	"created",
	"modified",
	"xMin",
	"yMin",
	"xMax",
	"yMax",
	"macStyle",
	"lowestRecPPEM",
	"fontDirectionHint",
	"indexToLocFormat",
	"glyphDataFormat",
}



NAME_TABLE = {
	0: "Copyright Notice",
	1: "Font Family",
	2: "Font Subfamily",
	3: "Unique Font Identifier",
	4: "Full Font Name",
	5: "Version",
	6: "PostScript Name",
	7: "Trademark",
	8: "Manufacturer Name",
	9: "Designer",
	10: "Description",
	11: "Vendor URL",
	12: "Designer URL",
	13: "License Description",
	14: "License Info URL",
	16: "Typographic Family",
	17: "Typographic Subfamily",
	18: "Compatible Full",
	19: "Sample Text",
	20: "PostScript CID Findfont Name",
	21: "WWS Family Name",
	22: "WWS Subfamily Name",
	23: "Light Background Pallete",
	24: "Dark Background Pallete",
	25: "Variations PostScript Name Prefix"
}



POST_TABLE = {
	"formatType",
	"italicAngle",
	"underlinePosition",
	"underlineThickness",
	"isFixedPitch",
	"minMemType42",
	"maxMemType42",
	"minMemType1",
	"maxMemType1",
}


HHEA_TABLE = {
	"tableVersion",
	"ascender",
	"descender",
	"lineGap",
	"advanceWidthMax",
	"minLeftSideBearing",
	"minRightSideBearing",
	"xMaxExtent",
	"caretSlopeRise",
	"caretSlopeRun",
	"caretOffset",
	"metricDataFormat",
	"numberOfHMetrics",
}




OS2_TABLE = {
	"version",
	"xAvgCharWidth",
	"usWeightClass",
	"usWidthClass",
	"fsType",
	"ySubscriptXSize",
	"ySubscriptYSize",
	"ySubscriptXOffset",
	"ySubscriptYOffset",
	"ySuperscriptXSize",
	"ySuperscriptYSize",
	"ySuperscriptXOffset",
	"ySuperscriptYOffset",
	"yStrikeoutSize",
	"yStrikeoutPosition",
	"sFamilyClass",
	"panose",
	"ulUnicodeRange1",
	"ulUnicodeRange2",
	"ulUnicodeRange3",
	"ulUnicodeRange4",
	"achVendID",
	"fsSelection",
	"usFirstCharIndex",
	"usLastCharIndex",
	"sTypoAscender",
	"sTypoDescender",
	"sTypoLineGap",
	"usWinAscent",
	"usWinDescent",
	"ulCodePageRange1",
	"ulCodePageRange2",
	"sxHeight",
	"sCapHeight",
	"usDefaultChar",
	"usBreakChar",
	"usMaxContext",
	"usLowerOpticalPointSize",
	"usUpperOpticalPointSize",
}






















class FlowLayout(QLayout):
	heightChanged = pyqtSignal(int)

	def __init__(self, parent, isList, isGlyph):
		super().__init__()
		self.setContentsMargins(QMargins())
		self.parent = parent
		self.itemList = []
		self.visibleItems = []

		self.baseHeight = 0
		self.isList = isList
		self.isGlyph = isGlyph





	def addItem(self, item):
		self.itemList.append(item)
		if item.widget().isLast:
			self.sort()
			self.parent.setFontFeatures()
		

	def sort(self):
		key, reverse = PREFS["sort"] if not self.isList else ("weight", False)
		self.itemList.sort(key=lambda i: i.widget().data[key], reverse=reverse)
		self.update()

	def count(self):
		return len(self.itemList)




	def itemAt(self, index):
		if index >= 0 and index < len(self.itemList):
			return self.itemList[index]


	def visibleAt(self, index):
		if index >= 0 and index < len(self.visibleItems):
			return self.visibleItems[index]

	def visibleIndex(self, widget):
		return next((i for i, item in enumerate(self.visibleItems) if item.widget() == widget), -1)




	def takeAt(self, index):
		if index >= 0 and index < len(self.itemList):
			return self.itemList.pop(index)

	def sizeHint(self):
		return self.minimumSize()

	def hasHeightForWidth(self):
		return True

	def minimumSize(self):
		return QSize(0,0)

	def heightForWidth(self, width):
		return self.baseHeight



	def setGeometry(self, rect):
		self.visibleItems = itemList = [item for item in self.itemList if not item.widget().isHidden()] if elem["search"].text() else self.itemList
		self.baseHeight = 0


		if itemList:
			baseWidth = rect.width()
			itemHeight = int(PREFS["rowFontSize"] * SC_FACTOR["rowHeight"])
			itemWidth = (int(PREFS["rowFontSize"] * SC_FACTOR["rowWidth"])) if not self.isGlyph else itemHeight
			x, y = rect.x(), rect.y()



			if (isGrid := not PREFS["listLayout"] and not self.isList or self.isGlyph):
				columns = max(1, round(baseWidth / itemWidth) if len(itemList) * itemWidth > baseWidth else len(itemList))
				width = (baseWidth + columns - 1) / columns


				for n, item in enumerate(itemList):
					# new row
					if x + width > baseWidth + columns:
						x = rect.x()
						y += itemHeight


					lastInRow = not (n + 1) % columns
					item.setGeometry(QRect(round(x), y, baseWidth - round(x) if lastInRow else round(width), itemHeight))
					x += width - 1

			else:
				for item in itemList:
					item.setGeometry(QRect(x, y, baseWidth, itemHeight))
					y += itemHeight




			self.baseHeight = y + (itemHeight if isGrid else 0)
		self.heightChanged.emit(self.baseHeight)





































class FontRow(QFrame):
	def __init__(self, fontData, isLast=True, isFamily=False, isGlyph=False):
		super().__init__()
		self.isLast = isLast
		self.isFamily = isFamily
		self.isGlyph = isGlyph


		name, data = fontData
		self.name = name
		self.data = {
		"name": name,
		"nameLow": name.lower(),
		"family": data["family"],
		"weight": data["weight"],
		"path": data["path"],
		"style": data["style"],
		}




		if not isFamily and not isGlyph:
			self.data.update({"folderPath": os.path.normpath(data["folderPath"])})

		if not isGlyph:
			if not isFamily:
				self.data.update({
				"fullName": data["fullName"],
				"type": sorted(i.lstrip(".") for i in data["type"]),
				"fontFamily": data["fontFamily"],
				"familyLen": len(data["fontFamily"])
				})

				self.styles = f"{self.data['familyLen']} style{'s' if self.data['familyLen'] != 1 else ''}"
				self.fontType = ", ".join(self.data["type"])
		else:
			self.data.update({
			"index": data["index"],
			"glyph": data["glyph"],
			})

			self.leaveEvent = lambda _: elem["tooltip"].hide()




		
		self.font = QFont(self.data["family"])
		self.font.setWeight(self.data["weight"])
		self.font.setStyle(self.data["style"])
		self.font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)










	def mousePressEvent(self, e):
		if e.buttons() == Qt.MouseButton.LeftButton:
			self.dragStartPos = e.pos()



	def mouseMoveEvent(self, e):
		if not self.isFamily and not self.isGlyph:
			if e.buttons() == Qt.MouseButton.LeftButton and (e.pos() - self.dragStartPos).manhattanLength() > QApplication.startDragDistance():

				scroll = elem["mainStack"].currentWidget()
				drag = QDrag(self)
				mimeData = QMimeData()

				if scroll.selected:
					mimeData.setProperty("fonts", scroll.selected)
				else:
					scroll.selected = [self]
					scroll.update()
					mimeData.setProperty("fonts", [self])


				drag.setMimeData(mimeData)
				drag.exec()
				self.dragStartPos = QPoint()
				scroll.selected = []
				scroll.update()








	def mouseReleaseEvent(self, e):
		if self.rect().contains(e.pos()) and e.button() == Qt.MouseButton.LeftButton:
			scroll = elem["mainStack"].currentWidget()
			main = not self.isFamily and not self.isGlyph


			if (key := elem["app"].keyboardModifiers()) and main:
				if key == Qt.KeyboardModifier.ControlModifier:
					scroll.selected = list(set(scroll.selected) ^ {self})
					scroll.lastSelected = self


				elif key == Qt.KeyboardModifier.ShiftModifier:
					layout = scroll.scrollLayout
					if (last := layout.visibleIndex(scroll.lastSelected)) >= 0:
						start, end = sorted([last, layout.visibleIndex(self)])
						scroll.selected = list(set(layout.visibleAt(i).widget() for i in range(start, end + 1)))


			else:
				if main and scroll.selected:
					scroll.selected = []
				else:
					if not self.isGlyph:
						if not self.isFamily:
							elem["mainStack"].addWidget(layout := FamilyWidget(self.data))
							elem["mainStack"].setCurrentWidget(layout)
					else:
						elem["app"].clipboard().setText(self.data["name"])
						elem["toast"].notify(f"Copied {self.data['name']} to clipboard")

			scroll.update()






	
	def event(self, e):
		if e.type() == QEvent.Type.ToolTip and self.isGlyph:
			elem["tooltip"].update(f"{self.data['glyph']} / u{ord(self.data['name']):04x}", isTimed=False)
		return super().event(e)











	def contextMenuEvent(self, e):
		if not self.isFamily and not self.isGlyph:
			menu = ContextMenu(self)

			currentText = (current := elem["sidebar"].btnGroup.checkedButton()).text()
			scroll = elem["mainStack"].currentWidget() 
			selected = elem["mainStack"].currentWidget().selected
			font = self.data["name"]
			fonts = {i.data["name"] for i in selected} if selected else {font}





			moveFont = lambda row, isCurrent: (
				[i.deleteLater() for i in (selected or [self]) if isCurrent],
				setattr(scroll, "selected", []) if selected else None,
				row.updateCount(),
				)

			menu.addRow(f"{'Remove from' if font in PREFS['favorites'] else 'Add to'} Favorites", lambda: (
				PREFS.update(favorites=list(set(PREFS["favorites"]) ^ fonts)),
				moveFont(elem["sidebar"].favFonts, current == elem["sidebar"].favFonts)
				))
	
			if currentText not in ["all", "favorites"] and not current.path:
				menu.addRow(f"Remove from {currentText}", lambda: (
					[PREFS["collections"][currentText].remove(i) for i in fonts],
					moveFont(current, True)
					))




			if len(elem["mainStack"].currentWidget().selected) < 2:
				menu.addRow("Reveal in folder", lambda: elem["sidebar"].revealFile(self.data["path"]))
			menu.exec(e.globalPos())

















































class FamilyInfo(QWidget):
	def __init__(self, parent, data):
		super().__init__(objectName="family-info")

		self.scrollLayout = layout = QVBoxLayout(contentsMargins=QMargins(), spacing=0)
		scroll = ScrollArea(boxLayout=True)




		font = ttLib.TTFont(data["path"])
		tables = {
		"name": NAME_TABLE,
		"head": HEAD_TABLE,
		"OS/2": OS2_TABLE,
		"hhea": HHEA_TABLE,
		"GSUB": "",
		"GPOS": "",
		"post": POST_TABLE,
		}

		addRow = lambda key, val: scroll.addWidget(QLabel(f"<b>{key}</b>: {val}", wordWrap=True, textInteractionFlags=Qt.TextInteractionFlag.TextSelectableByMouse, contextMenuPolicy=Qt.ContextMenuPolicy.NoContextMenu))
		nameLabels = []



		for table in tables:
			if table in font.keys():
				scroll.addWidget(l := QLabel(f"{table}", objectName="table-name", alignment=Qt.AlignmentFlag.AlignCenter))
				nameLabels.append(l)
				if scroll.scrollLayout.count() == 1:
					l.setStyleSheet("border-top: 0")
				tableAttrs = dir(font[table])
				

			
				if table == "name":
					nameIds = {}
					for record in font[table].names:
						if (nameID := record.nameID) in tables[table]:
							nameIds[nameID] = str(record)
					for i, val in nameIds.items():
						addRow(tables[table][i], val)



				elif table in ("head", "post", "hhea", "OS/2"):
					for key in tables[table]:
						if key in tableAttrs:

							value = getattr(font[table], key)
							if key in ["created", "modified"]:
								value = datetime(1904,1,1) + timedelta(seconds=value)
							addRow(key, value)



				if table in ["GSUB", "GPOS"]:
					layoutTable = font[table].table

					scripts = ", ".join(sorted(set(s.ScriptTag for s in layoutTable.ScriptList.ScriptRecord)))
					features = ", ".join(sorted(set(f.FeatureTag for f in layoutTable.FeatureList.FeatureRecord)))
					
					addRow(f"{table} scripts", scripts)
					addRow(f"{table} features", features)



	




		tableWrap = QWidget(objectName="table-names")
		tableLayout = QHBoxLayout(tableWrap, contentsMargins=QMargins(0,1,0,0), spacing=0)

		for i in sorted(set(font.keys()) & tables.keys(), key=lambda x: list(tables).index(x)):

			tableLayout.addWidget(btn := QPushButton(i, objectName="text-button"))
			btn.clicked.connect(lambda _, btn=btn: scroll.verticalScrollBar().setValue(next(l.pos().y() + (1 if tableLayout.indexOf(btn) else 0) for l in nameLabels if l.text() == self.sender().text())))
	
		btn.setStyleSheet("border: 0")




		layout.addWidget(scroll)
		layout.addWidget(tableWrap)
		self.setLayout(layout)
		font.close()



























class FamilyPreview(QWidget):
	def __init__(self, parent, data):
		super().__init__(parent)
		layout = QVBoxLayout(contentsMargins=QMargins(), spacing=0)

		prefsWrap = QWidget(objectName="preview-controls")
		self.scrollLayout = prefsLayout = QHBoxLayout(prefsWrap, contentsMargins=QMargins(), spacing=0)

		self.controls = parent




		self.textEdit = QTextEdit(contextMenuPolicy=Qt.ContextMenuPolicy.NoContextMenu)
		self.textEdit.setAcceptRichText(False)
		self.textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.textEdit.setPlainText(parent.previewData["text"])
		self.textEdit.moveCursor(QTextCursor.MoveOperation.End)
		self.textEdit.textChanged.connect(lambda: parent.previewData.update(text=self.textEdit.toPlainText()))






		self.font = QFont(data["family"])
		self.font.setWeight(data["weight"])
		self.font.setStyle(data["style"])
		self.font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)


		setFontSize = lambda val: (
			PREFS.update(previewSize=val),
			self.font.setPixelSize(val), 
			self.textEdit.setFont(self.font),
			)

		setLetterSpace = lambda val: (
			self.font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, val), 
			self.textEdit.setFont(self.font),
			parent.previewData.update(letSpace=val)
			)








		for label, nums, val, func in [
			("Font size", (10, 500), PREFS["previewSize"], setFontSize),
			("Line spacing", (-100, 200), parent.previewData["lineSpace"], self.setLineHeight),
			("Letter spacing", (-100, 200), parent.previewData["letSpace"], setLetterSpace),
			]:
			sliderWrap = QWidget()
			sliderLayout = QHBoxLayout(sliderWrap, contentsMargins=QMargins(), spacing=0)


			slider = QSlider(Qt.Orientation.Horizontal, objectName="slider")
			slider.setRange(*nums)
			slider.valueChanged.connect(lambda val, func=func: (func(val), elem["tooltip"].update(val, widget=sliderWrap, isAbove=True, isFont=True)))
			slider.setValue(val)



			sliderLayout.addWidget(QLabel(label))
			sliderLayout.addWidget(slider)
			prefsLayout.addWidget(sliderWrap)
		sliderWrap.setStyleSheet("border: 0")
		elem["tooltip"].hide()






		layout.addWidget(self.textEdit)
		layout.addWidget(prefsWrap)

		for i in (elems := parent.fontFeatures(data, self.setFontFeature)):
			layout.addWidget(i)
		self.setLayout(layout)


		self.canUpdate = False
		for i in self.findChildren(QPushButton):
			if i.text() in parent.previewData["feats"]:
				i.click()
		self.canUpdate = True
		setFontSize(PREFS["previewSize"])
		elem["main"].fontSizeChanged.connect(self.showEvent)









	def showEvent(self, e=False):
		self.textEdit.setTabStopDistance((m := PARAM["margin"]) * 4)
		self.textEdit.setFont(self.font)



	def setLineHeight(self, val):
		(format := QTextBlockFormat()).setLineHeight(0 + val, 4)
		cursor = QTextCursor(self.textEdit.document())
		cursor.select(QTextCursor.SelectionType.Document)
		cursor.mergeBlockFormat(format)

		self.controls.previewData["lineSpace"] = val



	def setFontFeature(self, feat):
		tag = QFont.Tag(feat.encode())
		self.font.setFeature(tag, 1) if not self.font.isFeatureSet(tag) else self.font.unsetFeature(tag)

		self.showEvent()
		if self.canUpdate:
			self.controls.previewData["feats"] = list(set(self.controls.previewData["feats"]) ^ {feat})
		self.textEdit.setFocus()






























class FamilyGlyphs(QWidget):
	def __init__(self, parent, data):
		super().__init__(parent)
		self.data = data
		layout = QVBoxLayout(contentsMargins=QMargins(), spacing=0)

		self.scrollLayout = (scroll := ScrollArea(isGlyph=True)).scrollLayout
		layout.addWidget(scroll)

		self.pageCount = 100
		self.page = 0





		font = ttLib.TTFont(data["path"])
		self.total = len(font.getGlyphOrder())

		self.charMap = {}
		for code, name in font.getBestCmap().items():
			self.charMap[code] = {"glyph": name, "index": str(font.getGlyphID(name))}
			
		font.close()





		nav = QWidget(objectName="glyph-controls")
		navLayout = QHBoxLayout(nav, contentsMargins=QMargins(), spacing=0)




		self.labelCount = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)

		left = QPushButton(f"{ICON['left']}{ICON['minus']}", objectName="icon-button") 
		left.clicked.connect(lambda: (
			setattr(self, "page", max(0, self.page - self.pageCount)),
			self.populateLayout()
			))


		right = QPushButton(f"{ICON['minus']}{ICON['right']}", objectName="icon-button")
		right.setStyleSheet("border: 0")
		right.clicked.connect(lambda: (
			setattr(self, "page", min(math.ceil(len(self.charMap) / self.pageCount) * self.pageCount - self.pageCount, self.page + self.pageCount)),
			self.populateLayout()
			))


		navLayout.addWidget(left, stretch=3)
		navLayout.addWidget(self.labelCount, stretch=1)
		navLayout.addWidget(right, stretch=3)



		layout.addWidget(nav)
		self.setLayout(layout)
		self.populateLayout()









	def populateLayout(self):
		while self.scrollLayout.count():
			self.scrollLayout.takeAt(0).widget().deleteLater()

		for i in list(self.charMap)[self.page : self.page + self.pageCount]:
			glyphData = self.charMap[i]
			self.data.update(index=glyphData["index"], glyph=glyphData["glyph"])
			self.scrollLayout.addWidget(FontRow((chr(i), self.data), isGlyph=True, isLast=False))


		self.labelCount.setText(f"{str(self.page // self.pageCount + 1)} / {math.ceil(len(self.charMap) / self.pageCount)} ({len(self.charMap)} / {self.total})")































class FamilyStyles(QWidget):
	def __init__(self, parent, data):
		super().__init__()
		self.data = data
		layout = QVBoxLayout(contentsMargins=QMargins(), spacing=0)


		self.scroll = ScrollArea(isList=True)
		self.scrollLayout = self.scroll.scrollLayout

		for n, i in enumerate(data["fontFamily"].items()):
			self.scroll.addWidget(FontRow(i, isFamily=True, isLast=n==len(data["fontFamily"]) - 1))	
		layout.addWidget(self.scroll)



		for i in parent.fontFeatures(data, self.setFontFeature):
			layout.addWidget(i)

		self.setLayout(layout)







	def setFontFeature(self, feat):
		for i in range(self.scrollLayout.count()):
			font = self.scrollLayout.itemAt(i).widget().font
			tag = QFont.Tag(feat.encode())

			font.setFeature(tag, 1) if not font.isFeatureSet(tag) else font.unsetFeature(tag)
		self.scroll.update()






















		

class FamilyControls(QWidget):
	def __init__(self, parent, familyStack, data):
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("family-controls")

		self.familyStack = familyStack
		self.familyData = data["fontFamily"]
		layout = QHBoxLayout(contentsMargins=QMargins(0,0,0,1), spacing=0)

		self.previewData = {"text": "Type here...", "lineSpace": 0, "letSpace": 0, "feats": []}







		back = QPushButton("Back")
		back.clicked.connect(lambda: (
			parent.deleteLater(),
			))


		styles = QPushButton("Styles")
		styles.clicked.connect(lambda: familyStack.setCurrentWidget(familyStack.widget(0)))
		# init styles
		familyStack.addWidget(FamilyStyles(self, data))




		dropBtns = []
		for label, cls in [("Glyphs", FamilyGlyphs), ("Preview", FamilyPreview), ("Info", FamilyInfo)]:
			drop = QPushButton(ICON["dropdown"], objectName="icon-button")
			drop.clicked.connect(lambda: self.initDropdown(self.sender().parent()))

			btn = CompoundWidget([QLabel(label, alignment=Qt.AlignmentFlag.AlignCenter), drop])
			btn.setProperty("current", data["fullName"])
			btn.setProperty("cls", cls)
			btn.clicked.connect(lambda _, btn=btn: self.addTab(btn))


			dropBtns.append(btn)
		btn.setStyleSheet("border: 0")




		btnGroup = QButtonGroup(self, exclusive=True)

		layout.addWidget(back, stretch=1)
		for i in (styles, *dropBtns):
			i.setCheckable(True)
			layout.addWidget(i, stretch=1)
			btnGroup.addButton(i)

		self.setLayout(layout)
		styles.click()
	











	def addTab(self, btn, fromDrop=False):
		index = btn.property("index")
		current = btn.property("current")
		cls = btn.property("cls")
		
		if not index or (fromDrop and not index):
			btn.setProperty("index", index := self.familyStack.count())
			self.familyStack.addWidget(cls(self, self.familyData[current]))
		elif fromDrop:
			self.familyStack.widget(index).deleteLater()
			self.familyStack.insertWidget(index, cls(self, self.familyData[current]))
		self.familyStack.setCurrentIndex(index)






	def initDropdown(self, btn):
		families = dict(sorted(self.familyData.items(), key=lambda i: i[1]["weight"]))

		DropdownMenu(self, btn, list(families), [btn.property("current")]).rowClicked.connect(lambda val: (
			btn.setProperty("current", val),
			self.addTab(btn, fromDrop=True),
			btn.setChecked(True)
			))








	def fontFeatures(self, data, func):
		feats, widgetRows = [], []
		font = ttLib.TTFont(data["path"])

		for table in {"GSUB", "GPOS"} & set(font.keys()):
		    if hasattr(font[table].table, "FeatureList") and font[table].table.FeatureList:
		        records = font[table].table.FeatureList.FeatureRecord
		        feats.extend(record.FeatureTag for record in records)
		font.close()




		if feats := sorted(set(feats)):
			total = len(feats)
			perRow = math.ceil(total / math.ceil(total / 10))

			
			for chunk in range(0, total, perRow):
				featWrap = QWidget(objectName="feature-wrap", acceptDrops=True)
				featLayout = QHBoxLayout(featWrap, contentsMargins=QMargins(0,1,0,0), spacing=0)
				

				for i in feats[chunk:chunk+perRow]:
					featLayout.addWidget(btn := QPushButton(i, checkable=True, objectName="text-button"))
					btn.clicked.connect(lambda: func(self.sender().text()))
				
				btn.setStyleSheet("border-right: 0")
				widgetRows.append(featWrap)
		return widgetRows
























class FamilyWidget(QWidget):
	def __init__(self, data):
		super().__init__()
		self.data = data
		self.scrollLayout = layout = QVBoxLayout(contentsMargins=QMargins(), spacing=0)
		layout.sort = lambda: None



		layout.addWidget(FamilyControls(self, familyStack := QStackedWidget(), data))
		layout.addWidget(familyStack)
		self.setLayout(layout)


		self.updateLayout = lambda: [familyStack.widget(i).scrollLayout.update() for i in range(familyStack.count())]
		self.searchItems = lambda text: familyStack.widget(0).scroll.searchItems(text)
		self.setFontFeatures = lambda : None





































class ScrollArea(QScrollArea):
	def __init__(self, isList=False, isGlyph=False, boxLayout=False):
		super().__init__()
		self.setObjectName("main-scroll")
		self.setWidgetResizable(True)
		self.setAcceptDrops(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.boxLayout = boxLayout
		self.isList = isList
		self.isGlyph = isGlyph


		self.scrollLayout = layout = FlowLayout(self, isList, isGlyph) if not boxLayout else QVBoxLayout(contentsMargins=QMargins(), spacing=0)
		layout.setAlignment(Qt.AlignmentFlag.AlignTop)
		if not boxLayout:
			layout.heightChanged.connect(self.keepViewport)
		self.addWidget = lambda w: layout.addWidget(w)
		self.updateLayout = layout.update



		container = QWidget(objectName="container")
		container.setLayout(layout)
		self.setWidget(container)




		self.selected = []
		self.lastSelected = None


		if not isList and not isGlyph:
			for seq, func in [
			(QKeySequence.StandardKey.SelectAll, lambda: setattr(self, "selected", [i.widget() for i in layout.visibleItems])),
			# (QKeySequence.StandardKey.Cancel, lambda: setattr(self, "selected", [])),
			]:
				QShortcut(seq, self, autoRepeat=False).activated.connect(lambda func=func: (func(), self.update()))












	def searchItems(self, text):
		text = text.casefold()
		layout = self.scrollLayout

		for i in range(layout.count()):
			(widget := layout.itemAt(i).widget()).setVisible(text in widget.data["nameLow"])
		layout.update()



	def keepViewport(self, newHeight):
		scrollBar = self.verticalScrollBar()
		viewportHeight = self.viewport().height()

		scrollRatio = scrollBar.value() / max(1, self.widget().height() - viewportHeight)
		scrollBar.setValue(int((newHeight - viewportHeight) * scrollRatio))
		self.widget().setFixedHeight(newHeight)




	def setFontFeatures(self):
		if not self.isList and not self.isGlyph:
			for i in range(self.scrollLayout.count()):
				font = self.scrollLayout.itemAt(i).widget().font
				font.clearFeatures()

				for feat in PREFS["features"]:
					if len(feat) == 4: 
						font.setFeature(QFont.Tag(feat.encode()), 1)
			self.update()






	def dragEnterEvent(self, e):
		urls = e.mimeData().urls()
		if len(urls) == 1 and os.path.isfile(path := urls[0].toLocalFile()) and path.lower().endswith((".ttf", ".otf")) and not self.isList and not self.isGlyph:
			e.accept()
		else:
			e.ignore()


	def dropEvent(self, e):
		path = e.mimeData().urls()[0].toLocalFile()

		self.fontThread = FontGatherer(os.path.dirname(path), filePaths=[path])
		self.fontThread.finished.connect(lambda data, path: self.initDropStack(data) if data else None)
		self.fontThread.start()



	def initDropStack(self, fontData):
		for name, data in fontData.items():
			data = {
			"path": data["path"],
			"fontFamily": data["fontFamily"],
			"fullName": data["fullName"]
			}

			elem["mainStack"].addWidget(layout := FamilyWidget(data))
			elem["mainStack"].setCurrentWidget(layout)









	def paintEvent(self, e):
		super().paintEvent(e)
		# return
		p = QPainter(self.viewport())
		scrollY = self.verticalScrollBar().value()
		p.translate(0, -scrollY)



		if (widget := self.widget().childAt(0, scrollY)) and not self.boxLayout:
			viewport = QRect(QPoint(0, scrollY), self.viewport().size())
			margin = int(PREFS["rowFontSize"] * SC_FACTOR["rowMargin"])
			fontSize = PREFS["rowFontSize"]

			infoMetric = p.fontMetrics()
			infoHeight = infoMetric.height()
			alignFlag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop

			(iconFont := QFont(PARAM["iconsName"])).setPixelSize(PREFS["fontSize"])
			textColor = QColor(COLOR["foreground"])
			iconWidth = QFontMetrics(iconFont).height() 
			borders = []




			i = self.scrollLayout.visibleIndex(widget)
			while (item := self.scrollLayout.visibleAt(i)) and (widget := item.widget()) and viewport.intersects((widget).geometry()):
				rect = widget.geometry().adjusted(margin, margin, -margin, 0)
				if widget in self.selected:
					p.fillRect(widget.geometry(), QColor(COLOR["selected"]))

				if (isFav := widget.data["name"] in PREFS["favorites"]):
					p.save()
					p.setPen(textColor)
					p.setFont(iconFont)
					p.drawText(rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight, ICON["favorite"])
					p.restore()





				# font info
				isGlyph = widget.isGlyph
				title = widget.data["name" if not isGlyph else "index"]
				p.setPen(textColor)
				p.drawText(rect, alignFlag, title)

				p.setPen(QColor(COLOR["mid"]))
				infoRect = rect.adjusted(infoMetric.horizontalAdvance(title) + margin * 2,0,(-iconWidth - margin) if isFav else 0,0)


				if not isGlyph:
					if not widget.isFamily:
						p.drawText(infoRect, alignFlag, widget.styles)

						infoRect = infoRect.adjusted(infoMetric.horizontalAdvance(widget.styles) + margin * 2,0,0,0)
						p.drawText(infoRect, alignFlag, widget.fontType)
					else:
						p.drawText(infoRect, alignFlag, str(widget.data["weight"]))
				rect.setTop(rect.y() + infoHeight)





				# main text
				(font := widget.font).setPixelSize(fontSize)
				p.save()
				p.setFont(font)
				p.setPen(textColor)
				

				text = widget.data["name"] if isGlyph else (PREFS["preview"] or title)
				metrics = p.fontMetrics()
				textRect = metrics.boundingRect(text)
				tightRect = metrics.tightBoundingRect(text)

				offset = abs(textRect.y() - tightRect.y())
				center = rect.center().y() - tightRect.height() // 2
				rect.setLeft(rect.left() - textRect.x())


				p.drawText(rect.x(), center - offset, rect.width(), rect.height(), (PREFS["rowAlign"] if not isGlyph else Qt.AlignmentFlag.AlignHCenter) | Qt.AlignmentFlag.AlignTop, text)





				# borders
				rect = widget.geometry()
				lastRow = rect.bottom() == self.widget().height() - 1 and self.widget().height() > self.viewport().height() - 1
				lastColumn = rect.right() == self.widget().rect().right()

				borders.extend(
					([QLine(rect.topRight(), rect.bottomRight())] if not lastColumn else []) + 
					([QLine(rect.bottomLeft(), rect.bottomRight())] if not lastRow else [])
				)
				p.restore()
				i += 1

			p.setPen(QColor(COLOR["border"]))
			p.drawLines(borders)
		p.end()








