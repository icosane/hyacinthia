from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextCursor
from qfluentwidgets import PlainTextEdit
import os, chardet, sys
from .config import cfg
from qfluentwidgets import ProgressBar

class DropPlainTextEdit(PlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            for url in e.mimeData().urls():
                if url.isLocalFile() and os.path.splitext(url.toLocalFile())[1].lower() in (".txt", ".md"):
                    e.acceptProposedAction()
                    return
        e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            if not url.isLocalFile():
                continue
            path = url.toLocalFile()
            if os.path.splitext(path)[1].lower() not in (".txt", ".md"):
                continue

            self._load_file(path)
            e.acceptProposedAction()
            break

    def _load_file(self, file_path):
        progress = ProgressBar(self)
        progress.setMaximumHeight(20)
        progress.setTextVisible(True)
        progress.setAlignment(Qt.AlignCenter)

        parent_layout = self.parentWidget().layout()
        parent_layout.insertWidget(parent_layout.indexOf(self), progress)

        file_size = os.path.getsize(file_path)
        progress.setMaximum(file_size)

        encoding = "utf-8"
        if chardet:
            with open(file_path, "rb") as sample_f:
                guess = chardet.detect(sample_f.read(1_048_576))
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
        finally:
            progress.deleteLater()

        full_text = "".join(text_chunks)
        self.setPlainText(full_text)

        if cfg.caret_at_end.value:
            QTimer.singleShot(0, self._move_cursor_to_end)

    def _move_cursor_to_end(self):
        self.moveCursor(QTextCursor.End)
        self.ensureCursorVisible()
        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())
        self.setFocus()
