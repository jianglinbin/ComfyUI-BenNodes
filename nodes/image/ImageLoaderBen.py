import os
import torch
import numpy as np
from PIL import Image, ImageOps, ImageSequence
import hashlib
import folder_paths
import node_helpers
from ...utils.base.base_node import BaseResolutionNode
from ...utils.image.image_utils import process_image_for_comfy

class LoadImageBen(BaseResolutionNode):
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        files = folder_paths.filter_files_content_types(files, ["image"])
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True}),
                "resize_mode": (s.SCALE_MODES, {"default": "none"}),
                "position": (s.SCALE_POSITIONS, {"default": "center"}),
                "resolution": (list(s.RESOLUTIONS.keys()), {"default": "720p"}),
                "aspect_ratio": (list(s.ASPECT_RATIOS.keys()), {"default": "16:9"}),
                "width": ("INT", {"default": 1080, "min": 16, "max": 32768, "step": 8}),
                "height": ("INT", {"default": 720, "min": 16, "max": 32768, "step": 8}),
                "feathering": ("INT", {"default": 0, "min": 0, "max": 256, "step": 1}),
                "upscale_method": (s.UPSCALE_METHODS, {"default": "bicubic"}),
            }
        }

    CATEGORY = "BenNodes/图像"
    DESCRIPTION = "加载单张图片，支持各种常见图片格式"

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "STRING")
    RETURN_NAMES = ("图片", "遮罩", "宽度", "高度", "文件名")
    FUNCTION = "load_image"
    
    def load_image(self, image, resize_mode, position, resolution, aspect_ratio, width, height, feathering=0, upscale_method="bicubic"):
        image_path = folder_paths.get_annotated_filepath(image)

        # 计算目标分辨率
        if resize_mode == "none":
            # 不进行缩放，使用原图尺寸
            target_width, target_height = width, height
        else:
            target_width, target_height = self.calculate_dimensions(resolution, aspect_ratio, width, height)

        img = node_helpers.pillow(Image.open, image_path)

        # 使用公共工具处理图像
        output_image, output_mask, w, h = process_image_for_comfy(
            img, resize_mode, target_width, target_height, feathering, upscale_method, position
        )

        # 提取文件名（不含路径）
        filename = os.path.basename(image_path)
        return (output_image, output_mask, w, h, filename)

    @classmethod
    def IS_CHANGED(s, image, resize_mode=None, position=None, resolution=None, aspect_ratio=None, width=None, height=None, feathering=None, upscale_method=None):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        # 加入所有可能影响输出的参数
        m.update(str(resize_mode).encode('utf-8'))
        m.update(str(position).encode('utf-8'))
        m.update(str(resolution).encode('utf-8'))
        m.update(str(aspect_ratio).encode('utf-8'))
        m.update(str(width).encode('utf-8'))
        m.update(str(height).encode('utf-8'))
        m.update(str(feathering).encode('utf-8'))
        m.update(str(upscale_method).encode('utf-8'))
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image, resize_mode=None, position=None, resolution=None, aspect_ratio=None, width=None, height=None, feathering=None, upscale_method=None):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True