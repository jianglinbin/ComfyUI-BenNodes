"""
Advanced Group Bypasser Node
高级忽略组节点 - 支持基于JSON规则的条件激活组

这是一个虚拟节点，主要逻辑在前端 JavaScript 实现
"""

from ...utils.i18n import t

class AdvancedGroupBypasserBen:
    """
    Advanced Group Bypasser 节点

    特性：
    - 无需连接,自动遍历所有组
    - JSON规则配置(使用组名称)
    - 基于规则的条件激活/禁用组
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_rules": ("STRING", {
                    "multiline": True,
                    "default": '{\n  "规则A": ["组1", "组2"],\n  "规则B": ["组3", "组4"]\n}',
                    "tooltip": t("adv_group_bypasser_rules_tooltip")
                }),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "execute"
    CATEGORY = f"BenNodes/{t('common_cat_control')}"
    OUTPUT_NODE = False
    
    def execute(self, json_rules):
        """
        虚拟节点，不执行任何操作
        所有逻辑在前端 JavaScript 实现
        """
        return ()

