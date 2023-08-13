import sys
import os
from json import JSONDecodeError
import re
import shutil

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json

import markdown


# TO DO:
# 1. autoload chapter/page from comic file if matches regex
# 2. control ui + code to  back it: checkbox to upload, button to save. button to all pending files?


class MainWindow(QDialog):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.comicSettings = {}

        self.setWindowTitle("Gatsby Comic Upload Tool")

        # setting geometry to the window
        self.setGeometry(100, 100, 300, 400)

        # creating a group box
        self.formGroupBox = QGroupBox()

        self.comicDirEdit = QLineEdit()
        self.comicDirEdit.textChanged.connect(self.setcomicdir)

        self.comicFileEdit = QLineEdit()
        self.comicFileEdit.textChanged.connect(self.setcomicfile)

        self.chapterEdit = QSpinBox()
        self.chapterEdit.valueChanged.connect(self.setchapter)

        self.pageEdit = QSpinBox()
        self.pageEdit.setMaximum(999)
        self.pageEdit.valueChanged.connect(self.setpage)

        self.noteEdit = QPlainTextEdit()
        self.noteEdit.textChanged.connect(self.setnote)

        self.datePostedEdit = QDateEdit()
        self.datePostedEdit.dateChanged.connect(self.setpostdate)

        # set the date posted to current date
        self.datePostedEdit.setDate(QDate().currentDate())
        self.previewLabel = QLabel()

        self.createform()

        mainLayout = QVBoxLayout()

        mainLayout.addWidget(self.formGroupBox)

        self.setLayout(mainLayout)

        self.readconfig()

    def createform(self):

        # create form layout
        layout = QFormLayout()
        UILayout = QHBoxLayout()

        comicDirLayout = QHBoxLayout()
        comicDirBtn = QPushButton()
        comicDirBtn.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        comicDirBtn.clicked.connect(self.getcomicdir)
        comicDirLayout.addWidget(self.comicDirEdit)
        comicDirLayout.addWidget(comicDirBtn)

        comicFileLayout = QHBoxLayout()
        comicFileBtn = QPushButton()
        comicFileBtn.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        comicFileBtn.clicked.connect(self.getcomicfile)
        comicFileLayout.addWidget(self.comicFileEdit)
        comicFileLayout.addWidget(comicFileBtn)

        linkLabel = QLabel(
            "Note accepts Markdown (<a href='https://www.markdownguide.org/cheat-sheet'>https://www.markdownguide.org/cheat-sheet</a>)")
        linkLabel.setOpenExternalLinks(True)
        linkLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        # adding rows
        # comic base dir
        layout.addRow(QLabel('Staging dir:'), comicDirLayout)
        layout.addRow(QLabel('(ex: gatsby-comic/comics/01 The Pilot)'))
        layout.addRow(QLabel('Comic file:'), comicFileLayout)
        layout.addRow(QLabel('ex: 01-012.jpg'))
        layout.addRow(QLabel('Chapter:'), self.chapterEdit)
        layout.addRow(QLabel('Page:'), self.pageEdit)
        layout.addRow(QLabel('Note:'), self.noteEdit)
        layout.addRow(linkLabel)
        layout.addRow(QLabel('Posted:'), self.datePostedEdit)

        stagingButton = QPushButton()
        stagingButton.setText("Stage")
        stagingButton.clicked.connect(self.performstaging)
        layout.addRow('Stage comic page:', stagingButton)

        UILayout.addLayout(layout)
        UILayout.addWidget(self.previewLabel)

        # set the layout
        self.formGroupBox.setLayout(UILayout)

    def performstaging(self):
        markdown.write_markdown(self.comicSettings)
        shutil.copy(self.comicSettings['comicfile'],
                  os.path.join(self.comicSettings['gatsbydir'], os.path.basename(self.comicSettings['comicfile'])))
        # Try to find and load the next sequential comic
        nextPage = self.comicSettings['page'] + 1
        nextComic = str(self.comicSettings['chapter']).rjust(2, '0') + \
            '-' + str(nextPage).rjust(3, '0') + '.jpg'
        nextComicFile = os.path.join(os.path.dirname(self.comicSettings['comicfile']), nextComic)
        if os.path.exists(nextComicFile):
            self.noteEdit.setPlainText('')
            self.pageEdit.setValue(nextPage)
            self.comicFileEdit.setText(nextComicFile)

    def getcomicdir(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose Comic Github Directory")
        if len(directory) > 0:
            self.comicDirEdit.setText(directory)

    def getcomicfile(self):
        file = QFileDialog.getOpenFileName(self, "Choose Comic File", "", "Image files (*.jpg)")[0]
        if len(file) > 0:
            self.comicFileEdit.setText(file)
            # try to extract chapter and page from filename
            m = re.match("(\d+)-(\d+)", os.path.basename(file))
            if m:
                self.chapterEdit.setValue(int(m.group(1)))
                self.pageEdit.setValue(int(m.group(2)))


    def setcomicpreview(self, comicFile):
        pix = QPixmap()
        pix.load(comicFile)
        self.previewLabel.setPixmap(pix.scaledToHeight(450))

    def setcomicdir(self):
        self.comicSettings["gatsbydir"] = self.comicDirEdit.text()

    def setcomicfile(self):
        comicfile = self.comicFileEdit.text()
        self.comicSettings["comicfile"] = comicfile
        self.setcomicpreview(comicfile)

    def setnote(self):
        self.comicSettings["note"] = self.noteEdit.toPlainText()

    def setchapter(self):
        self.comicSettings["chapter"] = self.chapterEdit.value()

    def setpage(self):
        self.comicSettings["page"] = self.pageEdit.value()

    def setpostdate(self):
        self.comicSettings["postdate"] = self.datePostedEdit.date().toString(Qt.ISODate)

    def writeconfig(self):
        mypath = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(mypath, 'w') as f:
            json.dump(self.comicSettings, f)

    def readconfig(self):
        try:
            with open('config.json', 'r') as f:
                self.comicSettings = json.load(f)
                comicFile = self.comicSettings["comicfile"]
                directory = os.path.dirname(comicFile)
                if len(directory) > 0:
                    os.chdir(directory)
                    self.setcomicpreview(comicFile)

        except (FileNotFoundError, JSONDecodeError) as e:
            self.comicSettings = {
                "gatsbydir": "",
                "comicfile": "",
                "chapter": 0,
                "page": 0,
                "note": "",
                "posteddate": QDate.currentDate().toString(Qt.ISODate)
            }
        self.settingsToControls()

    def settingsToControls(self):
        self.comicDirEdit.setText(self.comicSettings["gatsbydir"])
        self.comicFileEdit.setText(self.comicSettings["comicfile"])
        self.chapterEdit.setValue(self.comicSettings["chapter"])
        self.noteEdit.setPlainText(self.comicSettings["note"])
        self.pageEdit.setValue(self.comicSettings["page"])

    def closeEvent(self, event):
        self.writeconfig()


# main method
if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
