from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from .tts import generate

class TTSWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text: str, ref_file: str,
                 out_format: str, out_path: str):
        super().__init__()
        self.text = text
        self.ref_file = ref_file
        self.out_format = out_format
        self.out_path = out_path

    @pyqtSlot()
    def run(self):
        try:
            result_path = generate(self.text,
                                   self.ref_file,
                                   self.out_format,
                                   self.out_path)
            self.finished.emit(result_path)
        except Exception as exc:
            self.error.emit(str(exc))
