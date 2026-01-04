/**
 * 内存清理节点的前端实现
 */

import { app } from "../../scripts/app.js";

// 注册扩展
app.registerExtension({
    name: "Ben.MemoryCleanupDynamicBen",
    
    
    async nodeCreated(node) {
        if (node.comfyClass !== "MemoryCleanupBen") return;
        
        console.log(`[MemoryCleanup] Node created: ${node.id}`);
        
        // 设置中文标签
        const widgetLabels = {
            "cleanup_mode": "清理模式"
        };
        
        // 为每个清理模式添加描述
        const modeDescriptions = {
            "无": "⏭️ 不执行清理\n• 直接传递数据\n• 不清理任何内存\n\n适用：调试或跳过清理",
            "仅显存": "💾 只清理显存\n• 卸载模型\n• 清空VRAM缓存\n\n适用：显存不足时",
            "仅内存": "🧠 只清理内存\n• 清理文件缓存\n• 清理进程内存\n• 清理未使用DLL\n\n适用：内存不足时",
            "全部": "🔥 深度清理\n• 显存：卸载模型+清空缓存\n• 内存：全部清理\n\n适用：严重内存不足"
        };
        
        if (node.widgets) {
            for (const widget of node.widgets) {
                if (widgetLabels[widget.name]) {
                    widget.label = widgetLabels[widget.name];
                }
            }
        }
        
        // 添加模式描述到 widget
        const cleanupModeWidget = node.widgets?.find(w => w.name === "cleanup_mode");
        if (cleanupModeWidget) {
            // 创建动态 tooltip
            Object.defineProperty(cleanupModeWidget, 'tooltip', {
                get: function() {
                    const currentMode = this.value || "全部";
                    return modeDescriptions[currentMode] || "";
                },
                configurable: true
            });
        }
    },
    
    async loadedGraphNode(node) {
        if (node.comfyClass !== "MemoryCleanupBen") return;
        
        console.log(`[MemoryCleanup] Graph loaded, node: ${node.id}`);
        
        // 设置中文标签
        const widgetLabels = {
            "cleanup_mode": "清理模式"
        };
        
        // 为每个清理模式添加描述
        const modeDescriptions = {
            "无": "⏭️ 不执行清理\n• 直接传递数据\n• 不清理任何内存\n适用：调试或跳过清理",
            "仅显存": "💾 只清理显存\n• 卸载模型\n• 清空VRAM缓存\n适用：显存不足时",
            "仅内存": "🧠 只清理内存\n• 清理文件缓存\n• 清理进程内存\n• 清理未使用DLL\n适用：内存不足时",
            "全部": "🔥 深度清理\n• 显存：卸载模型+清空缓存\n• 内存：全部清理\n适用：严重内存不足"
        };
        
        if (node.widgets) {
            for (const widget of node.widgets) {
                if (widgetLabels[widget.name]) {
                    widget.label = widgetLabels[widget.name];
                }
            }
        }
        
        // 添加模式描述到 widget
        const cleanupModeWidget = node.widgets?.find(w => w.name === "cleanup_mode");
        if (cleanupModeWidget) {
            // 创建动态 tooltip
            Object.defineProperty(cleanupModeWidget, 'tooltip', {
                get: function() {
                    const currentMode = this.value || "全部";
                    return modeDescriptions[currentMode] || "";
                },
                configurable: true
            });
        }
    }
});

console.log("[MemoryCleanup] Extension loaded successfully");
