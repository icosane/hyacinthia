import sys,os
from PyQt6.QtWidgets import QApplication
from files.interface import MainWindow


if __name__ == "__main__":
    '''if cfg.get(cfg.dpiScale) != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))'''

    if os.name == 'nt':
        import ctypes
        myappid = u'icosane.hyacinthia.2109' 
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
