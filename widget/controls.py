




from main import *















class Controls(QWidget):
	def __init__(self):
		super().__init__()
		elem["controls"] = self
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("controls")

		layout = QHBoxLayout(contentsMargins=QMargins(0,0,0,1), spacing=0)





		sidebar = QPushButton(ICON["sidebar"])
		sidebar.clicked.connect(lambda: (
			(side := elem["sidebar"]).setVisible(side.isHidden()),
			DATA.update(hideSidebar=side.isHidden()),
			))






		self.preview = LineEdit(PREFS["preview"], objectName="controls-input", placeholder="Set preview")
		self.preview.contextMenuEvent = lambda _: None


		updateTimer = QTimer(self)
		updateTimer.setSingleShot(True)
		updateTimer.setInterval(300)
		updateTimer.timeout.connect(lambda: elem["mainStack"].currentWidget().update() if "mainStack" in elem else None)


		self.preview.textChanged.connect(lambda text: (
			# (self.preview.blockSignals(True), self.preview.setText(PARAM["preview"]), self.preview.blockSignals(False)) if not text else None,
			PREFS.update(preview=text.replace("\n", "")[:150]),
			updateTimer.start()
			))


		initDrop = QPushButton(ICON["dropdown"], objectName="icon-button")
		initDrop.clicked.connect(self.changePreview)
		self.previewWrap = CompoundWidget([self.preview, initDrop], checkable=False)







		tip = elem["tooltip"]

		slider = QSlider(Qt.Orientation.Horizontal)
		slider.setObjectName("slider")
		slider.setRange(30, 100)
		slider.focusOutEvent = lambda _: tip.hide()
		slider.sliderReleased.connect(tip.hide)

		updateLayouts = lambda: [elem["mainStack"].widget(i).updateLayout() for i in range(elem["mainStack"].count())]


		slider.setValue(PREFS["rowFontSize"])
		slider.valueChanged.connect(lambda val: (
			PREFS.update(rowFontSize=val),
			updateLayouts(),
			tip.update(PREFS["rowFontSize"], widget=self, isFont=True)
		))







		self.search = LineEdit(objectName="controls-input", placeholder="Search fonts")
		elem["search"] = self.search
		self.search.textChanged.connect(lambda text: debounce.start())

		clearSearch = QPushButton(ICON["close"], objectName="icon-button")
		clearSearch.hide()
		clearSearch.clicked.connect(lambda: (self.search.clear(), clearSearch.hide()))
		self.searchWrap = CompoundWidget([self.search, clearSearch])

		debounce = QTimer(self)
		debounce.setSingleShot(True)
		debounce.setInterval(300)
		debounce.timeout.connect(lambda: (
			elem["mainStack"].currentWidget().searchItems(self.search.text()), 
			elem["mainStack"].widget(0).searchItems(text) if not (text := self.search.text()) else None,
			clearSearch.setVisible(bool(text))
			))






		layoutType = QPushButton()
		updateIcon = lambda: layoutType.setText(ICON["listLayout" if PREFS["listLayout"] else "gridLayout"])
		updateIcon()


		layoutType.clicked.connect(lambda: (
			PREFS.update(listLayout=not PREFS["listLayout"]),
			updateIcon(),
			updateLayouts()
			))







		alignVal = {1: ICON["alignLeft"], 4: ICON["alignMid"], 2: ICON["alignRight"]}

		align = QPushButton(alignVal[PREFS["rowAlign"]])
		align.clicked.connect(lambda: (
			PREFS.update(rowAlign=list(alignVal)[(list(alignVal).index(PREFS["rowAlign"]) + 1) % len(alignVal)]),

			align.setText(alignVal[PREFS["rowAlign"]]),
			elem["mainStack"].currentWidget().repaint()
			))








		self.sortValues = {
		"Name (A-Z)": ("nameLow", False), 
		"Name (Z-A)": ("nameLow", True), 
		"Family size (1-9)": ("familyLen", False), 
		"Family size (9-1)": ("familyLen", True)
		}

		self.sortBtn = QPushButton(ICON["sort"])
		self.sortBtn.clicked.connect(self.sortLayout)




		self.features = QPushButton(ICON["features"])
		self.features.clicked.connect(self.setFontFeature)


		self.settings = QPushButton(ICON["settings"])
		self.settings.clicked.connect(self.initSettings)
		self.settings.setStyleSheet("border: 0")




	


		for i in sidebar, self.previewWrap, slider,  self.searchWrap, layoutType, align, self.sortBtn, self.features, self.settings:
			i.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
			
			if i in (self.previewWrap, self.searchWrap, slider):
				layout.addWidget(i, stretch=3 if i != self.searchWrap else 2)
			else:
				i.setObjectName("icon-button")
				layout.addWidget(i, stretch=1)

		self.setLayout(layout)

























	def sortLayout(self):
		current = next(key for key, value in self.sortValues.items() if value == tuple(PREFS["sort"]))

		DropdownMenu(self, self.sortBtn, list(self.sortValues), [current]).rowClicked.connect(lambda val: (
			PREFS.update(sort=self.sortValues[val]),
			[elem["mainStack"].widget(i).scrollLayout.sort() for i in range(elem["mainStack"].count())]
			))






	def setFontFeature(self):
		features = ["liga", "kern", "smcp", "c2sc", "onum", "lnum", "tnum", "pnum", "frac", "sups", "subs", "dlig", "swsh", "ss01", "calt"]

		menu = DropdownMenu(self, self.features, features, PREFS["features"], canAdd=True, keepOpen=True, userRows=PREFS["userFeatures"], key="userFeatures")
		menu.rowClicked.connect(lambda val: (
			PREFS.update(features=list(set(PREFS["features"]) ^ {val})),
			[elem["mainStack"].widget(i).setFontFeatures() for i in range(elem["mainStack"].count())]
			))

		menu.rowRemoved.connect(lambda val: (
			PREFS.update(features=[i for i in PREFS["features"] if i != val]),
			[elem["mainStack"].widget(i).setFontFeatures() for i in range(elem["mainStack"].count())]
			))







	def changePreview(self):
		previews = [
		"The quick brown fox jumps over the lazy dog",
		"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
		"0123456789",
		"""!@#$%^&()+-={}[]|\\:;\"'<>,.?/~""",
		]


		DropdownMenu(self, self.previewWrap, previews, [PREFS["preview"]], fixedWidth=True, canAdd=True, userRows=PREFS["userPreviews"], key="userPreviews").rowClicked.connect(lambda val: (
			PREFS.update(preview=val),
			self.preview.setText(PREFS["preview"]),
			elem["mainStack"].currentWidget().update()
			))










	def initSettings(self):
		resetTheme = QPushButton(ICON["reset"], objectName="icon-button")
		resetTheme.clicked.connect(lambda: (
			COLOR.update({k: PARAM[k] for k in COLOR if k in PARAM}),
			[styleBtn(btn, key) for key, (btn, _) in colorElems.items()],
			elem["main"].updateStylesheet()
			))

		invertTheme = QPushButton(ICON["invert"], objectName="icon-button")
		invertTheme.clicked.connect(lambda: (self.setTheme(), [styleBtn(btn, key) for key, (btn, _) in colorElems.items()]))
		theme = CompoundWidget([QLabel("Theme"), invertTheme, resetTheme], objectName="compound-row", checkable=False)





		resetFont = QPushButton(ICON["reset"], objectName="icon-button")
		resetFont.clicked.connect(lambda: (
			PREFS.update(font=PARAM["font"]),
			fontLabel.setText(f"Font ({PREFS['font']})"),
			elem["main"].updateStylesheet(),
			menu.setSizes(),
			))


		fontLabel = QPushButton(f"Font ({PREFS['font']})", cursor=Qt.CursorShape.PointingHandCursor)
		fontLabel.clicked.connect(lambda: (
			FontView(self, ["font"], [font], menu),
			setattr(menu, "canHide", False)
			))

		font = CompoundWidget([fontLabel, resetFont], objectName="compound-row", checkable=False)




		colorElems = {key: (QPushButton(text, cursor=Qt.CursorShape.PointingHandCursor, objectName="color"), text) for key, text in [
			("foreground", "Text"), 
			("background", "Background"), 
			("border", "Border"), 
			]}

		styleBtn = lambda btn, key: btn.setStyleSheet(f"background-color: {COLOR[key]}; color: {QColor(*[255 - i for i in QColor(COLOR[key]).getRgb()[:-1]]).name()};")

		for key, (btn, text) in colorElems.items():
			styleBtn(btn, key)
			btn.clicked.connect(lambda _, btn=btn, key=key: (
				ColorPicker(self, COLOR[key], [key], [btn], menu),
				setattr(menu, "canHide", False)
				))




		menu = DropdownMenu(self, self.settings, [], [], customRows=[theme, font] + [btn for btn, _ in colorElems.values()], keepOpen=True)








	def setTheme(self):
		val = 10
		for key in [
			"foreground", 
			"background", 
			"border", 
			]:
			(color := QColor(COLOR[key])).setHsv(color.hue(), color.saturation(), (v := (255 - color.value())) + (val if v <= 255 - val else -val))

			COLOR[key] = color.name()
		elem["main"].updateStylesheet()






















