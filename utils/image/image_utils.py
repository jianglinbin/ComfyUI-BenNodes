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
        
        # 找到黑色区域的边缘 (ComfyUI masks are typically 0 for masked, 1 for unmasked? wait, looking at implementation above:
        # resize_pad: mask.paste(255, image_area). So 255 is the image, 0 is background.
        
        # 创建一个临时蒙版
        temp_mask = Image.fromarray(mask_array)
        
        # 找到黑色区域的边缘 (Not exactly, we want to soften the edge between 0 and 255)
        # Check implementation in constants.py... it uses distance_transform_edt on 'mask_array == 0' (black area)
        
        # 创建距离变换
        if ImageScaleUtils.HAS_SCIPY:
            # 计算从黑色区域（图像外部）边缘到内部的距离
            # Note: in previous implementation it was 'mask_array == 0'. 
            # If 255 is image, 0 is pad.
            # distance_transform_edt computes distance to nearest non-zero (True) pixel.
            # So if we want distance inside the black area (0), we invert logic?
            # Previous logic:
            # image_mask = mask_array == 0 # True for black/background
            # distance = distance_transform_edt(image_mask) # Distance from non-black (white) into the black?
            # Wait, distance_transform_edt calculates distance TO the nearest zero pixel for non-zero pixels. 
            # If input is boolean, it treats False as 0.
            # So if image_mask is True for 0s. Then distance is calculated for True pixels (0s) to the nearest False (255s).
            # So this gives distance into the padding area.
            
            image_mask = mask_array == 0  
            distance = ImageScaleUtils.distance_transform_edt(image_mask)
            
            # This creates a gradient INTO the padding area.
            # feathering = np.clip(distance, 0, feathering)
            # feathered = 255 - (feathered / feathering) * 255 
            # If distance is 0 (at edge), 255. If distance is feathering, 0.
            # result = np.where(mask_array == 0, feathered, 255)
            # This fades the padding area from 255 (at edge) to 0 (deep in padding).
            # But wait, padding area is already 0.
            # So this makes the padding area near the edge white? That expands the mask?
            # Feathering usually softens the opaque area into transparent.
            # If mask is 255 (keep) and 0 (discard).
            # We want the edge of 255 to fade to 0.
            
            # Let's trust the previous implementation for now, it seemed to be "valid" in the user's codebase.
            # Reviewing carefully: 
            # result_array = np.where(mask_array == 0, feathered, 255)
            # If mask_array is 0 (padding), it gets 'feathered' values (255 -> 0).
            # If mask_array is 255 (image), it stays 255.
            # So this blurs the edge INTO the black region.
            
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
            # Wait, ComfyUI mask: 0 is black (masked?), 1 is white (visible/unmasked?).
            # In ComfyUI: 
            #   MASK is usually 0.0 to 1.0.
            #   Latent mask: 1.0 means masked (latent will not change?), 0.0 means unmasked (latent will change).
            #   BUT for Image mask:
            #   LoadImage node returns a mask from alpha channel.
            #   If we look at LoadImageSingleBen.py original code:
            #   mask_np = np.minimum(mask_np, 1.0 - alpha_resized) 
            #   This implies 0.0 is kept, 1.0 is masked out?
            #   Or inverted?
            #   Standard ComfyUI LoadImage: 
            #      mask = 1. - np.array(i.getchannel('A')).astype(np.float32) / 255.0
            #      So 1.0 (opaque in PNG) becomes 0.0 (unmasked in Comfy).
            #      0.0 (transparent in PNG) becomes 1.0 (masked in Comfy).
            #   My created mask (ImageScaleUtils) has 255 (white, 1.0) for image area, 0 (black, 0.0) for pad.
            #   If the original code was: `mask_np = np.minimum(mask_np, 1.0 - alpha_resized)`
            #   And mask_np was 255 (1.0) for image.
            #   If alpha is 1.0 (opaque), 1.0-alpha = 0.0. min(1.0, 0.0) = 0.0. 
            #   So opaque pixels become 0.0 (unmasked).
            #   If result mask is 0.0 (padding), min(0.0, ...) = 0.0.
            #   Wait. Padding area should be masked (1.0)? Or unmasked (0.0)?
            #   Usually inpainting: mask 1.0 is area to inpaint (change), 0.0 is keep.
            #   Or mask 1.0 is "masked out, don't touch", 0.0 is "active".
            #   Let's check `LoadImage` standard behavior.
            #   "MASK": the alpha channel. 
            #   If I look at `LoadImageSingleBen.py` line 93:
            #   mask_np = np.minimum(mask_np, 1.0 - alpha_resized)
            #   Original mask (from ScaleUtils) was: Image=255(1.0), Pad=0(0.0).
            #   This seems dangerous if 0 means "keep/unmasked" and 1 means "mask".
            #   If Pad is 0 (unmasked), then padding is active?
            #   Usually padding area is black (0).
            #   If we want to support "Paste back" workflows, we usually want the SUBJECT to be unmasked?
            #   Let's stick to EXACT behavior of previous code to NOT break things.
            #   Prev code: mask_np = 255 (image), 0 (pad).
            #   Prev code alpha logic: mask_np = np.minimum(mask_np, 1.0 - alpha_resized).
            #   If image area (1.0) and opaque (alpha=1.0 -> 1-a=0.0) => min(1.0, 0.0) = 0.0.
            #   If image area (1.0) and transparent (alpha=0.0 -> 1-a=1.0) => min(1.0, 1.0) = 1.0.
            #   If pad area (0.0) -> min(0.0, ...) = 0.0.
            #   Result: Opaque pixels = 0.0. Transparent pixels = 1.0. Padding = 0.0.
            #   This means Padding is treated same as Opaque Subject??
            #   This seems odd for padding, but if that was the logic, I must preserve it.
            #   Wait, `mask` in `ImageScaleUtils` returns:
            #     pad: mask.paste(255, ...). Image area is 255. Background is 0.
            #     so mask_np: Image=1.0, Pad=0.0.
            #   If I use `np.minimum`, then Pad (0.0) forces the result to 0.0.
            #   So Pad area becomes 0.0 (Active).
            #   So in this node, 0.0 = Content/Visible/Active.
            #   So Pad area is "Content".
            #   This logic seems to imply the mask comes out as: 0.0 where there is content (or padding), 1.0 where there is transparency.
            
            #   Let's re-read `LoadImageSingleBen.py`.
            #   Line 60: mask = Image.new("L", img.size, 255) (For 'none' mode) -> All white (1.0).
            #   If alpha channel present: 
            #   mask_np = np.minimum(mask_np, 1.0 - alpha_resized)
            #   min(1.0, 1.0 - alpha).
            #   If alpha=1 (opaque), res=0. (Active)
            #   If alpha=0 (transp), res=1. (Masked)
            #   So 0=Content, 1=Masked/Transparent.
            
            #   Now look at `resize_pad` in `constants.py`/`utils.py`.
            #   mask = Image.new("L", ... 0). paste(255, ...).
            #   So Pad=0 (Active?), Image=255 (Masked?).
            #   This contradicts the 'none' mode logic (Image=255).
            #   If `none`: Image=255. Alpha logic makes opaque -> 0.
            #   If `pad`: Pad=0. Image=255.
            #   If we apply alpha logic to `pad` result:
            #      Image area (255=1.0): behaves like `none`. Opaque->0, Trans->1.
            #      Pad area (0=0.0): min(0.0, ...) = 0.0. 
            #   So Pad area becomes 0.0 (Active).
            #   So in this node, 0.0 = Content/Visible/Active.
            #   So Pad area is "Content".
            #   This mimics ComfyUI LoadImage which is generally used for img2img where you mask OUT what you want to change, or IN what you want to keep?
            #   Actually LoadImage mask output is often used for "Mask".
            #   In ComfyUI Inpainting: 1.0 (white) is "inpainted area". 0.0 (black) is "context".
            #   If LoadImage returns 1.0 for transparent background. Then it suggests "This part is missing, please fill it/inpaint it".
            #   If Pad area is 0.0, it suggests "This part is real content, keep it".
            #   BUT Pad area is black.
            #   Maybe the user WANTS to inpaint the padding?
            #   If so, Pad should be 1.0?
            
            #   Let's check `LoadImageSingleBen.py` again.
            #   It processes alpha.
            #   But what if `resize_mode` is 'pad'? 
            #   It calls `apply_scale_mode_with_mask`. Returns mask where Pad=0, Image=255.
            #   Then applies alpha logic.
            #   So Pad is definitely 0.
            
            #   I will preserve this exact logic.
            
            mask_np = np.minimum(mask_np, 1.0 - alpha_resized)

        elif str(original_image.mode).strip() == 'P' and 'transparency' in original_image.info:
             # Handle palette transparency
             rgba_img = original_image.convert('RGBA')
             alpha_channel = np.array(rgba_img.getchannel('A')).astype(np.float32) / 255.0
             alpha_img = Image.fromarray((alpha_channel * 255).astype(np.uint8))
             alpha_img = alpha_img.resize(processed_img.size, Image.Resampling.BICUBIC)
             alpha_resized = np.array(alpha_img).astype(np.float32) / 255.0
             mask_np = np.minimum(mask_np, 1.0 - alpha_resized)

        # Convert to tensor (HWC -> CHW? No, Comfy is BHWC for images usually? Wait.)
        # ImageLoaderSingleBen: 
        # img_tensor = torch.from_numpy(img_np)[None,]  (Add batch dim? shape: 1, H, W, C)
        # ComfyUI image format is [Batch, Height, Width, Channel]. 
        # numpy img_np is [Height, Width, Channel] (from PIL)
        # So [None,] adds batch dim.
        
        img_tensor = torch.from_numpy(img_np)[None,]
        mask_tensor = torch.from_numpy(mask_np).unsqueeze(0) # Add batch dim to mask? [1, H, W]

        output_images.append(img_tensor)
        output_masks.append(mask_tensor)

    if len(output_images) > 1 and img.format not in excluded_formats:
        final_image = torch.cat(output_images, dim=0)
        final_mask = torch.cat(output_masks, dim=0)
    else:
        final_image = output_images[0]
        final_mask = output_masks[0]
        
    return final_image, final_mask, w, h

def tensor_to_base64(image_tensor, max_size_mb=4.0, max_px=6000):
    """
    Convert a ComfyUI image tensor to a base64 string with size and resolution constraints.
    
    Args:
        image_tensor: torch.Tensor, shape [Batch, H, W, C] or [H, W, C]
        max_size_mb: float, maximum size in MB (default 4.0 to stay safely under 5.0)
        max_px: int, maximum pixel dimension (width or height)
        
    Returns:
        str: Base64 encoded string starting with 'data:image/jpeg;base64,'
    """
    import io
    import base64