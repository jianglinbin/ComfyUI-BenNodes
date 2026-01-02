"""
列表索引选择节点
用于从列表中选择指定索引的元素
"""

import logging
import torch

# 配置日志
logging.basicConfig(level=logging.WARNING, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定义any_type，与TypeConverterBen保持一致
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True
    def __ne__(self, _):
        return False

any_type = AlwaysEqualProxy("*")

class ListIndexSelectorBen:
    """列表索引选择节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "*": (any_type,),  # 使用*作为参数名，接受任意类型
                "index": ("STRING", {"default": "0", "tooltip": "要选择的列表索引，从0开始计数，支持单个int值或逗号分隔的字符串值，如 0,1,2,3"})
            }
        }
    
    # 简化输出定义- 支持最多20个输出，使用any_type让ComfyUI自动推断类型
    RETURN_TYPES = tuple([any_type] * 20)
    RETURN_NAMES = tuple([f"ITEM_{i}" for i in range(20)])
    OUTPUT_NODE = False
    FUNCTION = "select"
    CATEGORY = "BenNodes/数据"
    
    def select(self, *args, **kwargs):
        """根据索引从列表中获取元素，类似convertAnything的简洁实现"""
        # 确保能正确获取输入数据
        # 从位置参数获取列表数据（ComfyUI通常这样传递连接的输入）
        if args:
            list_data = args[0]
        else:
            list_data = kwargs.get('*', None)
        index = kwargs.get('index', "0")
        
        # ComfyUI的批量图像是单个形状为[N, H, W, C]的张量，需要特殊处理
        
        try:
            # 只在调试时打印日志
            logger.debug(f"输入数据: {list_data}, 类型: {type(list_data).__name__}")
            logger.debug(f"索引: {index}")
            
            # 解析索引
            if isinstance(index, str):
                # 字符串类型索引，支持逗号分隔的多值
                index_strings = [i.strip() for i in index.split(",") if i.strip()]
                
                # 处理ADD指令：前端应该已经解析，但如果直接传递了ADD指令，这里也处理
                if len(index_strings) == 1 and index_strings[0].lower() == "add":
                    # 基础ADD指令，使用索引0
                    index_strings = ["0"]
                elif len(index_strings) > 1 and index_strings[0].lower() == "add":
                    # add,0,1,2等形式，使用后面的数值参数
                    index_strings = index_strings[1:]
            elif isinstance(index, int):
                # int类型索引，单值
                index_strings = [str(index)]
            else:
                # 其他类型转换为字符串
                index_strings = [str(index)]
            
            # 如果没有有效索引，默认使用索引0
            if not index_strings:
                index_strings = ["0"]
            
            logger.debug(f"解析后的索引: {index_strings}")
            
            # 检查输入
            if list_data is None:
                error_msg = "输入数据为空，请连接输入端口"
                logger.error(error_msg)
                # 返回None而不是错误字符串，避免下游节点崩溃
                return tuple([None] * 20)
            
            # 支持列表、元组和张量
            if not isinstance(list_data, (list, tuple, torch.Tensor)):
                error_msg = f"输入类型错误，需要列表、元组或张量，当前类型 {type(list_data).__name__}"
                logger.error(error_msg)
                # 返回None而不是错误字符串，避免下游节点崩溃
                return tuple([None] * 20)
            
            # 确定数据类型和长度
            is_batch_tensor = False
            if isinstance(list_data, torch.Tensor):
                # 检查是否为批量数据（4D张量: [N, H, W, C]）
                if len(list_data.shape) == 4:
                    is_batch_tensor = True
                    data_length = list_data.shape[0]  # 批量大小
                else:
                    data_length = list_data.shape[0]  # 普通张量长度
                logger.debug(f"张量形状: {list_data.shape}")
                logger.debug(f"{'批量张量' if is_batch_tensor else '普通张量'}, 数据长度: {data_length}")
            else:
                data_length = len(list_data)
                logger.debug(f"列表/元组长度: {data_length}")
            
            # 获取元素
            results = []
            for idx_str in index_strings:
                try:
                    idx = int(idx_str)
                    if 0 <= idx < data_length:
                        # 根据数据类型和是否为批量张量选择不同的索引方式
                        if isinstance(list_data, torch.Tensor):
                            if is_batch_tensor:
                                # 从批量张量中提取单个图像: [N, H, W, C] -> [H, W, C] -> [1, H, W, C]
                                # ComfyUI期望单个图像带有batch维度
                                element = list_data[idx].unsqueeze(0)
                            else:
                                # 普通张量索引
                                element = list_data[idx]
                        else:
                            # 列表或元组索引
                            element = list_data[idx]
                        results.append(element)
                        logger.debug(f"索引 {idx}: {element} (类型: {type(element).__name__})")
                    else:
                        error_msg = f"索引 {idx} 超出范围，数据长度为 {data_length}"
                        results.append(None)  # 返回None而不是错误字符串
                        logger.error(error_msg)
                except ValueError:
                    error_msg = f"无效的索引值 {idx_str}"
                    results.append(None)  # 返回None而不是错误字符串
                    logger.error(error_msg)
            
            # 填充到20个输出
            while len(results) < 20:
                results.append(None)
            
            result_tuple = tuple(results)
            logger.debug(f"返回结果: {result_tuple[:len(index_strings)]}")
            return result_tuple
            
        except Exception as e:
            error_msg = f"获取元素失败: {str(e)}"
            logger.error(error_msg)
            print(f"[ListIndexSelector错误] {error_msg}")
            # 返回None而不是错误字符串，避免下游节点崩溃
            return tuple([None] * 20)
