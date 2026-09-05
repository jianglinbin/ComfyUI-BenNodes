"""
Advanced Input Bypasser Node
高级忽略节点 - 支持基于JSON规则的条件激活

这是一个虚拟节点，主要逻辑在前端 JavaScript 实现
"""

from ...utils.i18n import t

class AdvancedNodeBypasserBen:
    """
    Advanced Input Bypasser 节点

    特性：
    - 动态输入槽位自动管理
    - JSON规则配置
    - 基于规则的条件激活/禁用
    - 透传节点自动跟随
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_rules": ("STRING", {
                    "multiline": True,
                    "default": '{\n  "规则A": [1, 2, 3],\n  "规则B": [4, 5, 6]\n}',
                    "tooltip": t("adv_node_bypasser_rules_tooltip")
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

