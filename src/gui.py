from PyQt5 import QtCore, QtGui, QtWidgets
import os
import traceback

import src.round_dimensions as round_dimensions
import src.math_utils as math_utils

from src.resources import get_resource_path


SPINBOX_VALUES = [0.5, 1, 2, 5, 10]



def get_next_value(x: float, is_previous: bool) -> float:
    c10: int = math_utils.count_10(x)
    x /= 10 ** c10
    l_SBV = len(SPINBOX_VALUES)
    i = 0

    if not is_previous:
        for i in range(0, l_SBV):
            v = SPINBOX_VALUES[i]
            if v > x + math_utils.PRECISION_VALUE:
                break
    else:
        for i in range(l_SBV - 1, -1, -1):
            v = SPINBOX_VALUES[i]
            if v < x - math_utils.PRECISION_VALUE:
                break
    nv = SPINBOX_VALUES[i] * 10 ** c10
    return nv




class SpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setRange(10**-6, 10**9)
        self.setSingleStep(0.1)
        self.setValue(1.0)

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        delta = e.angleDelta().y()
        is_prev = delta < 0
        self.setValue(get_next_value(self.value(), is_prev))

    def setValue(self, val: float) -> None:
        self.setDecimals(3 + 3 * int(val < 1))
        super().setValue(val)



class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)
        self.resize(10, 10)

        self.cb_multiple = SpinBox()
        self.cb_multiple.setToolTip("Кратность округления")
        self.cb_multiple.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)

        self.btn_round_closest = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/middle.svg")), "")
        self.btn_round_closest.setToolTip("Округлить до ближайшего")
        self.btn_round_closest.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.round_selected_dimensions(self.cb_multiple.value(), 0.5)
            )
        )
        self.btn_round_closest.setIconSize(QtCore.QSize(24, 24))

        self.btn_round_down = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/down.svg")), "")
        self.btn_round_down.setToolTip("Округлить вниз")
        self.btn_round_down.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.round_selected_dimensions(self.cb_multiple.value(), 0)
            )
        )
        self.btn_round_down.setIconSize(QtCore.QSize(24, 24))

        self.btn_round_up = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/up.svg")), "")
        self.btn_round_up.setToolTip("Округлить вверх")
        self.btn_round_up.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.round_selected_dimensions(self.cb_multiple.value(), 1)
            )
        )
        self.btn_round_up.setIconSize(QtCore.QSize(24, 24))

        self.btn_no_round = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/no_round.svg")), "")
        self.btn_no_round.setToolTip("Вернуть неокругленное значение")
        self.btn_no_round.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.remove_rounding_in_selected_dimensions()
            )
        )
        self.btn_no_round.setIconSize(QtCore.QSize(24, 24))


        self.btn_select_rounded = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/select_rounded.svg")), "")
        self.btn_select_rounded.setToolTip("Выбрать размеры с ручным вводом (округленные)")
        self.btn_select_rounded.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.select_rounded_dimensions()
            )
        )
        self.btn_select_rounded.setIconSize(QtCore.QSize(24, 24))


        self.btn_toggle_star = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/star.svg")), "")
        self.btn_toggle_star.setToolTip("Добавить/убрать звездочку")
        self.btn_toggle_star.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.toggle_star_in_selected_dimensions()
            )
        )
        self.btn_toggle_star.setIconSize(QtCore.QSize(24, 24))


        self.btn_sign_nothing = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/nothing.svg")), "")
        self.btn_sign_nothing.setToolTip("Убрать знак перед размером")
        self.btn_sign_nothing.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.set_sign_in_selected_dimensions(round_dimensions.DimensionSign.Nothing)
            )
        )
        self.btn_sign_nothing.setIconSize(QtCore.QSize(24, 24))

        self.btn_sign_diameter = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/diameter.svg")), "")
        self.btn_sign_diameter.setToolTip("Установить знак диаметра")
        self.btn_sign_diameter.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.set_sign_in_selected_dimensions(round_dimensions.DimensionSign.Diameter)
            )
        )
        self.btn_sign_diameter.setIconSize(QtCore.QSize(24, 24))

        self.btn_sign_square = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/square.svg")), "")
        self.btn_sign_square.setToolTip("Установить знак квадрата")
        self.btn_sign_square.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.set_sign_in_selected_dimensions(round_dimensions.DimensionSign.Square)
            )
        )
        self.btn_sign_square.setIconSize(QtCore.QSize(24, 24))

        self.btn_sign_radius = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/radius.svg")), "")
        self.btn_sign_radius.setToolTip("Установить знак радиуса")
        self.btn_sign_radius.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.set_sign_in_selected_dimensions(round_dimensions.DimensionSign.Radius)
            )
        )
        self.btn_sign_radius.setIconSize(QtCore.QSize(24, 24))

        self.btn_sign_metric = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/metric.svg")), "")
        self.btn_sign_metric.setToolTip("Установить знак метрической резьбы")
        self.btn_sign_metric.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.set_sign_in_selected_dimensions(round_dimensions.DimensionSign.MetricThread)
            )
        )
        self.btn_sign_metric.setIconSize(QtCore.QSize(24, 24))

        self.btn_switch_remote_lines = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/remote_lines.svg")), "")
        self.btn_switch_remote_lines.setToolTip("Переключить отображение выносных линий")
        self.btn_switch_remote_lines.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.switch_remote_lines_in_selected_dimensions()
            )
        )
        self.btn_switch_remote_lines.setIconSize(QtCore.QSize(24, 24))

        self.btn_switch_arrows = QtWidgets.QPushButton(QtGui.QIcon(get_resource_path("img/arrows.svg")), "")
        self.btn_switch_arrows.setToolTip("Переключить виды стрелок")
        self.btn_switch_arrows.clicked.connect(
            lambda: self.execute(
                lambda: round_dimensions.switch_arrows_in_selected_dimensions()
            )
        )
        self.btn_switch_arrows.setIconSize(QtCore.QSize(24, 24))


        self.layout_ = QtWidgets.QGridLayout()
        self.layout_.setContentsMargins(2, 2, 2, 2)
        self.layout_.setSpacing(2)
        self.layout_.addWidget(self.cb_multiple, 0, 0, 1, 3)
        self.layout_.addWidget(self.btn_round_closest, 0, 3, 1, 1)
        self.layout_.addWidget(self.btn_round_down, 0, 4, 1, 1)
        self.layout_.addWidget(self.btn_round_up, 0, 5, 1, 1)
        self.layout_.addWidget(self.btn_no_round, 0, 6, 1, 1)
        self.layout_.addWidget(self.btn_select_rounded, 0, 7, 1, 1)

        self.layout_.addWidget(self.btn_sign_nothing, 1, 0, 1, 1)
        self.layout_.addWidget(self.btn_sign_diameter, 1, 1, 1, 1)
        self.layout_.addWidget(self.btn_sign_square, 1, 2, 1, 1)
        self.layout_.addWidget(self.btn_sign_radius, 1, 3, 1, 1)
        self.layout_.addWidget(self.btn_sign_metric, 1, 4, 1, 1)
        self.layout_.addWidget(self.btn_toggle_star, 1, 5, 1, 1)
        self.layout_.addWidget(self.btn_switch_remote_lines, 1, 6, 1, 1)
        self.layout_.addWidget(self.btn_switch_arrows, 1, 7, 1, 1)
        self.setLayout(self.layout_)

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




if __name__ == "__main__":

    values = [0.01, 0.02, 0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000]
    nvs = [get_next_value(x, False) for x in values]
    pvs = [get_next_value(x, True) for x in values]
    print(values, nvs, pvs, sep="\n")