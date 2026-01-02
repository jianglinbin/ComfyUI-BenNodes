import os
import time
import base64
from PIL import Image
import io

class VisionProcessor:
    """视觉处理模块，负责处理图片、PDF、视频等视觉内容"""
    
    def __init__(self, current_config):
        self.current_config = current_config
    
    def call_vision_api(self, client, content_list):
        """调用视觉API"""
        try:
            # 移除所有空的text项，并检查是否有非空的text内容
            filtered_content_list = []
            has_non_empty_text = False
            
            for item in content_list:
                if item.get('type') == 'text':
                    text_content = item.get('text', '').strip()
                    if text_content:
                        filtered_content_list.append(item)
                        has_non_empty_text = True
                else:
                    filtered_content_list.append(item)
            
            # 如果没有非空的text内容，添加默认提示词
            if not has_non_empty_text:
                filtered_content_list.insert(0, {"type": "text", "text": "请分析这个内容"})
            
            # 使用过滤后的content_list
            content_list = filtered_content_list
            
            # 获取配置的模型参数和系统提示词
            config = self.current_config
            vision_model = config.get('vision_model', 'glm-4.6v-flash')
            system_prompt = config.get('system_prompt', '你是一个专业的内容分析助手，请仔细分析用户提供的内容并给出详细的分析结果。')
            temperature = config.get('temperature', 0.7)
            max_tokens = config.get('max_tokens', 2048)
            top_p = config.get('top_p', 0.9)
            frequency_penalty = config.get('frequency_penalty', 0.0)
            presence_penalty = config.get('presence_penalty', 0.0)
            
            # 构建消息列表，包含系统提示词和用户提示词
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content_list}
            ]
            
            # 记录API请求开始时间
            api_start_time = time.time()
            
            # 构建thinking参数
            thinking_enabled = config.get('thinking_enabled', True)
            thinking_param = {"type": "enabled"} if thinking_enabled else {"type": "disabled"}
            
            response = client.chat.completions.create(
                model=vision_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                thinking=thinking_param
            )
            
            # 记录API请求结束时间并打印时长
            api_end_time = time.time()
            print(f"API请求时长：{api_end_time - api_start_time:.2f}秒")
            
            return ([response.choices[0].message.content],)
        except Exception as e:
            return ([f"API调用失败: {str(e)}"],)
    
    def process_image_file(self, client, file_path, prompt):
        """处理图片文件"""
        with open(file_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_str}"}}
        ]
        return self.call_vision_api(client, content)
    
    def process_image_tensor(self, client, image_tensor, prompt):
        """处理图片张量（支持批量处理）"""
        tensor_shape = image_tensor.shape
        results = []
        
        # 处理4D张量 (batch_size, height, width, channels)
        if len(tensor_shape) == 4:
            batch_size = tensor_shape[0]
            for i in range(batch_size):
                # 提取单个批次的图片张量
                single_tensor = image_tensor[i]
                try:
                    base64_str = self.image_tensor_to_base64(single_tensor)
                    content = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_str}"}}
                    ]
                    # 调用API并获取结果
                    result = self.call_vision_api(client, content)
                    results.append(result[0])
                except Exception as e:
                    results.append(f"处理图片批次{i}失败: {str(e)}")
            # 返回批量结果
            return (results,)
        
        # 处理3D张量 (height, width, channels)
        elif len(tensor_shape) == 3:
            try:
                base64_str = self.image_tensor_to_base64(image_tensor)
                content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_str}"}}
                ]
                return self.call_vision_api(client, content)
            except Exception as e:
                return (f"处理图片失败: {str(e)}",)
        else:
            return (f"不支持的张量维度: {tensor_shape}",)
    
    def process_pdf_file(self, client, file_path, prompt):
        """处理PDF文件"""
        # 记录文件处理开始时间
        start_time = time.time()
        
        # 从配置获取max_pages参数
        max_pages = self.current_config.get('max_pages', 0)
        base64_images = self.pdf_to_base64_images(file_path, max_pages=max_pages)
        
        # 记录文件处理结束时间并打印时长
        file_process_time = time.time() - start_time
        print(f"文件处理时长：{file_process_time:.2f}秒")
        
        content = [{"type": "text", "text": prompt}]
        for img in base64_images:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}})
        return self.call_vision_api(client, content)
    
    def process_video_file(self, client, file_path, prompt):
        """处理视频文件"""
        # 记录文件处理开始时间
        start_time = time.time()
        
        # 直接读取并编码整个视频文件
        with open(file_path, "rb") as video_file:
            video_base = base64.b64encode(video_file.read()).decode('utf-8')
        
        # 记录文件处理结束时间并打印时长
        file_process_time = time.time() - start_time
        print(f"文件处理时长：{file_process_time:.2f}秒")
        
        # 构建API请求内容
        content = [
            {"type": "text", "text": prompt},
            {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{video_base}"}}  # 使用视频方式发送
        ]
        
        return self.call_vision_api(client, content)
    
    def process_video_input(self, client, video, prompt):
        """处理VIDEO类型输入"""
        # 记录文件处理开始时间
        start_time = time.time()
        
        video_base = None
        
        # 尝试不同方式获取视频数据
        if hasattr(video, 'path') and os.path.exists(video.path):
            # 如果视频对象有文件路径属性，直接读取文件
            with open(video.path, "rb") as video_file:
                video_base = base64.b64encode(video_file.read()).decode('utf-8')
        elif hasattr(video, 'filename') and os.path.exists(video.filename):
            # 另一种可能的文件路径属性
            with open(video.filename, "rb") as video_file:
                video_base = base64.b64encode(video_file.read()).decode('utf-8')
        elif hasattr(video, '_VideoFromFile__file') and os.path.exists(video._VideoFromFile__file):
            # 支持ComfyUI的VideoFromFile类型（通过名称修饰访问私有属性）
            with open(video._VideoFromFile__file, "rb") as video_file:
                video_base = base64.b64encode(video_file.read()).decode('utf-8')
        else:
            # 对于无法直接获取原始视频数据的情况，返回错误
            return (["不支持的视频类型，无法直接获取原始视频数据"],)
        if video_base is None:
            return (["无法获取视频数据"],)
        
        # 记录文件处理结束时间并打印时长
        file_process_time = time.time() - start_time
        print(f"视频处理时长：{file_process_time:.2f}秒")
        
        # 构建API请求内容
        content = [
            {"type": "text", "text": prompt},
            {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{video_base}"}}  # 使用视频方式发送
        ]
        return self.call_vision_api(client, content)
    def image_tensor_to_base64(self, image_tensor):
        """将ComfyUI的IMAGE张量转换为base64"""
        # 获取张量的维度
        tensor_shape = image_tensor.shape
        
        # 处理4D张量 (batch_size, height, width, channels) -> (height, width, channels)
        if len(tensor_shape) == 4:
            # 取第一个批次
            image_tensor = image_tensor[0]
        
        # 处理3D张量 (height, width, channels)
        if len(image_tensor.shape) == 3:
            image_tensor = (image_tensor * 255).byte()
            pil_image = Image.fromarray(image_tensor.cpu().numpy(), mode='RGB')
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        else:
            raise ValueError(f"不支持的张量维度: {tensor_shape}")