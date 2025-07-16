#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_train 
@File    ：app_controller.py
@Author  ：fengzhengxiong
@Date    ：2025/7/15 10:52 
'''


from PySide6.QtCore import QObject, Slot, QCoreApplication
from PySide6.QtWidgets import QMessageBox

from logic.command_builder import CommandBuilder

from .process_worker import ProcessWorker
from .conversion_worker import ConversionWorker
from .config_manager import ConfigManager


# ...
class AppController(QObject):
    def __init__(self, main_window, config: ConfigManager):
        super().__init__()
        self.window = main_window;
        self.config = config
        self.command_builder = CommandBuilder(self.config.python_exe, self.config.yolo_script)
        self.worker = None

        # 根据配置决定是否连接转换信号
        if self.config.enable_data_conversion:
            self.window.convert_requested.connect(self.on_start_conversion)

        self.window.train_requested.connect(self.on_start_training)
        self.window.validate_requested.connect(self.on_start_validation)
        self.window.export_requested.connect(self.on_start_exporting)
        self.window.stop_requested.connect(self.on_stop_task)
        self.window.closing.connect(self.on_window_closing)

    def _start_worker(self, worker_instance):
        if self.worker and self.worker.isRunning():
            self.window.show_message("警告", "已有任务在运行中！");
            return
        self.window.set_ui_state_busy(True);
        self.worker = worker_instance
        self.worker.log_message.connect(self.window.add_log)
        self.worker.finished.connect(self.on_any_task_finished)
        self.worker.start()

    @Slot(dict)
    def on_start_conversion(self, paths):
        labelme_root = paths['labelme_root']
        if not labelme_root: self.window.show_message("错误", "LabelMe数据集根目录不能为空！", is_error=True); return
        conversion_worker = ConversionWorker(labelme_root)
        conversion_worker.finished.connect(self.on_conversion_finished_callback)
        self._start_worker(conversion_worker)

    @Slot(bool, str)
    def on_conversion_finished_callback(self, is_success, result_or_error):
        """<<< 已移除自动填充，只显示结果信息"""
        if is_success:
            message = f"数据转换成功！\n生成的 data.yaml 位于: {result_or_error}\n请手动选择相关路径进行训练。"
            self.window.show_message("成功", message)
        else:
            self.window.show_message("转换失败", result_or_error, is_error=True)

    @Slot(bool, str)
    def on_any_task_finished(self, is_success, message):
        self.window.set_ui_state_busy(False)
        # 不再为转换任务显示通用结束信息，因为它有自己的回调
        if not isinstance(self.worker, ConversionWorker) and "用户手动终止" not in message:
            self.window.show_message("任务结束", message, is_error=not is_success)
        if self.worker:
            self.worker.wait();
            self.worker.deleteLater();
            self.worker = None

    # ... (on_start_training, on_start_validation 等所有其他方法都保持不变) ...
    @Slot(dict)
    def on_start_training(self, paths):
        self._start_worker(ProcessWorker(self.command_builder.build_train_command(paths['yaml_path'])))

    @Slot(dict)
    def on_start_validation(self, paths):
        self._start_worker(ProcessWorker(
            self.command_builder.build_validate_command(paths['yaml_path'], paths['best_pt_path'], paths['validation_folder'])))

    @Slot(dict)
    def on_start_exporting(self, paths):
        self._start_worker(
            ProcessWorker(self.command_builder.build_export_command(paths['yaml_path'], paths['best_pt_path'])))

    @Slot()
    def on_stop_task(self):
        if isinstance(self.worker, ProcessWorker) and self.worker.isRunning():
            self.worker.stop()
        else:
            self.window.add_log("[INFO] 当前任务无法被中途停止。")

    @Slot()
    def on_window_closing(self):
        if self.worker and self.worker.isRunning():
            reply = self.window.confirm_exit();
            if reply == QMessageBox.Yes:
                self.window.add_log("[INFO] 正在终止任务..."); self.on_stop_task(); QCoreApplication.processEvents(); (
                    self.worker.wait(5000) if self.worker else None); self.window.allow_close()
            else:
                self.window.prevent_close()
        else:
            self.window.allow_close()