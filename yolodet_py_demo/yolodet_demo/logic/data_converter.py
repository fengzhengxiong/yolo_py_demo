#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_train 
@File    ：data_converter.py
@Author  ：fengzhengxiong
@Date    ：2025/7/15 16:31 
'''

# logic/data_converter.py
import os
import json
import random
import yaml
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Dict, Any

# class LabelmeConverter:
#     # ... (您提供的完整 LabelmeConverter 类代码) ...
#     def __init__(self, dataset_root: str):
#         self.root = Path(dataset_root)
#         self.json_dir = self.root / 'jsons'
#         self.image_dir = self.root / 'images'
#         self.label_dir = self.root / 'labels'
#         self.classes: List[str] = []
#
#     def _discover_classes_and_jsons(self) -> List[Path]:
#         if not self.json_dir.exists():
#             raise FileNotFoundError(f"错误: 未在 '{self.root}' 找到 'jsons' 文件夹。")
#         json_files = list(self.json_dir.glob('*.json'))
#         if not json_files:
#             raise ValueError(f"'jsons' 文件夹 '{self.json_dir}' 中没有找到任何 .json 文件。")
#         class_set = set()
#         for json_path in json_files:
#             with open(json_path, 'r', encoding='utf-8') as f:
#                 data = json.load(f)
#                 for shape in data.get('shapes', []):
#                     class_set.add(shape['label'])
#         self.classes = sorted(list(class_set))
#         if not self.classes:
#             raise ValueError("在所有JSON文件中都未能发现任何标签(label)。")
#         return json_files
#
#     def _process_single_json(self, json_path: Path):
#         with open(json_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         h, w = data['imageHeight'], data['imageWidth']
#         txt_filename = json_path.stem + '.txt'
#         txt_path = self.label_dir / txt_filename
#         lines = []
#         for shape in data.get('shapes', []):
#             label = shape['label']
#             points = shape['points']
#             shape_type = shape.get('shape_type', 'polygon')
#             try:
#                 label_idx = self.classes.index(label)
#             except ValueError:
#                 continue
#             line = ""
#             if shape_type == 'rectangle' and len(points) == 2:
#                 x1, y1 = points[0]; x2, y2 = points[1]
#                 cx, cy = (x1 + x2) / 2 / w, (y1 + y2) / 2 / h
#                 width, height = abs(x2 - x1) / w, abs(y2 - y1) / h
#                 line = f"{label_idx} {cx:.6f} {cy:.6f} {width:.6f} {height:.6f}"
#             elif shape_type == 'polygon':
#                 norm_points = []
#                 for i, p_pair in enumerate(points):
#                     norm_points.append(p_pair[0] / w)
#                     norm_points.append(p_pair[1] / h)
#                 points_str = ' '.join(f"{p:.6f}" for p in norm_points)
#                 line = f"{label_idx} {points_str}"
#             if line:
#                 lines.append(line)
#         if len(lines) > 0:
#             with open(txt_path, 'w', encoding='utf-8') as f:
#                 f.write('\n'.join(lines))
#         return txt_path.name
#
#     def convert(self) -> Dict[str, Any]:
#         json_files = self._discover_classes_and_jsons()
#         self.label_dir.mkdir(parents=True, exist_ok=True)
#         total_files = len(json_files)
#         with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
#             futures = {executor.submit(self._process_single_json, json_path): json_path for json_path in json_files}
#             for future in as_completed(futures):
#                 try:
#                     future.result()
#                 except Exception as e:
#                     print(f"处理文件 {futures[future].name} 时出错: {e}")
#         return {
#             "status": "success",
#             "message": f"成功转换 {total_files} 个文件。",
#             "output_label_dir": str(self.label_dir),
#             "classes": self.classes,
#         }
#
# def split_dataset(dataset_path: str, classes: List[str], train_ratio: float = 0.8) -> str:
#     # ... (您提供的完整 split_dataset 函数代码) ...
#     dataset_path = Path(dataset_path)
#     image_dir = dataset_path / 'images'
#     label_dir = dataset_path / 'labels'
#     if not image_dir.exists() or not label_dir.exists():
#         raise FileNotFoundError(f"错误: 必须同时存在 'images' ({image_dir}) 和 'labels' ({label_dir}) 文件夹。")
#     image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
#     image_files = [p for p in image_dir.glob('*') if p.suffix.lower() in image_extensions]
#     if not image_files:
#         raise FileNotFoundError(f"错误: 在 'images' 文件夹 ({image_dir}) 中没有找到任何支持的图片文件。")
#     label_stems = {p.stem for p in label_dir.glob('*.txt')}
#     if not label_stems:
#         raise FileNotFoundError(f"错误: 在 'labels' 文件夹 ({label_dir}) 中没有找到任何 .txt 标签文件。")
#     matched_images = [p for p in image_files if p.stem in label_stems]
#     if not matched_images:
#         image_stems = {p.stem for p in image_files}
#         labels_not_in_images, images_not_in_labels = label_stems - image_stems, image_stems - label_stems
#         error_msg = f"在 'images' 文件夹中没有找到任何与 'labels' 文件夹中标签匹配的图片。\n"
#         error_msg += f"诊断信息: 共找到 {len(image_stems)} 张图片, {len(label_stems)} 个标签。\n"
#         if labels_not_in_images: error_msg += f"- 示例标签 (有标签但无对应图片): {list(labels_not_in_images)[:3]}...\n"
#         if images_not_in_labels: error_msg += f"- 示例图片 (有图片但无对应标签): {list(images_not_in_labels)[:3]}...\n"
#         error_msg += "请重点检查：文件名是否完全一致（除扩展名）？文件名是否包含特殊字符或大小写不一致？"
#         raise ValueError(error_msg)
#     random.shuffle(matched_images)
#     split_index = int(len(matched_images) * train_ratio)
#     train_files, val_files = matched_images[:split_index], matched_images[split_index:]
#     with open(dataset_path / 'train.txt', 'w', encoding='utf-8') as f:
#         for p in train_files: f.write(f'./images/{p.name}\n')
#     with open(dataset_path / 'val.txt', 'w', encoding='utf-8') as f:
#         for p in val_files: f.write(f'./images/{p.name}\n')
#     data_yaml_content = {'train': str(dataset_path / 'train.txt'), 'val': str(dataset_path / 'val.txt'), 'nc': len(classes), 'names': classes}
#     data_yaml_path = dataset_path / 'data.yaml'
#     with open(data_yaml_path, 'w', encoding='utf-8') as f:
#         yaml.dump(data_yaml_content, f, sort_keys=False, allow_unicode=True)
#     return str(data_yaml_path)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_demo 
@File    ：dataset_handler.py
@Author  ：fengzhengxiong
@Date    ：2025/7/14 11:20 
'''


import os
import json
import random
import yaml
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Dict, Any

class LabelmeConverter:
    def __init__(self, dataset_root: str):
        self.root = Path(dataset_root)
        self.json_dir = self.root / 'jsons'
        self.image_dir = self.root / 'images'
        self.label_dir = self.root / 'labels'
        self.classes: List[str] = []

    def _discover_classes_and_jsons(self) -> List[Path]:
        if not self.json_dir.exists():
            raise FileNotFoundError(f"错误: 未在 '{self.root}' 找到 'jsons' 文件夹。")
        json_files = list(self.json_dir.glob('*.json'))
        if not json_files:
            raise ValueError(f"'jsons' 文件夹 '{self.json_dir}' 中没有找到任何 .json 文件。")
        class_set = set()
        for json_path in json_files:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for shape in data.get('shapes', []):
                    class_set.add(shape['label'])
        self.classes = sorted(list(class_set))
        if not self.classes:
            raise ValueError("在所有JSON文件中都未能发现任何标签(label)。")
        return json_files

    def _process_single_json(self, json_path: Path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        h, w = data['imageHeight'], data['imageWidth']
        txt_filename = json_path.stem + '.txt'
        txt_path = self.label_dir / txt_filename
        lines = []
        for shape in data.get('shapes', []):
            label = shape['label']
            points = shape['points']
            shape_type = shape.get('shape_type', 'polygon')
            try:
                label_idx = self.classes.index(label)
            except ValueError:
                continue
            line = ""
            if shape_type == 'rectangle' and len(points) == 2:
                x1, y1 = points[0]; x2, y2 = points[1]
                cx, cy = (x1 + x2) / 2 / w, (y1 + y2) / 2 / h
                width, height = abs(x2 - x1) / w, abs(y2 - y1) / h
                line = f"{label_idx} {cx} {cy} {width} {height}"
            elif shape_type == 'polygon':
                norm_points = [p / (w if i % 2 == 0 else h) for i, p_pair in enumerate(points) for p in p_pair]
                points_str = ' '.join(f"{p:.6f}" for p in norm_points)
                line = f"{label_idx} {points_str}"
            if line:
                lines.append(line)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return txt_path.name

    def convert(self) -> Dict[str, Any]:
        json_files = self._discover_classes_and_jsons()
        self.label_dir.mkdir(parents=True, exist_ok=True)
        total_files = len(json_files)
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            futures = {executor.submit(self._process_single_json, json_path): json_path for json_path in json_files}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"处理文件 {futures[future].name} 时出错: {e}")
        return {
            "status": "success",
            "message": f"成功转换 {total_files} 个文件。",
            "output_label_dir": str(self.label_dir),
            "classes": self.classes,
        }

def split_dataset(dataset_path: str, classes: List[str], train_ratio: float = 0.8) -> str:
    dataset_path = Path(dataset_path)
    image_dir = dataset_path / 'images'
    label_dir = dataset_path / 'labels'
    if not image_dir.exists() or not label_dir.exists():
        raise FileNotFoundError(f"错误: 必须同时存在 'images' ({image_dir}) 和 'labels' ({label_dir}) 文件夹。")
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
    image_files = [p for p in image_dir.glob('*') if p.suffix.lower() in image_extensions]
    if not image_files:
        raise FileNotFoundError(f"错误: 在 'images' 文件夹 ({image_dir}) 中没有找到任何支持的图片文件。")
    label_stems = {p.stem for p in label_dir.glob('*.txt')}
    if not label_stems:
        raise FileNotFoundError(f"错误: 在 'labels' 文件夹 ({label_dir}) 中没有找到任何 .txt 标签文件。")
    matched_images = [p for p in image_files if p.stem in label_stems]
    if not matched_images:
        image_stems = {p.stem for p in image_files}
        labels_not_in_images, images_not_in_labels = label_stems - image_stems, image_stems - label_stems
        error_msg = f"在 'images' 文件夹中没有找到任何与 'labels' 文件夹中标签匹配的图片。\n"
        error_msg += f"诊断信息: 共找到 {len(image_stems)} 张图片, {len(label_stems)} 个标签。\n"
        if labels_not_in_images: error_msg += f"- 示例标签 (有标签但无对应图片): {list(labels_not_in_images)[:3]}...\n"
        if images_not_in_labels: error_msg += f"- 示例图片 (有图片但无对应标签): {list(images_not_in_labels)[:3]}...\n"
        error_msg += "请重点检查：文件名是否完全一致（除扩展名）？文件名是否包含特殊字符或大小写不一致？"
        raise ValueError(error_msg)
    random.shuffle(matched_images)
    split_index = int(len(matched_images) * train_ratio)
    train_files, val_files = matched_images[:split_index], matched_images[split_index:]
    with open(dataset_path / 'train.txt', 'w', encoding='utf-8') as f:
        for p in train_files: f.write(f'./images/{p.name}\n')
    with open(dataset_path / 'val.txt', 'w', encoding='utf-8') as f:
        for p in val_files: f.write(f'./images/{p.name}\n')
    data_yaml_content = {'train': str(dataset_path / 'train.txt'), 'val': str(dataset_path / 'val.txt'), 'nc': len(classes), 'names': classes}
    data_yaml_path = dataset_path / 'data.yaml'
    with open(data_yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data_yaml_content, f, sort_keys=False, allow_unicode=True)
    return str(data_yaml_path)