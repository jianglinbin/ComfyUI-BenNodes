"""
高级列表索引选择节点
用于从列表中选择指定模式的元素（起始位置、间隔、长度）
"""

import logging

import torch

from ...utils.constants.constants import any_type
from ...utils.i18n import t

logger = logging.getLogger(__name__)

# select_advanced 的参数名为 list（与输入端口名一致），会遮蔽内建 list/tuple 类型，
# 此处保存内建类型引用供 isinstance / 构造使用
_BUILTIN_LIST = list
_BUILTIN_TUPLE = tuple


class AdvancedListIndexSelectorBen:
    """高级列表索引选择节点"""

    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "list": ("*", {"forceInput": True}),
            },
            "optional": {
                "start_index": ("INT", {"default": 0, "min": 0, "step": 1, "tooltip": t("adv_list_selector_start_tooltip")}),
                "step": ("INT", {"default": 0, "min": 0, "step": 1, "tooltip": t("adv_list_selector_step_tooltip")}),
                "length": ("INT", {"default": 1, "min": 1, "step": 1, "tooltip": t("adv_list_selector_length_tooltip")})
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("SELECTED_LIST",)
    OUTPUT_NODE = False
    FUNCTION = "select_advanced"
    CATEGORY = f"BenNodes/{t('common_cat_data')}"

    def select_advanced(self, list, start_index=0, step=0, length=1):
        """根据高级规则从列表中获取元素"""

        try:
            # 验证输入
            if list is None:
                error_msg = t("adv_list_selector_empty_input")
                logger.error(error_msg)
                return (None,)

            # 验证参数
            if start_index < 0:
                logger.warning("起始序号 %s 小于0，将设为0", start_index)
                start_index = 0

            if step < 0:
                logger.warning("步长 %s 小于0，将设为0", step)
                step = 0

            if length <= 0:
                error_msg = t("adv_list_selector_length_invalid").format(length)
                logger.error(error_msg)
                return (None,)

            # 记录参数
            logger.debug("输入参数: 起始序号=%s, 步长=%s, 长度=%s", start_index, step, length)

            # 获取数据长度
            if isinstance(list, torch.Tensor):
                data_length = list.shape[0]
                logger.debug("张量形状: %s, 数据长度: %s", list.shape, data_length)
            elif isinstance(list, (_BUILTIN_LIST, _BUILTIN_TUPLE)):
                data_length = len(list)
                logger.debug("列表/元组长度: %s", data_length)
            else:
                error_msg = t("adv_list_selector_unsupported_type").format(type(list).__name__)
                logger.error(error_msg)
                return (None,)

            # 检查起始序号是否超出范围
            if start_index >= data_length:
                error_msg = t("adv_list_selector_start_out_of_range").format(start_index, data_length)
                logger.error(error_msg)
                return (None,)

            # 计算实际可获取的元素数量
            if step <= 1:
                # 连续选取模式（步长0或1等价）
                available_length = min(length, data_length - start_index)
                if available_length <= 0:
                    error_msg = t("adv_list_selector_no_elements").format(start_index)
                    logger.error(error_msg)
                    return (None,)
                indices = _BUILTIN_LIST(range(start_index, start_index + available_length))
            else:
                # 间隔选取模式（每隔 step-1 个取一个）
                max_possible = ((data_length - start_index - 1) // step) + 1 if start_index < data_length else 0
                available_length = min(length, max_possible)

                if available_length <= 0:
                    error_msg = t("adv_list_selector_no_elements_step").format(start_index, step)
                    logger.error(error_msg)
                    return (None,)

                indices = [start_index + i * step for i in range(available_length)]

            logger.debug("选择的索引: %s", indices)

            # 根据数据类型选择元素
            if isinstance(list, torch.Tensor):
                if len(list.shape) == 4:
                    # 四维张量 (批量图像: [N, H, W, C])
                    selected_indices_tensor = torch.tensor(indices, device=list.device)
                    selected = list[selected_indices_tensor]
                else:
                    # 一维及其他形状的张量
                    selected = list[indices]
            elif isinstance(list, (_BUILTIN_LIST, _BUILTIN_TUPLE)):
                selected = [list[i] for i in indices]
            else:
                error_msg = t("adv_list_selector_unsupported_type").format(type(list).__name__)
                logger.error(error_msg)
                return (None,)

            # 保持原始数据类型
            if isinstance(list, _BUILTIN_TUPLE):
                selected = _BUILTIN_TUPLE(selected)

            logger.debug("选择的元素数量: %s", len(selected))
            return (selected,)

        except Exception as e:
            error_msg = t("adv_list_selector_failed").format(str(e))
            logger.error(error_msg)
            return (None,)
