"""
ComfyUI-BenNodes: 自定义节点包
包含分辨率选择器、图像缩放和空Latent图像生成等节点
"""

import os

from .utils.i18n import t

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
    "FileUploaderBen": FileUploaderBen,
    "MemoryCleanupBen": MemoryCleanupDynamicBen,
    "NonNullSwitchBen": NonNullSwitchBen,
    "NodeBypasserBen": NodeBypasserBen,
    "AdvancedNodeBypasserBen": AdvancedNodeBypasserBen,
    "AdvancedGroupBypasserBen": AdvancedGroupBypasserBen,
    "GroupBypasserBen": GroupBypasserBen,
    "ParameterDistributorBen": ParameterDistributorBen,
}

# 节点显示名称映射（随 i18n 语言切换）
NODE_DISPLAY_NAME_MAPPINGS = {
    "ResolutionSelectorBen": t("display_ResolutionSelectorBen"),
    "PromptLineBen": t("display_PromptLineBen"),
    "ImageScalerBen": t("display_ImageScalerBen"),
    "EmptyLatentImageBen": t("display_EmptyLatentImageBen"),
    "ImageBatchLoaderBen": t("display_ImageBatchLoaderBen"),
    "ImageLoaderBen": t("display_ImageLoaderBen"),
    "TextSaverBen": t("display_TextSaverBen"),
    "TextSplitterBen": t("display_TextSplitterBen"),
    "JSONParserBen": t("display_JSONParserBen"),
    "ListIndexSelectorBen": t("display_ListIndexSelectorBen"),
    "AdvancedListIndexSelectorBen": t("display_AdvancedListIndexSelectorBen"),
    "TypeConverterBen": t("display_TypeConverterBen"),
    "TextProcessorBen": t("display_TextProcessorBen"),
    "TextJoinerBen": t("display_TextJoinerBen"),
    "FileUploaderBen": t("display_FileUploaderBen"),
    "MemoryCleanupBen": t("display_MemoryCleanupBen"),
    "NonNullSwitchBen": t("display_NonNullSwitchBen"),
    "NodeBypasserBen": t("display_NodeBypasserBen"),
    "AdvancedNodeBypasserBen": t("display_AdvancedNodeBypasserBen"),
    "AdvancedGroupBypasserBen": t("display_AdvancedGroupBypasserBen"),
    "GroupBypasserBen": t("display_GroupBypasserBen"),
    "ParameterDistributorBen": t("display_ParameterDistributorBen"),
}

WEB_DIRECTORY = "./js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
