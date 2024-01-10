
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QSize, QRect, QUrl, QThread, QByteArray, QStringListModel, QFileInfo, QDir, QFile, QPoint, QRectF, QEvent, QItemSelectionModel, QDateTime, QFileDevice, QTimer
from PyQt6.QtGui import *

import sys, ctypes, os, re, json, decimal, math, shutil, sass, codecs, unicodedata, subprocess


from fontTools import ttLib
from qframelesswindow import *


element = {}

element["platform"] = sys.platform
base = FramelessWindow if element["platform"] == "win32" else QWidget








def openData():
    global DATA
    with open("data.json", "r") as file:
        DATA = json.load(file)

def initData():
    global DATA
    DATA = {}
    for key, value in [("fontSize", 25), ("fontPreview", "The quick brown fox jumps over a lazy dog."), ("align", 1), ("grid", False), ("sidebarWidth", 300), ("sidebarHide", False), ("favorites", []), ("previewSize", 25), ("darkMode", False)]:
        DATA[key] = value

try:
    openData()
except:
    initData()




PADD = 10


from widget.sidebar import *
from widget.controls import *
from widget.font_window import *










class Thread(QThread):
    def run(self):
        element["main"].getFontData()



class InitPath(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.raise_()
        self.setObjectName("init-button")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText("Select or Drop font directory")
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setAcceptDrops(True)

        self.thread = Thread()
        self.thread.finished.connect(self.finilizePath)
        parent.wrapGrid.addWidget(self, 1 if parent.isWindows() else 0, 0)

        self.clicked.connect(lambda: self.selectDir(QDir.toNativeSeparators(QFileDialog.getExistingDirectory(self, "Select font directory"))))
        self.dropEvent = lambda e: self.selectDir(self.url)


    def dragEnterEvent(self, e):
        urls = e.mimeData().urls()
        if len(urls) == 1:
            url = urls[0].toLocalFile()
            if os.path.isdir(url):
                self.url = QDir.toNativeSeparators(url)
                e.accept()

    def selectDir(self, path):
        if path:
            DATA["path"] = path
            self.thread.start()
            self.setCursor(Qt.CursorShape.WaitCursor)

    def finilizePath(self):
        element["main"].generateFonts()
        self.deleteLater()










class Main(base): 
    def __init__(self):
        super().__init__()
        element["main"] = self
        # all widgets recieve focus to ensure that the custom combobox is hidden when any element is clicked
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        QFontDatabase.addApplicationFont("resource/fontview-icons.ttf")
        self.resetMargins = lambda l: l.setContentsMargins(0,0,0,0)
        self.isWindows = lambda: element["platform"] == "win32"

        self.wrapGrid = QGridLayout()
        if self.isWindows():
            self.wrapGrid.setSpacing(0)
            self.wrapGrid.addWidget(self.titleBar, 0, 0)
            self.titleBar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        self.splitter = QHBoxLayout()
        self.splitter.setSpacing(0)


        fontWindowLayout = QVBoxLayout()
        fontWindowLayout.setSpacing(0)
        for i in [self.wrapGrid, fontWindowLayout]:
            self.resetMargins(i)





        self.mainStack = QStackedWidget()
        self.scroll = ScrollLayout(grid = DATA["grid"], glyph = False, info = False)
        self.mainStack.addWidget(self.scroll)


        for i in [Controls(), self.mainStack]:
            fontWindowLayout.addWidget(i)


        self.splitter.addLayout(fontWindowLayout)
        self.wrapGrid.addLayout(self.splitter, 1 if self.isWindows() else 0, 0)

        self.setLayout(self.wrapGrid)
        self.setWindowGeometry()
        [self.getFontData(), self.generateFonts()] if "path" in DATA else InitPath(self)




    def getFontData(self):
        fontData = []
        for root, dirs, files in os.walk(DATA["path"]):
            for f in files:
                path = QDir.toNativeSeparators(root + "/" + f)
                suffix = QFileInfo(path).suffix()
                if suffix in ["ttf", "otf"]:
                    try:
                        ttFont = ttLib.TTFont(path)
                        # skip variable fonts
                        if not "fvar" in ttFont:
                            nameTable = ttFont["name"]
                            family = nameTable.getDebugName(1)
                            fullName = nameTable.getDebugName(4)
                            typeface = nameTable.getDebugName(16) if nameTable.getDebugName(16) else family

                            glyph = ttFont.getGlyphSet()
                            width = glyph["a"].width if "a" in glyph else 0


                            # qt wont recognize a family with name length over 31 on windows 10
                            if len(family) > 29:
                                family = family[:29]
                                # copy original font -> rename temp font to a shorter name -> load temp font -> delete temp font
                                self.renameFontFamily(family, path)
                            else:
                                QFontDatabase.addApplicationFont(path)


                            rawFont = QRawFont(path, 0)
                            weight = 100 if "thin" in str(nameTable.getDebugName(17)).lower() else rawFont.weight()
                            italic = rawFont.style()


                            fontData.append({"family": family, "fullName": fullName, "typeface": typeface, "weight": weight, "italic": italic, "type": suffix, "width": width, "path": path}) if not "fvar" in ttFont else None
                            ttFont.close()

                    except Exception as e:
                        print(e)



        self.fontList = []
        for t in sorted({t["typeface"] for t in fontData}):
            fontFamily = [i for i in fontData if i["typeface"] == t]
            fontType = sorted({i["type"] for i in fontFamily}, reverse = True)
            # remove duplicates, (ttf from otf)
            [fontFamily.remove(i) for i in fontFamily if [i["fullName"] for i in fontFamily].count(i["fullName"]) > 1]
            fontFamily.sort(key = lambda x: (x["weight"], x["width"]))


            # find closest to regular weight (400)
            closest = lambda lst: min(lst, key = lambda i: abs(i["weight"] - 400))
            if not all([i["italic"].value for i in fontFamily]):
                # exclude italics
                regular = closest([i for i in fontFamily if not i["italic"].value])
            else:
                regular = closest(fontFamily)


            self.fontList.append({"typeface": t, "family": regular["family"], "fullName": regular["fullName"], "weight": regular["weight"], "italic": regular["italic"], "length": len(fontFamily), "types": fontType, "path": regular["path"], "fontFamily": fontFamily})



    def generateFonts(self):
        self.splitter.insertWidget(0, Sidebar(self.fontList))
        for i in self.fontList:
            row = TypefaceRow(data = i, family = False)
            self.scroll.addWidget(row)
     

    def renameFontFamily(self, familyNew, path):
        file = QFileInfo(path)
        dst = file.absolutePath() + "/" + file.completeBaseName() + ".tmp"
        shutil.copy2(path, dst)

        ttFont = ttLib.TTFont(dst)
        for i in ttFont["name"].names:
            if i.nameID == 1:
                i.string = familyNew

        ttFont.save(dst)
        with open(dst, "rb") as f:
            QFontDatabase.addApplicationFontFromData(f.read())
        os.remove(dst)



    def setWindowGeometry(self):
        try:
            self.restoreGeometry(QByteArray.fromBase64(DATA["windowGeometry"].encode()))
        except:
             self.resize(self.screen().availableGeometry().size() / 1.7)


    def saveData(self):
        with open("data.json", "w") as f:
            json.dump(DATA, f)

    def closeEvent(self, e):
        DATA["windowGeometry"] = bytearray(self.saveGeometry().toBase64()).decode("utf-8")
        element["sidebar"].tree.iterateTree(func = "save", parent = False) if "path" in DATA else None
        self.saveData()
        





















if __name__ == "__main__":
    app = QApplication([])
    element["app"] = app

    app.setWindowIcon(QIcon("resource/logo.ico"))
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("fontview") if element["platform"] == "win32" else None

    app.setStyleSheet(sass.compile(filename = "style.qss", output_style = "compressed"))
    main = Main()
    main.show()

    sys.exit(app.exec())