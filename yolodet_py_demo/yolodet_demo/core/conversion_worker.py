#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_train 
@File    ：conversion_worker.py
@Author  ：fengzhengxiong
@Date    ：2025/7/15 16:32 
'''

from PySide6.QtCore import QThread, Signal
from logic.data_converter import LabelmeConverter, split_dataset  # 从我们刚创建的模块导入


class ConversionWorker(QThread):
    """
    在后台线程中执行LabelMe到YOLO格式的转换。
    """
    log_message = Signal(str)
    # finished 信号现在返回 (是否成功, 结果路径或错误信息)
    finished = Signal(bool, str)

    def __init__(self, labelme_root_path: str):
        super().__init__()
        self.root_path = labelme_root_path

    def run(self):
        try:
            self.log_message.emit("=" * 50)
            self.log_message.emit(f"开始处理数据集: {self.root_path}")

            # 步骤 1: 转换 LabelMe JSONs 到 YOLO txt
            self.log_message.emit("[步骤 1/2] 正在转换 LabelMe JSON 文件为 YOLO labels...")
            converter = LabelmeConverter(self.root_path)
            convert_result = converter.convert()
            self.log_message.emit(f"[成功] {convert_result['message']}")
            self.log_message.emit(f"发现的类别: {convert_result['classes']}")

            # 步骤 2: 划分数据集并生成 data.yaml
            self.log_message.emit("[步骤 2/2] 正在划分训练/验证集并生成 data.yaml...")
            # split_dataset 函数的第一个参数是数据集根目录
            data_yaml_path = split_dataset(self.root_path, convert_result['classes'])
            self.log_message.emit(f"[成功] 已生成YOLO配置文件: {data_yaml_path}")
            self.log_message.emit("=" * 50)

            # 发送成功信号，并附带生成的yaml文件路径
            self.finished.emit(True, data_yaml_path)

        except Exception as e:
            # 如果任何步骤出错，发送失败信号和错误信息
            error_msg = f"[错误] 数据转换失败: {e}"
            self.log_message.emit(error_msg)
            self.finished.emit(False, str(e))