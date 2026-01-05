from PyQt5.QtCore import Qt, QCoreApplication, pyqtSignal, QEvent
from qfluentwidgets import FluentIcon, BodyLabel, SimpleExpandGroupSettingCard, SwitchButton, LineEdit
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.QtGui import QKeySequence
from .config import cfg

class ShortcutsCard(SimpleExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(FluentIcon.TILES, QCoreApplication.translate("MainWindow", "Keyboard shortcuts"), QCoreApplication.translate("MainWindow", "Edit keyboard shortcuts"), parent)
        self.switchb = SwitchButton()
        self.addWidget(self.switchb)
        self.switchb.setChecked(cfg.get(cfg.shortcuts))
        self.switchb.checkedChanged.connect(self.shortcut_state)

        # First group
        self.modeButton0 = ShortcutEdit()
        self.modeLabel0 = BodyLabel(QCoreApplication.translate("MainWindow", "Configure launch shortcut"))
        self.modeButton0.setFixedWidth(155)
        self.modeButton0.shortcutChanged.connect(self.updatelaunchShortcut)
        launch_shortcut = cfg.get(cfg.launchcut).toString()
        self.modeButton0.setText(launch_shortcut)

        # Second group
        self.modeButton1 = ShortcutEdit()
        self.modeLabel1 = BodyLabel(QCoreApplication.translate("MainWindow", "Configure clear shortcut"))
        self.modeButton1.setFixedWidth(155)
        self.modeButton1.shortcutChanged.connect(self.updateClearShortcut)
        cl_shortcut = cfg.get(cfg.clcut).toString()
        self.modeButton1.setText(cl_shortcut)

        # Third group
        self.modeButton2 = ShortcutEdit()
        self.modeLabel2 = BodyLabel(QCoreApplication.translate("MainWindow", "Configure file selector shortcut"))
        self.modeButton2.setFixedWidth(155)
        self.modeButton2.shortcutChanged.connect(self.updateFileShortcut)
        file_shortcut = cfg.get(cfg.filecut).toString()
        self.modeButton2.setText(file_shortcut)

        # Fourth group
        self.modeButton3 = ShortcutEdit()
        self.modeLabel3 = BodyLabel(QCoreApplication.translate("MainWindow", "Configure voice input shortcut"))
        self.modeButton3.setFixedWidth(155)
        self.modeButton3.shortcutChanged.connect(self.updateVoiceShortcut)
        voice_shortcut = cfg.get(cfg.startvi).toString()
        self.modeButton3.setText(voice_shortcut)

        # Adjust the internal layout
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        # Add each group to the setting card
        self.add(self.modeLabel0, self.modeButton0)
        self.add(self.modeLabel1, self.modeButton1)
        self.add(self.modeLabel2, self.modeButton2)
        self.add(self.modeLabel3, self.modeButton3)

    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        # Add the widget group to the setting card
        self.addGroupWidget(w)

    def shortcut_state(self):
        cfg.set(cfg.shortcuts, self.switchb.isChecked())

    def updatelaunchShortcut(self, key, modifiers):
        shortcut_str = self._modifiers_to_string(key, modifiers)
        shortcut = QKeySequence(shortcut_str)
        cfg.set(cfg.launchcut, shortcut)

    def updateClearShortcut(self, key, modifiers):
        shortcut_str = self._modifiers_to_string(key, modifiers)
        shortcut = QKeySequence(shortcut_str)
        cfg.set(cfg.clcut, shortcut)

    def updateFileShortcut(self, key, modifiers):
        shortcut_str = self._modifiers_to_string(key, modifiers)
        shortcut = QKeySequence(shortcut_str)
        cfg.set(cfg.filecut, shortcut)

    def updateVoiceShortcut(self, key, modifiers):
        shortcut_str = self._modifiers_to_string(key, modifiers)
        shortcut = QKeySequence(shortcut_str)
        cfg.set(cfg.startvi, shortcut)

    def _modifiers_to_string(self, key, modifiers):
        names = []

        if Qt.ControlModifier in modifiers:
            names.append("Ctrl")
        if Qt.ShiftModifier in modifiers:
            names.append("Shift")
        if Qt.AltModifier in modifiers:
            names.append("Alt")
        if Qt.MetaModifier in modifiers:
            names.append("Meta")

        if key != 0:
            names.append(QKeySequence(key).toString())

        return "+".join(names)


    def set_launch_shortcut(self, shortcut):
        self.modeButton0.setText(shortcut.toString())

    def set_clear_shortcut(self, shortcut):
        self.modeButton1.setText(shortcut.toString())

    def set_file_shortcut(self, shortcut):
        self.modeButton2.setText(shortcut.toString())

    def set_voice_shortcut(self, shortcut):
        self.modeButton3.setText(shortcut.toString())

class ShortcutEdit(LineEdit):
    shortcutChanged = pyqtSignal(int, list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.current_key = 0
        self.current_modifiers = []

    def event(self, event):
        if event.type() == QEvent.KeyPress:
            # Reset current state
            self.current_key = 0
            self.current_modifiers = []

            key = event.key()
            mods = event.modifiers()

            # Ignore pure modifier key presses
            if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
                return True

            if key == Qt.Key_Space and not mods:
                return True

            self.current_key = key

            if mods & Qt.ControlModifier:
                self.current_modifiers.append(Qt.ControlModifier)
            if mods & Qt.ShiftModifier:
                self.current_modifiers.append(Qt.ShiftModifier)
            if mods & Qt.AltModifier:
                self.current_modifiers.append(Qt.AltModifier)
            if mods & Qt.MetaModifier:
                self.current_modifiers.append(Qt.MetaModifier)

            # Create key sequence
            combo_int = int(mods) | key
            key_seq = QKeySequence(combo_int)
            self.setText(key_seq.toString())

            self.shortcutChanged.emit(self.current_key, self.current_modifiers)
            return True

        return super().event(event)
