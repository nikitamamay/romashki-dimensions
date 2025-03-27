from PyQt5 import QtCore, QtGui, QtWidgets
import os
import traceback

import src.round_dimensions as round_dimensions
import src.math_utils as math_utils

from src.resources import get_resource_path

from src import config


SPINBOX_VALUES = [10/12, 1.0, 10/6, 2.0, 2.5, 100/24, 5.0, 100/12, 10.0]
SPINBOX_ERROR = 0.02


def get_next_value(x: float, is_previous: bool) -> float:
    c10: int = math_utils.count_10(x)
    x /= 10 ** c10
    l_SBV = len(SPINBOX_VALUES)
    i = 0

    if not is_previous:
        x *= (1 + SPINBOX_ERROR)
        for i in range(0, l_SBV):
            v = SPINBOX_VALUES[i]
            if v > x:
                break
    else:
        x *= (1 - SPINBOX_ERROR)
        for i in range(l_SBV - 1, -1, -1):
            v = SPINBOX_VALUES[i]
            if v < x:
                break
    nv = SPINBOX_VALUES[i] * 10 ** c10
    return nv




class FloatInputWidget(QtWidgets.QLineEdit):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setValue(1.0)
        self.textChanged.connect(self.text_changed)

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        delta = e.angleDelta().y()
        is_prev = delta < 0
        self.setValue(get_next_value(self.value(), is_prev))

    def setValue(self, val: float) -> None:
        self.setText(str(val))

    def value(self) -> float:
        s = self.text().replace(",", ".")
        try:
            return float(s)
        except:
            return 1.0

    def text_changed(self) -> None:
        state = self.validate()
        color = ["#ff7f7f", "#fffc7f", "#ffffff"][state]
        self.setStyleSheet(f"background-color: {color}; color: black")
        self.update()

    def validate(self) -> int:
        s = self.text().replace(",", ".")
        try:
            f = float(s)
            if f > 10**(-12) and f < 10**9:
                return 2
            return 1
        except:
            return 0


class ConfigWindow(QtWidgets.QWidget):
    icon_size_changed = QtCore.pyqtSignal(int)
    window_stays_on_top_changed = QtCore.pyqtSignal(bool)
    config_changed = QtCore.pyqtSignal()

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setWindowFlag(QtCore.Qt.WindowType.Window, True)
        self.setWindowTitle(f"Настройки - {config.PROGRAM_NAME}")

        self.cb_stays_on_top = QtWidgets.QCheckBox("Показывать окно поверх всех окон")
        self.cb_stays_on_top.setChecked(config.options["window_stays_on_top"])
        self.cb_stays_on_top.stateChanged.connect(self._stays_on_top_changed)

        self.sb_icon_size = QtWidgets.QSpinBox()
        self.sb_icon_size.setRange(0, 1024)
        self.sb_icon_size.setValue(config.options["icon_size"])
        self.sb_icon_size.valueChanged.connect(self._icon_size_changed)

        self.cb_angle_DMS = QtWidgets.QCheckBox("Измерять углы в градусах-минутах-секундах вместо десятичной системы")
        self.cb_angle_DMS.setChecked(config.options["is_angle_DMS"])
        self.cb_angle_DMS.stateChanged.connect(self._angleDMS_changed)

        self.cb_remember_window_pos = QtWidgets.QCheckBox("Запоминать местоположение и размеры окна")
        self.cb_remember_window_pos.setChecked(config.options["remember_window_geometry"])
        self.cb_remember_window_pos.stateChanged.connect(self._remember_pos_changed)

        self._layout = QtWidgets.QGridLayout()
        self.setLayout(self._layout)
        self._layout.addWidget(self.cb_stays_on_top, 0, 0, 1, 2)
        self._layout.addWidget(self.cb_remember_window_pos, 1, 0, 1, 2)
        self._layout.addWidget(QtWidgets.QLabel("Размер иконок:"), 2, 0, 1, 1)
        self._layout.addWidget(self.sb_icon_size, 2, 1, 1, 1)
        self._layout.addWidget(self.cb_angle_DMS, 3, 0, 1, 2)

    def _stays_on_top_changed(self, state: bool) -> None:
        state = bool(state)
        config.options["window_stays_on_top"] = state
        self.config_changed.emit()
        self.window_stays_on_top_changed.emit(state)

    def _angleDMS_changed(self, state: bool) -> None:
        state = bool(state)
        config.options["is_angle_DMS"] = state
        self.config_changed.emit()

    def _remember_pos_changed(self, state: bool) -> None:
        state = bool(state)
        config.options["remember_window_geometry"] = state
        self.config_changed.emit()

    def _icon_size_changed(self, size: int) -> None:
        config.options["icon_size"] = size
        self.config_changed.emit()
        self.icon_size_changed.emit(size)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self._config_saving_timer: int = 0
        self._window_moving_timer: int = 0

        self.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False)
        self.resize(10, 10)

        self.config_window = ConfigWindow(self)
        self.config_window.icon_size_changed.connect(self.resize_icons)
        self.config_window.config_changed.connect(lambda: config.save())
        self.config_window.window_stays_on_top_changed.connect(self.set_stays_on_top)

        self.fiw_multiple = FloatInputWidget()
        self.fiw_multiple.setToolTip("Кратность округления")
        self.fiw_multiple.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)

        self.btn_round_closest = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/middle.svg")), "")
        self.btn_round_closest.setToolTip("Округлить до ближайшего")
        self.btn_round_closest.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.round_selected_dimensions(self.fiw_multiple.value(), 0.5, config.options["is_angle_DMS"])
            )
        )

        self.btn_round_down = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/down.svg")), "")
        self.btn_round_down.setToolTip("Округлить вниз")
        self.btn_round_down.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.round_selected_dimensions(self.fiw_multiple.value(), 0, config.options["is_angle_DMS"])
            )
        )

        self.btn_round_up = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/up.svg")), "")
        self.btn_round_up.setToolTip("Округлить вверх")
        self.btn_round_up.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.round_selected_dimensions(self.fiw_multiple.value(), 1, config.options["is_angle_DMS"])
            )
        )

        self.btn_no_round = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/no_round.svg")), "")
        self.btn_no_round.setToolTip("Вернуть неокругленное значение")
        self.btn_no_round.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.remove_rounding_in_selected_dimensions()
            )
        )


        self.btn_select_rounded = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/select_rounded.svg")), "")
        self.btn_select_rounded.setToolTip("Выбрать размеры с ручным вводом (округленные)")
        self.btn_select_rounded.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.select_rounded_dimensions()
            )
        )


        self.btn_toggle_star = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/star.svg")), "")
        self.btn_toggle_star.setToolTip("Добавить/убрать звездочку")
        self.btn_toggle_star.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.toggle_star_in_selected_dimensions()
            )
        )


        self.btn_sign_nothing = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/nothing.svg")), "")
        self.btn_sign_nothing.setToolTip("Убрать знак перед размером")
        self.btn_sign_nothing.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.set_sign_in_selected_dimensions(round_dimensions.DimensionSign.Nothing)
            )
        )

        self.btn_sign_diameter = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/diameter.svg")), "")
        self.btn_sign_diameter.setToolTip("Установить знак диаметра")
        self.btn_sign_diameter.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.set_sign_in_selected_dimensions(round_dimensions.DimensionSign.Diameter)
            )
        )

        self.btn_sign_square = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/square.svg")), "")
        self.btn_sign_square.setToolTip("Установить знак квадрата")
        self.btn_sign_square.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.set_sign_in_selected_dimensions(round_dimensions.DimensionSign.Square)
            )
        )

        self.btn_sign_radius = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/radius.svg")), "")
        self.btn_sign_radius.setToolTip("Установить знак радиуса")
        self.btn_sign_radius.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.set_sign_in_selected_dimensions(round_dimensions.DimensionSign.Radius)
            )
        )

        self.btn_sign_metric = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/metric.svg")), "")
        self.btn_sign_metric.setToolTip("Установить знак метрической резьбы")
        self.btn_sign_metric.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.set_sign_in_selected_dimensions(round_dimensions.DimensionSign.MetricThread)
            )
        )

        self.btn_switch_remote_lines = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/remote_lines.svg")), "")
        self.btn_switch_remote_lines.setToolTip("Переключить отображение выносных линий")
        self.btn_switch_remote_lines.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.switch_remote_lines_in_selected_dimensions()
            )
        )

        self.btn_switch_arrows = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/arrows.svg")), "")
        self.btn_switch_arrows.setToolTip("Переключить виды стрелок")
        self.btn_switch_arrows.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.switch_arrows_in_selected_dimensions()
            )
        )

        self.btn_settings = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/settings.svg")), "")
        self.btn_settings.setToolTip("Перейти в настройки")
        self.btn_settings.clicked.connect(self.config_window.show)


        self.layout_ = QtWidgets.QGridLayout()
        self.layout_.setContentsMargins(2, 2, 2, 2)
        self.layout_.setSpacing(2)
        self.layout_.addWidget(self.fiw_multiple, 0, 0, 1, 4)
        self.layout_.addWidget(self.btn_round_closest, 0, 4, 1, 1)
        self.layout_.addWidget(self.btn_round_down, 0, 5, 1, 1)
        self.layout_.addWidget(self.btn_round_up, 0, 6, 1, 1)
        self.layout_.addWidget(self.btn_no_round, 0, 7, 1, 1)
        self.layout_.addWidget(self.btn_select_rounded, 0, 8, 1, 1)

        self.layout_.addWidget(self.btn_sign_nothing, 1, 0, 1, 1)
        self.layout_.addWidget(self.btn_sign_diameter, 1, 1, 1, 1)
        self.layout_.addWidget(self.btn_sign_square, 1, 2, 1, 1)
        self.layout_.addWidget(self.btn_sign_radius, 1, 3, 1, 1)
        self.layout_.addWidget(self.btn_sign_metric, 1, 4, 1, 1)
        self.layout_.addWidget(self.btn_toggle_star, 1, 5, 1, 1)
        self.layout_.addWidget(self.btn_switch_remote_lines, 1, 6, 1, 1)
        self.layout_.addWidget(self.btn_switch_arrows, 1, 7, 1, 1)
        self.layout_.addWidget(self.btn_settings, 1, 8, 1, 1)
        self.setLayout(self.layout_)

        self.resize_icons(config.options["icon_size"])
        self.set_stays_on_top(config.options["window_stays_on_top"])


    def execute(self, func) -> None:
        QtWidgets.qApp.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            func()
        except Exception as e:
            QtWidgets.qApp.restoreOverrideCursor()
            self.show_error(e=e)
        QtWidgets.qApp.restoreOverrideCursor()


    def show_error(self, text: str = "Произошла ошибка", e: Exception = None) -> None:
            if e is None:
                e_str = ""
            else:
                e_str = f"<br>{e.__class__.__name__}: {str(e)}<br><pre>{traceback.format_exc()}</pre>"
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"{text}{e_str}",
            )

    def resize_icons(self, new_size: int) -> None:
        size = QtCore.QSize(new_size, new_size)
        self.btn_round_closest.setIconSize(size)
        self.btn_round_down.setIconSize(size)
        self.btn_round_up.setIconSize(size)
        self.btn_no_round.setIconSize(size)
        self.btn_select_rounded.setIconSize(size)
        self.btn_toggle_star.setIconSize(size)
        self.btn_sign_nothing.setIconSize(size)
        self.btn_sign_diameter.setIconSize(size)
        self.btn_sign_square.setIconSize(size)
        self.btn_sign_radius.setIconSize(size)
        self.btn_sign_metric.setIconSize(size)
        self.btn_switch_remote_lines.setIconSize(size)
        self.btn_switch_arrows.setIconSize(size)
        self.btn_settings.setIconSize(size)
        self.fiw_multiple.setFont(QtGui.QFont("monospace", max(int(new_size * 10/24), 8)))

    def set_stays_on_top(self, state: bool) -> None:
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, state)
        self.show()

    def remember_geometry(self) -> None:
        if config.options["remember_window_geometry"]:
            x, y = self.x(), self.y()
            w, h = self.width(), self.height()
            config.options["window_geometry"] = [x, y, w, h]
            config.save()

    def moveEvent(self, a0):
        self._window_moving_timer = self.startTimer(2000)
        return super().moveEvent(a0)

    def resizeEvent(self, a0):
        self._window_moving_timer = self.startTimer(2000)
        return super().resizeEvent(a0)

    def save_config_delayed(self) -> None:
        self._config_saving_timer = self.startTimer(1000)

    def timerEvent(self, event: QtCore.QTimerEvent):
        if event.timerId() == self._config_saving_timer:
            config.save()
            self.killTimer(self._config_saving_timer)

        if event.timerId() == self._window_moving_timer:
            self.remember_geometry()
            self.killTimer(self._window_moving_timer)

        return super().timerEvent(event)

    def restore_geometry_from_config(self) -> None:
        if config.options["remember_window_geometry"]:
            x, y, w, h = config.options["window_geometry"]
            if x != 0 and y != 0 and w != 0 and h != 0:
                s = QtWidgets.qApp.screenAt(QtCore.QPoint(x, y))
                if not s is None:
                    self.move(x, y)
                    self.resize(w, h)

    def closeEvent(self, a0):
        config.save()
        return super().closeEvent(a0)


if __name__ == "__main__":

    # values = [0.01, 0.02, 0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000]
    values = [1]
    for x in values:
        print(x, get_next_value(x, False), get_next_value(x, True))
