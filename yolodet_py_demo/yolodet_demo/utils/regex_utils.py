#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_train 
@File    ：regex_utils.py
@Author  ：fengzhengxiong
@Date    ：2025/7/15 10:53 
'''

import re

# 用于从日志中捕获最佳模型的保存路径
# 例如，匹配 "Results saved to runs\train\exp3" 这样的行
RESULTS_DIR_REGEX = re.compile(r"Results saved to (.*)", re.IGNORECASE)