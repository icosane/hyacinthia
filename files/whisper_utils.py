from PyQt5.QtCore import Qt, QThread, pyqtSignal, QCoreApplication
import os, shutil
from faster_whisper import download_model
from .config import cfg
from qfluentwidgets import InfoBar, InfoBarPosition
from files.pathconfig import base_dir


class ModelDownloaderThread(QThread):
    download_finished = pyqtSignal(str)
    download_start = pyqtSignal(str)

    def run(self):
        try:
            self.download_start.emit("start")
            download_model(f"{cfg.get(cfg.whisper_model).value}", cache_dir="./files/models/whisper")
            self.download_finished.emit("success")
        except Exception as e:
            self.download_finished.emit(f"error: {str(e)}")

    def stop(self):
        self.quit()
        self.wait()  # Ensure thread is cleaned up after quitting

def model_downloader(main_window):
    model_path = f"./files/models/whisper/models--Systran--faster-whisper-{cfg.get(cfg.whisper_model).value}"
    if not os.path.exists(model_path):
        model_path = f"./files/models/whisper/models--mobiuslabsgmbh--faster-whisper-{cfg.get(cfg.whisper_model).value}"
    if not os.path.exists(model_path):
        if hasattr(main_window, 'model_thread') and main_window.model_thread.isRunning():
            main_window.model_thread.stop()  # Stop the existing thread if it's running

        main_window.model_thread = ModelDownloaderThread()
        main_window.model_thread.download_start.connect(main_window.whispermodel_download_finished)
        main_window.model_thread.download_finished.connect(main_window.whispermodel_download_finished)
        main_window.model_thread.start()

def update_model(main_window):
    model_name = cfg.get(cfg.whisper_model).value
    content = QCoreApplication.translate("MainWindow", "Delete currently selected speech-to-text model. Model to be removed: <b>{}</b>").format(cfg.get(cfg.whisper_model).value)

    # Ensure record_button is updated
    if model_name == 'None':
        main_window.update_record_button(False)
        main_window.update_remove_button(False)
        main_window.card_deletewhispermodel.setContent(content)
    else:
        model_downloader(main_window)
        main_window.update_record_button(True)
        main_window.update_remove_button(True)
        main_window.card_deletewhispermodel.setContent(content)

def whispermodelremover(main_window):
    directory = os.path.join(base_dir, "models", "whisper", f"models--Systran--faster-whisper-{cfg.get(cfg.whisper_model).value}")
    cur_model = cfg.get(cfg.whisper_model).value
    if not os.path.exists(directory):
        directory = os.path.join(base_dir, "models", "whisper", f"models--mobiuslabsgmbh--faster-whisper-{cfg.get(cfg.whisper_model).value}")
    if os.path.exists(directory) and os.path.isdir(directory):
        try:
            # Remove the directory and its contents
            shutil.rmtree(directory)
            cfg.set(cfg.whisper_model, 'None')


            InfoBar.success(
                title=QCoreApplication.translate("MainWindow", "Removed"),
                content=QCoreApplication.translate("MainWindow", f"Whisper model '{cur_model}' removed successfully"),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=main_window
            )
        except Exception as e:
            InfoBar.error(
                title=QCoreApplication.translate("MainWindow", "Failed"),
                content=QCoreApplication.translate("MainWindow", f"Unable to delete Whisper model: {e}"),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=main_window
            )
