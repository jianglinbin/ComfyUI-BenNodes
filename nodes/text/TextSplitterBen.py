"""
文本拆分节点
将输入的文本或文本列表按照指定的拆分符进行拆分
"""

from ...utils.i18n import t

class TextSplitBen:
    """文本拆分节点"""

    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "delimiter": ("STRING", {"default": "\n", "tooltip": t("text_split_delimiter_tooltip")}),
                "start_index": ("INT", {"default": 0, "min": 0, "max": 9999, "tooltip": t("text_split_start_index_tooltip")}),
                "max_rows": ("INT", {"default": 1000, "min": 1, "max": 9999, "tooltip": t("text_split_max_rows_tooltip")})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "split_text"
    CATEGORY = f"BenNodes/{t('common_cat_text')}"
    DESCRIPTION = t("text_split_description")

    def split_text(self, text, delimiter="\n", start_index=0, max_rows=1000):
        """处理文本拆分逻辑"""
        # 特殊处理空输入
        if not text:
            return ([],)
        
        # 确保text是字符串类型
        if isinstance(text, list):
            text = ' '.join(map(str, text))
        elif not isinstance(text, str):
            text = str(text)
        
        # 按照拆分符拆分文本
        split_result = text.split(delimiter)
        
        # 确保start_index在有效范围内
        start_index = max(0, start_index)
        end_index = start_index + max_rows
        
        # 截取指定范围的结果
        result = split_result[start_index:end_index]
        
        return (result,)