"""
类型转换节点
将任意类型的输入转换为用户指定的数据类型
"""

import json
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 定义any_type，类似comfyui-easy-use的实现
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True
    def __ne__(self, _):
        return False

any_type = AlwaysEqualProxy("*")


class TypeConverterBen:
    """类型转换节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "*": (any_type,),  # 使用*作为参数名，类似convertAnything
                "target_type": ([
                    "STRING", "LIST<STRING>",
                    "INT", "LIST<INT>", 
                    "FLOAT", "LIST<FLOAT>", 
                    "BOOLEAN", "LIST<BOOLEAN>"
                ], {
                    "default": "STRING",
                    "tooltip": "目标数据类型（选择LIST类型会将输入转换为列表）"
                }),
            }
        }
    
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    OUTPUT_NODE = False
    FUNCTION = "convert"
    CATEGORY = "BenNodes/数据"
    
    def convert(self, *args, **kwargs):
        """执行类型转换，类似convertAnything但支持更多类型和列表转换"""
        input_data = kwargs['*']
        target_type = kwargs['target_type']
        
        try:
            print(f"[TypeConverter] 输入数据: {input_data}, 类型: {type(input_data).__name__}")
            print(f"[TypeConverter] 目标类型: {target_type}")
            
            # 检查输入是否为列表
            is_input_list = isinstance(input_data, (list, tuple))
            
            # 判断目标类型是否为列表类型
            is_target_list = target_type.startswith("LIST<")
            base_type = target_type.replace("LIST<", "").replace(">", "") if is_target_list else target_type
            
            # 核心逻辑：根据目标类型决定输出
            if is_target_list:
                # 目标是列表类型
                if is_input_list:
                    # 输入是列表，对每个元素进行类型转换
                    result = [self._convert_single(item, base_type) for item in input_data]
                else:
                    # 输入是单值，转换后包装成列表
                    result = [self._convert_single(input_data, base_type)]
            else:
                # 目标是单值类型
                if is_input_list:
                    # 输入是列表，只取第一个元素并转换
                    if len(input_data) > 0:
                        result = self._convert_single(input_data[0], base_type)
                    else:
                        # 空列表，返回默认值
                        result = self._get_default_value(base_type)
                else:
                    # 输入是单值，转换为单值
                    result = self._convert_single(input_data, base_type)
            
            print(f"[TypeConverter] 转换结果: {result}, 类型: {type(result).__name__}")
            return (result,)
            
        except Exception as e:
            error_msg = f"类型转换失败: {str(e)}"
            logger.error(error_msg)
            print(f"[TypeConverter错误] {error_msg}")
            return (error_msg,)
    
    def _convert_single(self, data, target_type):
        """转换单个数据到指定类型"""
        if target_type == "STRING":
            return self._to_string_single(data)
        elif target_type == "INT":
            return self._to_int_single(data)
        elif target_type == "FLOAT":
            return self._to_float_single(data)
        elif target_type == "BOOLEAN":
            return self._to_boolean_single(data)
        else:
            return data
    
    def _get_default_value(self, target_type):
        """获取类型的默认值"""
        if target_type == "STRING":
            return ""
        elif target_type == "INT":
            return 0
        elif target_type == "FLOAT":
            return 0.0
        elif target_type == "BOOLEAN":
            return False
        else:
            return None
    
    def _to_string_single(self, data):
        """转换单个元素为字符串(不处理列表)"""
        if isinstance(data, str):
            return data
        elif isinstance(data, bool):
            return "true" if data else "false"
        elif data is None:
            return ""
        elif isinstance(data, dict):
            return json.dumps(data, ensure_ascii=False)
        else:
            return str(data)
    
    def _to_int_single(self, data):
        """转换单个元素为整数(不处理列表)"""
        if isinstance(data, int):
            return data
        elif isinstance(data, float):
            return int(data)
        elif isinstance(data, bool):
            return 1 if data else 0
        elif isinstance(data, str):
            # 尝试解析字符串
            data = data.strip()
            if not data:
                return 0
            # 处理布尔值字符串
            if data.lower() in ("true", "yes", "1"):
                return 1
            elif data.lower() in ("false", "no", "0"):
                return 0
            # 尝试转换为整数
            try:
                return int(float(data))  # 先转float再转int，支持"3.14"这样的字符串
            except ValueError:
                raise ValueError(f"无法将'{data}' 转换为整数")
        else:
            raise ValueError(f"无法将类型{type(data).__name__} 转换为整数")
    
    def _to_float_single(self, data):
        """转换单个元素为浮点数(不处理列表)"""
        if isinstance(data, float):
            return data
        elif isinstance(data, int):
            return float(data)
        elif isinstance(data, bool):
            return 1.0 if data else 0.0
        elif isinstance(data, str):
            # 尝试解析字符串
            data = data.strip()
            if not data:
                return 0.0
            # 处理布尔值字符串
            if data.lower() in ("true", "yes"):
                return 1.0
            elif data.lower() in ("false", "no"):
                return 0.0
            # 尝试转换为浮点数
            try:
                return float(data)
            except ValueError:
                raise ValueError(f"无法将'{data}' 转换为浮点数")
        else:
            raise ValueError(f"无法将类型{type(data).__name__} 转换为浮点数")
    
    def _to_boolean_single(self, data):
        """转换单个元素为布尔值(不处理列表)"""
        if isinstance(data, bool):
            return data
        elif isinstance(data, (int, float)):
            return data != 0
        elif isinstance(data, str):
            data = data.strip().lower()
            if data in ("true", "yes", "1", "on"):
                return True
            elif data in ("false", "no", "0", "off", ""):
                return False
            else:
                # 非空字符串视为True
                return True
        elif data is None:
            return False
        else:
            return bool(data)
    
    def _to_list(self, data):
        """转换为列表"""
        if isinstance(data, list):
            return data
        elif isinstance(data, tuple):
            return list(data)
        elif isinstance(data, str):
            # 尝试解析JSON字符串
            data = data.strip()
            if not data:
                return []
            if data.startswith('[') and data.endswith(']'):
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    pass
            # 如果包含逗号，按逗号分隔
            if ',' in data:
                return [item.strip() for item in data.split(',')]
            # 否则返回单元素列表
            return [data]
        elif isinstance(data, (int, float, bool)):
            return [data]
        elif data is None:
            return []
        else:
            # 尝试转换为列表
            try:
                return list(data)
            except:
                return [data]
