"""
文本处理器节点
用于处理多行文本，支持去除空行、空白字符等操作
"""

import logging

from ...utils.i18n import t

logger = logging.getLogger(__name__)


class TextProcessorBen:
    """文本处理器节点"""

    FUNCTION = "process_text"
    CATEGORY = f"BenNodes/{t('common_cat_text')}"
    DESCRIPTION = t("text_processor_description")

    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": t("text_processor_text_tooltip")
                }),
                "process_type": ([
                    "none",
                    "去除空行",
                    "去除空白字符",
                    "去除空白字符+空行"
                ], {
                    "default": "none",
                    "tooltip": t("text_processor_type_tooltip")
                }),
            }
        }

    # 两个输出：STRING（完整文本）和LIST<STRING>（按行分割的列表）
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = (t("text_processor_return_text"), t("text_processor_return_list"))
    OUTPUT_NODE = False
    OUTPUT_IS_LIST = (False, False)  # 第二个输出虽然是列表，但作为整体传递

    def process_text(self, text, process_type="none"):
        """处理文本

        Args:
            text: 输入的多行文本
            process_type: 处理类型

        Returns:
            tuple: (完整文本, 文本列表)
        """
        try:
            logger.debug("输入文本长度: %s, 处理类型: %s", len(text), process_type)

            # 检查输入是否为空
            if not text:
                logger.debug("输入文本为空")
                return ("", [])

            # 按行分割文本
            lines = text.split('\n')
            logger.debug("原始行数: %s", len(lines))

            # 根据处理类型进行处理
            if process_type == "none":
                # 不做任何处理
                processed_lines = lines

            elif process_type == "去除空行":
                # 只去除空行（完全空的行）
                processed_lines = [line for line in lines if line]

            elif process_type == "去除空白字符":
                # 去除每行首尾的空白字符（但保留空行）
                processed_lines = [line.strip() for line in lines]

            elif process_type == "去除空白字符+空行":
                # 先去除每行首尾的空白字符，再去除空行
                processed_lines = [line.strip() for line in lines]
                processed_lines = [line for line in processed_lines if line]

            else:
                # 未知处理类型，不做处理
                processed_lines = lines
                logger.warning("未知处理类型: %s，不做处理", process_type)

            # 生成输出
            # 输出1: 完整文本（用换行符连接）
            output_text = '\n'.join(processed_lines)

            # 输出2: 文本列表
            output_list = processed_lines

            logger.debug("输出: 文本长度 %s, 列表长度 %s", len(output_text), len(output_list))

            return (output_text, output_list)

        except Exception as e:
            error_msg = t("text_processor_failed").format(str(e))
            logger.exception(error_msg)
            return (f"{t('common_error_prefix')}{error_msg}", [])
