"""
分辨率选择器节点
提供预设分辨率和屏幕比例选择，自动计算输出宽度和高度
"""

from ...utils.base.base_node import BaseResolutionNode

class ResolutionSelector(BaseResolutionNode):
    """分辨率选择器节点"""

    # 基于宽度计算分辨率（重写基类默认值）
    BASE_DIMENSION = 'width'

    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数 - 无输入端口，所有参数通过节点设置面板配置"""
        # 获取基类的输入类型
        base_inputs = super().INPUT_TYPES()

        # 添加自定义配置
        return {
            "required": {
                "resolution": (list(cls.RESOLUTIONS.keys()), {"default": "720p", "forceInput": False}),  
                "aspect_ratio": (list(cls.ASPECT_RATIOS.keys()), {"default": "16:9", "forceInput": False}),
            },
            "optional": {
                "width": ("INT", {"default": 1280, "min": 16, "max": 32768, "step": 8, "forceInput": False}),
                "height": ("INT", {"default": 720, "min": 16, "max": 32768, "step": 8, "forceInput": False}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "resolution_text")
    FUNCTION = "calculate"
    CATEGORY = "BenNodes/数据"
    OUTPUT_NODE = True

    def calculate(self, resolution, aspect_ratio, width=1280, height=720, unique_id=None):
        """计算分辨率"""
        # 使用基类的方法计算最终分辨率
        width, height = self.calculate_dimensions(resolution, aspect_ratio, width, height)

        # 生成描述文本
        if resolution == "自定义":
            resolution_text = f"{width}x{height} (自定义)"
        else:
            resolution_text = f"{width}x{height} ({aspect_ratio})"

        # 返回结果
        return (width, height, resolution_text)