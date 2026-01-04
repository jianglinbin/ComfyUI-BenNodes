
import torch
import numpy as np
from PIL import Image
from ...utils.base.base_node import BaseResolutionNode
import concurrent.futures
import multiprocessing
from typing import List, Tuple
from ...utils.image.image_utils import process_image_for_comfy

class ImageScalerBen(BaseResolutionNode):
    # 使用继承自BaseResolutionNode的SCALE_MODES常量
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "resize_mode": (s.SCALE_MODES, {"default": "none"}),
                "position": (s.SCALE_POSITIONS, {"default": "center"}),
                "resolution": (list(s.RESOLUTIONS.keys()), {"default": "720p"}),
                "aspect_ratio": (list(s.ASPECT_RATIOS.keys()), {"default": "16:9"}),
                "width": ("INT", {"default": 1080, "min": 1, "max": 8192}),
                "height": ("INT", {"default": 720, "min": 1, "max": 8192}),
                "feathering": ("INT", {"default": 40, "min": 0, "max": 200}),
                "upscale_method": (s.UPSCALE_METHODS, {"default": "bicubic"}),
                "pad_color": ("STRING", {"default": "127,127,127", "placeholder": "R,G,B (例如: 255,0,0)"}),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "MASK", "width", "height")
    FUNCTION = "process"
    CATEGORY = "BenNodes/图像"
    OUTPUT_NODE = True

    # 继承基类的calculate_dimensions 方法，无需重写

    def _process_single_pil_image(self, pil_image, resize_mode, target_width, target_height, feathering, upscale_method, position="center", pad_color=(127, 127, 127)):
        """处理单张PIL图像"""
        try:
            img_tensor, mask_tensor, fw, fh = process_image_for_comfy(
                pil_image, resize_mode, target_width, target_height, feathering, upscale_method, position, pad_color
            )
            return img_tensor[0], mask_tensor[0], fw, fh
        except Exception as e:
            print(f"Error processing image in scaler: {e}")
            return torch.zeros((target_height, target_width, 3)), torch.zeros((target_height, target_width)), target_width, target_height

    def process(self, image, resolution, aspect_ratio, width, height, resize_mode, position, feathering, upscale_method="bicubic", node_id=None, pad_color="127,127,127"):
        target_width, target_height = self.calculate_dimensions(resolution, aspect_ratio, width, height)
        batch_size = image.shape[0]
        result_images = []
        result_masks = []
        final_width = target_width
        final_height = target_height
        
        # 解析pad_color参数 (格式: "R,G,B")
        try:
            color_parts = pad_color.split(",")
            if len(color_parts) == 3:
                pad_color_tuple = (int(color_parts[0].strip()), int(color_parts[1].strip()), int(color_parts[2].strip()))
            else:
                pad_color_tuple = (127, 127, 127)  # 默认灰色
        except (ValueError, AttributeError):
            pad_color_tuple = (127, 127, 127)  # 默认灰色
        
        # 批量转换为PIL图像
        # image tensor is [B, H, W, C]. Range 0..1.
        img_arrays = (image.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
        pil_images = [Image.fromarray(img_arrays[i]) for i in range(batch_size)]
        
        if batch_size > 1:
            cpu_count = multiprocessing.cpu_count()
            with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count) as executor:
                results = list(executor.map(
                    self._process_single_pil_image,
                    pil_images,
                    [resize_mode] * batch_size,
                    [target_width] * batch_size,
                    [target_height] * batch_size,
                    [feathering] * batch_size,
                    [upscale_method] * batch_size,
                    [position] * batch_size,
                    [pad_color_tuple] * batch_size
                ))
                
            for i, (img_tensor, mask_tensor, fw, fh) in enumerate(results):
                result_images.append(img_tensor)
                result_masks.append(mask_tensor)
                if i == (batch_size - 1):
                    final_width, final_height = fw, fh
        else:
            for i, pil_image in enumerate(pil_images):
                img_tensor, mask_tensor, fw, fh = self._process_single_pil_image(pil_image, resize_mode, target_width, target_height, feathering, upscale_method, position, pad_color_tuple)
                result_images.append(img_tensor)
                result_masks.append(mask_tensor)
                if i == (batch_size - 1):
                    final_width, final_height = fw, fh
        
        # 使用torch.stack批量合并结果
        output_image = torch.stack(result_images, dim=0)
        output_mask = torch.stack(result_masks, dim=0)
        
        return {
            "ui": {
                "resolution_info": [{"width": final_width, "height": final_height, "resolution": resolution, "aspect_ratio": aspect_ratio, "resize_mode": resize_mode, "pad_color": pad_color}],
            },
            "result": (output_image, output_mask, target_width, target_height),
        }
