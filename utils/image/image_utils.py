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
    def resize_contain(img, target_width, target_height, feathering, upscale_method="bicubic"):
        """
        contain: 保持原图宽高比，让图像的大边与目标尺寸对齐，小边根据大边的缩放比例计算。
        返回的是缩放后的图像实际尺寸，而不是包含空白区域的目标尺寸。
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

        # 创建与缩放后图像相同尺寸的全白遮罩
        mask = Image.new("L", (new_width, new_height), 255)

        # 应用羽化效果
        if feathering > 0:
            mask = ImageScaleUtils.apply_feather(mask, feathering)

        return resized_img, mask

    @staticmethod
    def resize_pad(img, target_width, target_height, feathering, upscale_method="bicubic", position="center", pad_color=(127, 127, 127)):
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

        mask = Image.new("L", (target_width, target_height), 255)
        mask.paste(0, (x_offset, y_offset, x_offset + new_width, y_offset + new_height))

        if feathering > 0:
            mask = ImageScaleUtils.apply_feather(mask, feathering)

        return new_img, mask

    @staticmethod
    def resize_crop(img, target_width, target_height, feathering, upscale_method="bicubic", position="center"):
        """
        crop/cover: 保持原图宽高比，缩放到至少填满目标容器，超出部分裁剪，无空白边。
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

        mask = Image.new("L", (target_width, target_height), 255)

        if feathering > 0:
            mask = ImageScaleUtils.apply_feather(mask, feathering)

        return result, mask

    @staticmethod
    def resize_fill(img, target_width, target_height, feathering, upscale_method="bicubic"):
        """
        fill: 直接拉伸图片至目标尺寸，不保持宽高比且无裁剪补边。
        """
        # 根据upscale_method选择插值方法
        resample_method = Image.Resampling.BICUBIC
        if upscale_method == "bilinear":
            resample_method = Image.Resampling.BILINEAR
        elif upscale_method == "lanczos":
            resample_method = Image.Resampling.LANCZOS

        # 直接拉伸到目标尺寸，不保持宽高比
        result = img.resize((target_width, target_height), resample_method)

        # 创建全白遮罩，因为整个区域都是图片内容
        mask = Image.new("L", (target_width, target_height), 255)

        # 应用羽化效果
        if feathering > 0:
            mask = ImageScaleUtils.apply_feather(mask, feathering)

        return result, mask

    @staticmethod
    def apply_scale_mode_with_mask(img, scale_mode, target_width, target_height, feathering, upscale_method="bicubic", position="center", pad_color=(127, 127, 127)):
        """
        根据指定的缩放模式处理图像并生成相应的遮罩
        这个方法调用对应的专用缩放方法以保持一致性
        """
        if scale_mode == "none":
            mask = Image.new("L", img.size, 255)
            if feathering > 0:
                mask = ImageScaleUtils.apply_feather(mask, feathering)
            return img, mask
        elif scale_mode == "contain":
            return ImageScaleUtils.resize_contain(img, target_width, target_height, feathering, upscale_method)
        elif scale_mode == "crop":
            return ImageScaleUtils.resize_crop(img, target_width, target_height, feathering, upscale_method, position)
        elif scale_mode == "pad":
            return ImageScaleUtils.resize_pad(img, target_width, target_height, feathering, upscale_method, position, pad_color)
        elif scale_mode == "fill":
            return ImageScaleUtils.resize_fill(img, target_width, target_height, feathering, upscale_method)
        else:
            mask = Image.new("L", img.size, 255)
            return img, mask
    
    @staticmethod
    def apply_feather(mask, feathering):
        """
        为遮罩添加羽化效果。
        羽化值越大，图像边缘的过渡越平滑（在图像范围内应用）。
        """
        # 转换为numpy数组
        mask_array = np.array(mask)
        
        # 如果羽化值为0，直接返回原遮罩
        if feathering <= 0:
            return mask
        
        # 找到黑色区域的边缘
        # 遮罩语义（见上方 resize_pad）：255=图像区，0=补边区
        # 羽化：在补边区内做距离变换，使图像边缘从 255 渐变到 0（软边）
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
        
        # Apply scaling
        processed_img, mask = ImageScaleUtils.apply_scale_mode_with_mask(
            current_frame, resize_mode, target_width, target_height, feathering, upscale_method, position, pad_color
        )
        
        if w is None:
            w, h = processed_img.size
            
        # Skip frames that don't match expected size (shouldn't happen with our scaling but safety check)
        if processed_img.size[0] != w or processed_img.size[1] != h:
            continue
            
        # Convert to numpy
        img_np = np.array(processed_img).astype(np.float32) / 255.0
        mask_np = np.array(mask).astype(np.float32) / 255.0
        
        # Handle alpha channel merging if present
        if 'A' in original_image.getbands():
            alpha_channel = np.array(original_image.getchannel('A')).astype(np.float32) / 255.0
            alpha_img = Image.fromarray((alpha_channel * 255).astype(np.uint8))
            alpha_img = alpha_img.resize(processed_img.size, Image.Resampling.BICUBIC)
            alpha_resized = np.array(alpha_img).astype(np.float32) / 255.0
            mask_np = np.minimum(mask_np, 1.0 - alpha_resized) # Use the image's alpha as the mask (1.0 = opaque)
            # 遮罩语义：0.0 = 可见区，1.0 = 被遮蔽/透明区（与 ComfyUI LoadImage 的 alpha 行为一致）
            # 图像不透明处 alpha 贡献 1.0-1.0=0.0（可见）；透明处贡献 1.0-0.0=1.0（遮蔽）
            # pad 模式补边区在本函数中为 1.0（被遮蔽），为兼容历史实现有意保留

        elif str(original_image.mode).strip() == 'P' and 'transparency' in original_image.info:
             # Handle palette transparency
             rgba_img = original_image.convert('RGBA')
             alpha_channel = np.array(rgba_img.getchannel('A')).astype(np.float32) / 255.0
             alpha_img = Image.fromarray((alpha_channel * 255).astype(np.uint8))
             alpha_img = alpha_img.resize(processed_img.size, Image.Resampling.BICUBIC)
             alpha_resized = np.array(alpha_img).astype(np.float32) / 255.0
             mask_np = np.minimum(mask_np, 1.0 - alpha_resized)

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
