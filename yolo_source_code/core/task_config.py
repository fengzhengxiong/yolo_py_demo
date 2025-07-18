#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_det_source_code 
@File    ：task_config.py
@Author  ：fengzhengxiong
@Date    ：2025/7/17 11:22 
'''

# ==========================================================
#  任务模板注册表
#
#  - key: 任务的唯一标识符 (e.g., 'train', 'validate')
#  - 'name': 在UI中显示的友好名称
#  - 'required_paths': 一个列表，包含此任务需要从UI获取哪些路径的key。
#                      这些key必须与 MainWindow._get_current_paths() 返回的字典中的key一致。
#  - 'command_template': 一个f-string格式的命令行模板。
#                        占位符 {key} 会被 MainWindow._get_current_paths() 提供的路径替换。
#                        {python_exe} 和 {yolo_script} 会被自动替换。
# ==========================================================

TASK_CONFIG = {
    'train': {
        'name': "训练",
        'required_paths': ['yaml_path', 'train_dataset_folder'],
        'command_template': (
            '{python_exe} {yolo_script} cfg="{yaml_path}" '
            'train '
            'data="{train_dataset_folder}/data.yaml" name=train_results  batch=-1'
        )
    },
    'validate': {
        'name': "验证",
        'required_paths': ['yaml_path', 'best_pt_path', 'validation_folder'],
        'command_template': (
            '{python_exe} {yolo_script} cfg="{yaml_path}" '
            'predict '
            'model="{best_pt_path}" source="{validation_folder}" name=val_results retina_masks=True batch=1'
        )
    },
    'export': {
        'name': "导出ONNX",
        'required_paths': ['best_pt_path', 'yaml_path'],
        'command_template': (
            '{python_exe} {yolo_script} cfg="{yaml_path}" '
            'export '
            'model="{best_pt_path}" batch=1'
        )
    },
}

def get_task_config(task_id: str) -> dict:
    """获取指定任务的配置，如果不存在则抛出异常。"""
    if task_id not in TASK_CONFIG:
        raise ValueError(f"任务 '{task_id}' 未在 task_config.py 中定义。")
    return TASK_CONFIG[task_id]