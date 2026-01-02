import os
import time

class TextProcessor:
    """文本处理模块，负责处理各种文本文件和内容"""
    
    # GLM-4.5-Flash 的 token 限制（预留一些空间给 prompt 和响应）
    MAX_CONTENT_CHARS = 100000  # 约 100K 字符，预留空间
    CHUNK_SIZE = 80000  # 每块大小
    
    def __init__(self, current_config):
        self.current_config = current_config
    
    def process_text_file(self, client, file_path, prompt, chunk_mode):
        """处理文本文件，支持大文件"""
        try:
            # 记录文件处理开始时间
            start_time = time.time()
            
            # 尝试多种编码读取
            content = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return ("无法读取文件，请检查文件编码",)
            
            file_name = os.path.basename(file_path)
            
            # 记录文件处理结束时间并打印时长
            file_process_time = time.time() - start_time
            print(f"文件处理时长：{file_process_time:.2f}秒")
            
            return self.process_text_content(client, content, prompt, chunk_mode, f"文本文件({file_name})")
            
        except Exception as e:
            return (f"读取文本文件失败: {str(e)}",)
    
    def process_text_content(self, client, content, prompt, chunk_mode, file_type):
        """处理文本内容，支持大文件分块"""
        content_len = len(content)
        
        # 小文件直接处理
        if content_len <= self.MAX_CONTENT_CHARS:
            result = self.call_text_api(client, f"{file_type}内容:\n{content}", prompt)
            return ([result[0]],)
        
        # 大文件分块处理
        print(f"文件较大({content_len}字符)，启用分块处理模式: {chunk_mode}")
        
        if chunk_mode == "first_chunk":
            # 只处理第一块
            chunk = content[:self.CHUNK_SIZE]
            result = self.call_text_api(client, f"{file_type}内容(前{self.CHUNK_SIZE}字符):\n{chunk}", prompt)
            return ([result[0]],)
        
        elif chunk_mode == "all_chunks_summary":
            # 分块处理并汇总
            chunks = self.split_text_into_chunks(content)
            results = []
            
            for i, chunk in enumerate(chunks):
                print(f"处理第 {i+1}/{len(chunks)} 块...")
                chunk_prompt = f"这是{file_type}的第{i+1}部分(共{len(chunks)}部分)，请分析:\n{prompt}"
                result = self.call_text_api(client, f"内容:\n{chunk}", chunk_prompt)
                results.append(f"=== 第{i+1}部分分析 ===\n{result[0]}")
            
            # 汇总所有结果
            combined = "\n\n".join(results)
            summary_prompt = f"以下是对{file_type}各部分的分析结果，请给出综合总结:\n\n{combined}"
            final_result = self.call_text_api(client, "", summary_prompt)
            
            return ([f"{combined}\n\n=== 综合总结 ===\n{final_result[0]}"],)
        
        else:  # auto 模式
            # 自动选择：如果不太大就处理第一块，否则提示用户
            if content_len <= self.CHUNK_SIZE * 2:
                chunk = content[:self.CHUNK_SIZE]
                return self.call_text_api(client, f"{file_type}内容(前{self.CHUNK_SIZE}字符，文件较大已截断):\n{chunk}", prompt)
            else:
                return ([f"文件过大({content_len}字符)，请选择处理模式:\n- first_chunk: 只分析前{self.CHUNK_SIZE}字符\n- all_chunks_summary: 分块分析并汇总(会多次调用API)"],)
    
    def split_text_into_chunks(self, text):
        """将文本分割成多个块"""
        chunks = []
        for i in range(0, len(text), self.CHUNK_SIZE):
            chunks.append(text[i:i + self.CHUNK_SIZE])
        return chunks
    
    def call_text_api(self, client, content, prompt):
        """调用文本API"""
        try:
            # 获取配置的模型参数和系统提示词
            config = self.current_config
            text_model = config.get('text_model', 'glm-4.5-flash')
            system_prompt = config.get('system_prompt', '你是一个专业的内容分析助手，请仔细分析用户提供的内容并给出详细的分析结果。')
            temperature = config.get('temperature', 0.7)
            max_tokens = config.get('max_tokens', 2048)
            top_p = config.get('top_p', 0.9)
            frequency_penalty = config.get('frequency_penalty', 0.0)
            presence_penalty = config.get('presence_penalty', 0.0)
            
            # 构建用户内容
            user_content = ""
            if content:
                if prompt.strip():
                    user_content = f"{prompt}\n\n{content}"
                else:
                    user_content = f"请分析这个内容：\n{content}"
            else:
                user_content = prompt.strip() if prompt.strip() else "请分析这个内容"
            
            # 构建消息列表，包含系统提示词和用户提示词
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
            
            # 记录API请求开始时间
            api_start_time = time.time()
            
            # 构建thinking参数
            thinking_enabled = config.get('thinking_enabled', True)
            thinking_param = {"type": "enabled"} if thinking_enabled else {"type": "disabled"}
            
            response = client.chat.completions.create(
                model=text_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                thinking=thinking_param
            )
            
            # 记录API请求结束时间并打印时长
            api_end_time = time.time()
            print(f"API请求时长：{api_end_time - api_start_time:.2f}秒")
            
            return (response.choices[0].message.content,)
        except Exception as e:
            return (f"API调用失败: {str(e)}",)
