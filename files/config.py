from enum import Enum
from faster_whisper import available_models
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QKeySequence
from qfluentwidgets import (qconfig, QConfig, OptionsConfigItem, Theme,
                            OptionsValidator, EnumSerializer, ConfigSerializer, ConfigItem, BoolValidator,RangeConfigItem,RangeValidator)

class Language(Enum):
    """ Language enumeration """

    ENGLISH = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
    RUSSIAN = QLocale(QLocale.Language.Russian, QLocale.Country.Russia)
    AUTO = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)

class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


filtered_models = [m for m in available_models() if not m.startswith('distil') and not m.endswith('.en') and m != 'turbo']

WhisperModel = Enum('WhisperModel', {**{"NONE": "None"}, **{m.upper(): m for m in filtered_models}})

class WhisperModelSerializer(ConfigSerializer):
    """ WhisperModel serializer """

    def __init__(self):
        self.model_map = {model.value: model for model in WhisperModel}

    def serialize(self, model):
        return model.value if model != WhisperModel.NONE else "None"

    def deserialize(self, value: str):
        if value == "None":
            return WhisperModel.NONE
        model = self.model_map.get(value)
        if model is None:
            raise ValueError(f"Invalid model: {value}")
        return model


class KeyCombinationSerializer(ConfigSerializer):
    def serialize(self, value: QKeySequence) -> object:
        return value[0] if not value.isEmpty() else 0

    def deserialize(self, value: object) -> QKeySequence:
        if isinstance(value, int):
            return QKeySequence(value)
        elif isinstance(value, str):
            return QKeySequence(value)
        else:
            return QKeySequence()



class KeyCombinationConfigItem(ConfigItem):
    def __init__(self, group: str, key: str, default: str):
        super().__init__(group, key, QKeySequence(default), serializer=KeyCombinationSerializer())

filtered_models = [m for m in available_models() if not m.startswith('distil') and not m.endswith('.en') and m != 'turbo']

WhisperModel = Enum('WhisperModel', {**{"NONE": "None"}, **{m.upper(): m for m in filtered_models}})

class WhisperModelSerializer(ConfigSerializer):
    """ WhisperModel serializer """

    def __init__(self):
        self.model_map = {model.value: model for model in WhisperModel}

    def serialize(self, model):
        return model.value if model != WhisperModel.NONE else "None"

    def deserialize(self, value: str):
        if value == "None":
            return WhisperModel.NONE
        model = self.model_map.get(value)
        if model is None:
            raise ValueError(f"Invalid model: {value}")
        return model

class Config(QConfig):
    language = OptionsConfigItem(
        "Settings", "language", QLocale.Language.English, OptionsValidator(Language), LanguageSerializer(), restart=True)
    themeMode = OptionsConfigItem("Window", "themeMode", Theme.AUTO,
                                OptionsValidator(Theme), EnumSerializer(Theme), restart=True)
    dpiScale = OptionsConfigItem(
        "Settings", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    fontsize = RangeConfigItem("Settings", "fontsize", 18, RangeValidator(1, 40))
    whisper_model = OptionsConfigItem(
        "Whisper", "whisper_model", WhisperModel.NONE, OptionsValidator(WhisperModel), WhisperModelSerializer(), restart=False)
    shortcuts = ConfigItem("Shortcuts", "shortcuts", False, BoolValidator())
    lineformat = ConfigItem("MainWindow", "lineformat", False, BoolValidator())
    """ocrcut = KeyCombinationConfigItem("Shortcuts", "OCR", "F1")
    tlcut = KeyCombinationConfigItem("Shortcuts", "Translation", "F2")
    clcut = KeyCombinationConfigItem("Shortcuts", "Clear windows", "F3")
    copycut = KeyCombinationConfigItem("Shortcuts", "SelectAndCopy", "F5")
    filecut = KeyCombinationConfigItem("Shortcuts", "FileTranslation", "F6")
    startvi = KeyCombinationConfigItem("Shortcuts", "VoiceInput", "F7")"""


cfg = Config()
qconfig.load('config/config.json', cfg)
