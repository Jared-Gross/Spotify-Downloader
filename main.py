from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
from PyQt5 import uic, QtPrintSupport
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5 import QtCore, QtWidgets, QtPrintSupport, QtGui
import sys, os, json, spotdl

Data_JSON_Contents = {}
Data_JSON = 'settings.json'
download_to_directory = []
theme = []
always_on_top = []
class ConvertThread(QThread):  
    data_downloaded = pyqtSignal(object)
    def __init__(self, file):
        QThread.__init__(self)
        self.file = file
    def run(self):
        # j = self.file
        self.data_downloaded.emit(f'1/{len(self.file)} - Starting.')
        # time.sleep(1)
        print('Starting download')
        print(self.file)
class mainwindowUI(QMainWindow):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        super(mainwindowUI, self).__init__(parent)
        uic.loadUi('UI/mainwindo.ui', self)
        self.setWindowTitle('Spotify Downloader')
        self.set_theme()
        
        self.actionAbout = self.findChild(QAction, 'actionAbout_2')
        self.actionAbout.triggered.connect(self.open_about)
        self.actionAbout.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogInfoView')))

        self.show()
    def set_theme(self):
        if theme[0] == 0: 
            QApplication.setPalette(QApplication.palette())
        if theme[0] == 1: 
            app.setStyle("Fusion")
            palette = QPalette()
            gradient = QLinearGradient(0, 0, 0, 400)
            gradient.setColorAt(0.0, QColor(40, 40, 40))
            gradient.setColorAt(1.0, QColor(30, 30, 30))
            palette.setBrush(QPalette.Window, QBrush(gradient))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(30, 30, 30))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
    def open_about(self):
        self.about = aboutwindowUI()
        self.about.show()
    def start_conversion(self, files):
        self.threads = []
        converter = ConvertThread(files)
        converter.data_downloaded.connect(self.on_data_ready)
        self.threads.append(converter)
        converter.start()
    def on_data_ready(self, text):
        try:
            # self.lblState.setHidden(False)
            self.progressBar.setHidden(False)
            if not text == 'Finished!':
                if not text == '':
                    currentNum = text.split('/')
                    currentNum = int(currentNum[0])
                    maxnum = text.split('/')
                    maxnum = maxnum[1]
                    maxnum = maxnum.split(' - ')
                    maxnum = int(maxnum[0])
                    self.progressBar.setValue(currentNum)
                    self.progressBar.setMaximum(maxnum)
            self.progressBar.setFormat(' ' + text)
            if text == '': 
                self.progressBar.setHidden(True)
        except Exception as e:
            print(e)

class settingsUI(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('Music_Generator/settings.ui', self)
        self.Default = self.findChild(QRadioButton, 'radDefault')
        self.Default.toggled.connect(lambda:self.RadClicked(self.Default))
        self.Dark = self.findChild(QRadioButton, 'radDark')
        self.Dark.toggled.connect(lambda:self.RadClicked(self.Dark))

        self.btnApply = self.findChild(QPushButton, 'btnApply')
        self.btnApply.clicked.connect(self.close)
        
        self.Default.setChecked(True if theme == 0 else False)
        self.Dark.setChecked(True if theme == 1 else False)
    def RadClicked(self, state):
        temp_num = 0
        temp_path = download_to_directory[0]
        temp_appear_on_top = always_on_top[0]
        Data_JSON_Contents.pop(0)
        if self.Default.isChecked(): temp_num = 0
        else: temp_num = 1
        Data_JSON_Contents.append(
            {
                "Download Path": [temp_path],
                "Appear on top": [temp_appear_on_top],
                "Theme": [temp_num]
            })
        with open(Data_JSON, mode='w+', encoding='utf-8') as file: json.dump(Data_JSON_Contents, file, ensure_ascii=True, indent=4)
        load_data_file(always_on_top, download_to_directory, theme)
        if theme[0] == 0: 
            QApplication.setPalette(QApplication.palette())
        if theme[0] == 1: 
            app.setStyle("Fusion")
            palette = QPalette()
            gradient = QLinearGradient(0, 0, 0, 400)
            gradient.setColorAt(0.0, QColor(40, 40, 40))
            gradient.setColorAt(1.0, QColor(30, 30, 30))
            palette.setBrush(QPalette.Window, QBrush(gradient))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(30, 30, 30))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
    def closeEvent(self, event):
        self.mainMenu = mainwindowUI()
        self.mainMenu.show()
        self.close()
class aboutwindowUI(QDialog):
    def __init__(self, parent=None):
        super(aboutwindowUI, self).__init__(parent)
        uic.loadUi('JordanProgramListOrginizer/aboutwindow.ui', self)
        self.setWindowTitle("About")
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogInfoView')))
        self.icon = self.findChild(QLabel, 'lblIcon')
        self.icon.setFixedSize(128,128)
        pixmap = QPixmap('icon.png')
        myScaledPixmap = pixmap.scaled(self.icon.size(), Qt.KeepAspectRatio)
        self.icon.setPixmap(myScaledPixmap)
        self.lisenceText = self.findChild(QLabel,'label_2')
        with open('LICENSE.md', 'r') as f: self.lisenceText.setText(f.read())
        self.btnClose = self.findChild(QPushButton, 'btnClose')
        self.btnClose.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogCloseButton')))
        self.btnClose.clicked.connect(self.close)
        self.resize(750,450)
        self.show()
def load_data_file(*args):
    global Data_JSON_Contents
    for i, j in enumerate(args): j.clear()
    with open(Data_JSON) as file:
        Data_JSON_Contents = json.load(file)
        for info in Data_JSON_Contents:
            for appear_on_top in info['Appear on top']: always_on_top.append(appear_on_top)
            for direcotry in info['Download Path']: download_to_directory.append(direcotry)
            for the in info['Theme']: theme.append(the)
if __name__ == '__main__':
    # if images directory doesnt exist we create it
    if not os.path.exists('Downloads'): os.makedirs('Downloads')
    # if data.json file doesn't exist, we create it
    if not os.path.isfile(Data_JSON):
        path = os.path.dirname(os.path.abspath(__file__)) + '/Downloads'
        path = path.replace('\\', '/')
        with open(Data_JSON, 'w+') as f: f.write('[{"Appear on top":["False"],"Download Path":["' + path + '}"],"Theme":[0]}]')
    # Load data file
    load_data_file(always_on_top, download_to_directory, theme)
    # start GUI
    app = QApplication(sys.argv)
    window = mainwindowUI()
    sys.exit(app.exec_())
# url = 'https://open.spotify.com/track/2DGa7iaidT5s0qnINlwMjJ'

# if 'track' in url:
#     os.popen(f'spotdl --song {url}').read()
# elif 'playlist' in url:
#     os.popen(f'spotdl --playlist {url}').read()
#     # os.popen(f'spordl --list {filename}').read()