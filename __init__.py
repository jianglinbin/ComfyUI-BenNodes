"""
ComfyUI-BenNodes: 自定义节点包
包含分辨率选择器、图像缩放和空Latent图像生成等节点
"""

import os

from .nodes.data.ResolutionSelectorBen import ResolutionSelectorBen
from .nodes.text.PromptLineBen import PromptLineBen
from .nodes.image.ImageScalerBen import ImageScalerBen
from .nodes.image.EmptyLatentImageBen import EmptyLatentImageBen
from .nodes.image.ImageBatchLoaderBen import ImageLoaderBatchBen
from .nodes.image.ImageLoaderBen import LoadImageBen
from .nodes.text.TextSaverBen import SaveTextBen
from .nodes.text.TextSplitterBen import TextSplitBen
from .nodes.data.JSONParserBen import JSONParserBen
from .nodes.data.ListIndexSelectorBen import ListIndexSelectorBen
from .nodes.data.AdvancedListIndexSelectorBen import AdvancedListIndexSelectorBen
from .nodes.data.TypeConverterBen import TypeConverterBen
from .nodes.text.TextProcessorBen import TextProcessorBen
from .nodes.text.TextJoinerBen import TextJoinBen
from .nodes.ai.GLMNodeBen import GLMNodeBen
from .nodes.ai.GLMConfigNodeBen import GLMConfigNodeBen
from .nodes.file.FileUploaderBen import FileUploaderBen

from .nodes.system.MemoryCleanupBen import MemoryCleanupDynamicBen
from .nodes.system.NonNullSwitchBen import NonNullSwitchBen
from .nodes.system.NodeBypasserBen import NodeBypasserBen
from .nodes.system.AdvancedNodeBypasserBen import AdvancedNodeBypasserBen
from .nodes.system.AdvancedGroupBypasserBen import AdvancedGroupBypasserBen
from .nodes.system.GroupBypasserBen import GroupBypasserBen
from .nodes.system.ParameterDistributorBen import ParameterDistributorBen

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "ResolutionSelectorBen": ResolutionSelectorBen,
    "PromptLineBen": PromptLineBen,
    "ImageScalerBen": ImageScalerBen,
    "EmptyLatentImageBen": EmptyLatentImageBen,
    "ImageBatchLoaderBen": ImageLoaderBatchBen,
    "ImageLoaderBen": LoadImageBen,
    "TextSaverBen": SaveTextBen,
    "TextSplitterBen": TextSplitBen, 
    "JSONParserBen": JSONParserBen,
    "ListIndexSelectorBen": ListIndexSelectorBen,
    "AdvancedListIndexSelectorBen": AdvancedListIndexSelectorBen,
    "TypeConverterBen": TypeConverterBen,
    "TextProcessorBen": TextProcessorBen,
    "TextJoinerBen": TextJoinBen,
    "GLMNodeBen": GLMNodeBen,
    "GLMConfigNodeBen": GLMConfigNodeBen,
    "FileUploaderBen": FileUploaderBen,
    "MemoryCleanupBen": MemoryCleanupDynamicBen,
    "NonNullSwitchBen": NonNullSwitchBen,
    "NodeBypasserBen": NodeBypasserBen,
    "AdvancedNodeBypasserBen": AdvancedNodeBypasserBen,
    "AdvancedGroupBypasserBen": AdvancedGroupBypasserBen,
    "GroupBypasserBen": GroupBypasserBen,
    "ParameterDistributorBen": ParameterDistributorBen,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "ResolutionSelectorBen": "选择分辨率",
    "PromptLineBen": "提示词行处理器",
    "ImageScalerBen": "图像缩放",
    "EmptyLatentImageBen": "空Latent",
    "ImageBatchLoaderBen": "加载图片批次",
    "ImageLoaderBen": "加载图片",
    "TextSaverBen": "保存文本",
    "TextSplitterBen": "文本拆分",
    "JSONParserBen": "JSON解析器",
    "ListIndexSelectorBen": "列表索引选择器",
    "AdvancedListIndexSelectorBen": "索引选择(高级)",
    "TypeConverterBen": "类型转换器",
    "TextProcessorBen": "文本处理器",
    "TextJoinerBen": "文本连接",
    "GLMNodeBen": "GLM多模态分析",
    "GLMConfigNodeBen": "GLM配置",
    "FileUploaderBen": "文件选择器",
    "MemoryCleanupBen": "释放显存内存",
    "NonNullSwitchBen": "非空切换",
    "NodeBypasserBen": "忽略节点",
    "AdvancedNodeBypasserBen": "忽略节点(高级)",
    "AdvancedGroupBypasserBen": "忽略组(高级)",
    "GroupBypasserBen": "忽略组",
    "ParameterDistributorBen": "参数分发器",
}

WEB_DIRECTORY = "./js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']