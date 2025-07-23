#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_source_code
@File    ：main_window.py
@Author  ：fengzhengxiong
@Date    ：2025/7/17 11:22 
'''


from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QTextEdit, QFileDialog, QMessageBox, QGroupBox
)
from PySide6.QtCore import Signal, Slot, Qt

class MainWindow(QMainWindow):
    convert_requested = Signal(dict)
    train_requested = Signal(dict)
    validate_requested = Signal(dict)
    export_requested = Signal(dict)

    stop_requested = Signal()
    closing = Signal()

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.setWindowTitle("YOLO Suite")
        self.setGeometry(100, 100, 900, 750)
        self._close_allowed = True

        self._create_widgets()
        self._layout_widgets()
        self._connect_signals()
        self._update_button_states()

    def _create_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        if self.config.enable_data_conversion:
            self.prepare_group = QGroupBox("辅助功能：数据准备 (LabelMe -> YOLO)")
            self.labelme_root_edit = QLineEdit()
            self.convert_button = QPushButton("转换数据集")
        else:
            self.prepare_group = None

        self.train_group = QGroupBox("1. 训练模块")
        self.train_dataset_edit = QLineEdit()
        self.yaml_path_edit = QLineEdit()

        self.validate_group = QGroupBox("2. 验证模块")
        self.validation_folder_edit = QLineEdit()
        self.validate_pt_edit = QLineEdit()

        self.actions_group = QGroupBox("3. 操作与日志")
        self.train_button = QPushButton("开始训练")
        self.validate_button = QPushButton("开始验证")
        self.export_button = QPushButton("导出为ONNX")
        self.stop_button = QPushButton("停止当前任务")
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)

    def _layout_widgets(self):
        main_layout = QVBoxLayout(self.central_widget)
        if self.prepare_group:
            prepare_layout = QVBoxLayout()
            prepare_layout.addLayout(self._create_path_selector("LabelMe数据集根目录:", self.labelme_root_edit, is_file=False))
            prepare_layout.addWidget(self.convert_button, 0, Qt.AlignCenter)
            self.prepare_group.setLayout(prepare_layout)
            main_layout.addWidget(self.prepare_group)

        train_layout = QVBoxLayout()
        train_layout.addLayout(self._create_path_selector("训练数据集文件夹:", self.train_dataset_edit, is_file=False))
        train_layout.addLayout(self._create_path_selector("训练配置文件 (yolo.yaml):", self.yaml_path_edit, is_file=True))
        self.train_group.setLayout(train_layout)

        validate_layout = QVBoxLayout()
        validate_layout.addLayout(self._create_path_selector("验证图片文件夹:", self.validation_folder_edit, is_file=False))
        validate_layout.addLayout(self._create_path_selector("模型文件 (best.pt):", self.validate_pt_edit, is_file=True))
        self.validate_group.setLayout(validate_layout)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.train_button)
        actions_layout.addWidget(self.validate_button)
        actions_layout.addWidget(self.export_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.stop_button)
        log_layout = QVBoxLayout()
        log_layout.addLayout(actions_layout)
        log_layout.addWidget(QLabel("运行日志:"))
        log_layout.addWidget(self.log_console)
        self.actions_group.setLayout(log_layout)

        main_layout.addWidget(self.train_group)
        main_layout.addWidget(self.validate_group)
        main_layout.addWidget(self.actions_group)

    def _connect_signals(self):
        if self.prepare_group:
            self.convert_button.clicked.connect(self._on_convert_clicked)
            self.labelme_root_edit.textChanged.connect(self._update_button_states)

        self.stop_button.clicked.connect(self.stop_requested.emit)

        # Connect text changed signals to update button states
        self.train_dataset_edit.textChanged.connect(self._update_button_states)
        self.yaml_path_edit.textChanged.connect(self._update_button_states)
        self.validation_folder_edit.textChanged.connect(self._update_button_states)
        self.validate_pt_edit.textChanged.connect(self._update_button_states)

    @Slot()
    def _update_button_states(self):
        if self.prepare_group:
            self.convert_button.setEnabled(bool(self.labelme_root_edit.text().strip()))

        train_folder = self.train_dataset_edit.text().strip()
        yaml_path = self.yaml_path_edit.text().strip()
        val_folder = self.validation_folder_edit.text().strip()
        best_pt = self.validate_pt_edit.text().strip()

        self.train_button.setEnabled(bool(train_folder) and bool(yaml_path))
        self.validate_button.setEnabled(bool(val_folder) and bool(best_pt))
        self.export_button.setEnabled(bool(yaml_path) and bool(best_pt))

    def _get_current_paths(self) -> dict:
        paths = {
            'train_dataset_folder': self.train_dataset_edit.text().strip(),
            'yaml_path': self.yaml_path_edit.text().strip(),
            'validation_folder': self.validation_folder_edit.text().strip(),
            'best_pt_path': self.validate_pt_edit.text().strip()
        }
        if self.prepare_group:
            paths['labelme_root'] = self.labelme_root_edit.text().strip()
        return paths

    def get_field_name_by_key(self, key: str) -> str:
        mapping = {
            'train_dataset_folder': "训练数据集文件夹",
            'yaml_path': "训练配置文件 (yolo.yaml)",
            'validation_folder': "验证图片文件夹",
            'best_pt_path': "模型文件 (best.pt)",
            'labelme_root': "LabelMe数据集根目录"
        }
        return mapping.get(key, key)

    def _on_convert_clicked(self):
        self.log_console.clear()
        self.convert_requested.emit(self._get_current_paths())

    @Slot(bool)
    def set_ui_state_busy(self, is_busy: bool):
        if self.prepare_group: self.prepare_group.setEnabled(not is_busy)
        self.train_group.setEnabled(not is_busy)
        self.validate_group.setEnabled(not is_busy)
        self.stop_button.setEnabled(is_busy)

        if is_busy:
            if self.prepare_group: self.convert_button.setEnabled(False)
            self.train_button.setEnabled(False)
            self.validate_button.setEnabled(False)
            self.export_button.setEnabled(False)
        else:
            self._update_button_states()

    def _create_path_selector(self, label_text, line_edit, is_file):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        layout.addWidget(line_edit)
        button = QPushButton("浏览...")
        button.clicked.connect(lambda: self._browse_path(line_edit, is_file))
        layout.addWidget(button)
        return layout

    def _browse_path(self, line_edit, is_file):
        path = ""
        if is_file:
            path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        else:
            path, _ = QFileDialog.getExistingDirectory(self, "选择文件夹"), ""
        if path:
            line_edit.setText(path)

    @Slot(str)
    def add_log(self, text):
        self.log_console.append(text)
        self.log_console.verticalScrollBar().setValue(self.log_console.verticalScrollBar().maximum())

    def show_message(self, title, text, is_error=False):
        if is_error:
            QMessageBox.critical(self, title, text)
        else:
            QMessageBox.information(self, title, text)

    def closeEvent(self, event):
        if not self._close_allowed:
            self.closing.emit()
            event.ignore()
        else:
            super().closeEvent(event)
            event.accept()

    @Slot()
    def allow_close(self):
        self._close_allowed = True
        self.close()

    @Slot()
    def prevent_close(self):
        self._close_allowed = False

    def confirm_exit(self) -> QMessageBox.StandardButton:
        return QMessageBox.question(self, '确认退出', "任务仍在运行中，确定要强制退出吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)