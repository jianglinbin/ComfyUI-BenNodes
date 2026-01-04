"""
Group Bypasser Node
通过选择组名和开关控制组的执行状态

这是一个虚拟节点，主要逻辑在前端 JavaScript 实现
"""

class GroupBypasserBen:
    """
    Group Bypasser 节点
    
    特性：
    - COMBO选择组名（自动更新组列表）
    - BOOL开关控制组的激活/忽略状态
    - 开启=激活组，关闭=忽略组
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
        }
    
    RETURN_TYPES = ()
    FUNCTION = "execute"
    CATEGORY = "BenNodes/控制"
    OUTPUT_NODE = False
    
    def execute(self):
        """
        虚拟节点，不执行任何操作
        所有逻辑在前端 JavaScript 实现
        """
        return ()


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "GroupBypasserBen": GroupBypasserBen
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "GroupBypasserBen": "忽略组"
}
