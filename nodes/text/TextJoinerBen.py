"""
文本连接节点
将输入的文本或文本列表按照指定的规则进行连接
"""

from ...utils.i18n import t

class TextJoinBen:
    """文本连接节点"""

    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "text1": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text2": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "delimiter": ("STRING", {"default": "", "tooltip": t("text_join_delimiter_tooltip")}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = (t("text_join_return_result"),)
    OUTPUT_IS_LIST = (False,)
    FUNCTION = "join_text"
    CATEGORY = f"BenNodes/{t('common_cat_text')}"
    DESCRIPTION = t("text_join_description")

    def join_text(self, text1, text2, delimiter=""):
        """处理文本连接逻辑"""
        # 检查输入类型
        text1_is_list = isinstance(text1, list)
        text2_is_list = isinstance(text2, list)

        # 验证输入：最多接受1个列表类型参数
        if text1_is_list and text2_is_list:
            raise ValueError(t("text_join_both_lists"))
        
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
