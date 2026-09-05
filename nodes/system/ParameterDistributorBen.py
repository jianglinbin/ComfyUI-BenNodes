"""
Parameter Distributor Node
参数分发器 - 当输出被连接时自动复制该输出参数，并添加新的空输出槽位，实现无限扩展

每个输出对应一个独立的 widget 值
"""

import logging

from ...utils.constants.constants import any_type
from ...utils.i18n import t

logger = logging.getLogger(__name__)


class ParameterDistributorBen:
    """
    Parameter Distributor 节点 / 参数分发器

    特性：
    - 动态输出槽位自动管理
    - 输出被连接后自动添加新输出
    - 支持任意类型的数据传递
    - 每个输出独立配置
    - 参数锁定功能
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    # 定义足够多的返回类型以支持多个输出
    RETURN_TYPES = tuple([any_type] * 20)  # 支持最多 20 个输出
    FUNCTION = "execute"
    CATEGORY = f"BenNodes/{t('common_cat_control')}"
    OUTPUT_NODE = False

    def execute(self, unique_id=None, extra_pnginfo=None):
        """
        从 workflow 中读取 widget 值并返回
        每个 widget 对应一个输出
        """
        logger.debug("unique_id: %s", unique_id)

        if extra_pnginfo and "workflow" in extra_pnginfo:
            workflow = extra_pnginfo["workflow"]
            nodes = workflow.get("nodes", [])

            # 找到当前节点
            for node in nodes:
                if str(node.get("id")) == str(unique_id):
                    widgets_values = node.get("widgets_values", [])
                    outputs = node.get("outputs", [])

                    logger.debug("widgets_values: %s, outputs count: %s", widgets_values, len(outputs))

                    # 返回所有 widget 的值，填充到 20 个输出
                    # 注意：最后一个 widget 是锁定开关，前端已经过滤掉了
                    if widgets_values:
                        # 截断到 20 个防止输出超长，用 None 填充未使用的输出
                        result = list(widgets_values[:20])
                        while len(result) < 20:
                            result.append(None)
                        logger.debug("Returning %s values (padded to 20)", len(widgets_values))
                        return tuple(result)
                    break

        # 如果没有找到值，返回 20 个 None
        logger.debug("No widget values found, returning 20 Nones")
        return tuple([None] * 20)
