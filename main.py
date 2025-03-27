from PyQt5 import QtCore, QtGui, QtWidgets
from sys import exit

import src.gui as gui
import src.round_dimensions as round_dimensions

from src.resources import *

from src import config

set_bundle_dir_by_main_file(__file__)



app = QtWidgets.QApplication([])
app.setWindowIcon(QtGui.QIcon(get_resource_path("icon/icon.ico")))
app.setApplicationName(config.PROGRAM_NAME)


if not round_dimensions.is_kompas_running():
    QtWidgets.QMessageBox.critical(
        None,
        "Компас-3D не запущен",
        "Не найдено запущенное приложение Компас-3D.\nПрограмма будет закрыта.",
        QtWidgets.QMessageBox.StandardButton.Ok,
    )
    exit(1)

w = gui.MainWindow()
w.show()
w.restore_geometry_from_config()

app.exec()
