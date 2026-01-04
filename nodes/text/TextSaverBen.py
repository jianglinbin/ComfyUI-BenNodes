import os
import time
import logging
import json
import numpy as np
import torch

import folder_paths

class SaveTextBen:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "texts": ("STRING", {"tooltip": "要保存的文本或文本批次"}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "保存文件的前缀。可以包含格式化信息，如%date:yyyy-MM-dd%或其他变量"}),
                "file_extension": ("STRING", {"default": ".txt", "tooltip": "保存文件的后缀名，例如.txt、.md、.json等"})
            },
            "optional": {
                "filename": ("STRING", {"tooltip": "可选的文件名。如果是批次处理，可以输入文件名列表。如果包含文件后缀，会自动去除"})
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_texts"

    OUTPUT_NODE = True

    CATEGORY = "BenNodes/文本"
    DESCRIPTION = "将输入的文本或文本批次保存到ComfyUI输出目录"

    def save_texts(self, texts, filename_prefix="ComfyUI", file_extension=".txt", filename=None, prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        
        # 处理文本批次
        if isinstance(texts, str):
            text_list = [texts]
        elif isinstance(texts, list):
            text_list = texts
        elif hasattr(texts, "shape"):
            # 如果是张量形式的文本批次
            text_list = []
            for i in range(texts.shape[0]):
                text_item = texts[i]
                if hasattr(text_item, "item"):
                    text_item = text_item.item()
                elif isinstance(text_item, np.ndarray):
                    text_item = text_item.tolist()
                text_list.append(str(text_item))
        else:
            text_list = [str(texts)]
        
        # 处理文件名参数
        filename_list = None
        if filename is not None:
            if isinstance(filename, str):
                filename_list = [filename]
            elif isinstance(filename, list):
                filename_list = filename
            elif hasattr(filename, "shape"):
                # 如果是张量形式的文件名批次
                filename_list = []
                for i in range(filename.shape[0]):
                    filename_item = filename[i]
                    if hasattr(filename_item, "item"):
                        filename_item = filename_item.item()
                    elif isinstance(filename_item, np.ndarray):
                        filename_item = filename_item.tolist()
                    filename_list.append(str(filename_item))
            else:
                filename_list = [str(filename)]
            
            # 去除文件名中的后缀
            for i in range(len(filename_list)):
                name, _ = os.path.splitext(filename_list[i])
                filename_list[i] = name
        
        # 获取基本保存路径
        base_output_folder, default_filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, 0, 0
        )
        
        # 确保子文件夹被正确解析和创建
        # 从filename_prefix中提取子文件夹（处理不同的路径分隔符）
        if '\\' in filename_prefix or '/' in filename_prefix:
            # 提取路径部分
            path_part = os.path.dirname(filename_prefix)
            if path_part:
                # 创建完整的输出文件夹路径
                full_output_folder = os.path.join(self.output_dir, path_part)
            else:
                full_output_folder = base_output_folder
        else:
            full_output_folder = base_output_folder
        
        # 确保文件夹存在
        if not os.path.exists(full_output_folder):
            os.makedirs(full_output_folder, exist_ok=True)
        
        results = list()
        
        # 确保文件后缀以.开头
        if not file_extension.startswith("."):
            file_extension = "." + file_extension
        
        for (batch_number, text) in enumerate(text_list):
            # 确定当前文件的名称
            if filename_list and batch_number < len(filename_list):
                # 从用户提供的文件名中提取纯文件名（去除可能的路径部分）
                current_filename = os.path.basename(filename_list[batch_number])
            else:
                filename_with_batch_num = default_filename.replace("%batch_num%", str(batch_number))
                current_filename = f"{filename_with_batch_num}_{counter:05}_{batch_number}"
            
            # 生成完整文件名
            file = f"{current_filename}{file_extension}"
            
            # 保存文本文件
            file_path = os.path.join(full_output_folder, file)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1
        
        return { "ui": { "files": results } }