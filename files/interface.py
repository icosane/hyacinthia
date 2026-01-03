import sys, os
from PyQt5.QtGui import QColor, QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QLabel, QStackedWidget, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QTranslator, QCoreApplication, QTimer, QSettings
'''sys.stdout = open(os.devnull, 'w')
import warnings
warnings.filterwarnings("ignore")'''
from qfluentwidgets import setThemeColor, TransparentToolButton, FluentIcon, PushSettingCard, isDarkTheme, MessageBox, FluentTranslator, IndeterminateProgressBar, PushButton, SubtitleLabel, ComboBoxSettingCard, OptionsSettingCard, HyperlinkCard, ScrollArea, InfoBar, InfoBarPosition, StrongBodyLabel, TransparentTogglePushButton, TextBrowser, TextEdit, BodyLabel, LineEdit, SimpleExpandGroupSettingCard, SwitchButton, ToolTipFilter, ToolTipPosition, SwitchSettingCard, ToolButton, PlainTextEdit, ComboBox, RangeSettingCard
from qframelesswindow.utils import getSystemAccentColor
from files.config import cfg, available_models


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
        self.settings_layout()
        self.setup_theme()
        #update_model(self)
        self.center()
        self.theme_changed.connect(self.update_theme)

    def setup_theme(self):
        if sys.platform in ["win32", "darwin"]:
            setThemeColor(getSystemAccentColor())
        if isDarkTheme():
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

    def show_settings_page(self):
        self.stacked_widget.setCurrentIndex(1)  # Switch to the settings page

    def show_main_page(self):
        self.stacked_widget.setCurrentIndex(0)  # Switch back to the main page

    def set_font(self):
        font = QFont()
        font.setPointSize(cfg.fontsize.value)
        self.textinputw.setFont(font)

    def main_layout(self):
        main_layout = QVBoxLayout()

        self.settings_button = ToolButton(FluentIcon.SETTING)
        self.file_button = ToolButton(FluentIcon.FOLDER)
        self.start_button = ToolButton(FluentIcon.PLAY)
        self.clear_button = ToolButton(FluentIcon.BROOM)
        self.mic_button = ToolButton(FluentIcon.MICROPHONE)

        self.comboBox1 = ComboBox()
        self.comboBox2 = ComboBox()

        items = ['voice1', 'voice2', 'voice3', 'voice4']
        items0 = ['mp3', 'wav']
        self.comboBox1.addItems(items)
        self.comboBox2.addItems(items0)

        settings_layout = QHBoxLayout()
        settings_layout.addWidget(self.settings_button)
        settings_layout.addWidget(self.file_button)
        settings_layout.addWidget(self.comboBox1)
        settings_layout.addWidget(self.comboBox2)
        settings_layout.addWidget(self.mic_button)
        settings_layout.addStretch()
        settings_layout.addWidget(self.clear_button)
        settings_layout.addWidget(self.start_button)
        settings_layout.setContentsMargins(5, 5, 5, 5)

        main_layout.addLayout(settings_layout)

        

        self.textinputw = PlainTextEdit()
        self.set_font()
        main_layout.addWidget(self.textinputw)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.stacked_widget.addWidget(main_widget)
        
        #tooltips
        self.settings_button.setToolTip(QCoreApplication.translate("MainWindow", "Settings"))
        self.settings_button.setToolTipDuration(2000)
        self.settings_button.installEventFilter(ToolTipFilter(self.settings_button, 0, ToolTipPosition.TOP))

        self.file_button.setToolTip(QCoreApplication.translate("MainWindow", "Open file"))
        self.file_button.setToolTipDuration(2000)
        self.file_button.installEventFilter(ToolTipFilter(self.file_button, 0, ToolTipPosition.TOP))

        self.start_button.setToolTip(QCoreApplication.translate("MainWindow", "Start"))
        self.start_button.setToolTipDuration(2000)
        self.start_button.installEventFilter(ToolTipFilter(self.start_button, 0, ToolTipPosition.TOP))

        self.clear_button.setToolTip(QCoreApplication.translate("MainWindow", "Clear"))
        self.clear_button.setToolTipDuration(2000)
        self.clear_button.installEventFilter(ToolTipFilter(self.clear_button, 0, ToolTipPosition.TOP))

        #connect
        self.settings_button.clicked.connect(self.show_settings_page)
        #self.file_button
        #self.start_button
        self.clear_button.clicked.connect(lambda: clearinput(self))
        #self.mic_button


    def settings_layout(self):
        settings_layout = QVBoxLayout()

        back_button_layout = QHBoxLayout()

        back_button = TransparentToolButton(FluentIcon.LEFT_ARROW)
        back_button.clicked.connect(self.show_main_page)

        back_button_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignTop)
        back_button_layout.setContentsMargins(5, 5, 5, 5)

        settings_layout.addLayout(back_button_layout)

        self.settings_title = SubtitleLabel(QCoreApplication.translate("MainWindow", "Settings"))
        self.settings_title.setTextColor(QColor(0, 0, 0), QColor(255, 255, 255))

        back_button_layout.addWidget(self.settings_title, alignment=Qt.AlignmentFlag.AlignTop)

        card_layout = QVBoxLayout()

        self.modelsins_title = StrongBodyLabel(QCoreApplication.translate("MainWindow", "Model management"))
        self.modelsins_title.setTextColor(QColor(0, 0, 0), QColor(255, 255, 255))
        card_layout.addSpacing(20)
        card_layout.addWidget(self.modelsins_title, alignment=Qt.AlignmentFlag.AlignTop)

        self.card_setwhispermodel = ComboBoxSettingCard(
            configItem=cfg.whisper_model,
            icon=FluentIcon.CLOUD_DOWNLOAD,
            title=QCoreApplication.translate("MainWindow","Whisper Model"),
            content=QCoreApplication.translate("MainWindow", "Change speech recognition model"),
            texts=['None',
                *[m for m in available_models() if not m.startswith('distil') and not m.endswith('.en') and m != 'turbo']]
        )

        card_layout.addWidget(self.card_setwhispermodel, alignment=Qt.AlignmentFlag.AlignTop)
        cfg.whisper_model.valueChanged.connect(self.whispermodel_changed.emit)

        self.card_deletewhispermodel = PushSettingCard(
            text=QCoreApplication.translate("MainWindow","Remove"),
            icon=FluentIcon.BROOM,
            title=QCoreApplication.translate("MainWindow","Remove Whisper model"),
            content=QCoreApplication.translate("MainWindow", "Delete currently selected speech-to-text model. Will be removed: <b>{}</b>").format(cfg.get(cfg.whisper_model).value),
        )

        card_layout.addWidget(self.card_deletewhispermodel, alignment=Qt.AlignmentFlag.AlignTop)
        #self.card_deletewhispermodel.clicked.connect(self.whispermodelremover)
        if ((cfg.get(cfg.whisper_model).value == 'None')):
            self.card_deletewhispermodel.button.setDisabled(True)

        self.miscellaneous_title = StrongBodyLabel(QCoreApplication.translate("MainWindow", "Miscellaneous"))
        self.miscellaneous_title.setTextColor(QColor(0, 0, 0), QColor(255, 255, 255))
        card_layout.addSpacing(20)
        card_layout.addWidget(self.miscellaneous_title, alignment=Qt.AlignmentFlag.AlignTop)

        self.fontsize_card = RangeSettingCard(
            cfg.fontsize,
            FluentIcon.FONT,
            title="Font Size",
            content="Font size in the input window"
        )
        card_layout.addWidget(self.fontsize_card,  alignment=Qt.AlignmentFlag.AlignTop )
        cfg.fontsize.valueChanged.connect(self.set_font)

        self.card_setlanguage = ComboBoxSettingCard(
            configItem=cfg.language,
            icon=FluentIcon.LANGUAGE,
            title=QCoreApplication.translate("MainWindow","Language"),
            content=QCoreApplication.translate("MainWindow", "Change UI language"),
            texts=["English", "Русский"]
        )

        card_layout.addWidget(self.card_setlanguage, alignment=Qt.AlignmentFlag.AlignTop)
        cfg.language.valueChanged.connect(self.restartinfo)

        self.card_theme = OptionsSettingCard(
            cfg.themeMode,
            FluentIcon.BRUSH,
            QCoreApplication.translate("MainWindow","Application theme"),
            QCoreApplication.translate("MainWindow", "Adjust appearance"),
            [QCoreApplication.translate("MainWindow","Light"), QCoreApplication.translate("MainWindow","Dark"), QCoreApplication.translate("MainWindow","Follow System Settings")]
        )

        card_layout.addWidget(self.card_theme, alignment=Qt.AlignmentFlag.AlignTop)
        self.card_theme.optionChanged.connect(self.theme_changed.emit)

        self.card_zoom = OptionsSettingCard(
            cfg.dpiScale,
            FluentIcon.ZOOM,
            QCoreApplication.translate("MainWindow","Interface zoom"),
            QCoreApplication.translate("MainWindow","Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                QCoreApplication.translate("MainWindow","Follow System Settings")
            ]
        )

        card_layout.addWidget(self.card_zoom, alignment=Qt.AlignmentFlag.AlignTop)
        cfg.dpiScale.valueChanged.connect(self.restartinfo)

        self.about_card = HyperlinkCard(
            url="https://github.com/icosane/hyacinthia",
            text="Github",
            icon=FluentIcon.INFO,
            title=QCoreApplication.translate("MainWindow", "About"),
            content=QCoreApplication.translate("MainWindow", "This software contains source code provided by NVIDIA Corporation. Licenses and details are on GitHub.")
        )
        card_layout.addWidget(self.about_card,  alignment=Qt.AlignmentFlag.AlignTop )

        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.card_widget = QWidget()
        self.card_widget.setLayout(card_layout)
        self.card_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.card_widget)
        settings_layout.addWidget(self.scroll_area)

    
        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)

        self.stacked_widget.addWidget(settings_widget)


    def clearinput(self):
        self.textinputw.clear()

    def restartinfo(self):
        InfoBar.warning(
            title=(QCoreApplication.translate("MainWindow", "Success")),
            content=(QCoreApplication.translate("MainWindow", "Setting takes effect after restart")),
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )