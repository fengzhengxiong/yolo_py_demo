Demo 开发介绍：
---
## 开发背景：
阿熊想成为一个yolo视觉大佬。

## 开发目的：
自我学习。我爱学习。

---
## 项目介绍：
- yolo_det_datasets：目标检测数据集（labelme 格式）
- yolo_seg_datasets：实例分割数据集（labelme 格式）
- yolo_source_code： 可视化源码

---
## 待做功能：
- 点击 开始训练的时候 自动清理 train_result,避免崩溃报错
- 区分开：det 数据集用 seg 模型（增加任务划分）
- 增加 yolo v8 v11 v12等的选项
- 打包exe
- 训练环境升级 加入到exe中

---
## 待做任务介绍：
- 将导出的 onnx 模型用c++重新部署：（手撕一遍 yolo 推理）
- openvino 部署
- onnxruntime 部署