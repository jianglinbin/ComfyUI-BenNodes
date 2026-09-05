import torch
from ...utils.base.base_node import BaseResolutionNode
from ...utils.i18n import t

class EmptyLatentImageBen(BaseResolutionNode):
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    @classmethod
    def INPUT_TYPES(cls):
        """定义输入参数"""
        return {
            "required": {
                "resolution": (list(cls.RESOLUTIONS.keys()), {"default": "1080p"}),
                "aspect_ratio": (list(cls.ASPECT_RATIOS.keys()), {"default": "16:9"}),
                "width": ("INT", {"default": 1920, "min": 16, "max": 16384, "step": 8}),
                "height": ("INT", {"default": 1080, "min": 16, "max": 16384, "step": 8}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
            },
            "optional": {
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    OUTPUT_TOOLTIPS = (t("empty_latent_output_tooltip"),)
    FUNCTION = "generate"

    CATEGORY = f"BenNodes/{t('common_cat_image')}"
    DESCRIPTION = t("empty_latent_description")

    # 继承基类的calculate_dimensions 方法，无需重写

    def generate(self, resolution, aspect_ratio, width, height, batch_size=1):
        calc_width, calc_height = self.calculate_dimensions(resolution, aspect_ratio, width, height)
        latent = torch.zeros([batch_size, 4, calc_height // 8, calc_width // 8], device=self.device)
        return ({"samples": latent},)
