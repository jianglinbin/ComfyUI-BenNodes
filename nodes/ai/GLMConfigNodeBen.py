import os
from ...utils.constants.constants import any_type

class GLMConfigNodeBen:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "vision_model": ("STRING", {"default": "glm-4.6v-flash", "placeholder": "视觉模型名称", "tooltip": "可选值：glm-4.6v-flash, glm-4v等"}),
                "text_model": ("STRING", {"default": "glm-4.5-flash", "placeholder": "文本模型名称", "tooltip": "可选值：glm-4.5-flash, glm-4, glm-3-turbo等"}),
                "max_pages": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1, "tooltip": "PDF处理最大页数，0表示不限制"}),
                "max_tokens": ("INT", {"default": 8192, "min": 1, "max": 8192, "step": 1, "tooltip": "模型生成的最大token数"}),
            "temperature": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.1, "tooltip": "建议0.1 - 0.3，确保输出高度贴近指令要求，避免自由发挥。"}),
            "top_p": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "建议0.5 - 0.7，限制候选词范围，过滤低概率干扰项，提升格式一致性。"}),
            "frequency_penalty": ("FLOAT", {"default": 0.0, "min": -2.0, "max": 2.0, "step": 0.1, "tooltip": "(当前版本不支持) 控制重复token的生成概率，值越大越不容易重复。"}),
            "presence_penalty": ("FLOAT", {"default": 0.0, "min": -2.0, "max": 2.0, "step": 0.1, "tooltip": "(当前版本不支持) 控制新主题的引入概率，值越大越容易引入新主题。"}),
            "chunk_mode": (["auto", "first_chunk", "all_chunks_summary"], {"default": "auto", "tooltip": "大文件处理模式：auto-自动选择，first_chunk-只处理第一块，all_chunks_summary-分块处理并汇总"}),
            "thinking_enabled": ("BOOLEAN", {"default": True, "tooltip": "是否启用思考功能，启用后模型会展示思考过程，默认开启"}),
            }
        }

    CATEGORY = "BenNodes/AI"
    DESCRIPTION = "GLM模型配置节点，管理模型选择参数"
    RETURN_TYPES = ("GLM_CONFIG",)
    RETURN_NAMES = ("glm_config",)
    FUNCTION = "create_config"

    def create_config(self, text_model="glm-4.5-flash", vision_model="glm-4.6v-flash", temperature=0.3, max_tokens=2048, top_p=0.7, frequency_penalty=0.0, presence_penalty=0.0, chunk_mode="auto", max_pages=0, thinking_enabled=True):
        # 创建配置字典
        config = {
            "text_model": text_model,
            "vision_model": vision_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "chunk_mode": chunk_mode,
            "max_pages": max_pages,
            "thinking_enabled": thinking_enabled
        }
        return (config,)

# 注册节点类型
glm_config_type = {
    "GLM_CONFIG": (
        GLMConfigNodeBen,
        "create_config",
        ["text_model", "vision_model", "temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty", "chunk_mode", "max_pages", "thinking_enabled"]
    )
}
