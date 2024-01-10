




from main import *
from widget.font_window import *












class Controls(QWidget):
    def __init__(self):
        super().__init__()
        element["controls"] = self
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setObjectName("controls")
        self.setFixedHeight(40)

        layout = QHBoxLayout()
        layout.setSpacing(0)
        element["main"].resetMargins(layout)

        element["app"].setEffectEnabled(Qt.UIEffect.UI_AnimateTooltip, False)
        element["app"].setEffectEnabled(Qt.UIEffect.UI_AnimateMenu, False)



        toggleSide = QPushButton("\uE007")
        toggleSide.clicked.connect(lambda: self.toggleSidebar(toggleSide))


        self.slide = QSlider(Qt.Orientation.Horizontal)
        self.slide.setObjectName("slider")
        self.slide.setRange(4, 20)
        self.slide.setValue(round(DATA["fontSize"] / 5))
        self.slide.valueChanged.connect(self.resizeFonts)

        self.fontSize = QLabel()
        self.calcFontSize = lambda val: ""+str(val)+"px / "+str(round(val * 0.75, 2))+"pt"
        self.fontSize.setText(self.calcFontSize(DATA["fontSize"]))



        viewBtns = [("\uE008", False), ("\uE009", True)]
        view = QPushButton(viewBtns[0][0] if not DATA["grid"] else viewBtns[1][0])
        view.clicked.connect(lambda: self.loopValues(viewBtns, view, ""))


        # viewBtns = [listView := QPushButton("\uE008"), gridView := QPushButton("\uE009")]
        # for b, val in [(listView, False), (gridView, True)]:
        #     b.clicked.connect(lambda e, val=val: self.changeLayout(val))

        #     b.clicked.connect(lambda e, b=b: [i.setChecked(True) if b == i else i.setChecked(False) for i in viewBtns])


        previewWrap = ComboBox(parent = self, edit = True, tabName = False, tab = False)
        for i in ["The quick brown fox jumps over the lazy dog.", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", """!"#$%&'()*+,-./0123456789:;<=>?""", "¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿"]:
            previewWrap.addItem(data = i, text = i, default = True if DATA["fontPreview"] == i else False)



        # 1 = Qt.AlignmentFlag.AlignLeft, 2 = right
        alignBtns = [("\uE00A", 1), ("\uE00B", 4), ("\uE00C", 2)]
        alignment = QPushButton()
        # adjust pixel smoothness to apppear sharper
        alignment.setStyleSheet("font-size: 16px")
        [alignment.setText(i[0]) for i in alignBtns if DATA["align"] == i[1]]
        alignment.clicked.connect(lambda: self.loopValues(alignBtns, alignment, "align"))

        # for b, flag in [(left, 1), (center, 4), (right, 2)]:
        #     b.clicked.connect(lambda e, flag=flag: self.alignRows(flag))

            # b.clicked.connect(lambda e, b=b: [i.setChecked(True) if b == i else i.setChecked(False) for i in alignBtns])
            # [b.setCheckable(True), b.setChecked(True)] if DATA["align"] == flag else None


        self.search = QLineEdit()
        self.search.setObjectName("search")
        self.search.setPlaceholderText("Search fonts")
        self.search.textEdited.connect(self.searchItems)


        theme = QPushButton()
        self.setIconTheme = lambda: theme.setText("\uE013" if DATA["darkMode"] else "\uE014")
        self.setIconTheme()
        theme.clicked.connect(self.invertTheme)

    


        for i in [toggleSide, view, alignment, theme]:
            i.setObjectName("icon")
  
        for i in [toggleSide, previewWrap, self.slide, self.search, view, alignment, theme]:
            i.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
            layout.addWidget(i)
            layout.setStretchFactor(i, 1)

        layout.setStretchFactor(previewWrap, 6)
        self.setLayout(layout)




    def toggleSidebar(self, button):
        sidebar = element["sidebar"]
        if not sidebar.isHidden():
            sidebar.hide()
            DATA["sidebarHide"] = True
        else:
            sidebar.show()
            DATA["sidebarHide"] = False
        # remove hover state
        button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, False)



    def invertTheme(self):
        DATA["darkMode"] = True if not DATA["darkMode"] else False
        self.setIconTheme()
        with open("style.qss", "r+") as f:
            qss = f.read()
            f.seek(0) 
            f.truncate()

            for i in re.findall("\$(.*):.*(\#.*);", qss):
                c = QColor(i[1])
                h = c.hue()
                newc = QColor().fromHsl(h + 180 if h < 180 else h - 180, c.saturation(), 255 - c.lightness()).name()

                qss = re.sub(i[1], ""+newc+"", qss)

            f.write(qss)
            app = element["app"]
            app.setStyleSheet(sass.compile(string = qss, output_style = "compressed"))
            app.style().unpolish(app)



    def restoreStates(self):
        self.alignRows(DATA["align"])
        self.setPreviewText(DATA["fontPreview"])
        self.resizeFonts(round(DATA["fontSize"] / 5))
        self.changeLayout(DATA["grid"])

        self.search.setEnabled(True)

        # preserve search state when family is closed with "back" button
        if self.sender() and self.sender().isCheckable():
            self.search.clear()
            if not all([i.isVisible() for i in self.currentWidget().items]):
                self.searchItems("")



    def loopValues(self, btns, button, func):
        index = [n for n, i in enumerate(btns) if button.text() == i[0]][0]
        index = 0 if button.text() == btns[-1][0] else index + 1

        button.setText(btns[index][0])
        self.alignRows(btns[index][1]) if func == "align" else self.changeLayout(btns[index][1])



    def searchItems(self, text):
        scroll = self.currentWidget()
        name = "typeface" if not "family" in element else "fullName"
        for i in scroll.items:
            if not text.lower() in i.data[name].lower():
                scroll.layout.removeWidget(i)
                i.hide()
            else:
                scroll.layout.addWidget(i)
                i.show()


    def changeLayout(self, val):
        # family is "list" only
        if not "family" in element:
            flowLayout = self.currentWidget().layout
            flowLayout.grid = val
            flowLayout.update()
            DATA["grid"] = val


    def alignRows(self, flag):
        [i.label.setAlignment(flag | Qt.AlignmentFlag.AlignVCenter) for i in self.currentWidget().items]
        DATA["align"] = flag


    def resizeFonts(self, val):
        val = val * 5
        [i.setFontSize(val) for i in self.currentWidget().items]

        QToolTip.showText(QPoint(QCursor.pos().x(), QCursor.pos().y() + 10), self.calcFontSize(val)) if self.sender() == self.slide else None
        # self.fontSize.setText(self.calcFontSize(val))
        DATA["fontSize"] = val


    def setPreviewText(self, text):
        # remove new lines
        text = "".join(text.splitlines())
        [i.label.setText(text) if text else i.label.setText(i.data["typeface"]) for i in self.currentWidget().items]
        DATA["fontPreview"] = text



    def currentWidget(self):
        if "family" in element:
            scroll = element["family"].scroll
        else:
            scroll = element["main"].mainStack.currentWidget()
        return scroll





