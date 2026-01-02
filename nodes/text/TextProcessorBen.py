"""
文本处理器节点
用于处理多行文本，支持去除空行、空白字符等操作
"""

import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class TextProcessorBen:
    """文本处理器节点"""
    
    FUNCTION = "process_text"
    CATEGORY = "BenNodes/文本"
    DESCRIPTION = "处理多行文本，支持去除空行、空白字符等操作"
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True, 
                    "default": "", 
                    "tooltip": "多行文本输入"
                }),
                "process_type": ([
                    "none",
                    "去除空行",
                    "去除空白字符",
                    "去除空白字符+空行"
                ], {
                    "default": "none",
                    "tooltip": "文本处理类型"
                }),
            }
        }
    
    # 两个输出：STRING（完整文本）和LIST<STRING>（按行分割的列表）
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("文本", "文本列表")
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
            print(f"[TextProcessor] 输入文本长度: {len(text)}")
            print(f"[TextProcessor] 处理类型: {process_type}")
            
            # 检查输入是否为空
            if not text:
                print(f"[TextProcessor] 输入文本为空")
                return ("", [])
            
            # 按行分割文本
            lines = text.split('\n')
            print(f"[TextProcessor] 原始行数: {len(lines)}")
            
            # 根据处理类型进行处理
            if process_type == "none":
                # 不做任何处理
                processed_lines = lines
                
            elif process_type == "去除空行":
                # 只去除空行（完全空的行）
                processed_lines = [line for line in lines if line]
                print(f"[TextProcessor] 去除空行后: {len(processed_lines)} 行")
                
            elif process_type == "去除空白字符":
                # 去除每行首尾的空白字符（但保留空行）
                processed_lines = [line.strip() for line in lines]
                print(f"[TextProcessor] 去除空白字符后: {len(processed_lines)} 行")
                
            elif process_type == "去除空白字符+空行":
                # 先去除每行首尾的空白字符，再去除空行
                processed_lines = [line.strip() for line in lines]
                processed_lines = [line for line in processed_lines if line]
                print(f"[TextProcessor] 去除空白字符+空行后: {len(processed_lines)} 行")
                
            else:
                # 未知处理类型，不做处理
                processed_lines = lines
                print(f"[TextProcessor] 未知处理类型，不做处理")
            
            # 生成输出
            # 输出1: 完整文本（用换行符连接）
            output_text = '\n'.join(processed_lines)
            
            # 输出2: 文本列表
            output_list = processed_lines
            
            print(f"[TextProcessor] 输出文本长度: {len(output_text)}")
            print(f"[TextProcessor] 输出列表长度: {len(output_list)}")
            
            return (output_text, output_list)
            
        except Exception as e:
            error_msg = f"文本处理失败: {str(e)}"
            logger.error(error_msg)
            print(f"[TextProcessor错误] {error_msg}")
            import traceback
            traceback.print_exc()
            return (f"错误: {error_msg}", [])
