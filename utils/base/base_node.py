"""
ComfyUI-BenNodes 基类定义
为分辨率相关节点提供通用功能
"""

from ..constants.constants import RESOLUTIONS, ASPECT_RATIOS, SCALE_MODES, SCALE_POSITIONS, UPSCALE_METHODS

class BaseResolutionNode:
    """分辨率相关节点的基类
    
    提供通用的分辨率计算功能和配置
    """
    
    # 从常量模块导入并设置为类属性，以便子类可以访问
    RESOLUTIONS = RESOLUTIONS
    ASPECT_RATIOS = ASPECT_RATIOS
    SCALE_MODES = SCALE_MODES
    SCALE_POSITIONS = SCALE_POSITIONS
    UPSCALE_METHODS = UPSCALE_METHODS
    
    # 默认基于高度计算（可以在子类中重写）
    BASE_DIMENSION = 'height'  # 'height' 或 'width'
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义通用输入参数
        
        子类可以重写或扩展此方法以添加额外的输入参数
        """
        return {
            "required": {
                "resolution": (list(RESOLUTIONS.keys()), {"default": "720p"}),
                "aspect_ratio": (list(ASPECT_RATIOS.keys()), {"default": "16:9"}),
                "width": ("INT", {"default": 1280, "min": 16, "max": 32768, "step": 8}),
                "height": ("INT", {"default": 720, "min": 16, "max": 32768, "step": 8}),
            }
        }
    
    def calculate_dimensions(self, resolution, aspect_ratio, width, height):
        """计算最终分辨率
        
        根据分辨率预设和宽高比计算最终的宽度和高度
        
        Args:
            resolution: 分辨率预设名称
            aspect_ratio: 宽高比预设名称
            width: 自定义宽度
            height: 自定义高度
            
        Returns:
            tuple: (计算后的宽度, 计算后的高度)
        """
        if resolution == "自定义":
            return width, height
        
        base_value = RESOLUTIONS[resolution]
        ratio_w, ratio_h = ASPECT_RATIOS[aspect_ratio]
        
        if self.BASE_DIMENSION == 'width':
            # 基于宽度计算
            new_width = base_value
            new_height = int(base_value * ratio_h / ratio_w)
        else:
            # 基于高度计算（默认）
            new_height = base_value
            new_width = int(base_value * ratio_w / ratio_h)
        
        # 确保结果是 8 的倍数（ComfyUI 常见要求）
        new_width = (new_width // 8) * 8
        new_height = (new_height // 8) * 8
        
        return new_width, new_height
