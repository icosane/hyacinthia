import sys,os
from files.pathconfig import initialize
initialize()
'''sys.stdout = open(os.devnull, 'w')
import warnings
warnings.filterwarnings("ignore")'''
from files.config import cfg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator
from files.interface import MainWindow
from qfluentwidgets import FluentTranslator
from files.pathconfig import base_dir

if __name__ == "__main__":
    if cfg.get(cfg.dpiScale) != "Auto":
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    if os.name == 'nt':
        import ctypes
        myappid = u'icosane.hyacinthia'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    appTranslator = QTranslator()
    lang_path = os.path.join(base_dir, "lang")
    appTranslator.load(locale, "lang", ".", lang_path)

    app.installTranslator(fluentTranslator)
    app.installTranslator(appTranslator)

    window = MainWindow()
    window.show()
    sys.excepthook = sys.__excepthook__
    sys.stderr = sys.__stderr__
    sys.exit(app.exec())
