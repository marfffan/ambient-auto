#!/usr/bin/env python3
"""Локализация приложения «Автояркость MacBook».

Переводы хранятся прямо в коде: не нужны .ts/.qm, lrelease и отдельные
пакеты переводов. Язык хранится в конфиге ключом ``language``:
``system`` (по локали сеанса) или код языка.

Добавить язык — значит дописать словарь в ``STRINGS`` и строку в
``LANGUAGES``.
"""

import os

LANGUAGES = (
    ("system", "Системный"),
    ("ru", "Русский"),
    ("en", "English"),
    ("de", "Deutsch"),
    ("es", "Español"),
    ("fr", "Français"),
)

DEFAULT_LANGUAGE = "en"

STRINGS = {
    "ru": {
        "window_title": "Автояркость MacBook",
        "header_title": "Автояркость MacBook",
        "switch_enabled": "Реагировать на освещение",
        "language_label": "Язык:",
        "language_system": "Системный",
        "group_now": "Сейчас",
        "row_lux": "Освещённость:",
        "row_band": "Полоса:",
        "row_screen": "Экран:",
        "row_keyboard": "Клавиатура:",
        "row_camera": "Камера:",
        "row_backend": "Источник экрана:",
        "band_dark": "тёмно",
        "band_normal": "свет",
        "band_bright": "ярко",
        "group_screen": "Экран",
        "screen_dark": "В темноте:",
        "screen_normal": "При свете:",
        "screen_bright": "При ярком свете:",
        "threshold_dark": "Считать тёмным ниже:",
        "threshold_bright": "Считать ярким выше:",
        "manual_pause": "Пауза после ручной правки:",
        "hysteresis_note": (
            "Гистерезис: выход из «темно» на +8 лк, из «ярко» на −30 лк, "
            "чтобы подсветка не дёргалась на границе."
        ),
        "group_keyboard": "Клавиатура",
        "kbd_off_light": "Полностью выключать при свете",
        "group_camera": "Камера",
        "cam_dark": "Усиление в темноте:",
        "cam_normal": "Усиление при свете:",
        "cam_bright": "Усиление при ярком свете:",
        "cam_note": "Частота всегда 30 кадров/с — без замедления в темноте.",
        "button_apply": "Применить",
        "button_reset": "Сбросить",
        "button_restart": "Перезапустить службу",
        "button_resume": "Вернуть управление",
        "footer_hint": (
            "Настройки сохраняются в ~/.config/ambient-auto/config.json "
            "и применяются в течение 2 секунд."
        ),
        "status_ready": "Готово",
        "status_saved": "Сохранено — применится в течение 2 секунд",
        "status_enabled": "Автоматика включена",
        "status_disabled": "Автоматика отключена",
        "status_reset": "Значения сброшены — нажмите «Применить»",
        "status_resumed": "Управление возвращено автоматике",
        "status_restarted": "Служба перезапущена",
        "status_restart_failed": "Служба не перезапущена",
        "no_data": "нет данных",
        "auto_off": "автоматика выключена",
        "no_link": "нет связи",
        "service_down": "Служба не запущена или ещё не ответила.",
        "auto_working": "Автоматика управляет яркостью по датчику.",
        "auto_off_hint": (
            "Автоматика выключена: яркость и подсветка не меняются. "
            "Включите переключатель сверху."
        ),
        "pause_left": (
            "Пауза после ручной правки: {minutes}:{seconds:02d}. "
            "Автоматика вернёт управление сама или по кнопке."
        ),
        "dialog_thresholds_title": "Проверьте пороги",
        "dialog_thresholds_text": (
            "Порог «ярко» должен быть хотя бы на {gap} лк выше порога «темно»."
        ),
        "dialog_save_title": "Не удалось сохранить",
        "dialog_save_text": "Не получается записать {path}:\n{error}",
        "dialog_reset_title": "Сбросить настройки",
        "dialog_reset_text": "Вернуть значения по умолчанию?",
        "dialog_error_title": "Ошибка",
        "dialog_restart_error": "Не удалось перезапустить: {error}",
        "dialog_error_generic": "Команда завершилась с ошибкой.",
        "backend_direct": "напрямую",
        "camera_line": "{fps} кадров/с, усиление {gain}",
        "msg_start": "Запуск",
        "msg_config_reloaded": "Настройки обновлены",
        "msg_enabled_on": "Автоматика включена",
        "msg_enabled_off": "Автоматика отключена",
        "msg_manual_override": "Яркость изменена вручную — возвращаю управление",
        "msg_manual_override_pause": (
            "Яркость изменена вручную ({percent}%) — пауза {minutes} мин"
        ),
        "msg_screen_kwin": "Экран: управление через KWin/KScreen",
        "msg_screen_sysfs": "KWin недоступен — временно пишу в sysfs",
        "msg_camera_applied": "Камера: усиление {gain}, {fps} кадров/с",
        "msg_camera_busy": "Камера открыта — настройки применены",
        "msg_apply_summary": (
            "Экран {screen}%, клавиатура {kbd}%, камера {gain} ({fps} fps)"
        ),
        "unit_percent": " %",
        "unit_lux": " лк",
        "unit_min": " мин",
        "unit_fps": "кадров/с",
        "pause_never": "не ставить",
    },
    "en": {
        "window_title": "MacBook Ambient Brightness",
        "header_title": "MacBook Ambient Brightness",
        "switch_enabled": "Respond to ambient light",
        "language_label": "Language:",
        "language_system": "System",
        "group_now": "Now",
        "row_lux": "Illuminance:",
        "row_band": "Band:",
        "row_screen": "Screen:",
        "row_keyboard": "Keyboard:",
        "row_camera": "Camera:",
        "row_backend": "Screen source:",
        "band_dark": "dark",
        "band_normal": "light",
        "band_bright": "bright",
        "group_screen": "Screen",
        "screen_dark": "In the dark:",
        "screen_normal": "In light:",
        "screen_bright": "In bright light:",
        "threshold_dark": "Consider dark below:",
        "threshold_bright": "Consider bright above:",
        "manual_pause": "Pause after manual change:",
        "hysteresis_note": (
            "Hysteresis: leaving \u201cdark\u201d at +8 lx and \u201cbright\u201d at \u221230 lx, "
            "so the backlight does not flicker at the threshold."
        ),
        "group_keyboard": "Keyboard",
        "kbd_off_light": "Turn off completely in light",
        "group_camera": "Camera",
        "cam_dark": "Gain in the dark:",
        "cam_normal": "Gain in light:",
        "cam_bright": "Gain in bright light:",
        "cam_note": "The frame rate is always 30 fps — no slowdown in the dark.",
        "button_apply": "Apply",
        "button_reset": "Reset",
        "button_restart": "Restart service",
        "button_resume": "Take back control",
        "footer_hint": (
            "Settings are saved to ~/.config/ambient-auto/config.json "
            "and applied within 2 seconds."
        ),
        "status_ready": "Ready",
        "status_saved": "Saved — will be applied within 2 seconds",
        "status_enabled": "Automation enabled",
        "status_disabled": "Automation disabled",
        "status_reset": "Values reset — press \u201cApply\u201d",
        "status_resumed": "Control returned to automation",
        "status_restarted": "Service restarted",
        "status_restart_failed": "Service was not restarted",
        "no_data": "no data",
        "auto_off": "automation is off",
        "no_link": "no connection",
        "service_down": "The service is not running or has not responded yet.",
        "auto_working": "Automation controls brightness from the sensor.",
        "auto_off_hint": (
            "Automation is off: brightness and backlight do not change. "
            "Turn on the switch above."
        ),
        "pause_left": (
            "Pause after manual change: {minutes}:{seconds:02d}. "
            "Automation will take control back automatically or via the button."
        ),
        "dialog_thresholds_title": "Check the thresholds",
        "dialog_thresholds_text": (
            "The \u201cbright\u201d threshold must be at least {gap} lx above the "
            "\u201cdark\u201d threshold."
        ),
        "dialog_save_title": "Could not save",
        "dialog_save_text": "Cannot write {path}:\n{error}",
        "dialog_reset_title": "Reset settings",
        "dialog_reset_text": "Restore the default values?",
        "dialog_error_title": "Error",
        "dialog_restart_error": "Could not restart: {error}",
        "dialog_error_generic": "The command finished with an error.",
        "backend_direct": "direct",
        "camera_line": "{fps} fps, gain {gain}",
        "msg_start": "Starting",
        "msg_config_reloaded": "Settings updated",
        "msg_enabled_on": "Automation enabled",
        "msg_enabled_off": "Automation disabled",
        "msg_manual_override": "Brightness changed manually — taking control back",
        "msg_manual_override_pause": (
            "Brightness changed manually ({percent}%) — paused for {minutes} min"
        ),
        "msg_screen_kwin": "Screen: controlled through KWin/KScreen",
        "msg_screen_sysfs": "KWin unavailable — writing to sysfs for now",
        "msg_camera_applied": "Camera: gain {gain}, {fps} fps",
        "msg_camera_busy": "Camera opened — settings applied",
        "msg_apply_summary": (
            "Screen {screen}%, keyboard {kbd}%, camera {gain} ({fps} fps)"
        ),
        "unit_percent": " %",
        "unit_lux": " lx",
        "unit_min": " min",
        "unit_fps": "fps",
        "pause_never": "never",
    },
    "de": {
        "window_title": "MacBook Umgebungshelligkeit",
        "header_title": "MacBook Umgebungshelligkeit",
        "switch_enabled": "Auf Umgebungslicht reagieren",
        "language_label": "Sprache:",
        "language_system": "Systemsprache",
        "group_now": "Jetzt",
        "row_lux": "Beleuchtungsstärke:",
        "row_band": "Bereich:",
        "row_screen": "Bildschirm:",
        "row_keyboard": "Tastatur:",
        "row_camera": "Kamera:",
        "row_backend": "Bildschirmquelle:",
        "band_dark": "dunkel",
        "band_normal": "hell",
        "band_bright": "sehr hell",
        "group_screen": "Bildschirm",
        "screen_dark": "Im Dunkeln:",
        "screen_normal": "Bei Licht:",
        "screen_bright": "Bei hellem Licht:",
        "threshold_dark": "Als dunkel gilt unter:",
        "threshold_bright": "Als hell gilt über:",
        "manual_pause": "Pause nach manueller Änderung:",
        "hysteresis_note": (
            "Hysterese: Verlassen von „dunkel“ bei +8 lx und von „hell“ bei "
            "−30 lx, damit die Beleuchtung an der Grenze nicht flackert."
        ),
        "group_keyboard": "Tastatur",
        "kbd_off_light": "Bei Licht vollständig ausschalten",
        "group_camera": "Kamera",
        "cam_dark": "Verstärkung im Dunkeln:",
        "cam_normal": "Verstärkung bei Licht:",
        "cam_bright": "Verstärkung bei hellem Licht:",
        "cam_note": "Die Bildrate ist immer 30 fps — keine Verlangsamung im Dunkeln.",
        "button_apply": "Anwenden",
        "button_reset": "Zurücksetzen",
        "button_restart": "Dienst neu starten",
        "button_resume": "Steuerung zurückholen",
        "footer_hint": (
            "Einstellungen werden in ~/.config/ambient-auto/config.json "
            "gespeichert und innerhalb von 2 Sekunden übernommen."
        ),
        "status_ready": "Bereit",
        "status_saved": "Gespeichert — wird in 2 Sekunden übernommen",
        "status_enabled": "Automatik eingeschaltet",
        "status_disabled": "Automatik ausgeschaltet",
        "status_reset": "Werte zurückgesetzt — „Anwenden“ drücken",
        "status_resumed": "Steuerung an die Automatik zurückgegeben",
        "status_restarted": "Dienst neu gestartet",
        "status_restart_failed": "Dienst wurde nicht neu gestartet",
        "no_data": "keine Daten",
        "auto_off": "Automatik ausgeschaltet",
        "no_link": "keine Verbindung",
        "service_down": "Der Dienst läuft nicht oder antwortet noch nicht.",
        "auto_working": "Die Automatik regelt die Helligkeit über den Sensor.",
        "auto_off_hint": (
            "Automatik aus: Helligkeit und Beleuchtung ändern sich nicht. "
            "Schalten Sie den Schalter oben ein."
        ),
        "pause_left": (
            "Pause nach manueller Änderung: {minutes}:{seconds:02d}. "
            "Die Automatik übernimmt wieder automatisch oder per Schaltfläche."
        ),
        "dialog_thresholds_title": "Schwellenwerte prüfen",
        "dialog_thresholds_text": (
            "Die Schwelle „hell“ muss mindestens {gap} lx über der Schwelle "
            "„dunkel“ liegen."
        ),
        "dialog_save_title": "Speichern fehlgeschlagen",
        "dialog_save_text": "{path} kann nicht geschrieben werden:\n{error}",
        "dialog_reset_title": "Einstellungen zurücksetzen",
        "dialog_reset_text": "Standardwerte wiederherstellen?",
        "dialog_error_title": "Fehler",
        "dialog_restart_error": "Neustart fehlgeschlagen: {error}",
        "dialog_error_generic": "Der Befehl ist mit einem Fehler beendet.",
        "backend_direct": "direkt",
        "camera_line": "{fps} fps, Verstärkung {gain}",
        "msg_start": "Start",
        "msg_config_reloaded": "Einstellungen aktualisiert",
        "msg_enabled_on": "Automatik eingeschaltet",
        "msg_enabled_off": "Automatik ausgeschaltet",
        "msg_manual_override": (
            "Helligkeit manuell geändert — Steuerung wird zurückgeholt"
        ),
        "msg_manual_override_pause": (
            "Helligkeit manuell geändert ({percent}%) — Pause {minutes} Min."
        ),
        "msg_screen_kwin": "Bildschirm: Steuerung über KWin/KScreen",
        "msg_screen_sysfs": "KWin nicht verfügbar — schreibe vorübergehend in sysfs",
        "msg_camera_applied": "Kamera: Verstärkung {gain}, {fps} fps",
        "msg_camera_busy": "Kamera geöffnet — Einstellungen angewendet",
        "msg_apply_summary": (
            "Bildschirm {screen}%, Tastatur {kbd}%, Kamera {gain} ({fps} fps)"
        ),
        "unit_percent": " %",
        "unit_lux": " lx",
        "unit_min": " Min.",
        "unit_fps": "fps",
        "pause_never": "nie",
    },
    "es": {
        "window_title": "Brillo automático del MacBook",
        "header_title": "Brillo automático del MacBook",
        "switch_enabled": "Reaccionar a la luz ambiental",
        "language_label": "Idioma:",
        "language_system": "Idioma del sistema",
        "group_now": "Ahora",
        "row_lux": "Iluminación:",
        "row_band": "Banda:",
        "row_screen": "Pantalla:",
        "row_keyboard": "Teclado:",
        "row_camera": "Cámara:",
        "row_backend": "Fuente de la pantalla:",
        "band_dark": "oscuro",
        "band_normal": "luz",
        "band_bright": "muy claro",
        "group_screen": "Pantalla",
        "screen_dark": "En la oscuridad:",
        "screen_normal": "Con luz:",
        "screen_bright": "Con luz intensa:",
        "threshold_dark": "Considerar oscuro por debajo de:",
        "threshold_bright": "Considerar claro por encima de:",
        "manual_pause": "Pausa tras cambio manual:",
        "hysteresis_note": (
            "Histéresis: salida de «oscuro» a +8 lx y de «claro» a −30 lx, "
            "para que la luz no parpadee en el límite."
        ),
        "group_keyboard": "Teclado",
        "kbd_off_light": "Apagar por completo con luz",
        "group_camera": "Cámara",
        "cam_dark": "Ganancia en la oscuridad:",
        "cam_normal": "Ganancia con luz:",
        "cam_bright": "Ganancia con luz intensa:",
        "cam_note": "La frecuencia es siempre de 30 fps: sin ralentización en la oscuridad.",
        "button_apply": "Aplicar",
        "button_reset": "Restablecer",
        "button_restart": "Reiniciar el servicio",
        "button_resume": "Recuperar el control",
        "footer_hint": (
            "La configuración se guarda en ~/.config/ambient-auto/config.json "
            "y se aplica en 2 segundos."
        ),
        "status_ready": "Listo",
        "status_saved": "Guardado: se aplicará en 2 segundos",
        "status_enabled": "Automatización activada",
        "status_disabled": "Automatización desactivada",
        "status_reset": "Valores restablecidos: pulse «Aplicar»",
        "status_resumed": "Control devuelto a la automatización",
        "status_restarted": "Servicio reiniciado",
        "status_restart_failed": "No se pudo reiniciar el servicio",
        "no_data": "sin datos",
        "auto_off": "automatización desactivada",
        "no_link": "sin conexión",
        "service_down": "El servicio no está en marcha o aún no responde.",
        "auto_working": "La automatización controla el brillo según el sensor.",
        "auto_off_hint": (
            "Automatización desactivada: el brillo y la luz no cambian. "
            "Active el interruptor de arriba."
        ),
        "pause_left": (
            "Pausa tras cambio manual: {minutes}:{seconds:02d}. "
            "La automatización recuperará el control sola o con el botón."
        ),
        "dialog_thresholds_title": "Compruebe los umbrales",
        "dialog_thresholds_text": (
            "El umbral «claro» debe ser al menos {gap} lx mayor que el umbral "
            "«oscuro»."
        ),
        "dialog_save_title": "No se pudo guardar",
        "dialog_save_text": "No se puede escribir {path}:\n{error}",
        "dialog_reset_title": "Restablecer configuración",
        "dialog_reset_text": "¿Restaurar los valores predeterminados?",
        "dialog_error_title": "Error",
        "dialog_restart_error": "No se pudo reiniciar: {error}",
        "dialog_error_generic": "El comando terminó con un error.",
        "backend_direct": "directo",
        "camera_line": "{fps} fps, ganancia {gain}",
        "msg_start": "Inicio",
        "msg_config_reloaded": "Configuración actualizada",
        "msg_enabled_on": "Automatización activada",
        "msg_enabled_off": "Automatización desactivada",
        "msg_manual_override": "Brillo cambiado manualmente: recupero el control",
        "msg_manual_override_pause": (
            "Brillo cambiado manualmente ({percent}%): pausa de {minutes} min"
        ),
        "msg_screen_kwin": "Pantalla: control mediante KWin/KScreen",
        "msg_screen_sysfs": "KWin no disponible: escribo temporalmente en sysfs",
        "msg_camera_applied": "Cámara: ganancia {gain}, {fps} fps",
        "msg_camera_busy": "Cámara abierta: configuración aplicada",
        "msg_apply_summary": (
            "Pantalla {screen}%, teclado {kbd}%, cámara {gain} ({fps} fps)"
        ),
        "unit_percent": " %",
        "unit_lux": " lx",
        "unit_min": " min",
        "unit_fps": "fps",
        "pause_never": "nunca",
    },
    "fr": {
        "window_title": "Luminosité automatique du MacBook",
        "header_title": "Luminosité automatique du MacBook",
        "switch_enabled": "Réagir à la lumière ambiante",
        "language_label": "Langue :",
        "language_system": "Langue du système",
        "group_now": "Maintenant",
        "row_lux": "Éclairement :",
        "row_band": "Plage :",
        "row_screen": "Écran :",
        "row_keyboard": "Clavier :",
        "row_camera": "Caméra :",
        "row_backend": "Source de l'écran :",
        "band_dark": "sombre",
        "band_normal": "éclairé",
        "band_bright": "très clair",
        "group_screen": "Écran",
        "screen_dark": "Dans l'obscurité :",
        "screen_normal": "À la lumière :",
        "screen_bright": "En pleine lumière :",
        "threshold_dark": "Considérer sombre en dessous de :",
        "threshold_bright": "Considérer clair au-dessus de :",
        "manual_pause": "Pause après réglage manuel :",
        "hysteresis_note": (
            "Hystérésis : sortie de « sombre » à +8 lx et de « clair » à −30 lx, "
            "pour éviter le clignotement à la limite."
        ),
        "group_keyboard": "Clavier",
        "kbd_off_light": "Éteindre complètement à la lumière",
        "group_camera": "Caméra",
        "cam_dark": "Gain dans l'obscurité :",
        "cam_normal": "Gain à la lumière :",
        "cam_bright": "Gain en pleine lumière :",
        "cam_note": (
            "La fréquence est toujours de 30 images/s : aucun ralentissement "
            "dans l'obscurité."
        ),
        "button_apply": "Appliquer",
        "button_reset": "Réinitialiser",
        "button_restart": "Redémarrer le service",
        "button_resume": "Reprendre le contrôle",
        "footer_hint": (
            "Les réglages sont enregistrés dans ~/.config/ambient-auto/config.json "
            "et appliqués en 2 secondes."
        ),
        "status_ready": "Prêt",
        "status_saved": "Enregistré — appliqué dans 2 secondes",
        "status_enabled": "Automatisme activé",
        "status_disabled": "Automatisme désactivé",
        "status_reset": "Valeurs réinitialisées — cliquez sur « Appliquer »",
        "status_resumed": "Contrôle rendu à l'automatisme",
        "status_restarted": "Service redémarré",
        "status_restart_failed": "Le service n'a pas redémarré",
        "no_data": "aucune donnée",
        "auto_off": "automatisme désactivé",
        "no_link": "pas de connexion",
        "service_down": "Le service n'est pas démarré ou ne répond pas encore.",
        "auto_working": "L'automatisme règle la luminosité selon le capteur.",
        "auto_off_hint": (
            "Automatisme désactivé : la luminosité et le rétroéclairage ne "
            "changent pas. Activez l'interrupteur en haut."
        ),
        "pause_left": (
            "Pause après réglage manuel : {minutes}:{seconds:02d}. "
            "L'automatisme reprendra le contrôle seul ou via le bouton."
        ),
        "dialog_thresholds_title": "Vérifiez les seuils",
        "dialog_thresholds_text": (
            "Le seuil « clair » doit être supérieur d'au moins {gap} lx au seuil "
            "« sombre »."
        ),
        "dialog_save_title": "Enregistrement impossible",
        "dialog_save_text": "Impossible d'écrire {path} :\n{error}",
        "dialog_reset_title": "Réinitialiser les réglages",
        "dialog_reset_text": "Revenir aux valeurs par défaut ?",
        "dialog_error_title": "Erreur",
        "dialog_restart_error": "Échec du redémarrage : {error}",
        "dialog_error_generic": "La commande s'est terminée par une erreur.",
        "backend_direct": "direct",
        "camera_line": "{fps} i/s, gain {gain}",
        "msg_start": "Démarrage",
        "msg_config_reloaded": "Réglages mis à jour",
        "msg_enabled_on": "Automatisme activé",
        "msg_enabled_off": "Automatisme désactivé",
        "msg_manual_override": (
            "Luminosité modifiée manuellement — je reprends le contrôle"
        ),
        "msg_manual_override_pause": (
            "Luminosité modifiée manuellement ({percent} %) — pause de {minutes} min"
        ),
        "msg_screen_kwin": "Écran : contrôle via KWin/KScreen",
        "msg_screen_sysfs": "KWin indisponible — écriture temporaire dans sysfs",
        "msg_camera_applied": "Caméra : gain {gain}, {fps} i/s",
        "msg_camera_busy": "Caméra ouverte — réglages appliqués",
        "msg_apply_summary": (
            "Écran {screen} %, clavier {kbd} %, caméra {gain} ({fps} i/s)"
        ),
        "unit_percent": " %",
        "unit_lux": " lx",
        "unit_min": " min",
        "unit_fps": "i/s",
        "pause_never": "jamais",
    },
}

# Ключи событий демона, которые умеет переводить приложение.
MESSAGE_KEYS = (
    "start",
    "config_reloaded",
    "enabled_on",
    "enabled_off",
    "manual_override",
    "manual_override_pause",
    "screen_kwin",
    "screen_sysfs",
    "camera_applied",
    "camera_busy",
    "apply_summary",
)


def look(text, key):
    """Перевод для конкретного языка с откатом на английский."""
    table = STRINGS.get(text) or STRINGS[DEFAULT_LANGUAGE]
    return table.get(key) or STRINGS[DEFAULT_LANGUAGE].get(key) or key


def t(language, key, **params):
    text = look(language, key)
    if params:
        try:
            return text.format(**params)
        except (KeyError, IndexError, ValueError):
            return text
    return text


def detect_system_language():
    """Язык интерфейса по локали сеанса."""
    for name in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(name, "")
        if not value:
            continue
        code = value.split(":")[0].split(".")[0].split("_")[0].lower()
        if code in STRINGS:
            return code
    return DEFAULT_LANGUAGE


def resolve_language(setting):
    """Превращает значение из конфига в конкретный язык."""
    if not setting or setting == "system":
        return detect_system_language()
    if setting in STRINGS:
        return setting
    return detect_system_language()


def normalize_language(setting):
    """Приводит значение из конфига к допустимому."""
    if setting in STRINGS or setting == "system":
        return setting
    return "system"
