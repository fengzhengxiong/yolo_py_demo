#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_train 
@File    ：main.py
@Author  ：fengzhengxiong
@Date    ：2025/7/15 10:33 
'''


import sys
from PySide6.QtWidgets import QApplication, QMessageBox

sys.path.append('.')

from gui.main_window import MainWindow
from core.app_controller import AppController
from core.config_manager import ConfigManager

if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        config = ConfigManager('config.ini')
    except (Exception) as e:
        QMessageBox.critical(None, "配置错误", str(e))
        sys.exit(1)

    # 将配置实例传递给 MainWindow
    main_win = MainWindow(config)

    # Controller 保持不变
    controller = AppController(main_win, config)

    main_win.show()
    sys.exit(app.exec())