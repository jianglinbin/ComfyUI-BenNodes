import os
import logging
import torch
import numpy as np
from PIL import Image
from ...utils.base.base_node import BaseResolutionNode
import folder_paths
import concurrent.futures
import multiprocessing
from ...utils.image.image_utils import process_image_for_comfy
from ...utils.i18n import t

logger = logging.getLogger(__name__)

class ImageLoaderBatchBen(BaseResolutionNode):
    """图片加载批次节点"""

    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        input_dir = folder_paths.get_input_directory()
        input_folders = [f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f))]

        return {
            "required": {
                "resize_mode": (cls.SCALE_MODES, {"default": "none"}),
                "position": (cls.SCALE_POSITIONS, {"default": "center"}),
                "resolution": (list(cls.RESOLUTIONS.keys()), {"default": "720p"}),
                "aspect_ratio": (list(cls.ASPECT_RATIOS.keys()), {"default": "16:9"}),
                "width": ("INT", {"default": 1080, "min": 16, "max": 32768, "step": 8}),
                "height": ("INT", {"default": 720, "min": 16, "max": 32768, "step": 8}),
                "folder_path": (sorted(input_folders), {"default": "", "label": t("image_batch_loader_folder_path_label")}),
                "feathering": ("INT", {"default": 0, "min": 0, "max": 256, "step": 1}),
                "upscale_method": (cls.UPSCALE_METHODS, {"default": "bicubic"}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "STRING")
    RETURN_NAMES = (t("image_common_return_image"), t("image_common_return_mask"),
                    t("image_common_return_width"), t("image_common_return_height"),
                    t("image_common_return_filename"))
    FUNCTION = "load_and_process_images"
    CATEGORY = f"BenNodes/{t('common_cat_image')}"

    def _process_image_task(self, img_path: str, resize_mode: str, target_width: int, target_height: int, feathering: int, upscale_method: str, position: str = "center"):
        """
        处理单张图像的任务函数（用于多线程）
        """
        try:
            img = Image.open(img_path).convert("RGB")
            img_tensor, mask_tensor, _, _ = process_image_for_comfy(
                img, resize_mode, target_width, target_height, feathering, upscale_method, position
            )
            return img_tensor[0], mask_tensor[0]
        except Exception as e:
            logger.error("处理图片失败 %s: %s", img_path, e)
            return None, None

    def load_and_process_images(self, resize_mode, position, resolution, aspect_ratio, width, height, folder_path="", feathering=0, upscale_method="bicubic", unique_id=None):
        """加载并处理图片（支持多线程处理）"""
        if not folder_path:
            raise ValueError(t("image_batch_loader_no_folder"))

        # 获取完整的文件夹路径
        full_folder_path = os.path.join(folder_paths.get_input_directory(), folder_path)

        if not os.path.isdir(full_folder_path):
            raise ValueError(t("image_batch_loader_folder_not_found").format(full_folder_path))

        # 获取文件夹中的所有图片文件
        image_paths = [os.path.join(full_folder_path, f) for f in os.listdir(full_folder_path)
                      if os.path.isfile(os.path.join(full_folder_path, f))
                      and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp'))]

        if not image_paths:
            raise ValueError(t("image_batch_loader_no_images").format(full_folder_path))

        # 计算目标分辨率
        if resize_mode == "none":
            # 不进行缩放，使用第一张图片的尺寸作为参考
            first_img = Image.open(image_paths[0]).convert("RGB")
            target_width, target_height = first_img.size
        else:
            target_width, target_height = self.calculate_dimensions(resolution, aspect_ratio, width, height)

        # 对于多张图片，即使resize_mode是"none"，也需要确保所有图片尺寸相同
        if len(image_paths) > 1 and resize_mode == "none":
            # 对于多张图片，强制使用"pad"模式确保尺寸一致（使用黑色背景填充）
            resize_mode = "pad"
            logger.debug("多张图片加载时自动使用 %s 模式确保尺寸一致", resize_mode)

        # 并行或串行处理（结果按文件顺序回填，保证批次顺序稳定）
        processed_images = []
        processed_masks = []
        image_names = []

        if len(image_paths) > 1:
            max_workers = multiprocessing.cpu_count()
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        self._process_image_task,
                        img_path, resize_mode, target_width, target_height, feathering, upscale_method, position
                    )
                    for img_path in image_paths
                ]
                results = [future.result() for future in futures]
        else:
            results = [self._process_image_task(img_path, resize_mode, target_width, target_height, feathering, upscale_method, position)
                       for img_path in image_paths]

        for img_path, (img_tensor, mask_tensor) in zip(image_paths, results):
            if img_tensor is not None:
                processed_images.append(img_tensor)
                processed_masks.append(mask_tensor)
                image_names.append(os.path.basename(img_path))

        if not processed_images:
            raise ValueError(t("image_batch_loader_load_failed"))

        # 转换为torch张量
        images_tensor = torch.stack(processed_images)
        masks_tensor = torch.stack(processed_masks)

        # 最终宽高取自第一张成功加载的图片（张量 shape: [H, W, C]）
        final_height, final_width = processed_images[0].shape[0], processed_images[0].shape[1]

        # 返回处理后的图片、遮罩和尺寸信息，以及文件名列表
        return (images_tensor, masks_tensor, final_width, final_height, image_names)
