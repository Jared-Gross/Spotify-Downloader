from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
from PyQt5 import uic, QtPrintSupport
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5 import QtCore, QtWidgets, QtPrintSupport, QtGui
import sys, os, json, spotdl, re, threading, subprocess
import time
Data_JSON_Contents = {}
Data_JSON = 'settings.json'
download_to_directory = []
theme = []
always_on_top = []
originalPalette = None

download_percentage = 0

file_calculate_percentage = ''

class CalculateThread(QThread):  
    calculate = pyqtSignal(int)
    def __init__(self, file):
        QThread.__init__(self)
        self.file = file
    def run(self):
        global download_percentage
        isRunning = True
        self.maxLen = None
        print(file_calculate_percentage)
        while True:
            if not file_calculate_percentage == '':
                if self.maxLen == None: self.maxLen = sum(1 for line in open(file_calculate_percentage))
                num_lines = sum(1 for line in open(file_calculate_percentage))
                download_percentage = (self.maxLen-num_lines) / self.maxLen*100
                self.calculate.emit(download_percentage)
                if num_lines == 0:
                    self.maxLen = None
                    isRunning = False
                    break
            time.sleep(0.1)
class DownloadThread(QThread):  
    data_downloaded = pyqtSignal(object)
    def __init__(self, url):
        QThread.__init__(self)
        self.url = url
    def run(self):
        global file_calculate_percentage
        self.data_downloaded.emit(f'Starting..')
        # time.sleep(1)
        url = self.url
        fileName = ''
        fileList = []
        if '/track/' in url:
            self.data_downloaded.emit(f' Downloading track...')
            os.popen(f'spotdl --folder "{download_to_directory[0]}" --song {url} --overwrite skip').read() # > test.txt'
        elif '/playlist/' in url:
            self.data_downloaded.emit(f'Getting all songs from playlist...')
            os.popen(f'spotdl --folder "{download_to_directory[0]}" --playlist {url} --overwrite skip').read()
            self.data_downloaded.emit(f'Downloading all songs from playlist....')
            for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
                if file.endswith(".txt"): fileList.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), file))
            fileName = fileList[0]
            file_calculate_percentage = fileName
            # threading.Thread(target=self.calculate_progress,args=(fileName,)).start()
            os.popen(f'spotdl --folder "{download_to_directory[0]}"  --list "{fileName}" --overwrite skip').read()
        elif '/album/' in url:
            self.data_downloaded.emit(f'Getting all songs from album...')
            os.popen(f'spotdl --folder "{download_to_directory[0]}" --album {url} --overwrite skip').read()
            self.data_downloaded.emit(f'Downloading all songs from album....')
            for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
                if file.endswith(".txt"): fileList.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), file))
            fileName = fileList[0]
            file_calculate_percentage = fileName
            # threading.Thread(target=self.calculate_progress,args=(fileName,)).start()
            os.popen(f'spotdl --folder "{download_to_directory[0]}"  --list "{fileName}" --overwrite skip').read()
        self.data_downloaded.emit('Finished Downloading!')
        time.sleep(1)
        self.data_downloaded.emit('')
        file_calculate_percentage = ''
        if not fileName == '': os.remove(fileName)
class mainwindowUI(QMainWindow):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        QApplication.setPalette(QApplication.palette())
        global originalPalette
        if originalPalette == None: originalPalette = QApplication.palette()
        super(mainwindowUI, self).__init__(parent)
        uic.loadUi('UI/mainwindo.ui', self)
        self.setStyleSheet(open("style.qss", "r").read())
        
        self.setWindowTitle('Spotify Downloader')
        self.setWindowIcon(QIcon('icon.png'))
        self.set_theme()
        
        self.txtURL = self.findChild(QLineEdit, 'url')
        self.txtURL.setToolTip('Provide a spotify link.')
        self.txtURL.textChanged.connect(self.verify_text)
        
        self.btnDownload = self.findChild(QPushButton,'btnDownload')
        self.btnDownload.clicked.connect(self.start_download)
        self.btnDownload.setToolTip('Downloads the link provided in the textbox.')
        
        self.btnCancel = self.findChild(QPushButton,'btnCancel')
        self.btnCancel.clicked.connect(self.cancel_download)
        self.btnCancel.setToolTip('Cancel downloads.')
        
        self.progressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setHidden(True)
        self.progressBar.setAlignment(QtCore.Qt.AlignLeft)
        self.progressBar.setMaximum(100)
        
        self.actionAbout = self.findChild(QAction, 'actionAbout_Spotify_Downloader')
        self.actionAbout.triggered.connect(self.open_about)
        self.actionAbout.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogInfoView')))

        self.actionDownload_location = self.findChild(QAction, 'actionDownload_location')
        self.actionDownload_location.triggered.connect(self.get_download_dir)
        self.actionDownload_location.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogNewFolder')))
        self.actionDownload_location.setStatusTip(f'Set default download location. {download_to_directory[0]}')
        
        self.actionOpen_Download_location = self.findChild(QAction,'actionOpen_Download_location')
        self.actionOpen_Download_location.triggered.connect(self.open_download_dir)
        self.actionOpen_Download_location.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DirOpenIcon')))
        self.actionOpen_Download_location.setStatusTip(f'Open default download location. {download_to_directory[0]}')

        self.actionAlways_appear_on_top = self.findChild(QAction, 'actionAlways_appear_on_top')
        self.actionAlways_appear_on_top.triggered.connect(self.set_appear_on_top)
        self.actionAlways_appear_on_top.setChecked(True if always_on_top[0] == 'True' else False)
        self.actionAlways_appear_on_top.setStatusTip('The program will appear always on top. (The program will restart)')

        if always_on_top[0] == 'True': self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.actionTheme = self.findChild(QAction, 'actionTheme')
        self.actionTheme.triggered.connect(self.open_theme)
        self.actionTheme.setStatusTip('Change from Dark mode to default mode.')
        self.btnDownload.setEnabled(False)
        self.btnCancel.setEnabled(False)
        self.btnCancel.setHidden(True)
        # self.btnDownload.setEnabled(False)
        self.show()
    def open_download_dir(self):
        FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
        # explorer would choke on forward slashes
        path = download_to_directory[0]
        path = path.replace('/', '\\')
        if os.path.isdir(path):
            subprocess.run([FILEBROWSER_PATH, path])
        elif os.path.isfile(path):
            subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])
    def verify_text(self):
        if not self.txtURL.text() == '': self.btnDownload.setEnabled(True)
        else: self.btnDownload.setEnabled(False)
    def get_download_dir(self):
        dir_ = QFileDialog.getExistingDirectory(None, 'Select a default download folder', 'C:\\', QFileDialog.ShowDirsOnly)
        if dir_:
            temp_num = theme[0]
            temp_appear_on_top = always_on_top[0]
            Data_JSON_Contents.pop(0)
            Data_JSON_Contents.append(
                {
                    "Download Path": [dir_],
                    "Appear on top": [temp_appear_on_top],
                    "Theme": [temp_num]
                })
            with open(Data_JSON, mode='w+', encoding='utf-8') as file: json.dump(Data_JSON_Contents, file, ensure_ascii=True, indent=4)
            load_data_file(always_on_top, download_to_directory, theme)
            self.actionDownload_location.setStatusTip(f'Set default download location. {download_to_directory[0]}')
            self.actionOpen_Download_location.setStatusTip(f'Open default download location. {download_to_directory[0]}')
    def set_appear_on_top(self):
        temp_num = theme[0]
        temp_path = download_to_directory[0]
        Data_JSON_Contents.pop(0)
        Data_JSON_Contents.append(
            {
                "Download Path": [temp_path],
                "Appear on top": [str(self.actionAlways_appear_on_top.isChecked())],
                "Theme": [temp_num]
            })
        with open(Data_JSON, mode='w+', encoding='utf-8') as file: json.dump(Data_JSON_Contents, file, ensure_ascii=True, indent=4)
        load_data_file(always_on_top, download_to_directory, theme)
        
        self.mainwindow = mainwindowUI()
        self.mainwindow.show()
        self.close()
    def set_theme(self):
        if theme[0] == 0: 
            app.setStyle("windowsvista")
            QApplication.setPalette(originalPalette)
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
    def open_theme(self):
        self.close()
        self.settings = settingsUI()
        self.settings.resize(300,100)
        self.settings.show()
    def start_download(self):
        if self.txtURL.text() == '': return
        p = re.compile('https://open.spotify.com/(track|playlist|album)/[a-zA-Z0-9]{22}')
        m = p.match(self.txtURL.text())
        if m:
            self.btnCancel.setEnabled(True)
            # self.btnCancel.setHidden(False)
            self.btnDownload.setEnabled(False)
            self.actionTheme.setEnabled(False)
            self.actionDownload_location.setEnabled(False)
            self.actionAlways_appear_on_top.setEnabled(False)
            self.threads = []
            self.downloader = DownloadThread(self.txtURL.text())
            self.downloader.data_downloaded.connect(self.on_data_ready)
            self.threads.append(self.downloader)
            self.downloader.start()
            
            # self.otherthreads = []
            self.calculator = CalculateThread('')
            self.calculator.calculate.connect(self.update_progress_bar)
            self.threads.append(self.calculator)
            self.calculator.start()
            
        else:
            QMessageBox.critical(self, 'Doesn\'t Match', f"The Spotfiy link: \n'{self.txtURL.text()}' isn't valid.", QMessageBox.Ok, QMessageBox.Ok)
    def cancel_download(self):
        self.on_data_ready('')
        for i in self.threads:
            i.terminate()
        self.threads.clear()
        fileName = ''
        fileList = []
        for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
            if file.endswith(".txt"): fileList.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), file))
        fileName = fileList[0]
        os.remove(fileName)
        # self.downloader.terminate()
        # self.calculator.terminate()
    def on_data_ready(self, text):
        try:
            # self.lblState.setHidden(False)
            if text == '':
                self.btnCancel.setHidden(True)
                self.btnCancel.setEnabled(False)
                self.progressBar.setHidden(True)
                self.actionTheme.setEnabled(True)
                self.actionAlways_appear_on_top.setEnabled(True)
                self.btnDownload.setEnabled(True)
                self.actionDownload_location.setEnabled(True)
                return
            self.progressBar.setHidden(False)
            self.progressBar.setFormat(' ' + text)
        except Exception as e: print(e)
    def update_progress_bar(self, value): self.progressBar.setValue(download_percentage)
class settingsUI(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/settings.ui', self)
        self.setWindowIcon(QIcon('icon.png'))
        self.Default = self.findChild(QRadioButton, 'radDefault')
        self.Default.toggled.connect(lambda:self.RadClicked(self.Default))
        self.Dark = self.findChild(QRadioButton, 'radDark')
        self.Dark.toggled.connect(lambda:self.RadClicked(self.Dark))

        self.btnApply = self.findChild(QPushButton, 'btnApply')
        self.btnApply.clicked.connect(self.close)
        
        self.Default.setChecked(True if theme[0] == 0 else False)
        self.Dark.setChecked(True if theme[0] == 1 else False)
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
            app.setStyle("windowsvista")
            QApplication.setPalette(originalPalette)
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
        uic.loadUi('UI/aboutwindow.ui', self)
        self.setWindowIcon(QIcon('icon.png'))
        self.setWindowTitle("About")
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogInfoView')))
        self.icon = self.findChild(QLabel, 'lblIcon')
        self.icon.setFixedSize(128,128)
        pixmap = QPixmap('icon.png')
        myScaledPixmap = pixmap.scaled(self.icon.size(), Qt.KeepAspectRatio)
        self.icon.setPixmap(myScaledPixmap)
        self.lisenceText = self.findChild(QLabel,'label_2')
        with open('LICENSE', 'r') as f: self.lisenceText.setText(f.read())
        self.btnClose = self.findChild(QPushButton, 'btnClose')
        self.btnClose.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogCloseButton')))
        self.btnClose.clicked.connect(self.close)
        self.resize(700,400)
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
        with open(Data_JSON, 'w+') as f: f.write('[{"Appear on top":["False"],"Download Path":["' + path + '"],"Theme":[0]}]')
    # Load data file
    load_data_file(always_on_top, download_to_directory, theme)
    # start GUI
    app = QApplication(sys.argv)
    window = mainwindowUI()
    sys.exit(app.exec_())
