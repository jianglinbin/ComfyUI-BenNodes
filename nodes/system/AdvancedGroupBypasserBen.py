"""
Advanced Group Bypasser Node
高级忽略组节点 - 支持基于JSON规则的条件激活组

这是一个虚拟节点，主要逻辑在前端 JavaScript 实现
"""

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
                    "tooltip": "JSON规则格式:\n{\n  \"规则名称\": [\"组名称列表\"],\n  ...\n}\n\n示例:\n{\n  \"规则A\": [\"组1\", \"组2\"],\n  \"规则B\": [\"组3\", \"组4\"]\n}\n\n说明:\n- 键: 规则的显示名称\n- 值: 要激活的组名称数组\n- 选择规则后,对应名称的组会被激活,其他组会被禁用"
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
    "AdvancedGroupBypasserBen": AdvancedGroupBypasserBen
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "AdvancedGroupBypasserBen": "忽略组(高级)"
}
