#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_train 
@File    ：command_builder.py
@Author  ：fengzhengxiong
@Date    ：2025/7/15 10:53 
'''

class CommandBuilder:
    def __init__(self, python_exe: str, yolo_script: str):
        self.python_exe = f'"{python_exe}"'
        self.yolo_script = f'"{yolo_script}"'

    def build_train_command(self, yaml_path: str) -> str:
        return f'{self.python_exe} {self.yolo_script} cfg="{yaml_path}"'

    def build_validate_command(self, yaml_path: str, best_pt_path: str, validation_folder_path: str) -> str:
        command = (
            f'{self.python_exe} {self.yolo_script} cfg="{yaml_path}" predict '
            f'model="{best_pt_path}" '
            f'source="{validation_folder_path}" '
            'name=val_results retina_masks=True batch=1'
        )
        return command

    def build_export_command(self, yaml_path: str, best_pt_path: str) -> str:
        return (
            f'{self.python_exe} {self.yolo_script} cfg="{yaml_path}" export '
            f'model="{best_pt_path}" '
            'batch=1'
        )