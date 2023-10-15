from PyQt5.QtWidgets import *
import window_mainwindow
import sys


def start_window():
    app = QApplication(sys.argv)
    main_window = window_mainwindow.MyMainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    start_window()
