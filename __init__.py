"""
ComfyUI-BenNodes: 自定义节点包
包含分辨率选择器、图像缩放和空Latent图像生成等节点
"""

import os

from .nodes.data.ResolutionSelector import ResolutionSelector
from .nodes.text.PromptLine import PromptLine
from .nodes.image.ImageScaler import ImageScaler
from .nodes.image.EmptyLatentImage import EmptyLatentImageBen
from .nodes.image.ImageLoader import ImageLoaderBatchBen
from .nodes.image.ImageLoaderSingleBen import LoadImageBen
from .nodes.text.SaveTextBen import SaveTextBen
from .nodes.text.TextSplit import TextSplitBen
from .nodes.data.JSONParser import JSONParserBen
from .nodes.data.ListIndexSelector import ListIndexSelectorBen
from .nodes.data.AdvancedListIndexSelector import AdvancedListIndexSelectorBen
from .nodes.data.TypeConverterBen import TypeConverterBen
from .nodes.text.TextProcessorBen import TextProcessorBen
from .nodes.text.TextJoin import TextJoinBen
from .nodes.ai.GLMNodeBen import GLMNodeBen
from .nodes.ai.GLMConfigNodeBen import GLMConfigNodeBen
from .nodes.file.FileUploader import FileUploaderBen

from .nodes.system.MemoryCleanupDynamic import MemoryCleanupDynamicBen
from .nodes.system.SwitchNOTNULL import SwitchNOTNULL
from .nodes.system.DynamicInputBypasser import DynamicInputBypasser

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "ResolutionSelector": ResolutionSelector,
    "PromptLine": PromptLine,
    "ImageScaler": ImageScaler,
    "EmptyLatentImageBen": EmptyLatentImageBen,
    "LoadImageBatchBen": ImageLoaderBatchBen,
    "LoadImageBen": LoadImageBen,
    "SaveTextBen": SaveTextBen,
    "TextSplitBen": TextSplitBen, 
    "JSONParserBen": JSONParserBen,
    "ListIndexSelectorBen": ListIndexSelectorBen,
    "AdvancedListIndexSelectorBen": AdvancedListIndexSelectorBen,
    "TypeConverterBen": TypeConverterBen,
    "TextProcessorBen": TextProcessorBen,
    "TextJoinBen": TextJoinBen,
    "GLMNodeBen": GLMNodeBen,
    "GLMConfigNodeBen": GLMConfigNodeBen,
    "FileUploaderBen": FileUploaderBen,
    "MemoryCleanupDynamicBen": MemoryCleanupDynamicBen,
    "SwitchNOTNULL": SwitchNOTNULL,
    "DynamicInputBypasser": DynamicInputBypasser,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ResolutionSelector": "选择分辨率 📐-Ben",
    "PromptLine": "提示词行处理器 📝-Ben",
    "ImageScaler": "图像缩放 🎨-Ben",
    "EmptyLatentImageBen": "空Latent 🎯-Ben",
    "LoadImageBatchBen": "加载图片批次 �️-Ben",
    "LoadImageBen": "加载图片 🖼️-Ben",
    "SaveTextBen": "保存文本 📄-Ben",
    "TextSplitBen": "文本拆分 📝-Ben",
    "JSONParserBen": "JSON解析器 �n-Ben",
    "ListIndexSelectorBen": "列表索引选择器 📌-Ben",
    "AdvancedListIndexSelectorBen": "索引选择(高级) 🎯-Ben",
    "TypeConverterBen": "类型转换器 🔄-Ben",
    "TextProcessorBen": "文本处理器 �-eBen",
    "TextJoinBen": "文本连接（支持列表） 📝-Ben",
    "GLMNodeBen": "GLM多模态分析 🧠-Ben",
    "GLMConfigNodeBen": "GLM配置节点 🧠-Ben",
    "FileUploaderBen": "文件选择器 �-Ben",
    "MemoryCleanupDynamicBen": "释放显存内存 🧹-Ben",
    "SwitchNOTNULL": "非空切换 🔄-Ben",
    "DynamicInputBypasser": "忽略节点 🔀-Ben",
}

WEB_DIRECTORY = "./js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']