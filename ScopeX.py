import sys
import os
import json
from pathlib import Path
from pynput import keyboard, mouse
from PyQt6 import QtCore, QtGui, QtWidgets


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

json_file_path = resource_path("crosshair_config.json")
with open(json_file_path, "r") as f:
    config = json.load(f)

config["example"] = "new value"

with open(json_file_path, "w") as f:
    json.dump(config, f, indent=4)

CONFIG_PATH = Path("crosshair_config.json")

class Crosshair(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("Crosshair Overlay")

        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.x(),
            screen.y(),
            screen.width(),
            screen.height() - 1
        )
        self.show()

        self.style = "Cross"
        self.size = 15
        self.thickness = 2
        self.gap = 3
        self.dot_radius = 4
        self.rotation = 0
        self.opacity = 1.0
        self.outline = True
        self.outline_thickness = 2
        self.outline_color = QtGui.QColor(255, 255, 255)
        self.color = QtGui.QColor(255, 0, 0)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    def set_style(self, val):
        self.style = val
        self.update()

    def set_size(self, val):
        self.size = val
        self.update()

    def set_thickness(self, val):
        self.thickness = val
        self.update()

    def set_gap(self, val):
        self.gap = val
        self.update()

    def set_dot_radius(self, val):
        self.dot_radius = val
        self.update()

    def set_rotation(self, val):
        self.rotation = val
        self.update()

    def set_opacity(self, val):
        self.opacity = val / 100.0
        self.update()

    def set_outline(self, val):
        if isinstance(val, bool):
            self.outline = val
        else:
            self.outline = (val == QtCore.Qt.CheckState.Checked)
        self.update()

    def set_outline_thickness(self, val):
        self.outline_thickness = val
        self.update()

    def set_outline_color(self, color):
        self.outline_color = color
        self.update()

    def set_color(self, color):
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.opacity)
        center = self.rect().center()

        painter.translate(center)
        painter.rotate(self.rotation)
        painter.translate(-center)

        if self.style == "Cross":
            self._draw_cross(painter, center)
        elif self.style == "Dot":
            self._draw_dot(painter, center)
        elif self.style == "Cross + Dot":
            self._draw_cross(painter, center)
            self._draw_dot(painter, center)
        elif self.style == "Circle":
            self._draw_circle(painter, center)
        elif self.style == "Shotgun":
            self._draw_shotgun(painter, center)

    def _draw_cross(self, painter, center):
        if self.outline:
            pen = QtGui.QPen(self.outline_color, self.thickness + self.outline_thickness * 2, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(center.x() - self.size - self.gap, center.y(), center.x() - self.gap, center.y())
            painter.drawLine(center.x() + self.gap, center.y(), center.x() + self.size + self.gap, center.y())
            painter.drawLine(center.x(), center.y() - self.size - self.gap, center.x(), center.y() - self.gap)
            painter.drawLine(center.x(), center.y() + self.gap, center.x(), center.y() + self.size + self.gap)

        pen = QtGui.QPen(self.color, self.thickness, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(center.x() - self.size - self.gap, center.y(), center.x() - self.gap, center.y())
        painter.drawLine(center.x() + self.gap, center.y(), center.x() + self.size + self.gap, center.y())
        painter.drawLine(center.x(), center.y() - self.size - self.gap, center.x(), center.y() - self.gap)
        painter.drawLine(center.x(), center.y() + self.gap, center.x(), center.y() + self.size + self.gap)

    def _draw_dot(self, painter, center):
        if self.outline:
            pen = QtGui.QPen(self.outline_color, self.outline_thickness, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(QtGui.QBrush(self.outline_color))
            painter.drawEllipse(center, self.dot_radius + self.outline_thickness, self.dot_radius + self.outline_thickness)

        pen = QtGui.QPen(self.color, 1)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(self.color))
        painter.drawEllipse(center, self.dot_radius, self.dot_radius)

    def _draw_circle(self, painter, center):
        radius = self.size + self.gap
        if self.outline:
            pen = QtGui.QPen(self.outline_color, self.outline_thickness)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, radius + self.outline_thickness, radius + self.outline_thickness)

        pen = QtGui.QPen(self.color, self.thickness)
        painter.setPen(pen)
        painter.drawEllipse(center, radius, radius)

    def _draw_shotgun(self, painter, center):
        length = self.size
        gap = self.gap
        thickness = self.thickness
        outline_thickness = self.outline_thickness

        points = [
            (center.x() - length, center.y() - length + gap, center.x() - length + gap, center.y() - length),
            (center.x() + length - gap, center.y() - length, center.x() + length, center.y() - length + gap),
            (center.x() - length, center.y() + length - gap, center.x() - length + gap, center.y() + length),
            (center.x() + length - gap, center.y() + length, center.x() + length, center.y() + length - gap),
        ]

        if self.outline:
            pen = QtGui.QPen(self.outline_color, thickness + outline_thickness * 2, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.SquareCap)
            painter.setPen(pen)
            for line in points:
                painter.drawLine(line[0], line[1], line[2], line[3])

            if self.dot_radius > 0:
                painter.setBrush(QtGui.QBrush(self.outline_color))
                painter.setPen(QtCore.Qt.PenStyle.NoPen)
                painter.drawEllipse(center, self.dot_radius + outline_thickness, self.dot_radius + outline_thickness)

        pen = QtGui.QPen(self.color, thickness, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.SquareCap)
        painter.setPen(pen)
        for line in points:
            painter.drawLine(line[0], line[1], line[2], line[3])

        if self.dot_radius > 0:
            painter.setBrush(QtGui.QBrush(self.color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawEllipse(center, self.dot_radius, self.dot_radius)


class CrosshairPreview(QtWidgets.QWidget):
    def __init__(self, crosshair):
        super().__init__()
        self.crosshair = crosshair
        self.setMinimumSize(200, 200)
        self.setMaximumSize(200, 200)
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtGui.QColor(40, 40, 40))
        self.setPalette(palette)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.crosshair.opacity)
        center = self.rect().center()

        painter.translate(center)
        painter.rotate(self.crosshair.rotation)
        painter.translate(-center)

        if self.crosshair.style == "Cross":
            self._draw_cross(painter, center)
        elif self.crosshair.style == "Dot":
            self._draw_dot(painter, center)
        elif self.crosshair.style == "Cross + Dot":
            self._draw_cross(painter, center)
            self._draw_dot(painter, center)
        elif self.crosshair.style == "Circle":
            self._draw_circle(painter, center)
        elif self.crosshair.style == "Shotgun":
            self._draw_shotgun(painter, center)

    def _draw_cross(self, painter, center):
        if self.crosshair.outline:
            pen = QtGui.QPen(self.crosshair.outline_color, self.crosshair.thickness + self.crosshair.outline_thickness * 2, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(center.x() - self.crosshair.size - self.crosshair.gap, center.y(), center.x() - self.crosshair.gap, center.y())
            painter.drawLine(center.x() + self.crosshair.gap, center.y(), center.x() + self.crosshair.size + self.crosshair.gap, center.y())
            painter.drawLine(center.x(), center.y() - self.crosshair.size - self.crosshair.gap, center.x(), center.y() - self.crosshair.gap)
            painter.drawLine(center.x(), center.y() + self.crosshair.gap, center.x(), center.y() + self.crosshair.size + self.crosshair.gap)

        pen = QtGui.QPen(self.crosshair.color, self.crosshair.thickness, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(center.x() - self.crosshair.size - self.crosshair.gap, center.y(), center.x() - self.crosshair.gap, center.y())
        painter.drawLine(center.x() + self.crosshair.gap, center.y(), center.x() + self.crosshair.size + self.crosshair.gap, center.y())
        painter.drawLine(center.x(), center.y() - self.crosshair.size - self.crosshair.gap, center.x(), center.y() - self.crosshair.gap)
        painter.drawLine(center.x(), center.y() + self.crosshair.gap, center.x(), center.y() + self.crosshair.size + self.crosshair.gap)

    def _draw_dot(self, painter, center):
        if self.crosshair.outline:
            pen = QtGui.QPen(self.crosshair.outline_color, self.crosshair.outline_thickness, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(QtGui.QBrush(self.crosshair.outline_color))
            painter.drawEllipse(center, self.crosshair.dot_radius + self.crosshair.outline_thickness, self.crosshair.dot_radius + self.crosshair.outline_thickness)

        pen = QtGui.QPen(self.crosshair.color, 1)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(self.crosshair.color))
        painter.drawEllipse(center, self.crosshair.dot_radius, self.crosshair.dot_radius)

    def _draw_circle(self, painter, center):
        radius = self.crosshair.size + self.crosshair.gap
        if self.crosshair.outline:
            pen = QtGui.QPen(self.crosshair.outline_color, self.crosshair.outline_thickness)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, radius + self.crosshair.outline_thickness, radius + self.crosshair.outline_thickness)

        pen = QtGui.QPen(self.crosshair.color, self.crosshair.thickness)
        painter.setPen(pen)
        painter.drawEllipse(center, radius, radius)

    def _draw_shotgun(self, painter, center):
        length = self.crosshair.size
        gap = self.crosshair.gap
        thickness = self.crosshair.thickness
        outline_thickness = self.crosshair.outline_thickness

        points = [
            (center.x() - length, center.y() - length + gap, center.x() - length + gap, center.y() - length),
            (center.x() + length - gap, center.y() - length, center.x() + length, center.y() - length + gap),
            (center.x() - length, center.y() + length - gap, center.x() - length + gap, center.y() + length),
            (center.x() + length - gap, center.y() + length, center.x() + length, center.y() + length - gap),
        ]

        if self.crosshair.outline:
            pen = QtGui.QPen(self.crosshair.outline_color, thickness + outline_thickness * 2, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.SquareCap)
            painter.setPen(pen)
            for line in points:
                painter.drawLine(line[0], line[1], line[2], line[3])

            if self.crosshair.dot_radius > 0:
                painter.setBrush(QtGui.QBrush(self.crosshair.outline_color))
                painter.setPen(QtCore.Qt.PenStyle.NoPen)
                painter.drawEllipse(center, self.crosshair.dot_radius + outline_thickness, self.crosshair.dot_radius + outline_thickness)

        pen = QtGui.QPen(self.crosshair.color, thickness, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.SquareCap)
        painter.setPen(pen)
        for line in points:
            painter.drawLine(line[0], line[1], line[2], line[3])

        if self.crosshair.dot_radius > 0:
            painter.setBrush(QtGui.QBrush(self.crosshair.color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawEllipse(center, self.crosshair.dot_radius, self.crosshair.dot_radius)


class KeyListenerWorker(QtCore.QObject):
    key_pressed_signal = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.keyboard_listener = None
        self.mouse_listener = None

    def listen(self):
        def on_key_press(key):
            if not self.running:
                return False
            try:
                key_name = key.char
            except AttributeError:
                key_name = str(key).replace('Key.', '')
            
            self.key_pressed_signal.emit(key_name)

        def on_mouse_click(x, y, button, pressed):
            if not self.running:
                return False
            if pressed:
                button_name = str(button).replace('Button.', 'mouse_')
                self.key_pressed_signal.emit(button_name)

        def on_mouse_scroll(x, y, dx, dy):
            if not self.running:
                return False
            if dy > 0:
                self.key_pressed_signal.emit('scroll_up')
            elif dy < 0:
                self.key_pressed_signal.emit('scroll_down')
            if dx > 0:
                self.key_pressed_signal.emit('scroll_right')
            elif dx < 0:
                self.key_pressed_signal.emit('scroll_left')

        self.keyboard_listener = keyboard.Listener(on_press=on_key_press)
        self.mouse_listener = mouse.Listener(
            on_click=on_mouse_click,
            on_scroll=on_mouse_scroll
        )
        
        self.keyboard_listener.start()
        self.mouse_listener.start()
        
        self.keyboard_listener.join()
        self.mouse_listener.join()
        
        self.finished.emit()

    def stop(self):
        self.running = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()


class SettingsWindow(QtWidgets.QWidget):
    key_pressed_signal = QtCore.pyqtSignal(str)
    config_changed = QtCore.pyqtSignal()

    def __init__(self, crosshair):
        super().__init__()

        self.crosshair = crosshair
        self.bindings = {}
        self.active_binding = None

        self._binding_outline_color = self.crosshair.outline_color
        self._binding_main_color = self.crosshair.color

        self.setWindowTitle("Crosshair Settings")
        self.resize(420, 600)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.style_tab(), "Style")
        self.tabs.addTab(self.appearance_tab(), "Appearance")
        self.tabs.addTab(self.bindings_tab(), "Bindings")

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.tabs)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.listener_thread = QtCore.QThread()
        self.listener_worker = KeyListenerWorker()
        self.listener_worker.moveToThread(self.listener_thread)
        self.listener_worker.key_pressed_signal.connect(self.on_global_key_pressed)
        self.listener_worker.finished.connect(self.listener_thread.quit)
        self.listener_thread.started.connect(self.listener_worker.listen)
        self.listener_thread.start()

        self.config_changed.connect(self.save_config)

        self.load_config()

    def closeEvent(self, event):
        self.save_config()
        self.listener_worker.stop()
        self.listener_thread.quit()
        self.listener_thread.wait(1000)
        if self.listener_thread.isRunning():
            self.listener_thread.terminate()
        event.accept()

    def style_tab(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.style_combo = QtWidgets.QComboBox()
        styles = ["Cross", "Dot", "Cross + Dot", "Circle", "Shotgun"]
        self.style_combo.addItems(styles)
        self.style_combo.setCurrentText(self.crosshair.style)
        self.style_combo.currentTextChanged.connect(self.on_style_changed)

        layout.addWidget(QtWidgets.QLabel("Crosshair Style"))
        layout.addWidget(self.style_combo)
        
        layout.addSpacing(20)
        layout.addWidget(QtWidgets.QLabel("Preview"))
        self.preview = CrosshairPreview(self.crosshair)
        preview_container = QtWidgets.QHBoxLayout()
        preview_container.addStretch()
        preview_container.addWidget(self.preview)
        preview_container.addStretch()
        layout.addLayout(preview_container)
        
        return w

    def on_style_changed(self, style):
        self.crosshair.set_style(style)
        self.config_changed.emit()

    def appearance_tab(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.size_slider = self._add_slider(layout, "Size", 1, 100, self.crosshair.size, self.on_size_changed)
        self.thickness_slider = self._add_slider(layout, "Thickness", 1, 20, self.crosshair.thickness, self.on_thickness_changed)
        self.gap_slider = self._add_slider(layout, "Gap", 0, 50, self.crosshair.gap, self.on_gap_changed)
        self.dot_radius_slider = self._add_slider(layout, "Dot Radius", 0, 50, self.crosshair.dot_radius, self.on_dot_radius_changed)
        self.rotation_slider = self._add_slider(layout, "Rotation", 0, 360, self.crosshair.rotation, self.on_rotation_changed)
        self.opacity_slider = self._add_slider(layout, "Opacity (%)", 0, 100, int(self.crosshair.opacity * 100), self.on_opacity_changed)

        self.outline_cb = QtWidgets.QCheckBox("Enable Outline")
        self.outline_cb.setChecked(self.crosshair.outline)
        self.outline_cb.stateChanged.connect(self.on_outline_changed)
        layout.addWidget(self.outline_cb)

        self.outline_thickness_slider = self._add_slider(layout, "Outline Thickness", 1, 10, self.crosshair.outline_thickness, self.on_outline_thickness_changed)

        self.outline_color_btn = QtWidgets.QPushButton("Set Outline Color")
        self.outline_color_btn.clicked.connect(self._pick_outline_color)
        layout.addWidget(self.outline_color_btn)

        self.color_btn = QtWidgets.QPushButton("Set Crosshair Color")
        self.color_btn.clicked.connect(self._pick_main_color)
        layout.addWidget(self.color_btn)

        return w

    def on_size_changed(self, val):
        self.crosshair.set_size(val)
        self.config_changed.emit()

    def on_thickness_changed(self, val):
        self.crosshair.set_thickness(val)
        self.config_changed.emit()

    def on_gap_changed(self, val):
        self.crosshair.set_gap(val)
        self.config_changed.emit()

    def on_dot_radius_changed(self, val):
        self.crosshair.set_dot_radius(val)
        self.config_changed.emit()

    def on_rotation_changed(self, val):
        self.crosshair.set_rotation(val)
        self.config_changed.emit()

    def on_opacity_changed(self, val):
        self.crosshair.set_opacity(val)
        self.config_changed.emit()

    def on_outline_changed(self, val):
        self.crosshair.set_outline(val)
        self.config_changed.emit()

    def on_outline_thickness_changed(self, val):
        self.crosshair.set_outline_thickness(val)
        self.config_changed.emit()

    def bindings_tab(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.bindings_list = QtWidgets.QListWidget()
        self.bindings_list.currentItemChanged.connect(self.on_binding_selection_changed)
        layout.addWidget(QtWidgets.QLabel("Key Bindings"))
        layout.addWidget(self.bindings_list)

        self.binding_key_display = QtWidgets.QLineEdit()
        self.binding_key_display.setPlaceholderText("Press any key or mouse button...")
        self.binding_key_display.setReadOnly(True)
        layout.addWidget(self.binding_key_display)
        
        self.add_binding_btn = QtWidgets.QPushButton("Click here, then press a key/mouse button")
        self.add_binding_btn.setCheckable(True)
        self.add_binding_btn.clicked.connect(self.start_key_capture)
        layout.addWidget(self.add_binding_btn)
        
        self.waiting_for_key = False

        layout.addWidget(QtWidgets.QLabel("Binding Configuration"))
        
        self.binding_style_combo = QtWidgets.QComboBox()
        self.binding_style_combo.addItems(["Cross", "Dot", "Cross + Dot", "Circle", "Shotgun"])
        self.binding_style_combo.currentTextChanged.connect(self.on_binding_config_changed)
        layout.addWidget(QtWidgets.QLabel("Style"))
        layout.addWidget(self.binding_style_combo)

        self.binding_size_slider = self._add_slider(layout, "Size", 1, 100, 15, self.on_binding_config_changed)
        self.binding_thickness_slider = self._add_slider(layout, "Thickness", 1, 20, 2, self.on_binding_config_changed)
        self.binding_gap_slider = self._add_slider(layout, "Gap", 0, 50, 3, self.on_binding_config_changed)
        self.binding_dot_radius_slider = self._add_slider(layout, "Dot Radius", 0, 50, 4, self.on_binding_config_changed)
        self.binding_rotation_slider = self._add_slider(layout, "Rotation", 0, 360, 0, self.on_binding_config_changed)
        self.binding_opacity_slider = self._add_slider(layout, "Opacity (%)", 0, 100, 100, self.on_binding_config_changed)
        
        self.binding_outline_cb = QtWidgets.QCheckBox("Enable Outline")
        self.binding_outline_cb.stateChanged.connect(self.on_binding_config_changed)
        layout.addWidget(self.binding_outline_cb)
        
        self.binding_outline_thickness_slider = self._add_slider(layout, "Outline Thickness", 1, 10, 2, self.on_binding_config_changed)

        self.binding_outline_color_btn = QtWidgets.QPushButton("Set Outline Color")
        self.binding_outline_color_btn.clicked.connect(self._pick_binding_outline_color)
        layout.addWidget(self.binding_outline_color_btn)

        self.binding_color_btn = QtWidgets.QPushButton("Set Crosshair Color")
        self.binding_color_btn.clicked.connect(self._pick_binding_main_color)
        layout.addWidget(self.binding_color_btn)

        self.delete_binding_btn = QtWidgets.QPushButton("Delete Selected Binding")
        self.delete_binding_btn.clicked.connect(self.delete_selected_binding)
        layout.addWidget(self.delete_binding_btn)

        return w

    def start_key_capture(self):
        self.waiting_for_key = True
        self.add_binding_btn.setText("Press any key or mouse button now...")
        self.binding_key_display.setText("")

    def _add_slider(self, layout, label, min_, max_, value, slot):
        layout.addWidget(QtWidgets.QLabel(label))
        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        slider.setRange(min_, max_)
        slider.setValue(value)
        slider.valueChanged.connect(slot)
        layout.addWidget(slider)
        return slider

    def _pick_outline_color(self):
        color = QtWidgets.QColorDialog.getColor(self.crosshair.outline_color, self, "Select Outline Color")
        if color.isValid():
            self.crosshair.set_outline_color(color)
            self.config_changed.emit()

    def _pick_main_color(self):
        color = QtWidgets.QColorDialog.getColor(self.crosshair.color, self, "Select Crosshair Color")
        if color.isValid():
            self.crosshair.set_color(color)
            self.config_changed.emit()

    def _pick_binding_outline_color(self):
        color = QtWidgets.QColorDialog.getColor(self._binding_outline_color, self, "Select Outline Color")
        if color.isValid():
            self._binding_outline_color = color
            self.on_binding_config_changed()

    def _pick_binding_main_color(self):
        color = QtWidgets.QColorDialog.getColor(self._binding_main_color, self, "Select Crosshair Color")
        if color.isValid():
            self._binding_main_color = color
            self.on_binding_config_changed()

    def on_binding_config_changed(self):
        item = self.bindings_list.currentItem()
        if not item:
            return
        key = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if not key:
            key = item.text()
        config = self.bindings.get(key)
        if not config:
            return

        config["style"] = self.binding_style_combo.currentText()
        config["size"] = self.binding_size_slider.value()
        config["thickness"] = self.binding_thickness_slider.value()
        config["gap"] = self.binding_gap_slider.value()
        config["dot_radius"] = self.binding_dot_radius_slider.value()
        config["rotation"] = self.binding_rotation_slider.value()
        config["opacity"] = self.binding_opacity_slider.value()
        config["outline"] = self.binding_outline_cb.isChecked()
        config["outline_thickness"] = self.binding_outline_thickness_slider.value()
        config["outline_color"] = self._binding_outline_color
        config["color"] = self._binding_main_color

        if key == self.active_binding:
            self.apply_binding_to_crosshair(config)
        
        self.config_changed.emit()

    def on_binding_selection_changed(self, current, previous=None):
        if not current:
            return
        key = current.data(QtCore.Qt.ItemDataRole.UserRole)
        if not key:
            key = current.text()
        config = self.bindings.get(key)
        if not config:
            return

        self._binding_outline_color = config.get("outline_color", QtGui.QColor(255, 255, 255))
        self._binding_main_color = config.get("color", QtGui.QColor(255, 0, 0))

        self.binding_style_combo.blockSignals(True)
        self.binding_style_combo.setCurrentText(config.get("style", "Cross"))
        self.binding_style_combo.blockSignals(False)
        
        self.binding_size_slider.blockSignals(True)
        self.binding_size_slider.setValue(config.get("size", 15))
        self.binding_size_slider.blockSignals(False)
        
        self.binding_thickness_slider.blockSignals(True)
        self.binding_thickness_slider.setValue(config.get("thickness", 2))
        self.binding_thickness_slider.blockSignals(False)
        
        self.binding_gap_slider.blockSignals(True)
        self.binding_gap_slider.setValue(config.get("gap", 3))
        self.binding_gap_slider.blockSignals(False)
        
        self.binding_dot_radius_slider.blockSignals(True)
        self.binding_dot_radius_slider.setValue(config.get("dot_radius", 4))
        self.binding_dot_radius_slider.blockSignals(False)
        
        self.binding_rotation_slider.blockSignals(True)
        self.binding_rotation_slider.setValue(config.get("rotation", 0))
        self.binding_rotation_slider.blockSignals(False)
        
        self.binding_opacity_slider.blockSignals(True)
        self.binding_opacity_slider.setValue(config.get("opacity", 100))
        self.binding_opacity_slider.blockSignals(False)
        
        self.binding_outline_cb.blockSignals(True)
        self.binding_outline_cb.setChecked(config.get("outline", True))
        self.binding_outline_cb.blockSignals(False)
        
        self.binding_outline_thickness_slider.blockSignals(True)
        self.binding_outline_thickness_slider.setValue(config.get("outline_thickness", 2))
        self.binding_outline_thickness_slider.blockSignals(False)

    def apply_binding_to_crosshair(self, config):
        self.crosshair.set_style(config["style"])
        self.crosshair.set_size(config["size"])
        self.crosshair.set_thickness(config["thickness"])
        self.crosshair.set_gap(config["gap"])
        self.crosshair.set_dot_radius(config["dot_radius"])
        self.crosshair.set_rotation(config["rotation"])
        self.crosshair.set_opacity(config["opacity"])
        self.crosshair.set_outline(config["outline"])
        self.crosshair.set_outline_thickness(config["outline_thickness"])
        self.crosshair.set_outline_color(config["outline_color"])
        self.crosshair.set_color(config["color"])

    def _default_crosshair_config(self):
        return {
            "style": "Cross",
            "size": 15,
            "thickness": 2,
            "gap": 3,
            "dot_radius": 4,
            "rotation": 0,
            "opacity": 100,
            "outline": True,
            "outline_thickness": 2,
            "outline_color": QtGui.QColor(255, 255, 255),
            "color": QtGui.QColor(255, 0, 0)
        }

    def _load_binding_config(self, key):
        config = self.bindings.get(key)
        if not config:
            return
        self.binding_style_combo.setCurrentText(config.get("style", "Cross"))
        self.binding_size_slider.setValue(config.get("size", 15))
        self.binding_thickness_slider.setValue(config.get("thickness", 2))
        self.binding_gap_slider.setValue(config.get("gap", 3))
        self.binding_dot_radius_slider.setValue(config.get("dot_radius", 4))
        self.binding_rotation_slider.setValue(config.get("rotation", 0))
        self.binding_opacity_slider.setValue(config.get("opacity", 100))
        self.binding_outline_cb.setChecked(config.get("outline", True))
        self.binding_outline_thickness_slider.setValue(config.get("outline_thickness", 2))
        self._binding_outline_color = config.get("outline_color", QtGui.QColor(255, 255, 255))
        self._binding_main_color = config.get("color", QtGui.QColor(255, 0, 0))

    def delete_selected_binding(self):
        item = self.bindings_list.currentItem()
        if not item:
            return
        key = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if not key:
            key = item.text()
        if key in self.bindings:
            del self.bindings[key]
            self.bindings_list.takeItem(self.bindings_list.currentRow())
            if key == self.active_binding:
                self.active_binding = None
            self.config_changed.emit()

    def on_global_key_pressed(self, key_name):
        if self.waiting_for_key:
            self.waiting_for_key = False
            self.add_binding_btn.setChecked(False)
            self.add_binding_btn.setText("Click here, then press a key/mouse button")
            
            display_name = key_name
            if key_name.startswith('mouse_'):
                display_name = key_name.replace('mouse_', 'Mouse ')
                display_name = display_name.replace('left', 'Left Click')
                display_name = display_name.replace('right', 'Right Click')
                display_name = display_name.replace('middle', 'Middle Click')
                display_name = display_name.replace('x1', 'MB4')
                display_name = display_name.replace('x2', 'MB5')
            elif key_name.startswith('scroll_'):
                display_name = key_name.replace('scroll_', 'Scroll ')
                display_name = display_name.replace('up', 'Up')
                display_name = display_name.replace('down', 'Down')
                display_name = display_name.replace('left', 'Left')
                display_name = display_name.replace('right', 'Right')
            
            if key_name in self.bindings:
                self.bindings_list.setCurrentRow(list(self.bindings.keys()).index(key_name))
                self.binding_key_display.setText(f"'{display_name}' already bound")
                return

            self.bindings[key_name] = self._default_crosshair_config()
            self.bindings_list.addItem(display_name)
            item = self.bindings_list.item(self.bindings_list.count() - 1)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, key_name)
            self.bindings_list.setCurrentRow(self.bindings_list.count() - 1)
            self._load_binding_config(key_name)
            self.binding_key_display.setText(f"Added binding: {display_name}")
            self.config_changed.emit()
            return
        
        if key_name in self.bindings:
            config = self.bindings[key_name]
            self.active_binding = key_name
            self.apply_binding_to_crosshair(config)

    def save_config(self):
        data = {
            "crosshair": {
                "style": self.crosshair.style,
                "size": self.crosshair.size,
                "thickness": self.crosshair.thickness,
                "gap": self.crosshair.gap,
                "dot_radius": self.crosshair.dot_radius,
                "rotation": self.crosshair.rotation,
                "opacity": int(self.crosshair.opacity * 100),
                "outline": self.crosshair.outline,
                "outline_thickness": self.crosshair.outline_thickness,
                "outline_color": self.crosshair.outline_color.name(),
                "color": self.crosshair.color.name()
            },
            "bindings": {}
        }
        
        for key, config in self.bindings.items():
            data["bindings"][key] = {
                "style": config["style"],
                "size": config["size"],
                "thickness": config["thickness"],
                "gap": config["gap"],
                "dot_radius": config["dot_radius"],
                "rotation": config["rotation"],
                "opacity": config["opacity"],
                "outline": config["outline"],
                "outline_thickness": config["outline_thickness"],
                "outline_color": config["outline_color"].name(),
                "color": config["color"].name()
            }
        
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_config(self):
        if not CONFIG_PATH.exists():
            return
        
        try:
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
            
            if "crosshair" in data:
                ch = data["crosshair"]
                self.crosshair.set_style(ch.get("style", "Cross"))
                self.crosshair.set_size(ch.get("size", 15))
                self.crosshair.set_thickness(ch.get("thickness", 2))
                self.crosshair.set_gap(ch.get("gap", 3))
                self.crosshair.set_dot_radius(ch.get("dot_radius", 4))
                self.crosshair.set_rotation(ch.get("rotation", 0))
                self.crosshair.set_opacity(ch.get("opacity", 100))
                self.crosshair.set_outline(ch.get("outline", True))
                self.crosshair.set_outline_thickness(ch.get("outline_thickness", 2))
                self.crosshair.set_outline_color(QtGui.QColor(ch.get("outline_color", "#ffffff")))
                self.crosshair.set_color(QtGui.QColor(ch.get("color", "#ff0000")))
                
                self.style_combo.setCurrentText(self.crosshair.style)
                self.size_slider.setValue(self.crosshair.size)
                self.thickness_slider.setValue(self.crosshair.thickness)
                self.gap_slider.setValue(self.crosshair.gap)
                self.dot_radius_slider.setValue(self.crosshair.dot_radius)
                self.rotation_slider.setValue(self.crosshair.rotation)
                self.opacity_slider.setValue(int(self.crosshair.opacity * 100))
                self.outline_cb.setChecked(self.crosshair.outline)
                self.outline_thickness_slider.setValue(self.crosshair.outline_thickness)
            
            if "bindings" in data:
                for key, config in data["bindings"].items():
                    self.bindings[key] = {
                        "style": config.get("style", "Cross"),
                        "size": config.get("size", 15),
                        "thickness": config.get("thickness", 2),
                        "gap": config.get("gap", 3),
                        "dot_radius": config.get("dot_radius", 4),
                        "rotation": config.get("rotation", 0),
                        "opacity": config.get("opacity", 100),
                        "outline": config.get("outline", True),
                        "outline_thickness": config.get("outline_thickness", 2),
                        "outline_color": QtGui.QColor(config.get("outline_color", "#ffffff")),
                        "color": QtGui.QColor(config.get("color", "#ff0000"))
                    }
                    
                    display_name = key
                    if key.startswith('mouse_'):
                        display_name = key.replace('mouse_', 'Mouse ')
                        display_name = display_name.replace('left', 'Left Click')
                        display_name = display_name.replace('right', 'Right Click')
                        display_name = display_name.replace('middle', 'Middle Click')
                        display_name = display_name.replace('x1', 'MB4')
                        display_name = display_name.replace('x2', 'MB5')
                    elif key.startswith('scroll_'):
                        display_name = key.replace('scroll_', 'Scroll ')
                        display_name = display_name.replace('up', 'Up')
                        display_name = display_name.replace('down', 'Down')
                        display_name = display_name.replace('left', 'Left')
                        display_name = display_name.replace('right', 'Right')
                    
                    self.bindings_list.addItem(display_name)
                    item = self.bindings_list.item(self.bindings_list.count() - 1)
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, key)
            
            print(f"Config loaded from {CONFIG_PATH}")
        except Exception as e:
            print(f"Error loading config: {e}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    
    crosshair = Crosshair()
    settings = SettingsWindow(crosshair)
    settings.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
