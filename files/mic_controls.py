from PyQt5.QtCore import QCoreApplication
from qfluentwidgets import FluentIcon
from files.config import cfg


def mic_button_clicked(self):
    self.voice_controller.toggle_recording()

def recording_started(self):
    self.current_text = self.textinputw.toPlainText()
    self.textinputw.clear()
    self.textinputw.setPlaceholderText(
        QCoreApplication.translate(
            "MainWindow",
            "Recording..." if self.voice_controller.model
            else "Loading Whisper model..."
        )
    )
    self.textinputw.repaint()
    self.mic_button.setIcon(FluentIcon.PAUSE)

def recording_stopped(self):
    self.mic_button.setIcon(FluentIcon.UPDATE)
    self.textinputw.clear()
    self.textinputw.setPlaceholderText(QCoreApplication.translate("MainWindow","Transcribing..."))

def transcription_ready(self, text):
    if (cfg.get(cfg.lineformat) is True):
        final = (self.current_text + '\n' + '\n' + text) if self.current_text else text  # start with new line
    else:
        final = (self.current_text + ' ' + text) if self.current_text else text  # default
    self.textinputw.setPlainText(final)
    self.textinputw.setPlaceholderText("")  # clear placeholder
    # Restore mic icon
    self.mic_button.setIcon(FluentIcon.MICROPHONE)