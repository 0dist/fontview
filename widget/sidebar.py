



from main import *











class ContextMenu(QMenu):
	def __init__(self, parent, item):
		super().__init__()
		layout = QVBoxLayout()
		element["main"].resetMargins(layout)


		revealRow = QPushButton()
		revealRow.setObjectName("button")
		revealRow.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
		revealRow.clicked.connect(lambda: parent.revealFile(item.data(100)))
		revealLay = QHBoxLayout()

		icon = QLabel("\uE005")
		icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
		icon.setFont(QFont("fontview-icons"))

		revealLay.addWidget(icon)
		revealLay.addWidget(QLabel("Open in Folder"))
		revealRow.setLayout(revealLay)
		# label gets cuf off from full width
		revealRow.adjustSize()
		self.setObjectName("context")


		layout.addWidget(revealRow)
		self.setLayout(layout)








class TreeItem(QStandardItem):
	def __init__(self, text):
		super().__init__()
		self.setText(text)
		self.setEditable(False)
		self.setCheckable(False)


		font = QFont("fontview-icons, "+QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()+"")
		self.setFont(font)






class DelegateTree(QStyledItemDelegate):
	def __init__(self, parent):
		super().__init__()
		self.parent = parent
		self.root = self.parent.rootIndex()

	def initStyleOption(self, option, index):
		text = index.data(0)
		folder = index.data(120)
		if folder:
			icon = "\uE002\u0020" if self.parent.isExpanded(index) else "\uE001\u0020"
		else:
			icon = "\uE003\u0020" if index.data(110) == "ttf" else "\uE004\u0020"
		super().initStyleOption(option, index)

		i = 1
		while index.parent() != self.root:
			index = index.parent()
			i += 1
		i = i - 1 if folder else i

		option.text = "\u0020\u0020\u0020\u0020\u0020" * i + icon + text





class TreePath(QTreeView):
	def __init__(self, data):
		super().__init__()
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
		self.setObjectName("tree")

		self.setItemDelegate(DelegateTree(self))
		self.setIndentation(0)
		self.setHeaderHidden(True)
		self.setExpandsOnDoubleClick(False)
		self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

		model = QStandardItemModel()
		# rootModel = model.invisibleRootItem()
		self.setModel(model)

		

		dirList = []
		for root, dirs, files in os.walk(DATA["path"]):
			for d in dirs:
				path = QDir.toNativeSeparators(root + "/" + d)
				file = QFileInfo(path)
				item = TreeItem(file.completeBaseName())
				item.setData(path, 100)
				item.setData(True, 120) # if folder

				appendTo = model
				for i in dirList:
					if root == i.data(100):
						appendTo = i
						break
				appendTo.appendRow(item)
				dirList.append(item)

			for f in files:
				path = QDir.toNativeSeparators(root + "/" + f)
				suffix = QFileInfo(path).suffix()
				if suffix in ["ttf", "otf"]:
					try:
						ttFont = ttLib.TTFont(path)["name"]
						typeface = ttFont.getDebugName(16) if ttFont.getDebugName(16) else ttFont.getDebugName(1)

						file = QFileInfo(path)
						item = TreeItem(file.completeBaseName())
						for val, slot in [(path, 100), (suffix, 110), (typeface, 130)]:
							item.setData(val, slot)


						appendTo = model
						for i in dirList:
							if root == i.data(100):
								appendTo = i
								break
						appendTo.appendRow(item)
					except Exception as e:
						print(e)

		# restore tree state
		self.iterateTree(func = "", parent = False)



	def iterateTree(self, func, parent):
		model = self.model()
		parent = self.model().invisibleRootItem().index() if not parent else parent
		items = [parent]


		state = []
		typeface = []
		while items:
			parent = items.pop()
			for i in range(model.rowCount(parent)):
				item = model.index(i, 0, parent)
				if item.data(120):
					# "unique" id to track expanded folders
					created = QFileInfo(item.data(100)).birthTime().toMSecsSinceEpoch()
					if func == "save" and self.isExpanded(item):
						state.append(created)
					elif not func:
						try:
							self.expand(item) if created in DATA["treeState"] else None
						except:
							pass

				elif item.data(130):
					typeface.append(item.data(130))
				items.append(item)

		match func:
			case "save":
				DATA["treeState"] = state
			case "get":
				return set(typeface)





	def mouseReleaseEvent(self, e):
		item = self.indexAt(e.pos())
		if e.button() == Qt.MouseButton.LeftButton and item.data(120):
			self.expand(item) if not self.isExpanded(item) else self.collapse(item)


			sidebar = element["sidebar"]
			sidebar.clearWidgets()			
			element["treeWidget"] = scroll = ScrollLayout(grid = DATA["grid"], glyph = False, info = False)
			# assign which fonts are in the folder
			self.model().setData(item, self.iterateTree(func = "get", parent = item), 140) if not item.data(140) else None

			for i in sidebar.data:
				if i["typeface"] in item.data(140):
					row = TypefaceRow(data = i, family = False)
					scroll.addWidget(row)

			element["main"].mainStack.addWidget(scroll)
			element["main"].mainStack.setCurrentWidget(scroll)
			for i in [sidebar.total, sidebar.favorites]:
				i.setChecked(False)


		super().mouseReleaseEvent(e)



	def contextMenuEvent(self, context):
		item = self.indexAt(context.pos())
		if item.isValid():
			menu = ContextMenu(self, item)
			menu.exec(QCursor.pos())


	def revealFile(self, path):
		path = QDir.toNativeSeparators(path)
		match element["platform"]:
			case "win32":
				subprocess.Popen("explorer /select, "+path+"")
			case "darwin":
				try:
					subprocess.Popen(["open", "-R", path])
				except Exception as e:
					print(e)
					# open without selection
					subprocess.Popen(["open", os.path.dirname(path)])
			case "linux":
				try:
					subprocess.Popen(["xdg-open", "--select", path])
				except Exception as e:
					print(e)
					subprocess.Popen(["xdg-open", os.path.dirname(path)])



	# def mousePressEvent(self, e):
	# 	index = self.indexAt(e.pos())
	# 	if index.isValid() and self.visualRect(index).contains(e.pos()):
	# 		super().mousePressEvent(e)
	# 	else:
	# 		e.ignore()




















class Total(QPushButton):
	def __init__(self, data, text):
		super().__init__()
		self.setObjectName("sidebar-button")
		self.setCheckable(True)

		layout = QHBoxLayout()

		self.num = QLabel(str(len(data)))
		layout.addWidget(QLabel(text))
		layout.setContentsMargins(PADD,0,PADD,0)
		layout.addStretch(1)
		layout.addWidget(self.num)

		self.setLayout(layout)

	def updateCount(self, data):
		self.num.setText(str(len(data)))









class Sidebar(QWidget):
	def __init__(self, data):
		super().__init__()
		element["sidebar"] = self
		self.data = data
		self.clearFavorites()
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		# self.setAttribute(Qt.WidgetAttribute.WA_Hover)
		self.setObjectName("sidebar")
		self.installEventFilter(self)


		wrapGrid = QGridLayout()
		element["main"].resetMargins(wrapGrid)

		layout = QVBoxLayout()
		layout.setSpacing(0)
		wrapGrid.addLayout(layout,0,0)
		layout.setAlignment(Qt.AlignmentFlag.AlignTop)

		self.setFixedWidth(DATA["sidebarWidth"])
		self.hide() if DATA["sidebarHide"] else None



		self.total = Total(data, "All")
		self.favorites = Total(DATA["favorites"], "Favorites")
		self.total.clicked.connect(self.clickTotal)
		self.favorites.clicked.connect(self.clickFavorites)

		btns = [self.total, self.favorites]
		for b in btns:
			b.clicked.connect(lambda e, b=b: [i.setChecked(True) if b == i else i.setChecked(False) for i in btns])



		pathWrap = QPushButton()
		pathWrap.setObjectName("sidebar-elem")
		pathWrap.setCursor(Qt.CursorShape.PointingHandCursor)
		pathWrap.clicked.connect(lambda: self.changePath(QDir.toNativeSeparators(QFileDialog.getExistingDirectory(self, "Select font directory"))))

		pathLabel = QLabel(os.path.basename(DATA["path"]))
		icon = QPushButton("\uE006")
		icon.setObjectName("row-icon")

		pathLay = QHBoxLayout()
		pathLay.setContentsMargins(PADD,0,PADD,0)
		pathLay.addWidget(icon)
		pathLay.addWidget(pathLabel)
		pathLay.addStretch(1)

		pathWrap.setLayout(pathLay)




		self.tree = TreePath(data)
		self.width = self.width()

		grip = QWidget()
		grip.setCursor(Qt.CursorShape.SplitHCursor)
		grip.mouseMoveEvent = self.resizeSidebar
		grip.setFixedWidth(5)
		wrapGrid.addWidget(grip,0, 0, Qt.AlignmentFlag.AlignRight)
	

		for i in [self.total, self.favorites, pathWrap, self.tree]:
			layout.addWidget(i)

		# set as default
		self.total.click()
		self.setLayout(wrapGrid)




	def resizeSidebar(self, e):
		x = self.mapFromGlobal(QCursor.pos()).x()
		if 200 < x < 400:
			if self.isHidden():
				self.show()
				DATA["sidebarHide"] = False

			self.setFixedWidth(x)
			DATA["sidebarWidth"] = x

		if x < 50 and self.isVisible():
			DATA["sidebarHide"] = True
			self.hide()


	def clearFavorites(self):
		fontList = [i["typeface"] for i in self.data]
		for i in DATA["favorites"][:]:
			DATA["favorites"].remove(i) if not i in fontList else None



	def changePath(self, path):
		if path and path != DATA["path"]:
			DATA["path"] = path
			self.thread = Thread()
			self.thread.finished.connect(self.finilizePath)
			self.thread.start()

	def finilizePath(self):
		self.deleteLater()
		self.clearWidgets()

		for i in element["main"].scroll.items:
			i.deleteLater()
		element["main"].scroll.items = []
		element["main"].generateFonts()




	def clickTotal(self, e):
		mainStack = element["main"].mainStack
		if self.favorites.isChecked():
			mainStack.removeWidget(self.scroll)
			mainStack.setCurrentWidget(element["main"].scroll)
			self.restoreStates()

		elif "treeWidget" in element:
			self.removeTreeWidget(mainStack)
			element["controls"].restoreStates()
		self.tree.clearSelection()


	def clickFavorites(self, e):
		mainStack = element["main"].mainStack
		if self.total.isChecked():
			self.initFavorites(mainStack)

		elif "treeWidget" in element:
			self.removeTreeWidget(mainStack)
			self.initFavorites(mainStack)
		self.tree.clearSelection()


	def initFavorites(self, mainStack):
		self.scroll = ScrollLayout(grid = DATA["grid"], glyph = False, info = False)

		for i in self.data:
			if i["typeface"] in DATA["favorites"]:
				row = TypefaceRow(data = i, family = False)
				self.scroll.addWidget(row)

		mainStack.addWidget(self.scroll)
		mainStack.setCurrentWidget(self.scroll)
		self.restoreStates()



	def clearWidgets(self):
		element["controls"].search.setEnabled(True)
		element["controls"].search.clear()

		self.checkFamily()
		if "treeWidget" in element:
			self.removeTreeWidget(element["main"].mainStack)
		if self.favorites.isChecked():
			element["main"].mainStack.removeWidget(self.scroll)


	def removeTreeWidget(self, mainStack):
		self.checkFamily()
		element.pop("treeWidget")
		mainStack.removeWidget(mainStack.currentWidget())

	def checkFamily(self):
		element["family"].deleteFamily() if "family" in element else None

	def restoreStates(self):
		self.checkFamily()
		element["controls"].restoreStates()




	# def eventFilter(self, obj, e):
	# 	if e.type() == QEvent.Type.HoverMove:
	# 		if  e.position().x() > self.geometry().width() - 5:
	# 			self.setCursor(Qt.CursorShape.SplitHCursor)
	# 		else:
	# 			self.setCursor(Qt.CursorShape.ArrowCursor)

	# 	if e.type() == QEvent.Type.MouseMove and self.cursor().shape() == Qt.CursorShape.SplitHCursor:
	# 		x = round(e.position().x())
	# 		# min/max width
	# 		if 200 < x < 400:
	# 			self.setFixedWidth(x)
	# 			DATA["sidebarWidth"] = x

	# 	return False
