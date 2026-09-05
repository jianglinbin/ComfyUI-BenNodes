"""
ComfyUI-BenNodes Shared Utilities
Contains image scaling logic and common processing functions
"""

import torch
import numpy as np
from PIL import Image, ImageOps, ImageSequence

try:
    import node_helpers
    NODE_HELPERS_AVAILABLE = True
except ImportError:
    NODE_HELPERS_AVAILABLE = False
    # 提供模拟实现
    class MockNodeHelpers:
        @staticmethod
        def pillow(func, *args, **kwargs):
            return func(*args, **kwargs)
    node_helpers = MockNodeHelpers()

class ImageScaleUtils:
    """
    提供各种图片缩放相关的工具方法
    """
    
    # 提前导入必要的库，避免在函数内部重复导入
    try:
        from scipy.ndimage import distance_transform_edt
        HAS_SCIPY = True
    except ImportError:
        HAS_SCIPY = False
    from PIL import ImageFilter
    
    @staticmethod
    def resize_contain(img, target_width, target_height, feathering, upscale_method="bicubic", alpha=None):
        """
        contain: 保持原图宽高比，让图像的大边与目标尺寸对齐，小边根据大边的缩放比例计算。
        返回的是缩放后的图像实际尺寸，而不是包含空白区域的目标尺寸。

        Args:
            alpha: 可选，原图的 alpha 通道（PIL L 模式），将按缩放几何对齐融入遮罩（透明处=255 被遮蔽）
        """
        img_width, img_height = img.size

        # 根据图像的大边与目标尺寸对齐来计算缩放比例
        if img_width > img_height:
            scale_factor = target_width / img_width
        else:
            scale_factor = target_height / img_height

        # 计算新的尺寸
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)

        # 根据upscale_method选择插值方法
        resample_method = Image.Resampling.BICUBIC
        if upscale_method == "bilinear":
            resample_method = Image.Resampling.BILINEAR
        elif upscale_method == "lanczos":
            resample_method = Image.Resampling.LANCZOS

        # 使用指定的插值方法进行缩放
        resized_img = img.resize((new_width, new_height), resample_method)

        # 遮罩语义（ComfyUI MASK：255=被遮蔽）：输出全部为图像内容，默认全 0（可见）；
        # 有 alpha 时透明像素处为 255（被遮蔽）
        mask_array = np.zeros((new_height, new_width), dtype=np.uint8)
        if alpha is not None:
            alpha_scaled = alpha.resize((new_width, new_height), Image.Resampling.BICUBIC)
            mask_array = np.maximum(mask_array, 255 - np.array(alpha_scaled, dtype=np.int16)).astype(np.uint8)
        mask = Image.fromarray(mask_array)

        # 应用羽化效果
        if feathering > 0:
            mask = ImageScaleUtils.apply_feather(mask, feathering)

        return resized_img, mask

    @staticmethod
    def resize_pad(img, target_width, target_height, feathering, upscale_method="bicubic", position="center", pad_color=(127, 127, 127), alpha=None):
        """
        pad: 保持原图宽高比先按contain规则缩放，再在空白区域补边，最终尺寸与目标容器完全一致。

        Args:
            img: PIL Image to resize
            target_width: Target width
            target_height: Target height
            feathering: Feathering amount for edges
            upscale_method: Interpolation method ("bicubic", "bilinear", "lanczos")
            position: Position for image placement ("center", "top", "bottom", "left", "right")
            pad_color: Color for padding area as RGB tuple, default (127, 127, 127)
            alpha: 可选，原图的 alpha 通道（PIL L 模式），仅在图像子矩形内融入遮罩（透明处=255 被遮蔽）
        """
        img_width, img_height = img.size

        scale_factor = min(target_width / img_width, target_height / img_height)
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)

        resample_method = Image.Resampling.BICUBIC
        if upscale_method == "bilinear":
            resample_method = Image.Resampling.BILINEAR
        elif upscale_method == "lanczos":
            resample_method = Image.Resampling.LANCZOS

        resized_img = img.resize((new_width, new_height), resample_method)

        # Use specified pad color instead of default gray
        new_img = Image.new("RGB", (target_width, target_height), pad_color)

        position_offsets = {
            "center": ((target_width - new_width) // 2, (target_height - new_height) // 2),
            "top": ((target_width - new_width) // 2, 0),
            "bottom": ((target_width - new_width) // 2, target_height - new_height),
            "left": (0, (target_height - new_height) // 2),
            "right": (target_width - new_width, (target_height - new_height) // 2),
        }
        x_offset, y_offset = position_offsets.get(position, position_offsets["center"])
        new_img.paste(resized_img, (x_offset, y_offset))

        # 遮罩语义（ComfyUI MASK：255=被遮蔽）：图像区=0，补边区=255
        mask = Image.new("L", (target_width, target_height), 255)
        mask.paste(0, (x_offset, y_offset, x_offset + new_width, y_offset + new_height))

        if alpha is not None:
            # alpha 仅作用于图像子矩形（与内容几何对齐），透明处=255（被遮蔽）；
            # 不透明的 alpha 不会清除补边区的 255
            alpha_scaled = alpha.resize((new_width, new_height), Image.Resampling.BICUBIC)
            region_box = (x_offset, y_offset, x_offset + new_width, y_offset + new_height)
            region_array = np.array(mask.crop(region_box), dtype=np.int16)
            alpha_blocked = 255 - np.array(alpha_scaled, dtype=np.int16)
            region_array = np.maximum(region_array, alpha_blocked).astype(np.uint8)
            mask.paste(Image.fromarray(region_array), (x_offset, y_offset))

        if feathering > 0:
            mask = ImageScaleUtils.apply_feather(mask, feathering)

        return new_img, mask

    @staticmethod
    def resize_crop(img, target_width, target_height, feathering, upscale_method="bicubic", position="center", alpha=None):
        """
        crop/cover: 保持原图宽高比，缩放到至少填满目标容器，超出部分裁剪，无空白边。

        Args:
            alpha: 可选，原图的 alpha 通道（PIL L 模式），按相同几何缩放并裁剪后融入遮罩（透明处=255 被遮蔽）
        """
        img_width, img_height = img.size

        scale_factor = max(target_width / img_width, target_height / img_height)
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)

        resample_method = Image.Resampling.BICUBIC
        if upscale_method == "bilinear":
            resample_method = Image.Resampling.BILINEAR
        elif upscale_method == "lanczos":
            resample_method = Image.Resampling.LANCZOS

        resized_img = img.resize((new_width, new_height), resample_method)

        position_offsets = {
            "center": ((new_width - target_width) // 2, (new_height - target_height) // 2),
            "top": ((new_width - target_width) // 2, 0),
            "bottom": ((new_width - target_width) // 2, new_height - target_height),
            "left": (0, (new_height - target_height) // 2),
            "right": (new_width - target_width, (new_height - target_height) // 2),
        }
        crop_x, crop_y = position_offsets.get(position, position_offsets["center"])
        result = resized_img.crop((crop_x, crop_y, crop_x + target_width, crop_y + target_height))

        # 遮罩语义（ComfyUI MASK：255=被遮蔽）：输出全部为图像内容，默认全 0（可见）；
        # 有 alpha 时按相同几何裁剪，透明像素处为 255（被遮蔽）
        mask_array = np.zeros((target_height, target_width), dtype=np.uint8)
        if alpha is not None:
            alpha_scaled = alpha.resize((new_width, new_height), Image.Resampling.BICUBIC)
            alpha_cropped = np.array(
                alpha_scaled.crop((crop_x, crop_y, crop_x + target_width, crop_y + target_height)),
                dtype=np.int16,
            )
            mask_array = (255 - alpha_cropped).astype(np.uint8)
        mask = Image.fromarray(mask_array)

        if feathering > 0:
            mask = ImageScaleUtils.apply_feather(mask, feathering)

        return result, mask

    @staticmethod
    def resize_fill(img, target_width, target_height, feathering, upscale_method="bicubic", alpha=None):
        """
        fill: 直接拉伸图片至目标尺寸，不保持宽高比且无裁剪补边。

        Args:
            alpha: 可选，原图的 alpha 通道（PIL L 模式），拉伸到目标尺寸后融入遮罩（透明处=255 被遮蔽）
        """
        # 根据upscale_method选择插值方法
        resample_method = Image.Resampling.BICUBIC
        if upscale_method == "bilinear":
            resample_method = Image.Resampling.BILINEAR
        elif upscale_method == "lanczos":
            resample_method = Image.Resampling.LANCZOS

        # 直接拉伸到目标尺寸，不保持宽高比
        result = img.resize((target_width, target_height), resample_method)

        # 遮罩语义（ComfyUI MASK：255=被遮蔽）：输出全部为图像内容，默认全 0（可见）；
        # 有 alpha 时拉伸到目标尺寸，透明像素处为 255（被遮蔽）
        mask_array = np.zeros((target_height, target_width), dtype=np.uint8)
        if alpha is not None:
            alpha_scaled = alpha.resize((target_width, target_height), Image.Resampling.BICUBIC)
            mask_array = (255 - np.array(alpha_scaled, dtype=np.int16)).astype(np.uint8)
        mask = Image.fromarray(mask_array)

        # 应用羽化效果
        if feathering > 0:
            mask = ImageScaleUtils.apply_feather(mask, feathering)

        return result, mask

    @staticmethod
    def apply_scale_mode_with_mask(img, scale_mode, target_width, target_height, feathering, upscale_method="bicubic", position="center", pad_color=(127, 127, 127), alpha=None):
        """
        根据指定的缩放模式处理图像并生成相应的遮罩
        这个方法调用对应的专用缩放方法以保持一致性

        Args:
            alpha: 可选，原图的 alpha 通道（PIL L 模式），由各缩放方法按自身几何融入遮罩
        """
        if scale_mode == "none":
            # 遮罩语义（ComfyUI MASK：255=被遮蔽）：图像原样输出，默认全 0（可见）；
            # 有 alpha 时透明像素处为 255（被遮蔽）
            mask_array = np.zeros((img.size[1], img.size[0]), dtype=np.uint8)
            if alpha is not None:
                mask_array = (255 - np.array(alpha, dtype=np.int16)).astype(np.uint8)
            mask = Image.fromarray(mask_array)
            if feathering > 0:
                mask = ImageScaleUtils.apply_feather(mask, feathering)
            return img, mask
        elif scale_mode == "contain":
            return ImageScaleUtils.resize_contain(img, target_width, target_height, feathering, upscale_method, alpha)
        elif scale_mode == "crop":
            return ImageScaleUtils.resize_crop(img, target_width, target_height, feathering, upscale_method, position, alpha)
        elif scale_mode == "pad":
            return ImageScaleUtils.resize_pad(img, target_width, target_height, feathering, upscale_method, position, pad_color, alpha)
        elif scale_mode == "fill":
            return ImageScaleUtils.resize_fill(img, target_width, target_height, feathering, upscale_method, alpha)
        else:
            # 未知模式按 none 处理
            return ImageScaleUtils.apply_scale_mode_with_mask(img, "none", target_width, target_height, feathering, upscale_method, position, pad_color, alpha)
    
    @staticmethod
    def apply_feather(mask, feathering):
        """
        为遮罩添加羽化效果。
        羽化值越大，图像边缘的过渡越平滑（在图像范围内应用）。
        """
        # 如果羽化值为0，直接返回原遮罩
        if feathering <= 0:
            return mask

        # 转换为numpy数组
        mask_array = np.array(mask)

        # 无渐变可做时直接返回：
        # - 全 255（无图像区）或全 0（无补边区，如 crop/fill/none 模式）
        # - 避免 scipy EDT 在无背景点时按数组边界计算产生意外晕影
        if mask_array.min() == 255 or mask_array.max() == 0:
            return mask

        # 遮罩语义（与 resize_pad 输出及 ComfyUI MASK 一致）：0=图像区（可见），255=补边区（被遮蔽）
        # 羽化：在图像区内做距离变换，使靠近补边区的图像边缘从 0 渐变到 255（软边）
        if ImageScaleUtils.HAS_SCIPY:
            image_mask = mask_array == 0
            distance = ImageScaleUtils.distance_transform_edt(image_mask)

            feathered = np.clip(distance, 0, feathering)
            feathered = 255 - (feathered / feathering) * 255
            feathered = feathered.astype(np.uint8)
            
            result_array = np.where(mask_array == 0, feathered, 255)
            
            return Image.fromarray(result_array)
        else:
            # Simple Gaussian blur fallback
            blur_radius = feathering / 2
            blurred_mask = mask.filter(ImageScaleUtils.ImageFilter.GaussianBlur(radius=blur_radius))
            blurred_array = np.array(blurred_mask)
            result_array = np.where(mask_array == 0, blurred_array, 255)
            return Image.fromarray(result_array)

def process_image_for_comfy(pil_image, resize_mode, target_width, target_height, feathering=0, upscale_method="bicubic", position="center", pad_color=(127, 127, 127)):
    """
    Unified image processing function for ComfyUI nodes.
    
    Args:
        pil_image: Source PIL Image
        resize_mode: "none", "contain", "pad", "crop", "fill"
        target_width: Target width
        target_height: Target height
        feathering: Feathering amount
        upscale_method: Interpolation method for upscaling (bilinear, bicubic, lanczos)
        position: Position for crop/pad ("center", "top", "bottom", "left", "right")
        pad_color: Color for padding area as RGB tuple, default (127, 127, 127)
        
    Returns:
        tuple: (output_image_tensor, output_mask_tensor, final_width, final_height)
    """

    # Handle EXIF orientation
    img = node_helpers.pillow(ImageOps.exif_transpose, pil_image)

    # Standardize mode
    if img.mode == 'I':
        img = img.point(lambda i: i * (1 / 255))
    
    output_images = []
    output_masks = []
    w, h = None, None
    
    excluded_formats = ['MPO']
    
    # Iterate over frames (for animated images) or single frame
    for i in ImageSequence.Iterator(img):
        # Keep transparency info
        original_image = i.copy()
        current_frame = i.convert("RGB")

        # 提取 alpha 通道（LA/RGBA 或带 transparency 的 P 模式），
        # 交给缩放函数按各自几何对齐融入遮罩（透明处=255 被遮蔽）
        alpha_channel = None
        if 'A' in original_image.getbands():
            alpha_channel = Image.fromarray(np.array(original_image.getchannel('A')).astype(np.uint8))
        elif str(original_image.mode).strip() == 'P' and 'transparency' in original_image.info:
            alpha_channel = Image.fromarray(np.array(original_image.convert('RGBA').getchannel('A')).astype(np.uint8))

        # Apply scaling
        processed_img, mask = ImageScaleUtils.apply_scale_mode_with_mask(
            current_frame, resize_mode, target_width, target_height, feathering, upscale_method, position, pad_color, alpha_channel
        )

        if w is None:
            w, h = processed_img.size

        # Skip frames that don't match expected size (shouldn't happen with our scaling but safety check)
        if processed_img.size[0] != w or processed_img.size[1] != h:
            continue

        # Convert to numpy
        img_np = np.array(processed_img).astype(np.float32) / 255.0
        mask_np = np.array(mask).astype(np.float32) / 255.0

        # 遮罩语义（ComfyUI MASK：1.0=被遮蔽，0.0=可见）：
        # - pad 补边区 1.0；crop/fill/contain/none 图像内容区 0.0
        # - 源图 alpha 透明处 1.0（由缩放函数按几何对齐融入）

        # 转为 ComfyUI 张量格式：图像 [B, H, W, C]，遮罩 [B, H, W]
        img_tensor = torch.from_numpy(img_np)[None,]
        mask_tensor = torch.from_numpy(mask_np).unsqueeze(0)

        output_images.append(img_tensor)
        output_masks.append(mask_tensor)

    if len(output_images) > 1 and img.format not in excluded_formats:
        final_image = torch.cat(output_images, dim=0)
        final_mask = torch.cat(output_masks, dim=0)
    else:
        final_image = output_images[0]
        final_mask = output_masks[0]

    return final_image, final_mask, w, h
