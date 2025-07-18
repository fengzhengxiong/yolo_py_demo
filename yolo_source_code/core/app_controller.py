#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_det_source_code 
@File    ：app_controller.py
@Author  ：fengzhengxiong
@Date    ：2025/7/17 11:22 
'''


from PySide6.QtCore import QObject, Slot, QCoreApplication
from PySide6.QtWidgets import QMessageBox

from .process_worker import ProcessWorker
from .conversion_worker import ConversionWorker
from .config_manager import ConfigManager
from .task_config import get_task_config


class AppController(QObject):
    def __init__(self, main_window, config: ConfigManager):
        super().__init__()
        self.window = main_window
        self.config = config
        self.worker = None

        # 将UI按钮的点击信号连接到一个通用的处理函数
        self.window.train_button.clicked.connect(lambda: self.on_start_generic_task('train'))
        self.window.validate_button.clicked.connect(lambda: self.on_start_generic_task('validate'))
        self.window.export_button.clicked.connect(lambda: self.on_start_generic_task('export'))

        # 保持不变的信号连接
        self.window.stop_requested.connect(self.on_stop_task)
        self.window.closing.connect(self.on_window_closing)
        if self.config.enable_data_conversion:
            self.window.convert_requested.connect(self.on_start_conversion)

    def _start_worker(self, worker_instance):
        if self.worker and self.worker.isRunning():
            self.window.show_message("警告", "已有任务在运行中！")
            return
        self.window.set_ui_state_busy(True)
        self.worker = worker_instance
        self.worker.log_message.connect(self.window.add_log)

        # 为不同类型的worker连接不同的完成回调
        if isinstance(self.worker, ProcessWorker):
            self.worker.finished.connect(self.on_process_task_finished)
        elif isinstance(self.worker, ConversionWorker):
            self.worker.finished.connect(self.on_conversion_finished_callback)

        self.worker.start()

    @Slot(str)
    def on_start_generic_task(self, task_id: str):
        """一个处理所有基于命令行的任务的通用槽函数。"""
        try:
            task_info = get_task_config(task_id)
            task_name = task_info['name']

            all_paths = self.window._get_current_paths()
            for required_key in task_info['required_paths']:
                if not all_paths.get(required_key):
                    field_name = self.window.get_field_name_by_key(required_key)
                    self.window.show_message("错误", f"执行“{task_name}”任务前，请先提供“{field_name}”的路径。",
                                             is_error=True)
                    return

            command_template = task_info['command_template']
            format_dict = {
                'python_exe': f'"{self.config.python_exe}"',
                'yolo_script': f'"{self.config.yolo_script}"',
                **all_paths
            }
            command = command_template.format(**format_dict)

            self.window.log_console.clear()
            self.window.add_log(f"--- 开始执行任务: {task_name} ---")
            self._start_worker(ProcessWorker(command))

        except Exception as e:
            self.window.show_message("配置错误", f"无法启动任务 '{task_id}': {e}", is_error=True)

    @Slot(bool, str)
    def on_process_task_finished(self, is_success, message):
        """处理 ProcessWorker 完成的通用回调。"""
        self.window.set_ui_state_busy(False)
        if "用户手动终止" not in message:
            self.window.show_message("任务结束", message, is_error=not is_success)
        if self.worker:
            self.worker.wait()
            self.worker.deleteLater()
            self.worker = None

    @Slot()
    def on_stop_task(self):
        if self.worker and self.worker.isRunning():
            if isinstance(self.worker, ProcessWorker):
                self.worker.stop()
            else:
                self.window.add_log("[INFO] 当前任务无法被中途停止。")
        else:
            self.window.add_log("[INFO] 没有正在运行的任务可以停止。")

    @Slot()
    def on_window_closing(self):
        if self.worker and self.worker.isRunning():
            reply = self.window.confirm_exit()
            if reply == QMessageBox.Yes:
                self.window.add_log("[INFO] 正在终止任务...")
                self.on_stop_task()
                QCoreApplication.processEvents()
                if self.worker:
                    self.worker.wait(5000)
                self.window.allow_close()
            else:
                self.window.prevent_close()
        else:
            self.window.allow_close()

    # --- 数据转换部分保持不变 ---
    @Slot(dict)
    def on_start_conversion(self, paths):
        labelme_root = paths['labelme_root']
        if not labelme_root:
            self.window.show_message("错误", "LabelMe数据集根目录不能为空！", is_error=True)
            return
        conversion_worker = ConversionWorker(labelme_root)
        self._start_worker(conversion_worker)

    @Slot(bool, str)
    def on_conversion_finished_callback(self, is_success, result_or_error):
        self.window.set_ui_state_busy(False)
        if is_success:
            message = f"数据转换成功！\n生成的 data.yaml 位于: {result_or_error}\n请手动选择相关路径进行训练。"
            self.window.show_message("成功", message)
        else:
            self.window.show_message("转换失败", result_or_error, is_error=True)
        if self.worker:
            self.worker.wait()
            self.worker.deleteLater()
            self.worker = None