import sys, os
from PyQt6.QtGui import QColor, QIcon, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QLabel, QStackedWidget, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QTranslator, QCoreApplication, QTimer, QSettings
'''sys.stdout = open(os.devnull, 'w')
import warnings
warnings.filterwarnings("ignore")'''
from qfluentwidgets import setThemeColor, TransparentToolButton, FluentIcon, PushSettingCard, isDarkTheme, MessageBox, FluentTranslator, IndeterminateProgressBar, PushButton, SubtitleLabel, ComboBoxSettingCard, OptionsSettingCard, HyperlinkCard, ScrollArea, InfoBar, InfoBarPosition, StrongBodyLabel, TransparentTogglePushButton, TextBrowser, TextEdit, BodyLabel, LineEdit, SimpleExpandGroupSettingCard, SwitchButton, ToolTipFilter, ToolTipPosition, SwitchSettingCard, ToolButton, PlainTextEdit, ComboBox
from qframelesswindow.utils import getSystemAccentColor


class MainWindow(QMainWindow):
    theme_changed = pyqtSignal()
    package_changed = pyqtSignal()
    whispermodel_changed = pyqtSignal()
    lang_changed = pyqtSignal()
    fileSelected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(QCoreApplication.translate("MainWindow", "hyacinthia"))
        #icon_path = os.path.join(res_dir, "AlyssumResources", "assets", "icon.ico")
        #self.setWindowIcon(QIcon(icon_path))
        #self.settings = QSettings('icosane', 'Alyssum')
        self.setMinimumSize(1280,600)
        #self.restore_settings()
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.main_layout()
        #self.settings_layout()
        self.setup_theme()
        #update_model(self)
        self.center()
        
    
    def setup_theme(self):
        if isDarkTheme():
            print('ytes')
            theme_stylesheet = """
                QWidget {
                    background-color: #1e1e1e;  /* Dark background */
                    border: none;
                }
                QFrame {
                    background-color: transparent;
                    border: none;
                }
            """
        else:
            theme_stylesheet = """
                QWidget {
                    background-color: #f0f0f0;  /* Light background */
                    border: none;
                }
                QFrame {
                    background-color: transparent;
                    border: none;
                }
            """
        QApplication.instance().setStyleSheet(theme_stylesheet)


    def update_theme(self):
        self.setup_theme()

    def center(self):
        screen_geometry = self.screen().availableGeometry()
        window_geometry = self.geometry()

        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2

        self.move(x, y)


    def main_layout(self):
        main_layout = QVBoxLayout()

        self.settings_button = ToolButton(FluentIcon.SETTING)
        self.file_button = ToolButton(FluentIcon.FOLDER)
        self.start_button = ToolButton(FluentIcon.PLAY)
        self.clear_button = ToolButton(FluentIcon.BROOM)
        self.mic_button = ToolButton(FluentIcon.MICROPHONE)
        self.comboBox = ComboBox()

        items = ['voice1', 'voice2', 'voice3', 'voice4']
        self.comboBox.addItems(items)

        settings_layout = QHBoxLayout()
        settings_layout.addWidget(self.settings_button)
        settings_layout.addWidget(self.file_button)
        settings_layout.addWidget(self.comboBox)
        settings_layout.addWidget(self.mic_button)
        settings_layout.addStretch()
        settings_layout.addWidget(self.clear_button)
        settings_layout.addWidget(self.start_button)
        settings_layout.setContentsMargins(5, 5, 5, 5)

        main_layout.addLayout(settings_layout)

        font = QFont()
        font.setPointSize(14)
        self.textinputw = PlainTextEdit()
        self.textinputw.setFont(font)
        main_layout.addWidget(self.textinputw)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.stacked_widget.addWidget(main_widget)
        