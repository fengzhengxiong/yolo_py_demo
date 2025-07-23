Demo 开发介绍：
---
## 开发背景：
阿熊正在做yolo的一些视觉项目，关于yolo的命令行训练，觉得没有一个界面可视化方便
遂开发了这款demo

## 开发目的：
自我学习。

## 开发环境：
- python = 3.13.5
- pyside6 = 6.9.1

## 训练环境：
certifi            2025.7.14
charset-normalizer 3.4.2
colorama           0.4.6
contourpy          1.3.2
cycler             0.12.1
dill               0.4.0
filelock           3.18.0
fonttools          4.58.5
fsspec             2025.5.1
idna               3.10
Jinja2             3.1.6
kiwisolver         1.4.8
MarkupSafe         3.0.2
matplotlib         3.10.3
mpmath             1.3.0
networkx           3.5
numpy              2.2.6
onnx               1.17.0
opencv-python      4.12.0.88
packaging          25.0
pandas             2.3.1
pillow             11.3.0
pip                25.1
protobuf           6.31.1
psutil             7.0.0
py-cpuinfo         9.0.0
pyparsing          3.2.3
python-dateutil    2.9.0.post0
pytz               2025.2
PyYAML             6.0.2
requests           2.32.4
scipy              1.16.0
setuptools         78.1.1
six                1.17.0
sympy              1.13.1
torch              2.5.1+cu121
torchaudio         2.5.1+cu121
torchvision        0.20.1+cu121
tqdm               4.67.1
typing_extensions  4.14.1
tzdata             2025.2
ultralytics        8.3.166
ultralytics-thop   2.0.14
urllib3            2.5.0
wheel              0.45.1

## 注意事项：
- 模型训练，验证，导出，是使用cmd命令行启动的。所以要注意跨平台的问题.
- 训练环境，demo环境，是两个虚拟环境
- 在运行demo的时候要先更改 config.ini 中的虚拟环境的路径
- 如果你的是 labelme 数据集，请先转为 coco 数据集： config.ini 中的 enable_data_conversion 设置为True
- 数据集转换 模块可以隐藏
- 注意显存问题
- 注意多线程问题

## 寄语：
- 该 demo 主要用于自我学习。
- 若有 bug ，自行修改（反正我用的时候没 bug）