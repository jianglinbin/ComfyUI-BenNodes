import os
import torch
from zhipuai import ZhipuAI
from ...utils.constants.constants import any_type

# 导入拆分后的模块
from .text_processor import TextProcessor
from .vision_processor import VisionProcessor
from .office_processor import OfficeProcessor

class GLMNodeBen:
    """GLM模型主节点，负责协调各个处理模块"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "prompt": ("STRING", {"default": "请分析这个内容", "multiline": True}),
                "system_prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "系统提示词，用于定义模型的角色和行为"}),
                "input": (any_type, {"default": "", "tooltip": "支持ComfyUI图片、视频数据类型，也可以是文件路径字符串，支持图片、视频、PDF,OFFICE文件。"}),
                "glm_config": ("GLM_CONFIG", {"default": None, "tooltip": "GLM配置节点，用于选择模型参数和分块模式，不包含API密钥"}),
                "api_key": ("STRING", {"default": "", "placeholder": "请输入GLM API密钥"}),
            }
        }

    CATEGORY = "BenNodes/AI"
    DESCRIPTION = "使用GLM分析图片、视频、PDF,OFFICE或文本文件，支持大文件分块处理"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("分析结果",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "analyze_content"

    def analyze_content(self, prompt="", system_prompt="", input="", glm_config=None, api_key=""):
        if not api_key:
            return (["请输入GLM API密钥"],)

        # 从配置节点获取模型参数（不包含API密钥）
        text_model = "glm-4.5-flash"
        vision_model = "glm-4.6v-flash"
        temperature = 0.3
        max_tokens = 8192
        top_p = 0.7
        frequency_penalty = 0.0
        presence_penalty = 0.0
        chunk_mode = "auto"
        max_pages = 0
        
        if glm_config is not None:
            text_model = glm_config.get("text_model", "glm-4.5-flash")
            vision_model = glm_config.get("vision_model", "glm-4.6v-flash")
            temperature = glm_config.get("temperature", 0.3)
            max_tokens = glm_config.get("max_tokens", 8192)
            top_p = glm_config.get("top_p", 0.7)
            frequency_penalty = glm_config.get("frequency_penalty", 0.0)
            presence_penalty = glm_config.get("presence_penalty", 0.0)
            chunk_mode = glm_config.get("chunk_mode", "auto")
            max_pages = glm_config.get("max_pages", 0)
        
        # 存储配置参数供各个处理模块使用
        current_config = {
            "api_key": api_key,
            "system_prompt": system_prompt,
            "text_model": text_model,
            "vision_model": vision_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "chunk_mode": chunk_mode,
            "max_pages": max_pages
        }
        
        client = ZhipuAI(api_key=api_key)
        
        # 初始化各个处理模块
        text_processor = TextProcessor(current_config)
        vision_processor = VisionProcessor(current_config)
        office_processor = OfficeProcessor()
        
        # 检查输入是否为空，需要特殊处理张量类型
        input_is_empty = False
        if input is None:
            input_is_empty = True
        elif isinstance(input, str):
            input_is_empty = not input.strip()
        elif hasattr(input, 'shape'):  # 处理张量类型
            import torch
            if isinstance(input, torch.Tensor):
                input_is_empty = input.numel() == 0
            else:
                input_is_empty = False
        else:
            input_is_empty = False

        # 如果没有提供输入文件/内容，直接分析prompt
        if input_is_empty:
            # 直接使用文本处理器分析prompt
            if not prompt.strip():
                return (["请提供prompt内容进行分析"],)
            result = text_processor.call_text_api(client, "", prompt)
            return ([result[0]],)

        # 动态判断输入类型并处理
        if isinstance(input, str) and os.path.exists(input):
            file_ext = os.path.splitext(input)[1].lower()
            
            # 文本文件处理（支持大文件）
            if file_ext in ['.txt', '.md', '.json', '.xml', '.csv', '.log', '.py', '.js', '.html', '.css']:
                return text_processor.process_text_file(client, input, prompt, chunk_mode)
            
            # 图片文件
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
                return vision_processor.process_image_file(client, input, prompt)
            
            # PDF文件
            elif file_ext in ['.pdf']:
                return vision_processor.process_pdf_file(client, input, prompt)
            
            # 视频文件
            elif file_ext in ['.mp4', '.avi', '.mov', '.webm', '.mkv']:
                return vision_processor.process_video_file(client, input, prompt)
            
            # Office文档
            elif file_ext in ['.docx']:
                content = office_processor.read_docx_content(input)
                return text_processor.process_text_content(client, content, prompt, chunk_mode, "Word文档")
            
            elif file_ext in ['.doc']:
                content = office_processor.read_doc_content(input)
                return text_processor.process_text_content(client, content, prompt, chunk_mode, "Word文档")
            
            elif file_ext in ['.xlsx']:
                content = office_processor.read_xlsx_content(input)
                return text_processor.process_text_content(client, content, prompt, chunk_mode, "Excel文档")
            
            elif file_ext in ['.xls']:
                content = office_processor.read_xls_content(input)
                return text_processor.process_text_content(client, content, prompt, chunk_mode, "Excel文档")
            
            elif file_ext in ['.pptx']:
                content = office_processor.read_pptx_content(input)
                return text_processor.process_text_content(client, content, prompt, chunk_mode, "PowerPoint文档")
            
            elif file_ext in ['.ppt']:
                content = office_processor.read_ppt_content(input)
                return text_processor.process_text_content(client, content, prompt, chunk_mode, "PowerPoint文档")
            
            else:
                return ([f"不支持的文件类型: {file_ext}"],)

        elif isinstance(input, torch.Tensor):
            return vision_processor.process_image_tensor(client, input, prompt)

        else:
            # 尝试处理视频输入（VIDEO类型）
            try:
                if hasattr(input, 'get_components'):
                    return vision_processor.process_video_input(client, input, prompt)
                else:
                    return (["不支持的输入类型，请提供有效的文件路径、图片或视频"],)
            except Exception as e:
                return ([f"处理错误: {str(e)}"],)