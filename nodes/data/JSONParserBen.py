"""
JSON解析节点
用于解析JSON字符串并支持路径提取功能
"""

import json

class JSONParserBen:
    """JSON解析节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "json_string": ("STRING", {"multiline": True, "default": "", "tooltip": "JSON字符串输入"}),
                "json_path": ("STRING", {"default": "", "tooltip": "路径表达式，用于提取特定值，留空返回整个JSON。支持多个路径，使用分号(;)分隔"})
            },
            "optional": {
                "output_type": (["AUTO", "STRING", "FLOAT", "INT", "BOOL", "LIST", "DICT"], 
                                {"default": "AUTO", "tooltip": "指定输出数据类型，AUTO表示自动判断"})
            }
        }
    
    RETURN_TYPES = ("STRING", "*",)
    RETURN_NAMES = ("JSON_TEXT", "PARSED_RESULT",)
    FUNCTION = "parse_json"
    CATEGORY = "BenNodes/数据"
    DESCRIPTION = "解析JSON字符串并支持路径提取和文本转换"
    
    def parse_json(self, json_string, json_path="", output_type="AUTO"):
        """处理JSON解析逻辑"""
        try:
            print(f"[JSONParser] 输入数据类型: {type(json_string)}")
            print(f"[JSONParser] 输入数据: {str(json_string)[:200]}")
            print(f"[JSONParser] JSON路径: {json_path}")
            print(f"[JSONParser] 输出类型: {output_type}")
            
            # 检查输入是否为空
            if not json_string:
                print(f"[JSONParser错误] JSON字符串为空")
                return (self.handle_error("JSON字符串为空"), None)
            
            # 预处理：提取有效的JSON部分
            json_string = self.extract_valid_json(json_string)
            
            # 解析JSON字符串
            parsed_json = json.loads(json_string)
            
            # 处理多个路径
            if json_path:
                # 使用分号分割路径
                paths = [path.strip() for path in json_path.split(';') if path.strip()]
                
                # 如果没有有效路径，返回整个JSON
                if not paths:
                    json_text = self.generate_output_text(parsed_json)
                    parsed_result = self.auto_convert_type(parsed_json, output_type)
                    return (json_text, parsed_result)
                
                # 对每个路径进行处理
                text_results = []
                parsed_results = []
                for path in paths:
                    try:
                        value = self.extract_value_by_path(parsed_json, path)
                        # 为JSON_TEXT生成简洁的结果
                        text_results.append(str(value))
                        parsed_results.append(self.auto_convert_type(value, output_type))
                    except Exception as e:
                        error_msg = self.handle_error(f"提取失败: {str(e)}")
                        text_results.append(error_msg)
                        parsed_results.append(error_msg)
                
                # 根据路径数量决定返回格式
                # 多路径情况返回字符串列表
                if len(paths) > 1:
                    json_text = text_results
                    parsed_result = parsed_results
                else:
                    # 单路径情况返回单个字符串
                    json_text = text_results[0]
                    parsed_result = parsed_results[0]
            else:
                # 没有路径，返回整个JSON
                json_text = self.generate_output_text(parsed_json)
                parsed_result = self.auto_convert_type(parsed_json, output_type)
            
            print(f"[JSONParser] 解析成功")
            print(f"[JSONParser] JSON_TEXT 类型: {type(json_text)}")
            print(f"[JSONParser] PARSED_RESULT 类型: {type(parsed_result)}")
            return (json_text, parsed_result)
            
        except json.JSONDecodeError as e:
            error_msg = self.handle_error(f"无效的JSON格式: {str(e)}")
            print(f"[JSONParser错误] {error_msg}")
            return (error_msg, error_msg)
        except KeyError as e:
            error_msg = self.handle_error(f"路径不存在: {str(e)}")
            print(f"[JSONParser错误] {error_msg}")
            return (error_msg, error_msg)
        except IndexError as e:
            error_msg = self.handle_error(f"数组索引越界: {str(e)}")
            print(f"[JSONParser错误] {error_msg}")
            return (error_msg, error_msg)
        except Exception as e:
            error_msg = self.handle_error(f"解析失败: {str(e)}")
            print(f"[JSONParser错误] {error_msg}")
            import traceback
            traceback.print_exc()
            return (error_msg, error_msg)
    
    def extract_valid_json(self, text):
        """从文本中提取有效的JSON部分
        
        找到最外层的JSON结构（从第一个{或[开始，到对应的}或]结束）        
        Args:
            text: 包含JSON的文本            
        Returns:
            str: 提取的JSON字符串
        """
        # 找到JSON的开始位置
        start_pos = None
        start_char = None
        
        for i, char in enumerate(text):
            if char in ('{', '['):
                start_pos = i
                start_char = char
                break
        
        if start_pos is None:
            raise ValueError("未找到JSON开始标记")
        
        # 找到对应的结束位置
        end_pos = None
        count = 0
        end_char = '}' if start_char == '{' else ']'
        
        for i, char in enumerate(text[start_pos:]):
            if char == start_char:
                count += 1
            elif char == end_char:
                count -= 1
                if count == 0:
                    end_pos = start_pos + i + 1
                    break
        
        if end_pos is None:
            raise ValueError("未找到JSON结束标记")
        
        return text[start_pos:end_pos]
    
    def extract_value_by_path(self, data, path):
        """根据路径表达式提取JSON值        
        支持格式：
        - 简单属性：'name'
        - 嵌套属性：'user.name'
        - 数组索引：'items[0].name'
        - 组合路径：'data.users[1].address.city'"""
        keys = path.split('.')
        result = data
        
        for key in keys:
            # 处理数组索引
            if '[' in key and ']' in key:
                array_key, index = key.split('[')
                index = int(index[:-1])
                result = result[array_key][index]
            else:
                result = result[key]
        
        return result
    
    def generate_output_text(self, data):
        """生成输出文本
        
        Args:
            data: 要转换为文本的数据            
        Returns:
            str: 格式化后的文本        
        """
        if isinstance(data, (dict, list)):
            return json.dumps(data, ensure_ascii=False, indent=2)
        else:
            # 如果是简单类型，直接转换为字符串
            return str(data)

    def auto_convert_type(self, value, target_type="AUTO"):
        """根据目标类型将值转换为适当的数据类型
        
        Args:
            value: 要转换的值
            target_type: 目标数据类型 (AUTO, STRING, FLOAT, INT, BOOL, LIST, DICT)
            
        Returns:
            转换后的值，根据指定的目标类型
        """
        # 如果目标类型是AUTO，尝试自动判断
        if target_type == "AUTO":
            if isinstance(value, (list, dict)):
                # 对于列表和字典，递归转换内部元素
                if isinstance(value, list):
                    return [self.auto_convert_type(item, target_type) for item in value]
                elif isinstance(value, dict):
                    return {k: self.auto_convert_type(v, target_type) for k, v in value.items()}
            
            # 尝试转换为数值类型
            if isinstance(value, str):
                # 尝试转换为bool
                lower_value = value.lower()
                if lower_value == "true":
                    return True
                elif lower_value == "false":
                    return False
                
                # 尝试转换为int
                try:
                    return int(value)
                except (ValueError, TypeError):
                    pass
                
                # 尝试转换为float
                try:
                    return float(value)
                except (ValueError, TypeError):
                    pass
            
            return value
        
        # 根据指定的目标类型进行转换
        if target_type == "STRING":
            return str(value)
        
        elif target_type == "FLOAT":
            if isinstance(value, list):
                return [float(item) for item in value]
            else:
                return float(value)
        
        elif target_type == "INT":
            if isinstance(value, list):
                return [int(item) for item in value]
            else:
                return int(value)
        
        elif target_type == "BOOL":
            if isinstance(value, list):
                return [bool(item) for item in value]
            else:
                return bool(value)
        
        elif target_type == "LIST":
            if isinstance(value, list):
                return value
            else:
                return [value]
        
        elif target_type == "DICT":
            if isinstance(value, dict):
                return value
            else:
                # 如果不是字典，尝试转换为字典
                try:
                    return dict(value)
                except (TypeError, ValueError):
                    # 转换失败，返回原始值
                    return value
        
        # 默认返回原始值
        return value
    
    def handle_error(self, error_message):
        """处理解析错误
        
        Args:
            error_message: 错误信息
            
        Returns:
            str: 错误处理后的文本
        """
        return f"错误：{error_message}"
