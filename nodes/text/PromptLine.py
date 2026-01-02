"""
提示词行处理器节点 - 处理多行提示词，支持提取指定范围的行
"""

class PromptLine:
    """提示词行处理器节点"""
    
    # 中文操作到英文操作的映射字典
    CHINESE_TO_ENGLISH = {
        "原始": "original",
        "大写": "uppercase",
        "小写": "lowercase",
        "首字母大写": "capitalize",
        "标题格式": "TitleCase",
        "去除空白": "strip",
        "反转": "Reverse",
        "长度": "Count",
        "去除空行": "RemoveEmptyLines"
    }
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        # 使用中文操作作为下拉框选项
        valid_operations_zh = list(cls.CHINESE_TO_ENGLISH.keys())
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "start_index": ("INT", {"default": 0, "min": 0, "max": 9999}),
                "max_rows": ("INT", {"default": 1000, "min": 1, "max": 9999}),
                "operation": (valid_operations_zh, {"default": "原始"})
            },
            "hidden": {
                "workflow_prompt": "PROMPT", "my_unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "generate_strings"
    CATEGORY = "BenNodes/文本"
    
    def generate_strings(self, prompt, start_index, max_rows, operation, workflow_prompt=None, my_unique_id=None):
        """处理多行提示词，提取指定范围的行并应用指定操作"""
        # 特殊处理空输入
        if not prompt:
            return ([],)
        
        # 确保prompt是字符串类型
        if isinstance(prompt, list):
            prompt = ' '.join(map(str, prompt))
        elif not isinstance(prompt, str):
            prompt = str(prompt)
        
        # 转换中文操作到英文
        if operation in self.CHINESE_TO_ENGLISH:
            operation = self.CHINESE_TO_ENGLISH[operation]
        
        # 解析操作（支持字符串、列表或逗号分隔格式）
        valid_operations = ["original", "uppercase", "lowercase", "capitalize", 
                          "TitleCase", "strip", "Reverse", "Count", "RemoveEmptyLines"]
        
        # 将操作转换为列表并找到第一个有效操作
        operations = []
        if isinstance(operation, str):
            if "," in operation:
                operations = [op.strip() for op in operation.split(",")]
            else:
                operations = [operation]
        elif isinstance(operation, list):
            operations = operation
        
        # 找到第一个有效操作
        selected_op = "original"
        for op in operations:
            if op in valid_operations:
                selected_op = op
                break
        
        lines = prompt.split('\n')
        
        # 移除空行操作（在行级别处理）
        if selected_op == "RemoveEmptyLines":
            lines = [line for line in lines if line.strip()]
        
        # 确保start_index在有效范围内
        start_index = max(0, start_index)
        end_index = start_index + max_rows
        rows = lines[start_index:end_index]
        
        # 定义操作映射字典
        def uppercase(line): return line.upper()
        def lowercase(line): return line.lower()
        def capitalize(line): return line.capitalize()
        def titlecase(line): return line.title()
        def strip(line): return line.strip()
        def reverse(line): return line[::-1]
        def count(line): return str(len(line))
        def original(line): return line
        
        # 操作映射
        operation_map = {
            "uppercase": uppercase,
            "lowercase": lowercase,
            "capitalize": capitalize,
            "TitleCase": titlecase,
            "strip": strip,
            "Reverse": reverse,
            "Count": count,
            "original": original
        }
        
        # 应用操作
        if selected_op == "RemoveEmptyLines":
            # RemoveEmptyLines已经在行级别处理过了
            processed_rows = rows
        else:
            processed_rows = [operation_map[selected_op](line) for line in rows]
        
        return (processed_rows,)