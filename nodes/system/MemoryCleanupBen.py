"""
动态内存清理节点
结合动态输入和内存清理功能
"""

import psutil
import ctypes
from ctypes import wintypes
import time
import platform
import subprocess
import gc
from server import PromptServer
import comfy.model_management


class AnyType(str):
    """用于表示任意类型的特殊类，在类型比较时总是返回相等"""
    def __eq__(self, _) -> bool:
        return True

    def __ne__(self, __value: object) -> bool:
        return False


any_type = AnyType("*")


class MemoryCleanupDynamicBen:
    """
    内存清理节点
    
    功能：
    1. 接收一个任意类型的输入
    2. 执行内存和显存清理
    3. 将输入直接传递到输出
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 清理模式选择
                "cleanup_mode": ([
                    "无",
                    "仅显存",
                    "仅内存", 
                    "全部"
                ], {
                    "default": "全部"
                }),
                # 单个输入 - 改为必需参数
                "input": (any_type, {}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }
    
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    FUNCTION = "execute"
    CATEGORY = "BenNodes/控制"
    OUTPUT_NODE = True
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # 返回当前时间戳，确保每次都执行
        return float(time.time())
    
    def get_ram_usage(self):
        """获取当前RAM使用情况"""
        memory = psutil.virtual_memory()
        return memory.percent, memory.available / (1024 * 1024)
    
    def clean_vram(self, offload_model, offload_cache):
        """清理VRAM"""
        try:
            if offload_model:
                comfy.model_management.unload_all_models()
            
            if offload_cache:
                gc.collect()
                comfy.model_management.soft_empty_cache()
                PromptServer.instance.prompt_queue.set_flag("free_memory", True)
            
            print(f"✓ VRAM清理完成 [卸载模型: {offload_model}, 清空缓存: {offload_cache}]")
                
        except Exception as e:
            print(f"✗ VRAM清理失败: {str(e)}")
    
    def clean_ram(self, clean_file_cache, clean_processes, clean_dlls, retry_times):
        """清理RAM"""
        try:
            before_usage, before_available = self.get_ram_usage()
            system = platform.system()
            
            for attempt in range(retry_times):
                if clean_file_cache:
                    try:
                        if system == "Windows":
                            ctypes.windll.kernel32.SetSystemFileCacheSize(-1, -1, 0)
                        elif system == "Linux":
                            subprocess.run(["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"], 
                                          check=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                    except:
                        pass
                
                if clean_processes:
                    if system == "Windows":
                        for process in psutil.process_iter(['pid', 'name']):
                            try:
                                handle = ctypes.windll.kernel32.OpenProcess(
                                    wintypes.DWORD(0x001F0FFF),
                                    wintypes.BOOL(False),
                                    wintypes.DWORD(process.info['pid'])
                                )
                                ctypes.windll.psapi.EmptyWorkingSet(handle)
                                ctypes.windll.kernel32.CloseHandle(handle)
                            except:
                                continue

                if clean_dlls:
                    try:
                        if system == "Windows":
                            ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
                        elif system == "Linux":
                            subprocess.run(["sync"], check=True)
                    except:
                        pass

                time.sleep(0.5)

            after_usage, after_available = self.get_ram_usage()
            freed_mb = after_available - before_available
            print(f"✓ RAM清理完成 [{before_usage:.1f}% → {after_usage:.1f}%, 释放: {freed_mb:.0f}MB]")

        except Exception as e:
            print(f"✗ RAM清理失败: {str(e)}")
    
    def execute(self, cleanup_mode, input, unique_id=None, extra_pnginfo=None):
        """
        执行节点逻辑
        1. 根据清理模式设置参数
        2. 执行内存清理
        3. 返回输入数据
        """
        # 根据清理模式设置参数
        if cleanup_mode == "无":
            # 不执行任何清理，直接传递输入
            print(f"📊 内存清理节点 [{cleanup_mode}]: 跳过清理")
            return (input,)
        elif cleanup_mode == "仅显存":
            offload_model = True
            offload_cache = True
            clean_file_cache = False
            clean_processes = False
            clean_dlls = False
            retry_times = 0
        elif cleanup_mode == "仅内存":
            offload_model = False
            offload_cache = False
            clean_file_cache = True
            clean_processes = True
            clean_dlls = True
            retry_times = 3
        else:  # "全部"
            offload_model = True
            offload_cache = True
            clean_file_cache = True
            clean_processes = True
            clean_dlls = True
            retry_times = 3
        
        # 执行VRAM清理
        if offload_model or offload_cache:
            self.clean_vram(offload_model, offload_cache)
        
        # 执行RAM清理
        if clean_file_cache or clean_processes or clean_dlls:
            self.clean_ram(clean_file_cache, clean_processes, clean_dlls, retry_times)
        
        # 打印统计信息
        print(f"📊 内存清理节点 [{cleanup_mode}]: 清理完成")
        
        return (input,)


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "MemoryCleanupDynamicBen": MemoryCleanupDynamicBen,
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "MemoryCleanupDynamicBen": "释放显存内存 🧹-Ben",
}
