



from main import *

















class ItemScroll(QScrollArea):
	def __init__(self, parent, key, fixedHeight=True, acceptDrops=True):
		super().__init__(parent)
		self.setObjectName("item-scroll")
		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.key = key
		self.acceptDrops = acceptDrops

		self.layout = QVBoxLayout(contentsMargins=QMargins(), spacing=0)
		self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)





		for i in PREFS[key]:
			self.layout.addWidget(self.userRow(os.path.basename(i), path=i) if "folder" in key else self.userRow(i))

		self.addWidget = lambda text, path=None: self.layout.insertWidget(self.layout.count() - 1, self.userRow(text, path))
		self.initAddBtn = lambda: self.layout.addWidget(btn := QPushButton(ICON["plus"], objectName="icon-button")) or btn
	

	

		container = QWidget(objectName="sidebar-container")
		if fixedHeight:
			container.resizeEvent = lambda e: self.adjustHeight()
			elem["main"].fontSizeChanged.connect(self.adjustHeight)
		container.setLayout(self.layout)
		self.setWidget(container)


		






	def sizeHint(self):
		return QSize(super().sizeHint().width(), self.maximumHeight())

	def adjustHeight(self):
		self.layout.itemAt(self.layout.count() - 1).widget().setFixedHeight(self.layout.itemAt(0).widget().height())

		# 6 visible rows
		maxHeight = self.layout.itemAt(0).widget().sizeHint().height() * 6
		canScroll = maxHeight < (contentHeight := self.widget().sizeHint().height())
		self.setFixedHeight(maxHeight if canScroll else contentHeight)




	def userRow(self, text, path=None):
		(btn := QPushButton(text, checkable=True, checked=False))
		btn.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

		count = QLabel()



		row = CompoundWidget([btn, count], acceptDrops=self.acceptDrops, objectName="scroll-item")
		row.contextMenuEvent = lambda e: self.rowContext(e, row, btn)
		row.text = lambda: btn.text()
		row.scroll = self
		row.count = lambda: int(count.text())
		row.path = os.path.normpath(path) if path else path

		row.updateCount = lambda val=0: count.setText(str(len(PREFS[self.key][row.text()]) if "collection" in self.key else val))

		row.updateCount()

		self.parent().btnGroup.addButton(row)
		return row
























class CollectionScroll(ItemScroll):
	def __init__(self, parent):
		super().__init__(parent, "collections")
		
		add = self.initAddBtn()
		add.clicked.connect(lambda: FloatingInput(self.widget(), add, self, key="collections", objectName="collection-input"))


		if not PREFS["showCollections"]:
			self.hide()
		





	def rowContext(self, e, row, btn):
		menu = ContextMenu(self)

		menu.addRow("Rename", lambda: FloatingInput(row, btn, self, key="collections", objectName="collection-input", replace=True, background=True, text=row.text()))

		if row.count():
			menu.addRow("Clear", lambda: (
				PREFS["collections"].update({row.text(): []}),
				row.updateCount(),
				row.click() if self.parent().btnGroup.checkedButton() == row else None
				))
			menu.addRow("Purge fonts", lambda: self.parent().purgeFonts(row))

		menu.addRow("Delete", lambda: (
			self.layout.removeWidget(row), 
			row.deleteLater(), 
			self.parent().allFonts.click() if self.parent().btnGroup.checkedButton() == row else None,
			PREFS["collections"].pop(row.text(), None),
			self.adjustHeight()
			))
		menu.exec(e.globalPos())





	
















class FolderScroll(ItemScroll):
	def __init__(self, parent):
		super().__init__(parent, "folders", fixedHeight=False, acceptDrops=False)
		
		self.add = self.initAddBtn()
		self.add.clicked.connect(lambda: self.addFolder(path) if (path := QFileDialog.getExistingDirectory(self, "Add font directory")) else None)
		self.add.setAcceptDrops(True)


		self.add.dragEnterEvent = lambda e: self.dragFolderIn(e)
		self.add.dragLeaveEvent = lambda e: self.dragFolderOut(e)
		self.add.dropEvent = lambda e: self.dropFolder(e)

		if not PREFS["showFolders"]:
			self.hide()
		





	def addFolder(self, path):
		path = os.path.normpath(path)
		if path not in [self.layout.itemAt(i).widget().path for i in range(self.layout.count() - 1)]:
			self.addWidget(os.path.basename(path), path=path)
			PREFS["folders"].append(path)
			elem["main"].queueThread(path)



	def rowContext(self, e, row, btn):
		menu = ContextMenu(self)

		menu.addRow("Show in folder", lambda: self.parent().revealFile(row.path))

		menu.addRow("Delete", lambda: (
			self.layout.removeWidget(row), 
			row.deleteLater(), 
			self.parent().allFonts.click() if self.parent().btnGroup.checkedButton() == row else None,
			PREFS["folders"].remove(row.path),
			self.removeFolderFonts(row),
			self.parent().allFonts.updateCount(str(elem["mainStack"].widget(0).scrollLayout.count())),
			# self.adjustHeight()
			))
		menu.exec(e.globalPos())





	def removeFolderFonts(self, row):
		selected = elem["mainStack"].widget(0).selected

		for i in reversed(range((layout := elem["mainStack"].widget(0).scrollLayout).count())):
			if (w := layout.itemAt(i).widget()).data["folderPath"] == row.path:
					if w in selected:
						selected.remove(w)
					layout.removeWidget(w)
					w.deleteLater()










	def dragFolderIn(self, e):
		if all(os.path.isdir(url.toLocalFile()) for url in e.mimeData().urls()):
			e.accept()
			self.add.setStyleSheet(f"background-color: {COLOR['selected']}")
		else:
			e.ignore()


	def dragFolderOut(self, e):
		self.add.setStyleSheet("")

	def dropFolder(self, e):
		for i in e.mimeData().urls():
			self.addFolder(i.toLocalFile())
		self.add.setStyleSheet("")



























class Sidebar(QWidget):
	def __init__(self):
		super().__init__()
		elem["sidebar"] = self
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("sidebar")

		self.setFixedWidth(DATA.get("sidebarWidth", 300))
		if DATA.get("hideSidebar"):
			self.hide()


		self.wrapGrid = QGridLayout(contentsMargins=QMargins())
		layout = QVBoxLayout(contentsMargins=QMargins(0,0,1,0), spacing=0)
	




		self.btnGroup = QButtonGroup(self, exclusive=True)
		self.btnGroup.buttonClicked.connect(self.switchFontStack)


		totalCount = QLabel("0")
		self.allFonts = CompoundWidget([QLabel("<b>All</b>"), totalCount])
		self.allFonts.updateCount = lambda val: totalCount.setText(val)
		elem["main"].threadFinished.connect(lambda data, path: (
			self.allFonts.updateCount(str(elem["mainStack"].widget(0).scrollLayout.count())),
			current.click() if (current := self.btnGroup.checkedButton()) != self.allFonts else None,
			self.updateFolderCount(data, path),
			))


		favCount = QLabel()
		self.favFonts = CompoundWidget([QLabel("<b>Favorites</b>"), favCount], acceptDrops=True)
		self.favFonts.contextMenuEvent = lambda e: self.favContext(e, self.favFonts)
		self.favFonts.path = None
		self.favFonts.updateCount = lambda val=None: favCount.setText(val or str(len(PREFS["favorites"])))
		self.favFonts.count = lambda: int(favCount.text())
		self.favFonts.updateCount()


		for btn, text in ((self.allFonts, "all"), (self.favFonts, "favorites")):
			btn.setObjectName("sidebar-btn")
			btn.text = lambda text=text: text
			self.btnGroup.addButton(btn)
			layout.addWidget(btn)







		createIcon = lambda: (btn := QPushButton(objectName="icon-button")).setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) or btn
		updateIcon = lambda btn, key: btn.setText(ICON["shown" if PREFS[key] else "hidden"])
		toggleWidget = lambda widget, icon, key: (
			PREFS.update({key: not widget.isVisible()}),
			widget.show() if PREFS[key] else widget.hide(),
			updateIcon(icon, key)
			)


		collectionWrap = CollectionScroll(self)

		collectIcon = createIcon()
		collections = CompoundWidget([QLabel("<b>Collections</b>"), collectIcon], checkable=False, objectName="sidebar-btn")
		# collections.contextMenuEvent = lambda e: self.collectContext(e, collectionWrap)
		collections.clicked.connect(lambda: toggleWidget(collectionWrap, collectIcon, "showCollections"))

		updateIcon(collectIcon, "showCollections")







		self.folderWrap = FolderScroll(self)
		folderIcon = createIcon()

		folders = CompoundWidget([QLabel("<b>Folders</b>"), folderIcon], checkable=False, objectName="sidebar-btn")
		# applyBorder()
		folders.clicked.connect(lambda: toggleWidget(self.folderWrap, folderIcon, "showFolders"))

		updateIcon(folderIcon, "showFolders")





		layout.addWidget(collections)
		layout.addWidget(collectionWrap)
		layout.addWidget(folders, 0, Qt.AlignmentFlag.AlignTop)
		layout.addWidget(self.folderWrap)

		self.allFonts.setChecked(True)









		self.grip = grip = QWidget()
		grip.setMinimumWidth(4)
		grip.setCursor(Qt.CursorShape.SplitHCursor)
		grip.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

		grip.mouseMoveEvent = self.resizeSidebar



		self.wrapGrid.addLayout(layout,0,0)
		self.wrapGrid.addWidget(grip,0,0, Qt.AlignmentFlag.AlignRight)
	
		self.setLayout(self.wrapGrid)















	def favContext(self, e, row):
		menu = ContextMenu(self)

		if row.count():
			menu.addRow("Clear", lambda: (
				PREFS.update(favorites=[]),
				row.updateCount(),
				row.click() if self.btnGroup.checkedButton() == row else None,
				elem["mainStack"].currentWidget().update(),
				elem["mainStack"].widget(0).update()
				))

			menu.addRow("Purge fonts", lambda: self.purgeFonts(row, isFav=True))
		menu.exec(e.globalPos())



	def updateFolderCount(self, data, path):
		for i in range(self.folderWrap.layout.count() - 1):
			if (row := self.folderWrap.layout.itemAt(i).widget()).path == os.path.normpath(path):
				row.updateCount(str(len(data)))



	def purgeFonts(self, row, isFav=False):
		layout = elem["mainStack"].widget(0).scrollLayout
		names = [layout.itemAt(i).widget().data["name"] for i in range(layout.count())]
		data = PREFS["collections"][row.text()] if not isFav else PREFS["favorites"]
		purged = list(set(data) & set(names))


		if not isFav:
			PREFS["collections"][row.text()] = purged
		else:
			PREFS["favorites"] = purged
		row.updateCount(str(len(purged)))
		if self.btnGroup.checkedButton() == row:
			row.click()









	def switchFontStack(self, btn):
		stack = elem["mainStack"]
		for i in reversed(range(1, 3)):
			if (widget := stack.widget(i)):
				stack.removeWidget(widget)
				widget.deleteLater()


		if btn.text() != "all":
			scroll = ScrollArea()
			layout = stack.widget(0).scrollLayout
			if not btn.path:
				prefData = PREFS["collections"][btn.text()] if btn.text() != "favorites" else PREFS["favorites"]
			else:
				prefData = [btn.path]


			# no duplicates
			names = set()
			widgets = []
			for i in range(layout.count()):
				if (w := layout.itemAt(i).widget()).data["name" if not btn.path else "folderPath"] in prefData and w.data["name"] not in names:
						names.add(w.data["name"])
						widgets.append(w)

			for n, i in enumerate(widgets):
				row = FontRow((i.data["name"], i.data), isLast=n==len(widgets) - 1)
				scroll.addWidget(row)
				

			stack.addWidget(scroll)
			stack.setCurrentWidget(scroll)
		else:
			stack.setCurrentIndex(0)











	def revealFile(self, path):
		if (osName := elem["platform"]) == "win32":
			subprocess.Popen(f'explorer /select, "{path}"')
		elif osName == "darwin":
			try:
				subprocess.run(["open", "-R", path], check=True)
			except subprocess.CalledProcessError as e:
				print(e)
				# open without selection
				subprocess.run(["open", os.path.dirname(path)])
		elif osName == "linux":
			try:
				subprocess.run(["xdg-open", "--select", path], check=True)
			except subprocess.CalledProcessError as e:
				print(e)
				subprocess.run(["xdg-open", os.path.dirname(path)])






	def resizeSidebar(self, e):
		x = self.mapFromGlobal(e.globalPosition().toPoint()).x()
		self.hide() if x < PREFS["fontSize"] * 2 else self.show()

		minWidth = PREFS["fontSize"] * SC_FACTOR["sidebarMin"]
		self.setFixedWidth(int(x := max(minWidth, min(x, minWidth * 2))))
		DATA.update(sidebarWidth=x, hideSidebar=not self.isVisible())


















