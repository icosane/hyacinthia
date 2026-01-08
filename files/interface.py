import sys, os
from PyQt5.QtGui import QColor, QIcon, QFont, QKeySequence, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QStackedWidget, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication, QTimer, QSettings, QThread
from qfluentwidgets import setThemeColor, TransparentToolButton, FluentIcon, PushSettingCard, isDarkTheme, MessageBox, IndeterminateProgressBar, SubtitleLabel, ComboBoxSettingCard, OptionsSettingCard, HyperlinkCard, ScrollArea, InfoBar, InfoBarPosition, StrongBodyLabel, ToolTipFilter, ToolTipPosition, SwitchSettingCard, ToolButton, PlainTextEdit, ComboBox, RangeSettingCard, ProgressBar
from qframelesswindow.utils import getSystemAccentColor
from ctranslate2 import get_cuda_device_count
from files.config import cfg, available_models
from files.whisper_utils import update_model, whispermodelremover
from files.voice_input import VoiceController
from files.mic_controls import recording_started, recording_stopped, transcription_ready
from files.pathconfig import voices_dir
from files.shortcuts import ShortcutsCard
from files.tts_worker import TTSWorker
from datetime import datetime



class MainWindow(QMainWindow):
    theme_changed = pyqtSignal()
    package_changed = pyqtSignal()
    whispermodel_changed = pyqtSignal()
    fileSelected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(QCoreApplication.translate("MainWindow", "hyacinthia"))
        #icon_path = os.path.join(res_dir, "AlyssumResources", "assets", "icon.ico")
        #self.setWindowIcon(QIcon(icon_path))
        self.settings = QSettings('icosane', 'hyacinthia')
        self.setMinimumSize(1280,600)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.current_text = ""

        self.voice_controller = VoiceController(
            whisper_model_name=cfg.get(cfg.whisper_model).value,
            device="cuda" if get_cuda_device_count() != 0 else "cpu"
        )

        self.main_layout()
        self.settings_layout()
        self.restore_settings()
        self.setup_theme()
        update_model(self)
        self.center()

        self.theme_changed.connect(self.update_theme)
        self.whispermodel_changed.connect(lambda: update_model(self))

        cfg.launchcut.valueChanged.connect(self.update_launch_shortcut)
        cfg.clcut.valueChanged.connect(self.update_clear_shortcut)

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

        self.voice_paths = [
            os.path.join(voices_dir, f)
            for f in os.listdir(voices_dir)
            if os.path.isfile(os.path.join(voices_dir, f))
        ]
        self.format = ['mp3', 'wav']

        display_names = [os.path.basename(p) for p in self.voice_paths]

        self.comboBox1.addItems(display_names)

        for i, full_path in enumerate(self.voice_paths):
            self.comboBox1.setItemData(i, full_path)

        self.comboBox2.addItems(self.format)

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

        self.progressbar = IndeterminateProgressBar(start=False)

        main_layout.addWidget(self.progressbar)

        #tooltips
        self.settings_button.setToolTip(QCoreApplication.translate("MainWindow", "Open Settings"))
        self.settings_button.setToolTipDuration(2000)
        self.settings_button.installEventFilter(ToolTipFilter(self.settings_button, 0, ToolTipPosition.TOP))

        self.file_button.setToolTip(QCoreApplication.translate("MainWindow", "Select file to import from"))
        self.file_button.setToolTipDuration(2000)
        self.file_button.installEventFilter(ToolTipFilter(self.file_button, 0, ToolTipPosition.TOP))

        self.start_button.setToolTip(QCoreApplication.translate("MainWindow", "Start TTS"))
        self.start_button.setToolTipDuration(2000)
        self.start_button.installEventFilter(ToolTipFilter(self.start_button, 0, ToolTipPosition.TOP))

        self.clear_button.setToolTip(QCoreApplication.translate("MainWindow", "Clear text"))
        self.clear_button.setToolTipDuration(2000)
        self.clear_button.installEventFilter(ToolTipFilter(self.clear_button, 0, ToolTipPosition.TOP))

        self.mic_button.setToolTip(QCoreApplication.translate("MainWindow", "Toggle Voice Input"))
        self.mic_button.setToolTipDuration(2000)
        self.mic_button.installEventFilter(ToolTipFilter(self.mic_button, 0, ToolTipPosition.TOP))

        self.comboBox1.setToolTip(QCoreApplication.translate("MainWindow", "Select Voice"))
        self.comboBox1.setToolTipDuration(2000)
        self.comboBox1.installEventFilter(ToolTipFilter(self.comboBox1, 0, ToolTipPosition.TOP))

        self.comboBox2.setToolTip(QCoreApplication.translate("MainWindow", "Select Output Format"))
        self.comboBox2.setToolTipDuration(2000)
        self.comboBox2.installEventFilter(ToolTipFilter(self.comboBox2, 0, ToolTipPosition.TOP))

        #connect
        self.settings_button.clicked.connect(self.show_settings_page)
        self.file_button.clicked.connect(self.open_file_and_load_text)
        self.start_button.clicked.connect(self.start_tts)
        self.clear_button.clicked.connect(self.clearinput)

        self.mic_button.clicked.connect(self.voice_controller.toggle_recording)
        self.voice_controller.recording_started.connect(lambda: recording_started(self))
        self.voice_controller.recording_stopped.connect(lambda: recording_stopped(self))
        self.voice_controller.transcription_ready.connect(lambda text: transcription_ready(self, text))


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

        self.modelsins_title = StrongBodyLabel(QCoreApplication.translate("MainWindow", "Voice‑Input Management"))
        self.modelsins_title.setTextColor(QColor(0, 0, 0), QColor(255, 255, 255))
        card_layout.addSpacing(20)
        card_layout.addWidget(self.modelsins_title, alignment=Qt.AlignmentFlag.AlignTop)

        self.card_setwhispermodel = ComboBoxSettingCard(
            configItem=cfg.whisper_model,
            icon=FluentIcon.CLOUD_DOWNLOAD,
            title=QCoreApplication.translate("MainWindow","Whisper Speech‑Recognition Model"),
            content=QCoreApplication.translate("MainWindow", "Select a different Whisper model for speech‑recognition"),
            texts=['None',
                *[m for m in available_models() if not m.startswith('distil') and not m.endswith('.en') and m != 'turbo']]
        )

        card_layout.addWidget(self.card_setwhispermodel, alignment=Qt.AlignmentFlag.AlignTop)
        cfg.whisper_model.valueChanged.connect(self.whispermodel_changed.emit)

        self.card_deletewhispermodel = PushSettingCard(
            text=QCoreApplication.translate("MainWindow","Remove"),
            icon=FluentIcon.BROOM,
            title=QCoreApplication.translate("MainWindow","Delete Whisper model"),
            content=QCoreApplication.translate("MainWindow", "Delete currently selected speech-to-text model. Model to be removed: <b>{}</b>").format(cfg.get(cfg.whisper_model).value),
        )

        card_layout.addWidget(self.card_deletewhispermodel, alignment=Qt.AlignmentFlag.AlignTop)
        self.card_deletewhispermodel.clicked.connect(lambda: whispermodelremover(self))
        if ((cfg.get(cfg.whisper_model).value == 'None')):
            self.card_deletewhispermodel.button.setDisabled(True)

        self.miscellaneous_title = StrongBodyLabel(QCoreApplication.translate("MainWindow", "Miscellaneous"))
        self.miscellaneous_title.setTextColor(QColor(0, 0, 0), QColor(255, 255, 255))
        card_layout.addSpacing(20)
        card_layout.addWidget(self.miscellaneous_title, alignment=Qt.AlignmentFlag.AlignTop)

        self.fontsize_card = RangeSettingCard(
            cfg.fontsize,
            FluentIcon.FONT,
            title=QCoreApplication.translate("MainWindow","Editor Font Size"),
            content=QCoreApplication.translate("MainWindow","Font size used in the transcription editor")
        )
        card_layout.addWidget(self.fontsize_card,  alignment=Qt.AlignmentFlag.AlignTop )
        cfg.fontsize.valueChanged.connect(self.set_font)

        self.card_switch_line_format = SwitchSettingCard(
            icon=FluentIcon.FONT_SIZE,
            title=QCoreApplication.translate("MainWindow","Transcription Output Format"),
            content=QCoreApplication.translate("MainWindow","Toggle between a single continuous paragraph and one line per sentence."),
            configItem=cfg.lineformat
        )

        card_layout.addWidget(self.card_switch_line_format, alignment=Qt.AlignmentFlag.AlignTop)

        self.cursor_position_card = SwitchSettingCard(
            icon=FluentIcon.EDIT,
            title=QCoreApplication.translate("MainWindow", "Caret position"),
            content=QCoreApplication.translate(
                "MainWindow",
                "When enabled the cursor moves to the end of the imported text. "
                "When disabled the cursor stays at the beginning."
            ),
            configItem=cfg.caret_at_end
        )
        card_layout.addWidget(self.cursor_position_card, alignment=Qt.AlignmentFlag.AlignTop)


        self.card_editshortcuts = ShortcutsCard()
        card_layout.addWidget(self.card_editshortcuts, alignment=Qt.AlignmentFlag.AlignTop)

        self.card_setlanguage = ComboBoxSettingCard(
            configItem=cfg.language,
            icon=FluentIcon.LANGUAGE,
            title=QCoreApplication.translate("MainWindow","Interface Language"),
            content=QCoreApplication.translate("MainWindow", "Select the language for the application UI"),
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
            QCoreApplication.translate("MainWindow","UI Scaling"),
            QCoreApplication.translate("MainWindow","Adjust the size of UI elements and fonts"),
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
            content=QCoreApplication.translate("MainWindow", "hyacinthia is a graphical front‑end for F5‑TTS. It includes NVIDIA‑provided source code. License information and project details are available on GitHub.")
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

        self.download_progressbar = IndeterminateProgressBar(start=False)
        settings_layout.addWidget(self.download_progressbar)

        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)

        self.stacked_widget.addWidget(settings_widget)


    def clearinput(self):
        self.textinputw.clear()

    def update_remove_button(self, enabled):
        if hasattr(self, 'card_deletewhispermodel'):
            self.card_deletewhispermodel.button.setEnabled(enabled)

    def update_record_button(self, enabled):
        if hasattr(self, 'mic_button'):
            self.mic_button.setEnabled(enabled)
            self.mic_button.repaint()

    def restartinfo(self):
        InfoBar.warning(
            title=(QCoreApplication.translate("MainWindow", "Settings Saved")),
            content=(QCoreApplication.translate("MainWindow", "Changes will be applied after the application restarts")),
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

    def whispermodel_download_finished(self, status):
        if status == "start":
            self.download_progressbar.start()
            InfoBar.info(
                title=QCoreApplication.translate("MainWindow", "Downloading Model"),
                content=QCoreApplication.translate("MainWindow", "Downloading Whisper model '{}'").format(cfg.get(cfg.whisper_model).value),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=4000,
                parent=self
            )
            self.update_remove_button(False)

        elif status == "success":
            if hasattr(self, 'model_thread') and self.model_thread.isRunning():
                self.model_thread.stop()  # Stop the thread after success
            self.download_progressbar.stop()
            InfoBar.success(
                title=QCoreApplication.translate("MainWindow", "Download Complete"),
                content=QCoreApplication.translate("MainWindow", "Whisper model '{}' installed successfully!").format(cfg.get(cfg.whisper_model).value),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=4000,
                parent=self
            )
            self.update_remove_button(True)

        else:
            InfoBar.error(
                title=QCoreApplication.translate("MainWindow", "Download Failed"),
                content=QCoreApplication.translate("MainWindow", f"Unable to download Whisper model: {status}"),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=4000,
                parent=self
            )
            self.update_remove_button(False)

    def save_settings(self):
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.setValue('selected_voice_index', self.comboBox1.currentIndex())
        self.settings.setValue('selected_format_index', self.comboBox2.currentIndex())

    def restore_settings(self):
        size = self.settings.value("size")
        pos = self.settings.value("pos")

        if size is not None:
            self.resize(size)
        if pos is not None:
            self.move(pos)
        saved_voice_index = self.settings.value('selected_voice_index', type=int)
        saved_format_index = self.settings.value('selected_format_index', type=int)
        if saved_voice_index is not None:
            self.comboBox1.setCurrentIndex(saved_voice_index)
        if saved_format_index is not None:
            self.comboBox2.setCurrentIndex(saved_format_index)

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if cfg.get(cfg.shortcuts):
            pressed = QKeySequence(int(event.modifiers()) | event.key())

            if pressed.matches(cfg.get(cfg.launchcut)) == QKeySequence.ExactMatch:
                self.start_button.click()
            elif pressed.matches(cfg.get(cfg.clcut)) == QKeySequence.ExactMatch:
                self.clear_button.click()
            elif pressed.matches(cfg.get(cfg.filecut)) == QKeySequence.ExactMatch:
                pass
            elif pressed.matches(cfg.get(cfg.startvi)) == QKeySequence.ExactMatch:
                self.voice_controller.toggle_recording()

        super().keyPressEvent(event)

    def update_launch_shortcut(self, shortcut):
        self.card_editshortcuts.set_launch_shortcut(shortcut)

    def update_clear_shortcut(self, shortcut):
        self.card_editshortcuts.set_clear_shortcut(shortcut)

    def update_file_shortcut(self, shortcut):
        self.card_editshortcuts.set_file_shortcut(shortcut)

    def update_voice_shortcut(self, shortcut):
        self.card_editshortcuts.set_voice_shortcut(shortcut)

    def start_tts(self):
        text = self.textinputw.toPlainText().strip()
        if not text:
            InfoBar.warning(
                title=QCoreApplication.translate("MainWindow", "Nothing to synthesize"),
                content=QCoreApplication.translate("MainWindow", "Please type or load some text first."),
                parent=self,
                duration=2000,
            )
            return

        ref_file = self.comboBox1.currentData()
        out_format = self.comboBox2.currentText()

        formatted_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        default_name = f"hyacinthia_output_{formatted_time}." + out_format
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            QCoreApplication.translate("MainWindow", "Save generated speech as…"),
            os.path.join(os.path.expanduser("~"), default_name),
            f"{out_format.upper()} Files (*.{out_format});;All Files (*)",
        )
        if not save_path:
            return

        for w in (self.start_button, self.comboBox1, self.comboBox2,
              self.file_button, self.clear_button, self.mic_button):
            w.setEnabled(False)
        self.start_button.setIcon(FluentIcon.PAUSE)
        self.progressbar.start()

        self._tts_thread = QThread(self)             # keep a reference on the instance
        self._tts_worker = TTSWorker(text, ref_file, out_format, save_path)
        self._tts_worker.moveToThread(self._tts_thread)


        self._tts_thread.started.connect(self._tts_worker.run)
        self._tts_worker.finished.connect(self._on_tts_finished)
        self._tts_worker.error.connect(self._on_tts_error)

        self._tts_worker.finished.connect(self._tts_thread.quit)
        self._tts_worker.error.connect(self._tts_thread.quit)

        self._tts_thread.finished.connect(self._tts_thread.deleteLater)
        self._tts_thread.finished.connect(self._tts_worker.deleteLater)

        self._tts_thread.start()

    def _on_tts_finished(self, saved_path: str):
        self.progressbar.stop()
        self.start_button.setEnabled(True)
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)
        self.file_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.mic_button.setEnabled(True)
        self.start_button.setIcon(FluentIcon.PLAY)

        InfoBar.success(
            title=QCoreApplication.translate("MainWindow", "TTS finished"),
            content=QCoreApplication.translate("MainWindow", "File saved to: {0}").format(saved_path),
            parent=self,
            duration=3000,
        )

    def _on_tts_error(self, message: str):
        self.progressbar.stop()
        self.start_button.setEnabled(True)
        self.comboBox1.setEnabled(True)
        self.comboBox2.setEnabled(True)
        self.file_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.mic_button.setEnabled(True)
        self.start_button.setIcon(FluentIcon.PLAY)

        MessageBox(
            QCoreApplication.translate("MainWindow", "Error while generating speech"),
            message,
            self,
        ).exec()



    def open_file_and_load_text(self):
        last_folder = self.settings.value("last_folder", os.path.expanduser("~"))
        if not os.path.isdir(last_folder):
            last_folder = os.path.expanduser("~")

        dialog = QFileDialog(
            self,
            QCoreApplication.translate("MainWindow", "Open Text File"),
            last_folder,
            QCoreApplication.translate(
                "MainWindow",
                "Text Files (*.txt *.md);;All Files (*)"
            ),
        )
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if not dialog.exec():
            return

        file_path = dialog.selectedFiles()[0]

        self.settings.setValue("last_folder", os.path.dirname(file_path))

        progress = ProgressBar(self)
        progress.setMaximumHeight(20)
        progress.setTextVisible(True)
        progress.setAlignment(Qt.AlignmentFlag.AlignCenter)

        parent_layout = self.textinputw.parentWidget().layout()
        parent_layout.insertWidget(parent_layout.indexOf(self.textinputw), progress)

        file_size = os.path.getsize(file_path)
        progress.setMaximum(file_size)

        try:
            import chardet
        except ImportError:
            chardet = None

        sample_bytes = b""
        try:
            with open(file_path, "rb") as sample_f:
                sample_bytes = sample_f.read(1_048_576)
        except Exception as e:
            progress.deleteLater()
            MessageBox(
                QCoreApplication.translate("MainWindow", "Error opening file"),
                QCoreApplication.translate(
                    "MainWindow",
                    "Could not read the selected file:\n{0}"
                ).format(str(e)),
                self,
            ).exec()
            return

        # Guess the encoding
        encoding = "utf-8"
        if chardet:
            guess = chardet.detect(sample_bytes)
            if guess["encoding"] and guess["confidence"] >= 0.6:
                encoding = guess["encoding"]

        text_chunks = []
        chunk_size = 256 * 1024

        try:
            with open(file_path, "r", encoding=encoding, errors="strict") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    text_chunks.append(chunk)
                    progress.setValue(f.tell())
        except UnicodeDecodeError:
            with open(file_path, "r", encoding=sys.getdefaultencoding(),
                      errors="replace") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    text_chunks.append(chunk)
                    progress.setValue(f.tell())
        except Exception as e:
            progress.deleteLater()
            MessageBox(
                QCoreApplication.translate("MainWindow", "Error reading file"),
                QCoreApplication.translate(
                    "MainWindow",
                    "Could not read the selected file:\n{0}"
                ).format(str(e)),
                self,
            ).exec()
            return
        finally:
            progress.deleteLater()

        full_text = "".join(text_chunks)
        self.textinputw.setPlainText(full_text)
        if cfg.caret_at_end.value:
            def _scroll_to_end():
                self.textinputw.moveCursor(QTextCursor.End)
                self.textinputw.ensureCursorVisible()
                sb = self.textinputw.verticalScrollBar()
                sb.setValue(sb.maximum())
                self.textinputw.setFocus()
            QTimer.singleShot(0, _scroll_to_end)

        self.fileSelected.emit(file_path)

        InfoBar.success(
            title=QCoreApplication.translate("MainWindow", "File Loaded"),
            content=QCoreApplication.translate(
                "MainWindow",
                "Successfully loaded “{0}”."
            ).format(os.path.basename(file_path)),
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2500,
            parent=self,
        )
