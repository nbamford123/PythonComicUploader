import sys
import os
from json import JSONDecodeError
import re
import shutil

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json

import markdownhelper
import githelper

os.environ["GIT_PYTHON_TRACE"] = "1"


class MainWindow(QDialog):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.comicSettings = {}

        self.setWindowTitle("Solar Salvage Comic Upload Tool")

        # setting geometry to the window
        self.setGeometry(100, 100, 300, 400)

        # creating a group box
        self.formGroupBox = QGroupBox()

        self.repoDirEdit = QLineEdit()
        self.repoDirEdit.textChanged.connect(self.set_repo_dir)

        self.comicDirEdit = QLineEdit()
        self.comicDirEdit.textChanged.connect(self.set_comic_dir)

        self.comicFileEdit = QLineEdit()
        self.comicFileEdit.textChanged.connect(self.set_comic_file)

        self.chapterEdit = QSpinBox()
        self.chapterEdit.valueChanged.connect(self.set_chapter)

        self.pageEdit = QSpinBox()
        self.pageEdit.setMaximum(999)
        self.pageEdit.valueChanged.connect(self.set_page)

        self.noteEdit = QPlainTextEdit()
        self.noteEdit.textChanged.connect(self.set_note)

        self.datePostedEdit = QDateEdit()
        self.datePostedEdit.dateChanged.connect(self.set_post_date)

        # set the date posted to current date
        self.datePostedEdit.setDate(QDate().currentDate())
        self.previewLabel = QLabel()
        self.statusLabel = QLabel()

        self.create_form()

        mainLayout = QVBoxLayout()

        mainLayout.addWidget(self.formGroupBox)

        self.setLayout(mainLayout)

        self.read_config()

    def create_form(self):

        # create form layout
        layout = QFormLayout()
        UILayout = QHBoxLayout()

        repoDirLayout = QHBoxLayout()
        repoDirBtn = QPushButton()
        repoDirBtn.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        repoDirBtn.clicked.connect(self.get_repo_dir)
        repoDirLayout.addWidget(self.repoDirEdit)
        repoDirLayout.addWidget(repoDirBtn)

        comicDirLayout = QHBoxLayout()
        comicDirBtn = QPushButton()
        comicDirBtn.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        comicDirBtn.clicked.connect(self.get_comic_dir)
        comicDirLayout.addWidget(self.comicDirEdit)
        comicDirLayout.addWidget(comicDirBtn)

        comicFileLayout = QHBoxLayout()
        comicFileBtn = QPushButton()
        comicFileBtn.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        comicFileBtn.clicked.connect(self.get_comic_file)
        comicFileLayout.addWidget(self.comicFileEdit)
        comicFileLayout.addWidget(comicFileBtn)

        linkLabel = QLabel(
            "Note accepts Markdown (<a href='https://www.markdownguide.org/cheat-sheet'>https://www.markdownguide.org/cheat-sheet</a>)")
        linkLabel.setOpenExternalLinks(True)
        linkLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        # adding rows
        # comic base dir
        layout.addRow(QLabel('Repo base dir:'), repoDirLayout)
        layout.addRow(QLabel('(ex: C:/Users/natha/solar-salvage)'))
        layout.addRow(QLabel('Comic staging dir:'), comicDirLayout)
        layout.addRow(QLabel('(ex: C:/Users/natha/solar-salvage/comics/01 The Pilot)'))
        layout.addRow(QLabel('Comic file:'), comicFileLayout)
        layout.addRow(QLabel('ex: 01-012.jpg'))
        layout.addRow(QLabel('Chapter:'), self.chapterEdit)
        layout.addRow(QLabel('Page:'), self.pageEdit)
        layout.addRow(QLabel('Note:'), self.noteEdit)
        layout.addRow(linkLabel)
        layout.addRow(QLabel('Posted:'), self.datePostedEdit)
        layout.addRow(QLabel('note: posted dates in the future will not be published until then'))

        stagingButton = QPushButton()
        stagingButton.setText("Stage")
        stagingButton.clicked.connect(self.perform_staging)
        layout.addRow('Stage comic page:', stagingButton)

        mergeButton = QPushButton()
        mergeButton.setText("Publish changes")
        mergeButton.clicked.connect(self.perform_merge)
        layout.addRow('Publish all changes:', mergeButton)

        UILayout.addLayout(layout)
        previewLayout = QVBoxLayout()
        previewLayout.addWidget(self.previewLabel)
        previewLayout.addWidget(self.statusLabel)
        UILayout.addLayout(previewLayout)

        # set the layout
        self.formGroupBox.setLayout(UILayout)

    def perform_merge(self):
        githelper.publish_comic(self.comicSettings['repo_dir'], self.comicSettings['chapter'], self.comicSettings['page'])

    def perform_staging(self):
        self.statusLabel.setText('')
        markdownhelper.write_markdown(self.comicSettings)
        shutil.copy(self.comicSettings['comic_file'],
                    os.path.join(self.comicSettings['gatsby_dir'], os.path.basename(self.comicSettings['comic_file'])))
        self.statusLabel.setText(f"Staged comic page {self.comicSettings['chapter']}-{self.comicSettings['page']}")
        # Try to find and load the next sequential comic
        nextPage = self.comicSettings['page'] + 1
        nextComic = str(self.comicSettings['chapter']).rjust(2, '0') + \
                    '-' + str(nextPage).rjust(3, '0') + '.jpg'
        nextComicFile = os.path.join(os.path.dirname(self.comicSettings['comic_file']), nextComic)
        if os.path.exists(nextComicFile):
            self.noteEdit.setPlainText('')
            self.pageEdit.setValue(nextPage)
            self.comicFileEdit.setText(nextComicFile)

    def get_repo_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose Base Github Directory")
        if len(directory) > 0:
            self.repoDirEdit.setText(directory)

    def get_comic_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose Comic Github Directory")
        if len(directory) > 0:
            self.comicDirEdit.setText(directory)

    def get_comic_file(self):
        file = QFileDialog.getOpenFileName(self, "Choose Comic File", "", "Image files (*.jpg)")[0]
        if len(file) > 0:
            self.comicFileEdit.setText(file)
            # try to extract chapter and page from filename
            m = re.match("(\d+)-(\d+)", os.path.basename(file))
            if m:
                self.chapterEdit.setValue(int(m.group(1)))
                self.pageEdit.setValue(int(m.group(2)))

    def set_comic_preview(self, comicFile):
        pix = QPixmap()
        pix.load(comicFile)
        self.previewLabel.setPixmap(pix.scaledToHeight(450))

    def set_repo_dir(self):
        self.comicSettings["repo_dir"] = self.repoDirEdit.text()

    def set_comic_dir(self):
        self.comicSettings["gatsby_dir"] = self.comicDirEdit.text()

    def set_comic_file(self):
        comic_file = self.comicFileEdit.text()
        self.comicSettings["comic_file"] = comic_file
        self.set_comic_preview(comic_file)

    def set_note(self):
        self.comicSettings["note"] = self.noteEdit.toPlainText()

    def set_chapter(self):
        self.comicSettings["chapter"] = self.chapterEdit.value()

    def set_page(self):
        self.comicSettings["page"] = self.pageEdit.value()

    def set_post_date(self):
        self.comicSettings["posted_date"] = self.datePostedEdit.date().toString(Qt.ISODate)

    def write_config(self):
        mypath = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(mypath, 'w') as f:
            json.dump(self.comicSettings, f)

    def read_config(self):
        try:
            with open('config.json', 'r') as f:
                self.comicSettings = json.load(f)
                comicFile = self.comicSettings["comic_file"]
                directory = os.path.dirname(comicFile)
                if len(directory) > 0:
                    os.chdir(directory)
                    self.set_comic_preview(comicFile)

        except (FileNotFoundError, JSONDecodeError) as e:
            self.comicSettings = {
                "repo_dir": "",
                "gatsby_dir": "",
                "comic_file": "",
                "chapter": 0,
                "page": 0,
                "note": "",
                "posted_date": QDate.currentDate().toString(Qt.ISODate)
            }
        self.settings_to_controls()

    def settings_to_controls(self):
        self.repoDirEdit.setText(self.comicSettings["repo_dir"])
        self.comicDirEdit.setText(self.comicSettings["gatsby_dir"])
        self.comicFileEdit.setText(self.comicSettings["comic_file"])
        self.chapterEdit.setValue(self.comicSettings["chapter"])
        self.noteEdit.setPlainText(self.comicSettings["note"])
        self.pageEdit.setValue(self.comicSettings["page"])

    def closeEvent(self, event):
        self.write_config()


# main method
if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
