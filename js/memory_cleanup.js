/**
 * 内存清理节点的前端实现
 */

import { app } from "../../scripts/app.js";

// 注册扩展
import { t } from "./i18n.js";
app.registerExtension({
    name: "Ben.MemoryCleanupDynamicBen",
    
    
    async nodeCreated(node) {
        if (node.comfyClass !== "MemoryCleanupBen") return;
        
        console.log(`[MemoryCleanup] Node created: ${node.id}`);
        
        // 设置中文标签
        const widgetLabels = {
            "cleanup_mode": t("cleanup_mode_label")
        };
        
        // 为每个清理模式添加描述
        const modeDescriptions = {
            "无": t("cleanup_desc_none"),
            "仅显存": t("cleanup_desc_vram_only"),
            "仅内存": t("cleanup_desc_ram_only"),
            "全部": t("cleanup_desc_all")
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
            "cleanup_mode": t("cleanup_mode_label")
        };
        
        // 为每个清理模式添加描述
        const modeDescriptions = {
            "无": t("cleanup_desc_none"),
            "仅显存": t("cleanup_desc_vram_only"),
            "仅内存": t("cleanup_desc_ram_only"),
            "全部": t("cleanup_desc_all")
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
