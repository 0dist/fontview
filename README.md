## Overview
Currently it can:
- View 1 font directory at a time
- Index only .ttf/.otf font files
- Basic text formatting
- Display font info and glyph data

To-do:
- Font collection managment
- View multiple directories
- Custom text previews
- Optimize font resizing
- Custom theme

Known issues:
- Sorts incorrectly by font weight on Linux



## How to run
```
git clone https://github.com/0dist/fontview
cd fontview
pip install -r requirements.txt
main.py
```


## Example
![example](https://github.com/0dist/fontview/blob/master/example.jpg)

## Credits
This app uses [PyQt-Frameless-Window
](https://github.com/zhiyiYo/PyQt-Frameless-Window) that replaces default Windows title bar