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
    
    # 支持的文件类型
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.webm', '.mkv'}
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
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
        """
        加载文件并返回对应格式的数据
        
        根据文件类型自动返回：
        - 图片文件 → IMAGE 类型（torch.Tensor）
        - 视频文件 → VIDEO 类型（使用 ComfyUI 标准 VideoFromFile，读取所有帧）
        - 其他文件 → 文件路径字符串
        
        Args:
            file: 文件名（相对于 input 目录）
            
        Returns:
            图片张量 / 视频对象 / 文件路径字符串
        """
        if not file:
            raise ValueError("请选择文件")
        
        # 获取完整路径
        input_dir = folder_paths.get_input_directory()
        file_path = os.path.join(input_dir, file)
        
        if not os.path.isfile(file_path):
            raise ValueError(f"文件不存在: {file_path}")
        
        # 获取文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        # 根据文件类型处理
        if file_ext in self.IMAGE_EXTENSIONS:
            # 图片文件：转换为 IMAGE 类型
            try:
                img = Image.open(file_path).convert("RGB")
                img_np = np.array(img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_np)[None,]  # 添加批次维度 [1, H, W, C]
                print(f"已加载图片: {file_path} (大小: {file_size} 字节, 尺寸: {img.size})")
                return (img_tensor,)
            except Exception as e:
                raise ValueError(f"图片加载失败: {e}")
        
        elif file_ext in self.VIDEO_EXTENSIONS:
            # 视频文件：使用 ComfyUI 标准 VIDEO 类型（读取所有帧，无限制）
            try:
                if COMFY_VIDEO_AVAILABLE:
                    # 使用 ComfyUI 标准 VIDEO 类型（完全兼容 SaveVideo 等节点）
                    video = InputImplVideoFromFile(file_path)
                    print(f"已加载视频: {file_path} (大小: {file_size} 字节)")
                    return (video,)
                else:
                    # 降级：返回文件路径（GLMNodeBen 可以处理路径）
                    print(f"ComfyUI VIDEO API 不可用，返回文件路径: {file_path}")
                    return (file_path,)
            except Exception as e:
                raise ValueError(f"视频加载失败: {e}")
        
        else:
            # 其他文件：返回路径字符串（PDF、Office 文档等）
            print(f"已加载文件: {file_path} (大小: {file_size} 字节)")
            return (file_path,)


class FileUploaderMultiBen:
    """批量文件上传节点 - 支持从文件夹选择并上传多个文件"""
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "folder_path": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "file_pattern": ("STRING", {"default": "*.*", "multiline": False}),
                "max_files": ("INT", {"default": 100, "min": 1, "max": 10000, "step": 1}),
            }
        }
    
    RETURN_TYPES = ("LIST", "INT")
    RETURN_NAMES = ("文件路径列表", "文件数量")
    FUNCTION = "upload_files"
    CATEGORY = "BenNodes/文件"
    OUTPUT_NODE = False

    def upload_files(self, folder_path: str, file_pattern: str = "*.*", max_files: int = 100) -> Tuple[list, int]:
        """
        批量加载文件并返回文件路径列表
        
        Args:
            folder_path: 文件夹名称（相对于 input 目录）
            file_pattern: 文件匹配模式，如 "*.pdf", "*.txt", "*.*"
            max_files: 最大加载文件数
            
        Returns:
            (文件路径列表, 文件数量)
        """
        if not folder_path:
            raise ValueError("请选择文件夹")
        
        # 获取完整路径
        input_dir = folder_paths.get_input_directory()
        full_folder_path = os.path.join(input_dir, folder_path)
        
        if not os.path.isdir(full_folder_path):
            raise ValueError(f"文件夹不存在: {full_folder_path}")
        
        # 获取文件夹中的所有文件
        all_files = [f for f in os.listdir(full_folder_path) 
                    if os.path.isfile(os.path.join(full_folder_path, f))]
        
        # 根据文件模式筛选
        if file_pattern and file_pattern != "*.*":
            import fnmatch
            filtered_files = [f for f in all_files if fnmatch.fnmatch(f.lower(), file_pattern.lower())]
        else:
            filtered_files = all_files
        
        if not filtered_files:
            raise ValueError(f"文件夹中没有找到匹配的文件: {full_folder_path} (模式: {file_pattern})")
        
        # 排序并限制数量
        filtered_files.sort()
        filtered_files = filtered_files[:max_files]
        
        # 生成完整路径列表
        file_paths = [os.path.join(full_folder_path, f) for f in filtered_files]
        file_count = len(file_paths)
        
        print(f"已加载 {file_count} 个文件从: {full_folder_path}")
        
        return (file_paths, file_count)
