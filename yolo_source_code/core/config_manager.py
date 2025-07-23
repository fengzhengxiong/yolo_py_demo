#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_source_code
@File    ：config_manager.py
@Author  ：fengzhengxiong
@Date    ：2025/7/17 10:10 
'''


import configparser

class ConfigManager:
    def __init__(self, config_path='config.ini'):
        self.config = configparser.ConfigParser()
        if not self.config.read(config_path):
            raise FileNotFoundError(f"配置文件 '{config_path}' 未找到或读取失败。")

        self._load_env_config()
        self._load_feature_config()

    def _load_env_config(self):
        try:
            self.python_exe = self.config.get('Environment', 'python_executable')
            self.yolo_script = self.config.get('Environment', 'yolo_script')
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise ValueError(f"配置文件[Environment]部分格式错误: {e}")

    def _load_feature_config(self):
        try:
            self.enable_data_conversion = self.config.getboolean('Features', 'enable_data_conversion')
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.enable_data_conversion = False
        except ValueError as e:
            raise ValueError(f"配置文件[Features]部分格式错误: {e}")