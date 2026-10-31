#!/usr/bin/env python3
"""Приложение управления автоподсветкой MacBook.

Пишет настройки в ~/.config/ambient-auto/config.json, демон ambient-auto
подхватывает их в течение пары секунд. Показывает текущее состояние из
/run/ambient-auto/status.json.

Интерфейс переводится на несколько языков (см. i18n.py). Выбранный язык
хранится в конфиге ключом ``language`` и применяется сразу, без перезапуска.
"""

import copy
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from i18n import (
    LANGUAGES,
    MESSAGE_KEYS,
    normalize_language,
    resolve_language,
    t,
)

CONFIG_DIR = Path.home() / ".config" / "ambient-auto"
CONFIG_PATH = Path(os.environ.get("AMBIENT_CONFIG", CONFIG_DIR / "config.json"))
STATUS_PATH = Path(os.environ.get("AMBIENT_STATUS", "/run/ambient-auto/status.json"))
ICON_PATH = "/usr/share/icons/hicolor/scalable/apps/ambient-auto.svg"

BAND_KEYS = {"dark": "band_dark", "normal": "band_normal", "bright": "band_bright"}

HYSTERESIS_DARK = 8      # лк: выходим из «темно» чуть позже
HYSTERESIS_BRIGHT = 30   # лк: выходим из «ярко» чуть раньше
MIN_GAP = 40             # минимальная разница между порогами, лк

DEFAULTS = {
    "enabled": True,
    "poll_seconds": 2.0,
    "manual_pause_minutes": 0,
    "language": "system",
    "screen": {
        "dark": 5,
        "normal": 15,
        "bright": 35,
        "dark_enter": 12,
        "dark_exit": 20,
        "bright_enter": 100,
        "bright_exit": 70,
    },
    "keyboard": {
        "dark": 60,
        "normal": 0,
        "bright": 0,
        "dark_enter": 12,
        "dark_exit": 20,
        "bright_enter": 100,
        "bright_exit": 70,
    },
    "camera": {
        "dark": 200,
        "normal": 128,
        "bright": 128,
        "fps": 30,
    },
}


class ValidationError(Exception):
    pass


def load_config():
    cfg = copy.deepcopy(DEFAULTS)
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError):
        return cfg
    if not isinstance(raw, dict):
        return cfg

    def merge(section, source):
        if isinstance(source, dict):
            for key in section:
                if key in source and isinstance(source[key], (int, float)):
                    section[key] = int(source[key])

    if "enabled" in raw:
        cfg["enabled"] = bool(raw["enabled"])
    merge(cfg["screen"], raw.get("screen"))
    merge(cfg["keyboard"], raw.get("keyboard"))
    merge(cfg["camera"], raw.get("camera"))
    for key in ("poll_seconds", "manual_pause_minutes"):
        if isinstance(raw.get(key), (int, float)):
            cfg[key] = raw[key]
    cfg["language"] = normalize_language(raw.get("language"))
    return cfg


def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    temporary = CONFIG_PATH.with_suffix(".json.tmp")
    with open(temporary, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(temporary, CONFIG_PATH)


def read_status():
    try:
        with open(STATUS_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def percent_box(low=0, high=100):
    box = QSpinBox()
    box.setRange(low, high)
    box.setSingleStep(1)
    box.setMinimumWidth(90)
    return box


def lux_box():
    box = QSpinBox()
    box.setRange(0, 5000)
    box.setSingleStep(5)
    box.setMinimumWidth(100)
    return box


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(860, 900)
        self.setMinimumSize(760, 700)

        self._kbd_backup = (25, 0)
        self._loading = True
        self._lang_setting = "system"
        self._lang = resolve_language("system")
        self._row_labels = []

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_status())
        devices = QHBoxLayout()
        devices.setSpacing(12)
        devices.addWidget(self._build_screen_group(), 1)
        devices.addWidget(self._build_keyboard_group(), 1)
        layout.addLayout(devices)
        layout.addWidget(self._build_camera_group())
        layout.addLayout(self._build_buttons())

        self.note_footer = QLabel()
        self.note_footer.setWordWrap(True)
        self.note_footer.setStyleSheet("color: palette(mid);")
        layout.addWidget(self.note_footer)
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(central)
        self.setCentralWidget(scroll)

        cfg = load_config()
        self._lang_setting = normalize_language(cfg.get("language"))
        self._lang = resolve_language(self._lang_setting)
        self._load_into_widgets(cfg)
        self._retranslate()
        self._loading = False

        self.statusBar().showMessage(self._t("status_ready"))

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_status)
        self._timer.start(1000)
        self._update_status()

    # ---------- перевод ----------

    def _t(self, key, **params):
        return t(self._lang, key, **params)

    def _caption(self, key):
        label = QLabel()
        self._row_labels.append((label, key))
        return label

    def _fill_language_combo(self):
        self.combo_language.blockSignals(True)
        self.combo_language.clear()
        for code, native in LANGUAGES:
            text = self._t("language_system") if code == "system" else native
            self.combo_language.addItem(text, code)
        index = self.combo_language.findData(self._lang_setting)
        self.combo_language.setCurrentIndex(index if index >= 0 else 0)
        self.combo_language.blockSignals(False)

    def _retranslate(self):
        self._lang = resolve_language(self._lang_setting)

        self.setWindowTitle(self._t("window_title"))
        self.label_title.setText(self._t("header_title"))
        self.switch_enabled.setText(self._t("switch_enabled"))
        self.label_language.setText(self._t("language_label"))
        self._fill_language_combo()

        self.group_now.setTitle(self._t("group_now"))
        for label, key in self._row_labels:
            label.setText(self._t(key))

        self.group_screen.setTitle(self._t("group_screen"))
        self.group_keyboard.setTitle(self._t("group_keyboard"))
        self.group_camera.setTitle(self._t("group_camera"))
        self.note_hysteresis.setText(self._t("hysteresis_note"))
        self.note_camera.setText(self._t("cam_note"))
        self.note_footer.setText(self._t("footer_hint"))

        self.chk_kbd_off.setText(self._t("kbd_off_light"))
        self.button_apply.setText(self._t("button_apply"))
        self.button_reset.setText(self._t("button_reset"))
        self.button_restart.setText(self._t("button_restart"))
        self.button_resume.setText(self._t("button_resume"))

        self._apply_units()
        self._update_status()

    def _apply_units(self):
        for box in (
            self.sp_screen_dark,
            self.sp_screen_normal,
            self.sp_screen_bright,
            self.sp_kbd_dark,
            self.sp_kbd_normal,
            self.sp_kbd_bright,
        ):
            box.setSuffix(self._t("unit_percent"))
        for box in (
            self.sp_screen_dark_enter,
            self.sp_screen_bright_enter,
            self.sp_kbd_dark_enter,
            self.sp_kbd_bright_enter,
        ):
            box.setSuffix(self._t("unit_lux"))
        self.sp_pause.setSuffix(self._t("unit_min"))
        self.sp_pause.setSpecialValueText(self._t("pause_never"))

    # ---------- интерфейс ----------

    def _build_header(self):
        box = QHBoxLayout()
        self.label_title = QLabel()
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.label_title.setFont(font)
        box.addWidget(self.label_title)
        box.addStretch(1)

        self.label_language = QLabel()
        self.combo_language = QComboBox()
        self.combo_language.setMinimumWidth(140)
        self.combo_language.currentIndexChanged.connect(self._on_language_changed)
        box.addWidget(self.label_language)
        box.addWidget(self.combo_language)

        self.switch_enabled = QCheckBox()
        self.switch_enabled.setStyleSheet("font-weight: 600;")
        self.switch_enabled.toggled.connect(self._on_enabled_toggled)
        box.addWidget(self.switch_enabled)
        return box

    def _build_status(self):
        self.group_now = QGroupBox()
        grid = QGridLayout(self.group_now)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(8)

        self.label_lux = QLabel("—")
        self.label_lux.setStyleSheet("font-size: 20px; font-weight: 600;")
        self.label_band = QLabel("—")
        self.label_screen = QLabel("—")
        self.label_keyboard = QLabel("—")
        self.label_camera = QLabel("—")
        self.label_backend = QLabel("—")
        self.label_pause = QLabel()
        self.label_pause.setWordWrap(True)

        grid.addWidget(self._caption("row_lux"), 0, 0)
        grid.addWidget(self.label_lux, 0, 1)
        grid.addWidget(self._caption("row_band"), 0, 2)
        grid.addWidget(self.label_band, 0, 3)
        grid.addWidget(self._caption("row_screen"), 1, 0)
        grid.addWidget(self.label_screen, 1, 1)
        grid.addWidget(self._caption("row_keyboard"), 1, 2)
        grid.addWidget(self.label_keyboard, 1, 3)
        grid.addWidget(self._caption("row_camera"), 2, 0)
        grid.addWidget(self.label_camera, 2, 1)
        grid.addWidget(self._caption("row_backend"), 2, 2)
        grid.addWidget(self.label_backend, 2, 3)

        pause_box = QHBoxLayout()
        pause_box.addWidget(self.label_pause, 1)
        self.button_resume = QPushButton()
        self.button_resume.clicked.connect(self._on_resume)
        self.button_resume.setVisible(False)
        pause_box.addWidget(self.button_resume)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(self.group_now)
        wrapper_layout.addLayout(pause_box)
        return wrapper

    def _build_screen_group(self):
        self.group_screen = QGroupBox()
        form = QFormLayout(self.group_screen)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(8)

        self.sp_screen_dark = percent_box(1, 100)
        self.sp_screen_normal = percent_box(1, 100)
        self.sp_screen_bright = percent_box(1, 100)
        self.sp_screen_dark_enter = lux_box()
        self.sp_screen_bright_enter = lux_box()
        self.sp_pause = QSpinBox()
        self.sp_pause.setRange(0, 60)
        self.sp_pause.setMinimumWidth(120)

        form.addRow(self._caption("screen_dark"), self.sp_screen_dark)
        form.addRow(self._caption("screen_normal"), self.sp_screen_normal)
        form.addRow(self._caption("screen_bright"), self.sp_screen_bright)
        form.addRow(self._caption("threshold_dark"), self.sp_screen_dark_enter)
        form.addRow(self._caption("threshold_bright"), self.sp_screen_bright_enter)
        form.addRow(self._caption("manual_pause"), self.sp_pause)

        self.note_hysteresis = QLabel()
        self.note_hysteresis.setWordWrap(True)
        self.note_hysteresis.setStyleSheet("color: palette(mid);")
        form.addRow(self.note_hysteresis)
        return self.group_screen

    def _build_keyboard_group(self):
        self.group_keyboard = QGroupBox()
        form = QFormLayout(self.group_keyboard)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(8)

        self.sp_kbd_dark = percent_box(0, 100)
        self.sp_kbd_normal = percent_box(0, 100)
        self.sp_kbd_bright = percent_box(0, 100)
        self.sp_kbd_dark_enter = lux_box()
        self.sp_kbd_bright_enter = lux_box()
        self.chk_kbd_off = QCheckBox()
        self.chk_kbd_off.toggled.connect(self._on_kbd_off_toggled)

        form.addRow(self.chk_kbd_off)
        form.addRow(self._caption("screen_dark"), self.sp_kbd_dark)
        form.addRow(self._caption("screen_normal"), self.sp_kbd_normal)
        form.addRow(self._caption("screen_bright"), self.sp_kbd_bright)
        form.addRow(self._caption("threshold_dark"), self.sp_kbd_dark_enter)
        form.addRow(self._caption("threshold_bright"), self.sp_kbd_bright_enter)
        return self.group_keyboard

    def _build_camera_group(self):
        self.group_camera = QGroupBox()
        form = QFormLayout(self.group_camera)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(8)

        self.sp_cam_dark = QSpinBox()
        self.sp_cam_normal = QSpinBox()
        self.sp_cam_bright = QSpinBox()
        for box in (self.sp_cam_dark, self.sp_cam_normal, self.sp_cam_bright):
            box.setRange(0, 255)
            box.setSingleStep(5)
            box.setMinimumWidth(90)

        form.addRow(self._caption("cam_dark"), self.sp_cam_dark)
        form.addRow(self._caption("cam_normal"), self.sp_cam_normal)
        form.addRow(self._caption("cam_bright"), self.sp_cam_bright)

        self.note_camera = QLabel()
        self.note_camera.setWordWrap(True)
        self.note_camera.setStyleSheet("color: palette(mid);")
        form.addRow(self.note_camera)
        return self.group_camera

    def _build_buttons(self):
        box = QHBoxLayout()
        self.button_apply = QPushButton()
        self.button_apply.setDefault(True)
        self.button_apply.setMinimumHeight(34)
        self.button_apply.clicked.connect(self._on_apply)
        self.button_reset = QPushButton()
        self.button_reset.clicked.connect(self._on_reset)
        self.button_restart = QPushButton()
        self.button_restart.clicked.connect(self._on_restart)
        box.addWidget(self.button_apply)
        box.addWidget(self.button_reset)
        box.addStretch(1)
        box.addWidget(self.button_restart)
        return box

    # ---------- загрузка и сохранение ----------

    def _load_into_widgets(self, cfg):
        self.switch_enabled.setChecked(bool(cfg["enabled"]))
        self._lang_setting = normalize_language(cfg.get("language"))
        self._fill_language_combo()

        screen = cfg["screen"]
        self.sp_screen_dark.setValue(int(screen["dark"]))
        self.sp_screen_normal.setValue(int(screen["normal"]))
        self.sp_screen_bright.setValue(int(screen["bright"]))
        self.sp_screen_dark_enter.setValue(int(screen["dark_enter"]))
        self.sp_screen_bright_enter.setValue(int(screen["bright_enter"]))
        self.sp_pause.setValue(int(cfg.get("manual_pause_minutes", 0)))

        keyboard = cfg["keyboard"]
        self.sp_kbd_dark.setValue(int(keyboard["dark"]))
        normal, bright = int(keyboard["normal"]), int(keyboard["bright"])
        if normal == 0 and bright == 0:
            self._kbd_backup = (25, 0)
            self.chk_kbd_off.setChecked(True)
        else:
            self._kbd_backup = (normal, bright)
            self.chk_kbd_off.setChecked(False)
        self.sp_kbd_normal.setValue(normal)
        self.sp_kbd_bright.setValue(bright)
        self._sync_kbd_off_state()
        self.sp_kbd_dark_enter.setValue(int(keyboard["dark_enter"]))
        self.sp_kbd_bright_enter.setValue(int(keyboard["bright_enter"]))

        camera = cfg["camera"]
        self.sp_cam_dark.setValue(int(camera["dark"]))
        self.sp_cam_normal.setValue(int(camera["normal"]))
        self.sp_cam_bright.setValue(int(camera["bright"]))

    def _collect(self):
        cfg = copy.deepcopy(DEFAULTS)
        cfg["enabled"] = self.switch_enabled.isChecked()
        cfg["language"] = normalize_language(self._lang_setting)

        for device, dark_enter, bright_enter in (
            ("screen", self.sp_screen_dark_enter, self.sp_screen_bright_enter),
            ("keyboard", self.sp_kbd_dark_enter, self.sp_kbd_bright_enter),
        ):
            enter_dark = dark_enter.value()
            enter_bright = bright_enter.value()
            if enter_bright - enter_dark < MIN_GAP:
                raise ValidationError(
                    self._t("dialog_thresholds_text", gap=MIN_GAP)
                )
            cfg[device]["dark_enter"] = enter_dark
            cfg[device]["dark_exit"] = enter_dark + HYSTERESIS_DARK
            cfg[device]["bright_enter"] = enter_bright
            cfg[device]["bright_exit"] = max(
                enter_dark + HYSTERESIS_DARK + 1, enter_bright - HYSTERESIS_BRIGHT
            )

        cfg["screen"]["dark"] = self.sp_screen_dark.value()
        cfg["screen"]["normal"] = self.sp_screen_normal.value()
        cfg["screen"]["bright"] = self.sp_screen_bright.value()

        cfg["keyboard"]["dark"] = self.sp_kbd_dark.value()
        if self.chk_kbd_off.isChecked():
            cfg["keyboard"]["normal"] = 0
            cfg["keyboard"]["bright"] = 0
        else:
            cfg["keyboard"]["normal"] = self.sp_kbd_normal.value()
            cfg["keyboard"]["bright"] = self.sp_kbd_bright.value()

        cfg["camera"]["dark"] = self.sp_cam_dark.value()
        cfg["camera"]["normal"] = self.sp_cam_normal.value()
        cfg["camera"]["bright"] = self.sp_cam_bright.value()
        cfg["camera"]["fps"] = 30
        cfg["manual_pause_minutes"] = self.sp_pause.value()
        return cfg

    def _apply(self, quiet=False):
        try:
            cfg = self._collect()
        except ValidationError as error:
            QMessageBox.warning(self, self._t("dialog_thresholds_title"), str(error))
            return False
        try:
            save_config(cfg)
        except OSError as error:
            QMessageBox.critical(
                self,
                self._t("dialog_save_title"),
                self._t("dialog_save_text", path=CONFIG_PATH, error=error),
            )
            return False
        if cfg["language"] != self._lang_setting:
            self._lang_setting = cfg["language"]
            self._retranslate()
        if not quiet:
            self.statusBar().showMessage(self._t("status_saved"), 5000)
        return True

    # ---------- реакции ----------

    def _on_language_changed(self, index):
        if self._loading:
            return
        code = self.combo_language.itemData(index)
        if not code or code == self._lang_setting:
            return
        previous = self._lang_setting
        self._lang_setting = code
        try:
            cfg = self._collect()
            save_config(cfg)
        except ValidationError as error:
            self._lang_setting = previous
            self._fill_language_combo()
            QMessageBox.warning(self, self._t("dialog_thresholds_title"), str(error))
            return
        except OSError as error:
            self._lang_setting = previous
            self._fill_language_combo()
            QMessageBox.critical(
                self,
                self._t("dialog_save_title"),
                self._t("dialog_save_text", path=CONFIG_PATH, error=error),
            )
            return
        self._retranslate()
        self.statusBar().showMessage(self._t("status_saved"), 5000)

    def _on_enabled_toggled(self, checked):
        if self._loading:
            return
        try:
            cfg = self._collect()
        except ValidationError as error:
            self._loading = True
            self.switch_enabled.setChecked(not checked)
            self._loading = False
            QMessageBox.warning(self, self._t("dialog_thresholds_title"), str(error))
            return
        cfg["enabled"] = checked
        try:
            save_config(cfg)
        except OSError as error:
            self._loading = True
            self.switch_enabled.setChecked(not checked)
            self._loading = False
            QMessageBox.critical(
                self,
                self._t("dialog_save_title"),
                self._t("dialog_save_text", path=CONFIG_PATH, error=error),
            )
            return
        self.statusBar().showMessage(
            self._t("status_enabled" if checked else "status_disabled"), 5000
        )

    def _on_kbd_off_toggled(self, checked):
        if checked:
            normal = self.sp_kbd_normal.value()
            bright = self.sp_kbd_bright.value()
            if normal or bright:
                self._kbd_backup = (normal, bright)
        self._sync_kbd_off_state()
        if not checked:
            normal, bright = self._kbd_backup
            self.sp_kbd_normal.setValue(normal)
            self.sp_kbd_bright.setValue(bright)

    def _sync_kbd_off_state(self):
        off = self.chk_kbd_off.isChecked()
        self.sp_kbd_normal.setEnabled(not off)
        self.sp_kbd_bright.setEnabled(not off)
        if off:
            self.sp_kbd_normal.setValue(0)
            self.sp_kbd_bright.setValue(0)

    def _on_apply(self):
        self._apply()

    def _on_reset(self):
        if (
            QMessageBox.question(
                self,
                self._t("dialog_reset_title"),
                self._t("dialog_reset_text"),
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self._loading = True
        self._load_into_widgets(copy.deepcopy(DEFAULTS))
        self._loading = False
        self.statusBar().showMessage(self._t("status_reset"))

    def _on_resume(self):
        self._apply(quiet=True)
        self.statusBar().showMessage(self._t("status_resumed"), 5000)
        QTimer.singleShot(1500, self._update_status)

    def _on_restart(self):
        try:
            result = subprocess.run(
                ["/usr/bin/pkexec", "systemctl", "restart", "ambient-auto.service"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError) as error:
            QMessageBox.critical(
                self,
                self._t("dialog_error_title"),
                self._t("dialog_restart_error", error=error),
            )
            return
        if result.returncode == 0:
            self.statusBar().showMessage(self._t("status_restarted"), 5000)
        else:
            detail = result.stderr.decode(errors="replace").strip()
            QMessageBox.warning(
                self,
                self._t("status_restart_failed"),
                detail or self._t("dialog_error_generic"),
            )

    # ---------- живое состояние ----------

    def _daemon_message(self, status):
        key = status.get("message_key")
        if isinstance(key, str) and key in MESSAGE_KEYS:
            params = status.get("message_params")
            if isinstance(params, dict):
                return self._t("msg_" + key, **params)
            return self._t("msg_" + key)
        message = status.get("message")
        return str(message) if message else None

    def _update_status(self):
        status = read_status()
        if status is None:
            self.label_lux.setText("—")
            self.label_band.setText(self._t("no_data"))
            self.label_screen.setText("—")
            self.label_keyboard.setText("—")
            self.label_camera.setText("—")
            self.label_backend.setText("—")
            self.label_pause.setText(self._t("service_down"))
            self.button_resume.setVisible(False)
            return

        age = time.time() - float(status.get("time", 0))
        enabled = bool(status.get("enabled"))
        band_key = BAND_KEYS.get(str(status.get("band")))
        self.label_lux.setText(
            f"{int(status.get('lux', 0))}{self._t('unit_lux')}"
        )

        if not enabled:
            self.label_band.setText(self._t("auto_off"))
        elif age > 10:
            self.label_band.setText(self._t("no_link"))
        elif band_key:
            self.label_band.setText(self._t(band_key))
        else:
            self.label_band.setText("—")

        screen = status.get("screen") or {}
        keyboard = status.get("keyboard") or {}
        camera = status.get("camera") or {}

        screen_percent = screen.get("percent")
        self.label_screen.setText(
            f"{int(screen_percent)}{self._t('unit_percent')}"
            if screen_percent is not None
            else "—"
        )
        self.label_keyboard.setText(
            f"{int(keyboard.get('percent', 0))}{self._t('unit_percent')}"
        )
        self.label_camera.setText(
            self._t(
                "camera_line",
                fps=int(camera.get("fps", 30)),
                gain=int(camera.get("gain", 0)),
            )
        )
        backend = screen.get("backend")
        if backend == "kwin":
            self.label_backend.setText("KWin")
        elif backend == "sysfs":
            self.label_backend.setText(self._t("backend_direct"))
        else:
            self.label_backend.setText("—")

        paused_until = float(screen.get("paused_until") or 0)
        if enabled and paused_until > time.time():
            left = int(paused_until - time.time())
            self.label_pause.setText(
                self._t("pause_left", minutes=left // 60, seconds=left % 60)
            )
            self.button_resume.setVisible(True)
        elif not enabled:
            self.label_pause.setText(self._t("auto_off_hint"))
            self.button_resume.setVisible(False)
        else:
            self.label_pause.setText(self._t("auto_working"))
            self.button_resume.setVisible(False)

        message = self._daemon_message(status)
        if message and age <= 10:
            self.statusBar().showMessage(message, 4000)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ambient-auto")
    app.setApplicationDisplayName(t(resolve_language("system"), "window_title"))
    window = MainWindow()

    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == "--screenshot":
        window.show()
        app.processEvents()
        window.grab().save(args[1])
        return 0

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
