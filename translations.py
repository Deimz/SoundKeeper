"""Tray translations and Windows preferred UI language selection."""

import ctypes
from ctypes import wintypes

TRANSLATIONS = {
    "en": {
        "active": "Active (Keep-Alive)",
        "startup": "Launch at Startup",
        "settings": "Settings",
        "wait": "Wait duration",
        "duration": "Sound duration",
        "reset": "Restore defaults",
        "language": "Language",
        "auto": "Follow system / Auto",
        "quit": "Quit",
        "seconds": "{value} s",
        "minutes": "{minutes} min {seconds} s",
        "audio_error": "Audio unavailable; retrying",
        "save_error": (
            "Settings could not be saved. Changes apply only to this session."
        ),
        "startup_error": "The startup setting could not be changed.",
        "already_running": "SoundKeeper is already running!",
    },
    "zh-Hans": {
        "active": "启用音频保活",
        "startup": "开机启动",
        "settings": "设置",
        "wait": "等待时长",
        "duration": "播放时长",
        "reset": "恢复默认设置",
        "language": "语言",
        "auto": "跟随系统 / Auto",
        "quit": "退出",
        "seconds": "{value} 秒",
        "minutes": "{minutes} 分 {seconds} 秒",
        "audio_error": "音频不可用，正在重试",
        "save_error": "无法保存设置。更改仅在本次运行期间生效。",
        "startup_error": "无法更改开机启动设置。",
        "already_running": "SoundKeeper 已在运行！",
    },
    "fr": {
        "active": "Actif (Keep-Alive)",
        "startup": "Lancer au démarrage",
        "settings": "Paramètres",
        "wait": "Durée d'attente",
        "duration": "Durée du son",
        "reset": "Rétablir les paramètres par défaut",
        "language": "Langue",
        "auto": "Suivre le système / Auto",
        "quit": "Quitter",
        "seconds": "{value} s",
        "minutes": "{minutes} min {seconds} s",
        "audio_error": "Audio indisponible ; nouvelle tentative en cours",
        "save_error": (
            "Impossible d'enregistrer les paramètres. "
            "Les modifications ne s'appliquent qu'à cette session."
        ),
        "startup_error": "Impossible de modifier le lancement au démarrage.",
        "already_running": "SoundKeeper est déjà en cours d'exécution !",
    },
    "ru": {
        "active": "Поддерживать аудиоустройство активным",
        "startup": "Запускать при входе в Windows",
        "settings": "Настройки",
        "wait": "Время ожидания",
        "duration": "Длительность звука",
        "reset": "Восстановить настройки по умолчанию",
        "language": "Язык",
        "auto": "Язык системы / Auto",
        "quit": "Выход",
        "seconds": "{value} с",
        "minutes": "{minutes} мин {seconds} с",
        "audio_error": "Аудиоустройство недоступно; повторная попытка",
        "save_error": (
            "Не удалось сохранить настройки. "
            "Изменения действуют только в текущем сеансе."
        ),
        "startup_error": "Не удалось изменить настройку автозапуска.",
        "already_running": "SoundKeeper уже запущен!",
    },
    "es": {
        "active": "Activo (Keep-Alive)",
        "startup": "Iniciar con Windows",
        "settings": "Configuración",
        "wait": "Tiempo de espera",
        "duration": "Duración del sonido",
        "reset": "Restaurar valores predeterminados",
        "language": "Idioma",
        "auto": "Seguir el sistema / Auto",
        "quit": "Salir",
        "seconds": "{value} s",
        "minutes": "{minutes} min {seconds} s",
        "audio_error": "Audio no disponible; reintentando",
        "save_error": (
            "No se pudo guardar la configuración. "
            "Los cambios solo se aplican a esta sesión."
        ),
        "startup_error": "No se pudo cambiar el inicio con Windows.",
        "already_running": "¡SoundKeeper ya está en ejecución!",
    },
    "ar": {
        "active": "إبقاء جهاز الصوت نشطًا",
        "startup": "التشغيل عند بدء Windows",
        "settings": "الإعدادات",
        "wait": "مدة الانتظار",
        "duration": "مدة الصوت",
        "reset": "استعادة الإعدادات الافتراضية",
        "language": "اللغة",
        "auto": "اتباع لغة النظام / Auto",
        "quit": "خروج",
        "seconds": "{value} ثانية",
        "minutes": "{minutes} دقيقة و{seconds} ثانية",
        "audio_error": "الصوت غير متاح؛ جارٍ إعادة المحاولة",
        "save_error": "تعذر حفظ الإعدادات. تسري التغييرات على هذه الجلسة فقط.",
        "startup_error": "تعذر تغيير إعداد التشغيل عند بدء Windows.",
        "already_running": "SoundKeeper قيد التشغيل بالفعل!",
    },
}


def preferred_ui_languages():
    """Read the ordered Windows UI language list, not regional number formats."""
    try:
        function = ctypes.windll.kernel32.GetUserPreferredUILanguages
        function.argtypes = (
            wintypes.DWORD,
            ctypes.POINTER(wintypes.ULONG),
            wintypes.LPWSTR,
            ctypes.POINTER(wintypes.ULONG),
        )
        function.restype = wintypes.BOOL
        count = wintypes.ULONG()
        size = wintypes.ULONG()
        flags = 0x8  # MUI_LANGUAGE_NAME
        if not function(flags, ctypes.byref(count), None, ctypes.byref(size)):
            return []
        buffer = ctypes.create_unicode_buffer(size.value)
        if not function(flags, ctypes.byref(count), buffer, ctypes.byref(size)):
            return []
        return [name for name in buffer[: size.value].split("\0") if name]
    except (AttributeError, OSError):
        return []


def resolve_language(language, preferred):
    """Match supported language families in preference order; fall back to English."""
    if language in TRANSLATIONS:
        return language
    for name in preferred:
        family = name.replace("_", "-").split("-")[0].lower()
        candidate = "zh-Hans" if family == "zh" else family
        if candidate in TRANSLATIONS:
            return candidate
    return "en"


def translate(language, key, **values):
    text = TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(
        key, TRANSLATIONS["en"][key]
    )
    # Isolate embedded numbers/Latin text to preserve Arabic bidirectional ordering.
    if language == "ar":
        values = {
            name: "\u2068" + str(value) + "\u2069" for name, value in values.items()
        }
    return text.format(**values)
