"""
ComfyUI-BenNodes 共享常量定义
包含所有节点共用的分辨率、宽高比常量和图片缩放工具类
"""

# 定义any_type，用于接受任何类型的输入
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True
    def __ne__(self, _):
        return False

any_type = AlwaysEqualProxy("*")

# 分辨率预设（值表示基准尺寸）
RESOLUTIONS = {
    "270p": 270,
    "360p": 360,
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
    "2K": 1440,
    "4K": 2160,
    "5K": 2880,
    "8K": 4320,
    "自定义": None,
}

# 屏幕比例预设
ASPECT_RATIOS = {
    "16:9": (16, 9),      # 宽屏标准
    "4:3": (4, 3),        # 标准
    "1:1": (1, 1),        # 正方形
    "3:2": (3, 2),        # 摄影
    "2:3": (2, 3),        # 竖版摄影
    "9:16": (9, 16),      # 竖屏
    "21:9": (21, 9),      # 超宽屏
    "32:9": (32, 9),      # 超超宽屏
    "9:18": (9, 18),      # 手机全面屏(竖屏)
    "9:19": (9, 19),      # 手机(竖屏)
    "9:19.5": (9, 19.5),  # 手机(竖屏)
    "9:20": (9, 20),      # 手机(竖屏)
    "5:4": (5, 4),        # 显示器
    "3:4": (3, 4),        # 竖版标准
}

# 缩放模式预设
SCALE_MODES = ["none", "contain", "crop", "pad", "fill"]

SCALE_POSITIONS = ["center", "top", "bottom", "left", "right"]

# 放大插值方法预设
UPSCALE_METHODS = ["bilinear", "bicubic", "lanczos"]