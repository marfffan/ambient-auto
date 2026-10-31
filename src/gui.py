#!/usr/bin/env python3
"""Приложение управления автоподсветкой MacBook.

Пишет настройки в ~/.config/ambient-auto/config.json, демон ambient-auto
подхватывает их в течение пары секунд. Показывает текущее состояние из
/run/ambient-auto/status.json.
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

CONFIG_DIR = Path.home() / ".config" / "ambient-auto"
CONFIG_PATH = CONFIG_DIR / "config.json"
STATUS_PATH = Path(os.environ.get("AMBIENT_STATUS", "/run/ambient-auto/status.json"))
ICON_PATH = "/usr/share/icons/hicolor/scalable/apps/ambient-auto.svg"

BAND_NAMES = {"dark": "тёмно", "normal": "свет", "bright": "ярко"}
HYSTERESIS_DARK = 8      # лк: выходим из «темно» чуть позже
HYSTERESIS_BRIGHT = 30   # лк: выходим из «ярко» чуть раньше
MIN_GAP = 40             # минимальная разница между порогами, лк

DEFAULTS = {
    "enabled": True,
    "poll_seconds": 2.0,
    "manual_pause_minutes": 0,
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
    return cfg


def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    temporary = CONFIG_DIR / "config.json.tmp"
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
    box.setSuffix(" %")
    box.setSingleStep(1)
    box.setMinimumWidth(90)
    return box


def lux_box():
    box = QSpinBox()
    box.setRange(0, 5000)
    box.setSuffix(" лк")
    box.setSingleStep(5)
    box.setMinimumWidth(100)
    return box


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Автояркость MacBook")
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(820, 900)
        self.setMinimumSize(720, 700)

        self._kbd_backup = (25, 0)
        self._loading = True

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

        hint = QLabel(
            "Настройки сохраняются в ~/.config/ambient-auto/config.json "
            "и применяются в течение 2 секунд."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: palette(mid);")
        layout.addWidget(hint)
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(central)
        self.setCentralWidget(scroll)
        self.statusBar().showMessage("Готово")

        self._load_into_widgets(load_config())
        self._loading = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_status)
        self._timer.start(1000)
        self._update_status()

    # ---------- интерфейс ----------

    def _build_header(self):
        box = QHBoxLayout()
        title = QLabel("Автояркость MacBook")
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        title.setFont(font)
        box.addWidget(title)
        box.addStretch(1)
        self.switch_enabled = QCheckBox("Реагировать на освещение")
        self.switch_enabled.setStyleSheet("font-weight: 600;")
        self.switch_enabled.toggled.connect(self._on_enabled_toggled)
        box.addWidget(self.switch_enabled)
        return box

    def _build_status(self):
        group = QGroupBox("Сейчас")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(8)

        self.label_lux = QLabel("—")
        self.label_lux.setStyleSheet("font-size: 20px; font-weight: 600;")
        self.label_band = QLabel("—")
        self.label_screen = QLabel("—")
        self.label_keyboard = QLabel("—")
        self.label_camera = QLabel("—")
        self.label_backend = QLabel("—")
        self.label_pause = QLabel("")
        self.label_pause.setWordWrap(True)

        grid.addWidget(QLabel("Освещённость:"), 0, 0)
        grid.addWidget(self.label_lux, 0, 1)
        grid.addWidget(QLabel("Полоса:"), 0, 2)
        grid.addWidget(self.label_band, 0, 3)
        grid.addWidget(QLabel("Экран:"), 1, 0)
        grid.addWidget(self.label_screen, 1, 1)
        grid.addWidget(QLabel("Клавиатура:"), 1, 2)
        grid.addWidget(self.label_keyboard, 1, 3)
        grid.addWidget(QLabel("Камера:"), 2, 0)
        grid.addWidget(self.label_camera, 2, 1)
        grid.addWidget(QLabel("Источник экрана:"), 2, 2)
        grid.addWidget(self.label_backend, 2, 3)

        pause_box = QHBoxLayout()
        pause_box.addWidget(self.label_pause)
        pause_box.addStretch(1)
        self.button_resume = QPushButton("Вернуть управление")
        self.button_resume.clicked.connect(self._on_resume)
        self.button_resume.setVisible(False)
        pause_box.addWidget(self.button_resume)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(group)
        wrapper_layout.addLayout(pause_box)
        self._pause_box = pause_box
        self._pause_wrapper = wrapper
        return wrapper

    def _build_screen_group(self):
        group = QGroupBox("Экран")
        form = QFormLayout(group)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(8)

        self.sp_screen_dark = percent_box(1, 100)
        self.sp_screen_normal = percent_box(1, 100)
        self.sp_screen_bright = percent_box(1, 100)
        self.sp_screen_dark_enter = lux_box()
        self.sp_screen_bright_enter = lux_box()
        self.sp_pause = QSpinBox()
        self.sp_pause.setRange(0, 60)
        self.sp_pause.setSuffix(" мин")
        self.sp_pause.setSpecialValueText("не ставить")
        self.sp_pause.setMinimumWidth(120)

        form.addRow("В темноте:", self.sp_screen_dark)
        form.addRow("При свете:", self.sp_screen_normal)
        form.addRow("При ярком свете:", self.sp_screen_bright)
        form.addRow("Считать тёмным ниже:", self.sp_screen_dark_enter)
        form.addRow("Считать ярким выше:", self.sp_screen_bright_enter)
        form.addRow("Пауза после ручной правки:", self.sp_pause)
        note = QLabel(
            "Гистерезис: выход из «темно» на +8 лк, из «ярко» на −30 лк, "
            "чтобы подсветка не дёргалась на границе."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: palette(mid);")
        form.addRow(note)
        return group

    def _build_keyboard_group(self):
        group = QGroupBox("Клавиатура")
        form = QFormLayout(group)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(8)

        self.sp_kbd_dark = percent_box(0, 100)
        self.sp_kbd_normal = percent_box(0, 100)
        self.sp_kbd_bright = percent_box(0, 100)
        self.sp_kbd_dark_enter = lux_box()
        self.sp_kbd_bright_enter = lux_box()
        self.chk_kbd_off = QCheckBox("Полностью выключать при свете")
        self.chk_kbd_off.toggled.connect(self._on_kbd_off_toggled)

        form.addRow(self.chk_kbd_off)
        form.addRow("В темноте:", self.sp_kbd_dark)
        form.addRow("При свете:", self.sp_kbd_normal)
        form.addRow("При ярком свете:", self.sp_kbd_bright)
        form.addRow("Считать тёмным ниже:", self.sp_kbd_dark_enter)
        form.addRow("Считать ярким выше:", self.sp_kbd_bright_enter)
        return group

    def _build_camera_group(self):
        group = QGroupBox("Камера")
        form = QFormLayout(group)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(8)

        self.sp_cam_dark = QSpinBox()
        self.sp_cam_normal = QSpinBox()
        self.sp_cam_bright = QSpinBox()
        for box in (self.sp_cam_dark, self.sp_cam_normal, self.sp_cam_bright):
            box.setRange(0, 255)
            box.setSingleStep(5)
            box.setMinimumWidth(90)
        self.sp_cam_dark.setSuffix("")
        self.sp_cam_normal.setSuffix("")
        self.sp_cam_bright.setSuffix("")

        form.addRow("Усиление в темноте:", self.sp_cam_dark)
        form.addRow("Усиление при свете:", self.sp_cam_normal)
        form.addRow("Усиление при ярком свете:", self.sp_cam_bright)
        note = QLabel("Частота всегда 30 кадров/с — без замедления в темноте.")
        note.setWordWrap(True)
        note.setStyleSheet("color: palette(mid);")
        form.addRow(note)
        return group

    def _build_buttons(self):
        box = QHBoxLayout()
        self.button_apply = QPushButton("Применить")
        self.button_apply.setDefault(True)
        self.button_apply.setMinimumHeight(34)
        self.button_apply.clicked.connect(self._on_apply)
        self.button_reset = QPushButton("Сбросить")
        self.button_reset.clicked.connect(self._on_reset)
        self.button_restart = QPushButton("Перезапустить службу")
        self.button_restart.clicked.connect(self._on_restart)
        box.addWidget(self.button_apply)
        box.addWidget(self.button_reset)
        box.addStretch(1)
        box.addWidget(self.button_restart)
        return box

    # ---------- загрузка и сохранение ----------

    def _load_into_widgets(self, cfg):
        self.switch_enabled.setChecked(bool(cfg["enabled"]))

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

        for device, dark_enter, bright_enter in (
            ("screen", self.sp_screen_dark_enter, self.sp_screen_bright_enter),
            ("keyboard", self.sp_kbd_dark_enter, self.sp_kbd_bright_enter),
        ):
            enter_dark = dark_enter.value()
            enter_bright = bright_enter.value()
            if enter_bright - enter_dark < MIN_GAP:
                raise ValidationError(
                    "Порог «ярко» должен быть хотя бы на "
                    f"{MIN_GAP} лк выше порога «темно»."
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
            QMessageBox.warning(self, "Проверьте пороги", str(error))
            return False
        try:
            save_config(cfg)
        except OSError as error:
            QMessageBox.critical(
                self,
                "Не удалось сохранить",
                f"Не получается записать {CONFIG_PATH}:\n{error}",
            )
            return False
        if not quiet:
            self.statusBar().showMessage(
                "Сохранено — применится в течение 2 секунд", 5000
            )
        return True

    # ---------- реакции ----------

    def _on_enabled_toggled(self, checked):
        if self._loading:
            return
        try:
            cfg = self._collect()
        except ValidationError as error:
            self._loading = True
            self.switch_enabled.setChecked(not checked)
            self._loading = False
            QMessageBox.warning(self, "Проверьте пороги", str(error))
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
                "Не удалось сохранить",
                f"Не получается записать {CONFIG_PATH}:\n{error}",
            )
            return
        self.statusBar().showMessage(
            "Автоматика включена" if checked else "Автоматика отключена", 5000
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
                "Сбросить настройки",
                "Вернуть значения по умолчанию?",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self._loading = True
        self._load_into_widgets(copy.deepcopy(DEFAULTS))
        self._loading = False
        self.statusBar().showMessage("Значения сброшены — нажмите «Применить»")

    def _on_resume(self):
        self._apply(quiet=True)
        self.statusBar().showMessage("Управление возвращено автоматике", 5000)
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
            QMessageBox.critical(self, "Ошибка", f"Не удалось перезапустить: {error}")
            return
        if result.returncode == 0:
            self.statusBar().showMessage("Служба перезапущена", 5000)
        else:
            detail = result.stderr.decode(errors="replace").strip()
            QMessageBox.warning(
                self,
                "Служба не перезапущена",
                detail or "Команда завершилась с ошибкой.",
            )

    # ---------- живое состояние ----------

    def _update_status(self):
        status = read_status()
        if status is None:
            self.label_lux.setText("—")
            self.label_band.setText("нет данных")
            self.label_screen.setText("—")
            self.label_keyboard.setText("—")
            self.label_camera.setText("—")
            self.label_backend.setText("—")
            self.label_pause.setText("Служба не запущена или ещё не ответила.")
            self.button_resume.setVisible(False)
            return

        age = time.time() - float(status.get("time", 0))
        enabled = bool(status.get("enabled"))
        band = BAND_NAMES.get(str(status.get("band")), "—")
        self.label_lux.setText(f"{int(status.get('lux', 0))} лк")

        if not enabled:
            self.label_band.setText("автоматика выключена")
        elif age > 10:
            self.label_band.setText("нет связи")
        else:
            self.label_band.setText(band)

        screen = status.get("screen") or {}
        keyboard = status.get("keyboard") or {}
        camera = status.get("camera") or {}

        screen_percent = screen.get("percent")
        self.label_screen.setText(
            f"{int(screen_percent)} %" if screen_percent is not None else "—"
        )
        self.label_keyboard.setText(f"{int(keyboard.get('percent', 0))} %")
        self.label_camera.setText(
            f"{int(camera.get('fps', 30))} кадров/с, усиление "
            f"{int(camera.get('gain', 0))}"
        )
        backend = screen.get("backend")
        self.label_backend.setText(
            {"kwin": "KWin", "sysfs": "напрямую"}.get(backend, "—")
        )

        paused_until = float(screen.get("paused_until") or 0)
        if enabled and paused_until > time.time():
            left = int(paused_until - time.time())
            self.label_pause.setText(
                f"Пауза после ручной правки: {left // 60}:{left % 60:02d}. "
                "Автоматика вернёт управление сама или по кнопке."
            )
            self.button_resume.setVisible(True)
        elif not enabled:
            self.label_pause.setText(
                "Автоматика выключена: яркость и подсветка не меняются. "
                "Включите переключатель сверху."
            )
            self.button_resume.setVisible(False)
        else:
            self.label_pause.setText("Автоматика управляет яркостью по датчику.")
            self.button_resume.setVisible(False)

        message = status.get("message")
        if message and age <= 10:
            self.statusBar().showMessage(str(message), 4000)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ambient-auto")
    app.setApplicationDisplayName("Автояркость MacBook")
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
