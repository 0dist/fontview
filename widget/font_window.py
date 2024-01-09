









from main import *






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
    15: "Reserved",
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










class FlowLayout(QLayout):
    def __init__(self, parent, grid, glyph):
        super().__init__()
        self.itemList = []
        self.parent = parent
        self.grid = grid
        self.glyph = glyph

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def sizeHint(self):
        return self.minimumSize()

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0))

    def minimumSize(self):
        size = QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margin, _, _, _ = self.getContentsMargins()

        size += QSize(2 * margin, 2 * margin)
        return size

    def setGeometry(self, rect):
        self.doLayout(rect)


    def doLayout(self, rect):
        rect = self.parent.rect()
        rectWidth = rect.width()
        itemWidth = 500 if not self.glyph else 100
        y = rect.y()
        x = height = 0
        # items per row
        div = round(rectWidth / itemWidth) if len(self.itemList) * itemWidth > rectWidth else len(self.itemList)
        div = div if div else 1


        for item in self.itemList:
            width = rectWidth if not self.grid else ((rectWidth + div - 2) / div)
            height = item.sizeHint().height() if not self.glyph else itemWidth
            nextX = x + width

            if nextX > rectWidth:
                x = 0
                nextX = x + width
                # -1 border pixel
                y = y + height - 1

            # if not x:
            #     element["app"].style().unpolish(element["app"])
            #     item.widget().setObjectName("first-item")
            # else:
            #     item.widget().setObjectName("item")
  

            item.setGeometry(QRect(round(x), y, round(width), height))
            # -1 border pixel
            x = nextX - 1

        return y + height


















class FamilyGlyphs(QWidget):
    def __init__(self, data):
        super().__init__()
        layout = QVBoxLayout()
        element["main"].resetMargins(layout)
        layout.setSpacing(0)


        self.glyphStack = QStackedWidget()
        self.page = 0


        arrows = QWidget()
        arrows.setObjectName("nav-arrows")
        arrows.setFixedHeight(40)
        arrowLayout = QHBoxLayout()
        arrowLayout.setSpacing(0)
        element["main"].resetMargins(arrowLayout)



        prev = QPushButton("\uE012\uE010")        
        prev.clicked.connect(lambda e: self.glyphStack.setCurrentIndex(self.glyphStack.currentIndex() - 1))
        forw = QPushButton("\uE010\uE011")
        forw.clicked.connect(self.nextPage)

        for i in [prev, forw]:
            i.setObjectName("nav-icon")
            arrowLayout.addWidget(i)
            i.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        arrows.setLayout(arrowLayout)


        self.font = QFont(data["family"])
        self.font.setWeight(data["weight"])
        self.font.setStyle(data["italic"])
        self.charMap = list(ttLib.TTFont(data["path"])["cmap"].getBestCmap().keys())

        # initiate first page
        forw.click()


        layout.addWidget(arrows)
        layout.addWidget(self.glyphStack)
        self.setLayout(layout)




    def increaseCount(self):
        self.page = self.page + 100
        return self.page

    def nextPage(self, e):
        nextIndex = self.glyphStack.currentIndex() + 1
        if self.page < len(self.charMap) and not self.glyphStack.widget(nextIndex):
            scroll = ScrollLayout(grid = True, glyph = True, info = False)

            for key in self.charMap[self.page : self.increaseCount()]:
                label = QLabel(chr(key))
                label.setStyleSheet("font-size: 50px")
                label.setFont(self.font)
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                label.setObjectName("item")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                scroll.addWidget(label)

            self.glyphStack.addWidget(scroll)
            self.glyphStack.setCurrentWidget(scroll)
        else:
            self.glyphStack.setCurrentIndex(nextIndex)













class FamilyInfo(QWidget):
    def __init__(self, data):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        layout = QVBoxLayout()
        element["main"].resetMargins(layout)

        scroll = ScrollLayout(grid = False, glyph = False, info = True)
        layout.addWidget(scroll)


        info = []
        [info.append({"name": NAME_TABLE[i.nameID], "value": str(i), "id": i.nameID}) for i in ttLib.TTFont(data["path"])["name"].names if str(i) and i.nameID < 26 and i.nameID not in [i["id"] for i in info]]
        info.sort(key = lambda x: x["id"])


        for i in info:
            row = QWidget()
            rowLayout = QHBoxLayout()

            for i in [name := QLabel(i["name"]), value := QLabel(i["value"])]:
                name.setFixedWidth(220)
                value.setWordWrap(True)
                i.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                rowLayout.addWidget(i)

            row.setLayout(rowLayout)
            scroll.addWidget(row)


        self.setLayout(layout)









class FamilyPreview(QTextEdit):
    def __init__(self, data):
        super().__init__()
        # self.installEventFilter(self)
        self.setAcceptRichText(False)
        self.setTabStopDistance(20)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.font = QFont(data["family"])
        self.setStyleSheet("QTextEdit{font-size: "+str(DATA["previewSize"])+"px;}")
        # self.font.setPointSizeF(DATA["previewSize"])
        self.font.setWeight(data["weight"])
        self.font.setStyle(data["italic"])
        self.setPlainText(element["family"].controls.familyPreview)

        self.textChanged.connect(lambda: self.changePreview())
        self.setFont(self.font)


    def changePreview(self):
        element["family"].controls.familyPreview = self.toPlainText()

    def eventFilter(self, obj, e):
        # if e.type() == QEvent.Type.KeyPress:
        #     element["app"].setCursorFlashTime(0)
        # elif e.type() == QEvent.Type.KeyRelease:
        #     element["app"].setCursorFlashTime(1060)

        if element["app"].queryKeyboardModifiers() == Qt.KeyboardModifier.ControlModifier and e.type() == QEvent.Type.Wheel:
            if e.angleDelta().y() > 0:
                DATA["previewSize"] += 1
            elif e.angleDelta().y() < 0 and DATA["previewSize"] > 10:
                DATA["previewSize"] -= 1
            self.resizeFont()

        return False


    def resizeFont(self):
        self.setStyleSheet("QTextEdit{font-size: "+str(DATA["previewSize"])+"px;}")


















class ComboBox(QPushButton):
    def __init__(self, parent, edit, tabName, tab):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        # if label is a qlineedit
        self.edit = edit
        main = element["main"]

        layout = QHBoxLayout()
        main.resetMargins(layout)
        layout.setSpacing(0)



        if not self.edit:
            self.initTab = lambda button, data: parent.initFamilyTab(button, tab(data), familyStack)
            familyStack = element["family"].familyStack
            data = element["family"].data

            label = QPushButton(tabName)
            label.clicked.connect(lambda: [familyStack.setCurrentIndex(label.property("tab")), parent.setCheckedState(self)] if label.property("tab") else [self.initTab(label, data), label.setProperty("current", self.items.currentItem().text()), parent.setCheckedState(self)])
        else:
            label = QLineEdit(DATA["fontPreview"])
            label.setObjectName("edit")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.textChanged.connect(parent.setPreviewText)


        openCombo = QPushButton("\uE00D")
        openCombo.setObjectName("dropdown-icon")
        openCombo.setFixedWidth(parent.height())
        openCombo.clicked.connect(self.showCombo)


        for i in [label, openCombo]:
            # expand to full width/height
            i.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Ignored)
            layout.addWidget(i)





        self.combo = QWidget(main)
        self.combo.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        comboWrap = QVBoxLayout()
        main.resetMargins(comboWrap)

        self.items = QListWidget()
        self.items.setObjectName("combo")
        self.items.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.items.itemActivated.connect(lambda row: self.selectRow(label, row))
        self.items.itemClicked.connect(lambda row: self.selectRow(label, row))
        comboWrap.addWidget(self.items)
        self.combo.setLayout(comboWrap)



        self.setLayout(layout)
        self.items.focusOutEvent = lambda e: self.hideCombo(openCombo)
        self.moveEvent = lambda e: self.combo.hide() if self.combo.isVisible() else None



    def showCombo(self):
        if not self.combo.isVisible():
            self.combo.raise_()
            self.combo.show()
            self.items.setFocus()
            self.resize()
        else:
            self.combo.hide()

    def hideCombo(self, openCombo):
        self.combo.hide() if not element["app"].widgetAt(QCursor.pos()) == openCombo else None


    def resize(self):
        elemPos = self.mapTo(element["main"], self.parent().pos()) if not self.edit else self.mapToParent(self.parent().pos())

        itemCount = self.items.count() if self.items.count() < 10 else 10
        # (+/-1) border pixel
        height = self.items.visualItemRect(self.items.currentItem()).height() * itemCount + 1

        comboRect = QRect(elemPos.x() - 1, elemPos.y() + self.height(), self.width() + 1, height)
        self.combo.setGeometry(comboRect)



    def addItem(self, data, text, default):
        item = QListWidgetItem(text)
        # random data slot
        item.setData(100, data)
        self.items.addItem(item)
        self.items.setCurrentItem(item) if default else None


    def selectRow(self, label, row):
        rowText = row.text()
        if not self.edit:
            if label.property("current") != rowText:
                self.parent().setCheckedState(self)
                label.setProperty("current", rowText)
                self.initTab(label, row.data(100))
                self.finishSelection(label)
        else:
            if label.text() != rowText:
                label.setText(rowText)
                self.finishSelection(label)

    def finishSelection(self, label):
        self.combo.hide()
        label.clearFocus()



















        

class FamilyControls(QWidget):
    def __init__(self, data, familyStack):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        # +1 border pixel
        self.setFixedHeight(41)
        self.setObjectName("family-controls")

        layout = QHBoxLayout()
        layout.setSpacing(0)
        element["main"].resetMargins(layout)


        back = QPushButton("Back")
        styles = QPushButton("Family")
        styles.clicked.connect(lambda: [familyStack.setCurrentIndex(0), self.setCheckedState(styles)])


        self.familyPreview = "Type here..."
        self.previewWrap = ComboBox(parent = self, edit = False, tabName = "Preview", tab = lambda data: FamilyPreview(data))
        self.glyphWrap = ComboBox(parent = self, edit = False, tabName = "Glyphs", tab = lambda data: FamilyGlyphs(data))
        self.infoWrap = ComboBox(parent = self, edit = False, tabName = "Info", tab = lambda data: FamilyInfo(data))

        for w in [self.glyphWrap, self.infoWrap, self.previewWrap]:
            for i in data["fontFamily"]:
                w.addItem(data = i, text = i["fullName"], default = True if i["fullName"] == data["fullName"] else False)



        self.btns = [back, styles, self.previewWrap, self.glyphWrap, self.infoWrap]
        for i in self.btns:
            layout.addWidget(i)
            i.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
            i.setObjectName("button")
            i.setCheckable(True)

        self.setLayout(layout)
        back.clicked.connect(lambda: [element["family"].deleteFamily(), element["controls"].restoreStates()])
        styles.setChecked(True)


    def setCheckedState(self, button):
        [i.setChecked(True) if button == i else i.setChecked(False) for i in self.btns]

    def initFamilyTab(self, button, layout, familyStack):
        tab = button.property("tab")
        if not tab:
            tab = familyStack.count()
            familyStack.addWidget(layout)
        else:
            familyStack.removeWidget(familyStack.widget(tab))
            familyStack.insertWidget(tab , layout)

        button.setProperty("tab", tab)
        familyStack.setCurrentWidget(layout)















class FamilyLayout(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        element["family"] = self
        layout = QVBoxLayout()
        element["main"].resetMargins(layout)
        layout.setSpacing(0)


        self.familyStack = QStackedWidget()
        self.scroll = ScrollLayout(grid = False, glyph = False, info = False)
        self.familyStack.addWidget(self.scroll)

        self.controls = FamilyControls(data, self.familyStack)


        layout.addWidget(self.controls)
        layout.addWidget(self.familyStack)

        self.setLayout(layout)



        for i in data["fontFamily"]:
            row = TypefaceRow(data = i, family = True)
            self.scroll.addWidget(row)



    def deleteFamily(self):
        self.deleteLater()
        element["main"].mainStack.removeWidget(self)
        element.pop("family")
        # the combo dropdowns are assigned to main widget, so they are not deleted when family is
        for i in [self.controls.previewWrap, self.controls.glyphWrap, self.controls.infoWrap]:
            i.combo.deleteLater()
















class TypefaceRow(QWidget):
    def __init__(self, data, family):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setObjectName("item")
        self.data = data

        self.calcHeight = lambda val: round(val * 3.5)
        self.setFixedHeight(self.calcHeight(DATA["fontSize"]))



        rowWrap = QVBoxLayout()
        rowWrap.setContentsMargins(PADD,PADD,0,0)
        rowWrap.setSpacing(0)


        self.label = QLabel(DATA["fontPreview"] if DATA["fontPreview"] else data["typeface"])
        self.label.setObjectName("label")

        self.font = QFont(data["family"])
        # self.font.setPointSizeF(round(DATA["fontSize"] * 0.75, 2))
        self.label.setStyleSheet("font-size: "+str(DATA["fontSize"])+"px;")
        self.font.setWeight(data["weight"])
        self.font.setStyle(data["italic"])
        self.label.setFont(self.font)
        self.label.setAlignment(DATA["align"] | Qt.AlignmentFlag.AlignVCenter)
        self.label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)


        infoWrap = QHBoxLayout()
        infoWrap.setSpacing(15)


        if not family:
            typeface = QLabel(data["typeface"])
            length = str(data["length"])
            length = QLabel(length + " styles" if int(length) > 1 else length + " style")
            types = QLabel(", ".join(data["types"]).upper())



            btns = QWidget()
            btns.hide()

            btnsLay = QHBoxLayout()
            btnsLay.setSpacing(15)
            btnsLay.setContentsMargins(0,0,15,0)
            btns.setLayout(btnsLay)
            btns.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

            addToFav = QPushButton()
            self.setFavText = lambda val: addToFav.setText(val) if addToFav.text() != val else None
            addToFav.clicked.connect(lambda: self.addToFavorites(addToFav))
            revealFile = QPushButton("\uE005")
            revealFile.clicked.connect(lambda: element["sidebar"].tree.revealFile(data["path"]))

            for i in [addToFav, revealFile]:
                i.setObjectName("row-icon")
                i.setCursor(Qt.CursorShape.PointingHandCursor)
                btnsLay.addWidget(i)

            self.leaveEvent = lambda e: btns.hide()
            self.enterEvent = lambda e: self.showButtons(btns)


            info = [typeface, length, types, btns]
            self.mouseReleaseEvent = self.showFamily
        else:
            fullName = QLabel(data["fullName"])
            info = [fullName]

        for i in info:
            infoWrap.addWidget(i)
            i.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        infoWrap.insertStretch(3 if len(info) > 1 else 1)



        rowWrap.addLayout(infoWrap)
        rowWrap.addWidget(self.label)
        self.setLayout(rowWrap)





    def showButtons(self, btns):
        self.setFavText("\uE00F") if self.data["typeface"] in DATA["favorites"] else self.setFavText("\uE00E")
        btns.show()


    def addToFavorites(self, button):
        typeface = self.data["typeface"]
        if not typeface in DATA["favorites"]:
            DATA["favorites"].append(typeface)
            self.setFavText("\uE00F")
        else:
            DATA["favorites"].remove(typeface)
            self.setFavText("\uE00E")
            [self.deleteLater(), element["controls"].currentWidget().items.remove(self)] if element["sidebar"].favorites.isChecked() else None
        element["sidebar"].favorites.updateCount(DATA["favorites"])



    def setFontSize(self, val):
        self.setFixedHeight(self.calcHeight(val))
        self.label.setStyleSheet("font-size: "+str(val)+"px;")


    def showFamily(self, e):
        if self.rect().contains(e.pos()) and e.button() == Qt.MouseButton.LeftButton:
            layout = FamilyLayout(self.data)
            element["main"].mainStack.addWidget(layout)
            element["main"].mainStack.setCurrentWidget(layout)
            element["controls"].search.setEnabled(False)
























class ScrollLayout(QScrollArea):
    def __init__(self, grid, glyph, info):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.items = []

        scrollInner = QWidget()
        scrollInner.setObjectName("scroll-base")
        self.layout = FlowLayout(scrollInner, grid, glyph) if not info else QVBoxLayout() 
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # self.layout.setContentsMargins(20,20,20,0)
        element["main"].resetMargins(self.layout)
        scrollInner.setLayout(self.layout)
        self.setWidget(scrollInner)



    def addWidget(self, item):
        self.layout.addWidget(item)
        self.items.append(item)

        


