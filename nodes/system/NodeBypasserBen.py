"""
Dynamic Input Bypasser Node
通过单个主开关控制多个输入连接节点的执行状态

这是一个虚拟节点，主要逻辑在前端 JavaScript 实现
"""

from ...utils.i18n import t

class NodeBypasserBen:
    """
    Dynamic Input Bypasser 节点

    特性：
    - 动态输入槽位自动管理
    - 单一主开关控制所有连接节点
    - 透传节点自动跟随
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
        }

    RETURN_TYPES = ()
    FUNCTION = "execute"
    CATEGORY = f"BenNodes/{t('common_cat_control')}"
    OUTPUT_NODE = False
    
    def execute(self):
        """
        虚拟节点，不执行任何操作
        所有逻辑在前端 JavaScript 实现
        """
        return ()

