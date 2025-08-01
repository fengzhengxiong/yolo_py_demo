#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：yolo_source_code
@File    ：data_converter.py
@Author  ：fengzhengxiong
@Date    ：2025/7/17 10:11 
'''


import os
import json
import random
import yaml
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any


class LabelmeConverter:
    """
    一个健壮的LabelMe到YOLO格式转换器。
    它结合了您两个版本的优点，并修复了关键的bug。
    """

    def __init__(self, dataset_root: str):
        self.root = Path(dataset_root)
        self.json_dir = self.root / 'jsons'
        # 保持 image_dir 的定义，split_dataset 函数会用到
        self.image_dir = self.root / 'images'
        self.label_dir = self.root / 'labels'
        self.classes: List[str] = []

    def _discover_classes_and_jsons(self) -> List[Path]:
        """
        自动从所有JSON文件中发现类别。这是一个很好的功能，我们予以保留。
        """
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
        """
        处理单个JSON文件，包含了对矩形和多边形的正确转换逻辑。
        """
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
                # 优化：当标签不在类别列表中时，打印警告而不是静默忽略
                print(f"警告: 在文件 '{json_path.name}' 中发现未知标签 '{label}'，将被忽略。")
                continue

            line = ""
            if shape_type == 'rectangle' and len(points) == 2:
                # 矩形逻辑是正确的，我们保持并优化格式
                x1, y1 = points[0]
                x2, y2 = points[1]
                cx = (x1 + x2) / 2 / w
                cy = (y1 + y2) / 2 / h
                width = abs(x2 - x1) / w
                height = abs(y2 - y1) / h
                # 优化：使用固定的小数位数，使输出更整洁
                line = f"{label_idx} {cx:.6f} {cy:.6f} {width:.6f} {height:.6f}"

            elif shape_type == 'polygon':
                # <<< 核心修正：采用您之前代码中的正确逻辑来处理多边形
                norm_points = []
                for point_pair in points:  # point_pair is [x, y]
                    x_norm = point_pair[0] / w
                    y_norm = point_pair[1] / h
                    norm_points.append(x_norm)
                    norm_points.append(y_norm)

                # 优化：使用固定的小数位数
                points_str = ' '.join(f"{p:.6f}" for p in norm_points)
                line = f"{label_idx} {points_str}"

            if line:
                lines.append(line)

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return txt_path.name

    def convert(self) -> Dict[str, Any]:
        """
        转换流程的总入口。
        """
        json_files = self._discover_classes_and_jsons()
        self.label_dir.mkdir(parents=True, exist_ok=True)
        total_files = len(json_files)

        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            futures = {executor.submit(self._process_single_json, json_path): json_path for json_path in json_files}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    # 提供更详细的错误日志
                    json_path_for_error = futures[future]
                    print(f"处理文件 {json_path_for_error.name} 时发生严重错误: {e}")

        return {
            "status": "success",
            "message": f"成功转换 {total_files} 个文件。",
            "output_label_dir": str(self.label_dir),
            "classes": self.classes,
        }


# ==========================================================
#  split_dataset 函数保持不变，它已经是正确的
# ==========================================================
def split_dataset(dataset_path: str, classes: List[str], train_ratio: float = 0.9) -> str:
    dataset_path = Path(dataset_path)
    image_dir = dataset_path / 'images'
    label_dir = dataset_path / 'labels'
    val_images_dir = dataset_path / 'val_images'

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

    if val_files:
        val_images_dir.mkdir(parents=True, exist_ok=True)
        for img_path in val_files:
            destination_path = val_images_dir / img_path.name
            shutil.copy2(img_path, destination_path)

    data_yaml_content = {
        'train': str(dataset_path / 'train.txt'),
        'val': str(dataset_path / 'val.txt'),
        'nc': len(classes),
        'names': classes
    }
    data_yaml_path = dataset_path / 'data.yaml'
    with open(data_yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data_yaml_content, f, sort_keys=False, allow_unicode=True)

    return str(data_yaml_path)