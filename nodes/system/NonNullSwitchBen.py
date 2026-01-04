"""
NonNullSwitch Node
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


class NonNullSwitchBen:
    """
    非空切换节点（动态输入版本）
    
    功能：
    - 固定显示"主数据源"和"备选1"两个输入
    - 当两者都连接后，自动添加新的备选输入
    - 按顺序检查所有输入，返回第一个非空值
    - 如果所有输入都为空，抛出错误
    
    使用场景：
    - 多级容错切换（主数据源 → 备选1 → 备选2 → ...）
    - 优先级数据选择
    - 复杂工作流的数据路由
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {}  # 由JavaScript动态管理
        }
    
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    FUNCTION = "switch"
    CATEGORY = "BenNodes/控制"
    
    def switch(self, **kwargs):
        """
        切换逻辑：
        1. 按输入顺序检查每个参数
        2. 返回第一个非空值
        3. 如果所有输入都为空，抛出错误
        """
        # 定义输入顺序
        input_order = ["主数据源", "备选1"]
        # 添加可能的额外备选输入（备选2, 备选3, ...）
        for i in range(2, 20):  # 支持最多20个输入
            input_order.append(f"备选{i}")
        
        # 调试信息
        print(f"[NonNullSwitch] 收到 {len(kwargs)} 个输入: {list(kwargs.keys())}")
        
        # 按定义的顺序检查输入
        for input_name in input_order:
            if input_name in kwargs:
                value = kwargs[input_name]
                value_info = f"<tensor shape={getattr(value, 'shape', None)}>" if hasattr(value, 'shape') else str(value)
                print(f"[NonNullSwitch] {input_name}: type={type(value)}, value={value_info}")
                
                if not is_none(value):
                    print(f"[NonNullSwitch] 返回 {input_name}")
                    return (value,)
        
        # 所有输入都为空
        raise ValueError(
            "NonNullSwitch 错误：所有输入都为空！\n"
            "请确保至少连接一个有效的输入。"
        )


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "NonNullSwitchBen": NonNullSwitchBen
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "NonNullSwitchBen": "非空切换"
}
