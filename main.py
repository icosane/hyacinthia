import sys,os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from files.interface import MainWindow
from files.config import cfg
from files.cudaconfig import get_lib_paths
from ctranslate2 import get_cuda_device_count


if __name__ == "__main__":
    if get_cuda_device_count() != 0:
        for dll_path in get_lib_paths():
            if os.path.exists(dll_path):
                os.environ["PATH"] = dll_path + os.pathsep + os.environ["PATH"]

    if cfg.get(cfg.dpiScale) != "Auto":
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    if os.name == 'nt':
        import ctypes
        myappid = u'icosane.hyacinthia' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    #locale = cfg.get(cfg.language).value
    #fluentTranslator = FluentTranslator(locale)
    #appTranslator = QTranslator()
    #lang_path = os.path.join(res_dir, "AlyssumResources", "lang")
    #appTranslator.load(locale, "lang", ".", lang_path)

    #app.installTranslator(fluentTranslator)
    #app.installTranslator(appTranslator)

    window = MainWindow()
    window.show()
    #sys.excepthook = ErrorHandler()
    #sys.stderr = ErrorHandler()
    sys.exit(app.exec())
