import os
import logging

import folder_paths
import torch
from PIL import Image
import numpy as np
from ...utils.constants.constants import any_type
from ...utils.i18n import t

logger = logging.getLogger(__name__)

# 尝试导入 ComfyUI 的标准 VIDEO 类型
try:
    from comfy_api.latest._input_impl.video_types import VideoFromFile as InputImplVideoFromFile
    COMFY_VIDEO_AVAILABLE = True
except ImportError:
    COMFY_VIDEO_AVAILABLE = False
    InputImplVideoFromFile = None


class FileUploaderBen:
    """通用文件上传节点 - 支持从磁盘选择并上传任何类型的文件
    
    根据文件类型自动输出对应格式：
    - 图片文件：输出 IMAGE 类型（torch.Tensor）
    - 视频文件：输出 VIDEO 类型（使用 ComfyUI 标准 VideoFromFile，读取所有帧，无限制）
    - 其他文件：输出文件路径（STRING）

    输出可以直接连接到 SaveVideo 等节点
    """
    
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.webm', '.mkv'}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = (t("file_uploader_return_output"),)
    FUNCTION = "upload_file"
    CATEGORY = f"BenNodes/{t('common_cat_file')}"
    OUTPUT_NODE = False

    def upload_file(self, file: str):
        if not file:
            raise ValueError(t("file_uploader_no_file"))

        input_dir = folder_paths.get_input_directory()
        file_path = os.path.join(input_dir, file)

        if not os.path.isfile(file_path):
            raise ValueError(t("file_uploader_file_not_found").format(file_path))
        
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        if file_ext in self.IMAGE_EXTENSIONS:
            try:
                img = Image.open(file_path).convert("RGB")
                img_np = np.array(img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_np)[None,]
                logger.debug("已加载图片: %s (大小: %s 字节, 尺寸: %s)", file_path, file_size, img.size)
                return (img_tensor,)
            except Exception as e:
                raise ValueError(t("file_uploader_image_load_failed").format(e))

        elif file_ext in self.VIDEO_EXTENSIONS:
            try:
                if COMFY_VIDEO_AVAILABLE:
                    video = InputImplVideoFromFile(file_path)
                    logger.debug("已加载视频: %s (大小: %s 字节)", file_path, file_size)
                    return (video,)
                else:
                    logger.warning("ComfyUI VIDEO API 不可用，返回文件路径: %s", file_path)
                    return (file_path,)
            except Exception as e:
                raise ValueError(t("file_uploader_video_load_failed").format(e))

        else:
            logger.debug("已加载文件: %s (大小: %s 字节)", file_path, file_size)
            return (file_path,)
