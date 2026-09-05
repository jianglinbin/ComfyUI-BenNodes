"""
列表索引选择节点
用于从列表中选择指定索引的元素
"""

import logging

import torch

from ...utils.constants.constants import any_type
from ...utils.i18n import t

logger = logging.getLogger(__name__)

class ListIndexSelectorBen:
    """列表索引选择节点"""

    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "*": (any_type,),  # 使用*作为参数名，接受任意类型
                "index": ("STRING", {"default": "0", "tooltip": t("list_index_selector_index_tooltip")})
            }
        }

    # 简化输出定义- 支持最多20个输出，使用any_type让ComfyUI自动推断类型
    RETURN_TYPES = tuple([any_type] * 20)
    RETURN_NAMES = tuple([f"ITEM_{i}" for i in range(20)])
    OUTPUT_NODE = False
    FUNCTION = "select"
    CATEGORY = f"BenNodes/{t('common_cat_data')}"

    def select(self, *args, **kwargs):
        """根据索引从列表中获取元素，类似convertAnything的简洁实现"""
        # 确保能正确获取输入数据
        # 从位置参数获取列表数据（ComfyUI通常这样传递连接的输入）
        if args:
            list_data = args[0]
        else:
            list_data = kwargs.get('*', None)
        index = kwargs.get('index', "0")

        # ComfyUI的批量图像是单个形状为[N, H, W, C]的张量，需要特殊处理

        try:
            # 只在调试时打印日志
            logger.debug("输入数据: %s, 类型: %s", list_data, type(list_data).__name__)
            logger.debug("索引: %s", index)

            # 解析索引
            if isinstance(index, str):
                # 字符串类型索引，支持逗号分隔的多值
                index_strings = [i.strip() for i in index.split(",") if i.strip()]

                # 处理ADD指令：前端应该已经解析，但如果直接传递了ADD指令，这里也处理
                if len(index_strings) == 1 and index_strings[0].lower() == "add":
                    # 基础ADD指令，使用索引0
                    index_strings = ["0"]
                elif len(index_strings) > 1 and index_strings[0].lower() == "add":
                    # add,0,1,2等形式，使用后面的数值参数
                    index_strings = index_strings[1:]
            elif isinstance(index, int):
                # int类型索引，单值
                index_strings = [str(index)]
            else:
                # 其他类型转换为字符串
                index_strings = [str(index)]

            # 如果没有有效索引，默认使用索引0
            if not index_strings:
                index_strings = ["0"]

            logger.debug("解析后的索引: %s", index_strings)

            # 检查输入
            if list_data is None:
                error_msg = t("list_index_selector_empty_input")
                logger.error(error_msg)
                # 返回None而不是错误字符串，避免下游节点崩溃
                return tuple([None] * 20)

            # 支持列表、元组和张量
            if not isinstance(list_data, (list, tuple, torch.Tensor)):
                error_msg = t("list_index_selector_invalid_type").format(type(list_data).__name__)
                logger.error(error_msg)
                # 返回None而不是错误字符串，避免下游节点崩溃
                return tuple([None] * 20)

            # 确定数据类型和长度
            is_batch_tensor = False
            if isinstance(list_data, torch.Tensor):
                # 检查是否为批量数据（4D张量: [N, H, W, C]）
                if len(list_data.shape) == 4:
                    is_batch_tensor = True
                data_length = list_data.shape[0]
                logger.debug("张量形状: %s", list_data.shape)
                logger.debug("%s, 数据长度: %s", '批量张量' if is_batch_tensor else '普通张量', data_length)
            else:
                data_length = len(list_data)
                logger.debug("列表/元组长度: %s", data_length)

            # 获取元素
            results = []
            for idx_str in index_strings:
                try:
                    idx = int(idx_str)
                    if 0 <= idx < data_length:
                        # 根据数据类型和是否为批量张量选择不同的索引方式
                        if isinstance(list_data, torch.Tensor):
                            if is_batch_tensor:
                                # 从批量张量中提取单个图像: [N, H, W, C] -> [H, W, C] -> [1, H, W, C]
                                # ComfyUI期望单个图像带有batch维度
                                element = list_data[idx].unsqueeze(0)
                            else:
                                # 普通张量索引
                                element = list_data[idx]
                        else:
                            # 列表或元组索引
                            element = list_data[idx]
                        results.append(element)
                        logger.debug("索引 %s: 类型 %s", idx, type(element).__name__)
                    else:
                        error_msg = t("list_index_selector_index_out_of_range").format(idx, data_length)
                        results.append(None)  # 返回None而不是错误字符串
                        logger.error(error_msg)
                except ValueError:
                    error_msg = t("list_index_selector_invalid_index").format(idx_str)
                    results.append(None)  # 返回None而不是错误字符串
                    logger.error(error_msg)

            # 填充到20个输出
            while len(results) < 20:
                results.append(None)

            result_tuple = tuple(results)
            logger.debug("返回结果数量: %s", len(index_strings))
            return result_tuple

        except Exception as e:
            error_msg = t("list_index_selector_failed").format(str(e))
            logger.error(error_msg)
            # 返回None而不是错误字符串，避免下游节点崩溃
            return tuple([None] * 20)
