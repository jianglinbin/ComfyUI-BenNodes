"""
Advanced Input Bypasser Node
高级忽略节点 - 支持基于JSON规则的条件激活

这是一个虚拟节点，主要逻辑在前端 JavaScript 实现
"""

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
                    "tooltip": "JSON规则格式:\n{\n  \"规则名称\": [输入ID列表],\n  ...\n}\n\n示例:\n{\n  \"规则A\": [1, 2, 3],\n  \"规则B\": [4, 5, 6]\n}\n\n说明:\n- 键: 规则的显示名称\n- 值: 要激活的输入ID数组(从1开始)\n- 选择规则后,对应ID的输入会被激活,其他输入会被禁用"
                }),
            },
        }
    
    RETURN_TYPES = ()
    FUNCTION = "execute"
    CATEGORY = "BenNodes/控制"
    OUTPUT_NODE = False
    
    def execute(self, json_rules):
        """
        虚拟节点，不执行任何操作
        所有逻辑在前端 JavaScript 实现
        """
        return ()


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "AdvancedNodeBypasserBen": AdvancedNodeBypasserBen
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "AdvancedNodeBypasserBen": "忽略节点(高级)"
}
