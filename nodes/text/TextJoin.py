"""
文本连接节点
将输入的文本或文本列表按照指定的规则进行连接
"""

class TextJoinBen:
    """文本连接节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "text1": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text2": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "delimiter": ("STRING", {"default": "", "tooltip": "用于连接文本的分隔符，默认为空"}),
            },
            "hidden": {
                "workflow_prompt": "PROMPT", "my_unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("连接结果",)
    OUTPUT_IS_LIST = (False,)
    FUNCTION = "join_text"
    CATEGORY = "BenNodes/文本"
    DESCRIPTION = "将两个输入文本或文本列表按照指定的规则进行连接。支持一个输入为列表类型，另一个为字符串类型。"
    
    def join_text(self, text1, text2, delimiter="", workflow_prompt=None, my_unique_id=None):
        """处理文本连接逻辑"""
        # 检查输入类型
        text1_is_list = isinstance(text1, list)
        text2_is_list = isinstance(text2, list)
        
        # 验证输入：最多接受1个列表类型参数
        if text1_is_list and text2_is_list:
            raise ValueError("两个输入参数不能同时为列表类型")
        
        # 情况1：两个输入都是字符串
        if not text1_is_list and not text2_is_list:
            return (text1 + delimiter + text2,)
        
        # 情况2：text1是列表，text2是字符串
        if text1_is_list:
            result = []
            for item in text1:
                if delimiter:
                    result.append(f"{item}{delimiter}{text2}")
                else:
                    result.append(f"{item}{text2}")
            return (result,)
        
        # 情况3：text1是字符串，text2是列表
        if text2_is_list:
            result = []
            for item in text2:
                if delimiter:
                    result.append(f"{text1}{delimiter}{item}")
                else:
                    result.append(f"{text1}{item}")
            return (result,)
        
        # 默认返回空字符串
        return ("",)
