"""
高级列表索引选择节点
用于从列表中选择指定模式的元素（起始位置、间隔、长度）
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

class AdvancedListIndexSelectorBen:
    """高级列表索引选择节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "list": ("*", {"forceInput": True}),
            },
            "optional": {
                "start_index": ("INT", {"default": 0, "min": 0, "step": 1, "tooltip": "起始序号，从0开始计数"}),
                "step": ("INT", {"default": 0, "min": 0, "step": 1, "tooltip": "间隔值，0表示不间隔，1表示每隔1个取一个，2表示每隔2个取一个，以此类推"}),
                "length": ("INT", {"default": 1, "min": 1, "step": 1, "tooltip": "要选择的元素个数"})
            }
        }
    
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("SELECTED_LIST",)
    OUTPUT_NODE = False
    FUNCTION = "select_advanced"
    CATEGORY = "BenNodes/数据"
    
    def select_advanced(self, list, start_index=0, step=1, length=1):
        """根据高级规则从列表中获取元素"""
        
        try:
            # 验证输入
            if list is None:
                error_msg = "输入列表为空，请连接输入端口"
                logger.error(error_msg)
                return (None,)
            
            # 验证参数
            if start_index < 0:
                logger.warning(f"起始序号 {start_index} 小于0，将设为0")
                start_index = 0
            
            if step < 0:
                logger.warning(f"间隔值 {step} 小于0，将设为0")
                step = 0
            
            if length <= 0:
                error_msg = f"长度 {length} 必须大于0"
                logger.error(error_msg)
                return (None,)
            
            # 记录参数
            logger.debug(f"输入参数: 起始序号={start_index}, 间隔值={step}, 长度={length}")
            
            # 获取数据长度
            if isinstance(list, torch.Tensor):
                data_length = list.shape[0]
                logger.debug(f"张量形状: {list.shape}, 数据长度: {data_length}")
            elif isinstance(list, (list, tuple)):
                data_length = len(list)
                logger.debug(f"列表/元组长度: {data_length}")
            else:
                error_msg = f"不支持的数据类型: {type(list).__name__}"
                logger.error(error_msg)
                return (None,)
            
            # 检查起始序号是否超出范围
            if start_index >= data_length:
                error_msg = f"起始序号 {start_index} 超出数据范围，数据长度为 {data_length}"
                logger.error(error_msg)
                return (None,)
            
            # 计算实际可获取的元素数量
            if step == 0:
                # 不间隔模式
                available_length = min(length, data_length - start_index)
                if available_length <= 0:
                    error_msg = f"从起始序号 {start_index} 开始没有可用的元素"
                    logger.error(error_msg)
                    return (None,)
                indices = list(range(start_index, start_index + available_length))
            else:
                # 间隔模式
                # 计算最大可获取的元素数量
                max_possible = ((data_length - start_index - 1) // step) + 1 if start_index < data_length else 0
                available_length = min(length, max_possible)
                
                if available_length <= 0:
                    error_msg = f"从起始序号 {start_index} 开始，间隔 {step} 时没有可用的元素"
                    logger.error(error_msg)
                    return (None,)
                
                indices = [start_index + i * step for i in range(available_length)]
            
            logger.debug(f"选择的索引: {indices}")
            
            # 根据数据类型选择元素
            if isinstance(list, torch.Tensor):
                if len(list.shape) == 1:
                    # 一维张量
                    selected = list[indices]
                elif len(list.shape) == 4:
                    # 四维张量 (批量图像: [N, H, W, C])
                    selected_indices_tensor = torch.tensor(indices, device=list.device)
                    selected = list[selected_indices_tensor]
                else:
                    # 其他形状的张量
                    selected = list[indices]
            elif isinstance(list, (list, tuple)):
                selected = [list[i] for i in indices]
            else:
                error_msg = f"不支持的数据类型: {type(list).__name__}"
                logger.error(error_msg)
                return (None,)
            
            # 保持原始数据类型
            if isinstance(list, tuple):
                selected = tuple(selected)
            
            logger.debug(f"选择的元素数量: {len(selected)}")
            return (selected,)
            
        except Exception as e:
            error_msg = f"高级索引选择失败: {str(e)}"
            logger.error(error_msg)
            print(f"[AdvancedListIndexSelector错误] {error_msg}")
            return (None,)