

from PyQt6.QtGui import QFontDatabase
import sys, json












try:
	with open("data.json", "r") as file:
		DATA = json.load(file)
except:
	DATA = {}

elem = {}
elem["platform"] = sys.platform








ICON = {
	"sidebar": "\uE000",
	"listLayout": "\uE001",
	"gridLayout": "\uE002",
	"settings": "\uE003",
	"sort": "\uE004",
	"features": "\uE006",

	"alignLeft": "\uE007",
	"alignMid": "\uE008",
	"alignRight": "\uE009",

	
	"dropdown": "\uE00B",
	"plus": "\uE00C",
	"minus": "\uE00D",
	"favorite": "\uE00E",
	"close": "\uE00F",

	"reset": "\uE012",
	"invert": "\uE013",

	"left": "\uE010",
	"right": "\uE011",
	"shown": "\uE00B",
	"hidden": "\uE00A",
}





SC_FACTOR = {
	"margin": 0.6,

	"rowHeight": 3.5,
	"rowWidth": 8,
	"rowMargin": 0.3,

	"sidebarMin": 12,
	"fontBoxSize": 20,
}






PARAM = {
	"iconsName": "fontview-icons",
	"titleHeight": 26

}


colorParam = {
	"foreground": "#2d2d2d",
	"background": "#f6f6f6",
	"border": "#c0c0c0",

}



prefParam = {
	"fontSize": 16,
	"rowFontSize": 40,

	"listLayout": True,
	"rowAlign": 1,

	"sort": ("nameLow", False),
	"preview": "The quick brown fox jumps over the lazy dog",
	"userPreviews": [],
	"previewSize": 40,

	"favorites": [],
	"collections": {},
	"folders": [],
	"features": [],
	"userFeatures": [],

	"showCollections": True,
	"showFolders": True,
}



PARAM.update(colorParam | prefParam)

COLOR = {key: DATA.get(key, PARAM[key]) for key in colorParam}
PREFS = {key: DATA.get(key, PARAM[key]) for key in prefParam}






def setFontConf():
	for key, val in [
	("font", QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()
	)]:
		PARAM[key] = val
		PREFS[key] = DATA.get(key, val)















