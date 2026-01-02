"""
SwitchNOTNULL Node
非空切换节点 - 优先输出默认参数，若为空则输出备选参数
"""


class AnyType(str):
    """特殊类型，允许任意类型的连接"""
    def __eq__(self, _) -> bool:
        return True
    
    def __ne__(self, __value: object) -> bool:
        return False


any_type = AnyType("*")


def is_none(value):
    """检查值是否为 None"""
    return value is None


class SwitchNOTNULL:
    """
    非空切换节点
    
    功能：
    - 优先输出默认参数（如果不为空）
    - 如果默认参数为空，输出备选参数
    - 如果两者都为空，抛出错误
    
    使用场景：
    - 当某个节点可能被 bypass 时，提供备选数据源
    - 实现数据的容错切换
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "default": (any_type,),
                "alternative": (any_type,),
            }
        }
    
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    FUNCTION = "switch"
    CATEGORY = "BenNodes/系统"
    
    def switch(self, default=None, alternative=None):
        """
        切换逻辑：
        1. 如果 default 不为空，返回 default
        2. 否则，如果 alternative 不为空，返回 alternative
        3. 否则，抛出错误
        """
        # 调试信息
        default_info = f"<tensor shape={getattr(default, 'shape', None)}>" if hasattr(default, 'shape') else str(default)
        alternative_info = f"<tensor shape={getattr(alternative, 'shape', None)}>" if hasattr(alternative, 'shape') else str(alternative)
        print(f"[SwitchNOTNULL] default type: {type(default)}, value: {default_info}")
        print(f"[SwitchNOTNULL] alternative type: {type(alternative)}, value: {alternative_info}")
        
        if not is_none(default):
            print("[SwitchNOTNULL] Returning default")
            return (default,)
        
        if not is_none(alternative):
            print("[SwitchNOTNULL] Returning alternative")
            return (alternative,)
        
        raise ValueError(
            "SwitchNOTNULL 错误：默认参数和备选参数都为空！\n"
            "请确保至少连接一个有效的输入。"
        )


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "SwitchNOTNULL": SwitchNOTNULL
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "SwitchNOTNULL": "非空切换 🔄-Ben"
}
