import os
import folder_paths
from typing import Tuple
import torch
from PIL import Image
import numpy as np
from ...utils.constants.constants import any_type

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
    
    输出可以直接连接到 GLMNodeBen 或 SaveVideo 等节点
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
    RETURN_NAMES = ("输出",)
    FUNCTION = "upload_file"
    CATEGORY = "BenNodes/文件"
    OUTPUT_NODE = False

    def upload_file(self, file: str):
        if not file:
            raise ValueError("请选择文件")
        
        input_dir = folder_paths.get_input_directory()
        file_path = os.path.join(input_dir, file)
        
        if not os.path.isfile(file_path):
            raise ValueError(f"文件不存在: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        if file_ext in self.IMAGE_EXTENSIONS:
            try:
                img = Image.open(file_path).convert("RGB")
                img_np = np.array(img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_np)[None,]
                print(f"已加载图片: {file_path} (大小: {file_size} 字节, 尺寸: {img.size})")
                return (img_tensor,)
            except Exception as e:
                raise ValueError(f"图片加载失败: {e}")
        
        elif file_ext in self.VIDEO_EXTENSIONS:
            try:
                if COMFY_VIDEO_AVAILABLE:
                    video = InputImplVideoFromFile(file_path)
                    print(f"已加载视频: {file_path} (大小: {file_size} 字节)")
                    return (video,)
                else:
                    print(f"ComfyUI VIDEO API 不可用，返回文件路径: {file_path}")
                    return (file_path,)
            except Exception as e:
                raise ValueError(f"视频加载失败: {e}")
        
        else:
            print(f"已加载文件: {file_path} (大小: {file_size} 字节)")
            return (file_path,)
