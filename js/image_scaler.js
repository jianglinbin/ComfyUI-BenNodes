import { app } from "../../scripts/app.js";
import { RESOLUTIONS, ASPECT_RATIOS, getWidget, hideWidget, showWidget, calcDims, updateResolutionControls } from "./shared.js";

app.registerExtension({
    name: "ben.imageResolutionEditor.2",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "ImageScalerBen") return;

        // 移除所有宽度限制，让节点可以自由调整大小
        
        const origCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (origCreated) origCreated.apply(this, arguments);

            this.properties = this.properties || {};
            this.properties.previewWidth = 1280;
            this.properties.previewHeight = 720;
            
            // 移除最小宽度限制，让节点可以自由调整大小
            
            // 添加调试信息，跟踪minWidth设置和初始大小
            console.log(`[ImageScaler] onNodeCreated - minWidth: ${this.minWidth}, initial size: ${JSON.stringify(this.size)}`);
            
            // 添加大小变化监听器（如果可用）
            if (this.onResize) {
                const origResize = this.onResize;
                this.onResize = function() {
                    origResize.apply(this, arguments);
                    console.log(`[ImageScaler] onResize - new size: ${JSON.stringify(this.size)}, minWidth: ${this.minWidth}`);
                };
            }

            const node = this;

            const update = () => {
                const resizeModeW = getWidget(node, "resize_mode");
                const resW = getWidget(node, "resolution");
                const ratioW = getWidget(node, "aspect_ratio");
                const wW = getWidget(node, "width");
                const hW = getWidget(node, "height");
                const featherW = getWidget(node, "feathering");
                const upscaleMethodW = getWidget(node, "upscale_method");
                const positionW = getWidget(node, "position");
                // 创建颜色选择器UI
                if (!this.widgets.find(w => w.name === "pad_color")) {
                    this.addWidget("color", "pad_color", "#7f7f7f", (value) => {
                        // 颜色变化时的处理
                        update();
                    });
                }
                const padColorW = getWidget(node, "pad_color");
                
                if (!resizeModeW || !resW) return;

                const resizeMode = resizeModeW.value;
                const isCustom = resW.value === "自定义";

                hideWidget(resW);
                hideWidget(ratioW);
                hideWidget(wW);
                hideWidget(hW);
                hideWidget(featherW);
                hideWidget(upscaleMethodW);
                hideWidget(positionW);
                hideWidget(padColorW);

                if (resizeMode !== "none") {
                    showWidget(resW);
                    
                    if (resizeMode !== "contain" && resizeMode !== "none") {
                        showWidget(ratioW);
                    }
                    
                    if (isCustom) {
                        showWidget(wW);
                        showWidget(hW);
                        hideWidget(ratioW);
                    }
                }

                if (resizeMode === "pad") {
                    showWidget(featherW);
                    showWidget(padColorW);  // 只在pad模式下显示颜色选择
                }

                if (["contain", "crop", "pad"].includes(resizeMode) && upscaleMethodW) {
                    showWidget(upscaleMethodW);
                }

                if (["crop", "pad"].includes(resizeMode) && positionW) {
                    showWidget(positionW);
                }

                let d;
                if (resizeMode === "none") {
                    d = { width: 1080, height: 720 };
                } else {
                    d = calcDims(resW.value, ratioW?.value || "16:9", wW?.value || 1080, hW?.value || 720);
                }
                
                node.properties.previewWidth = d.width;
                node.properties.previewHeight = d.height;

                if (!isCustom && wW && hW) {
                    wW.value = d.width;
                    hW.value = d.height;
                }

                node.size = node.computeSize();
                node.setDirtyCanvas(true);
            };

            ["resolution", "aspect_ratio", "resize_mode"].forEach(n => {
                const w = getWidget(node, n);
                if (w) {
                    const orig = w.callback;
                    w.callback = v => {
                        if (orig) orig.call(w, v);
                        update();
                    };
                }
            });



            // 初始化时调用update函数，确保节点大小正确
            update();
            // 使用setTimeout再次调用，确保所有控件都已初始化
            setTimeout(update, 200);
        };

        nodeType.prototype.onExecuted = function (msg) {
            console.log("[ImageScaler] onExecuted called", msg);

            const info = msg?.resolution_info?.[0];
            if (info) {
                this.properties.previewWidth = info.width;
                this.properties.previewHeight = info.height;
            }

            this.setDirtyCanvas(true);
        };

        nodeType.prototype.onDrawForeground = function (ctx) {
            if (this.flags.collapsed) return;

            // 布局常量
            const HEADER_HEIGHT = 45;
            const WIDGET_HEIGHT = 32;
            const PADDING = 20;

            const wc = (this.widgets || []).filter(w => !w.hidden).length;
            const widgetsAreaHeight = HEADER_HEIGHT + wc * WIDGET_HEIGHT + PADDING;

            ctx.save();

            ctx.fillStyle = "#888";
            ctx.font = "12px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "bottom";
            const infoText = `${this.properties.previewWidth} x ${this.properties.previewHeight}`;
            ctx.fillText(infoText, this.size[0] / 2, this.size[1] - 8);

            ctx.restore();
        };

        // 保存原始的computeSize方法
        const origComputeSize = nodeType.prototype.computeSize;
        
        // 恢复原始的computeSize方法，移除所有高度限制
        if (origComputeSize) {
            nodeType.prototype.computeSize = origComputeSize;
        } else {
            // 如果没有原始方法，创建一个简单的方法，让节点可以自由调整大小
            nodeType.prototype.computeSize = function () {
                return [this.size ? this.size[0] : 350, this.size ? this.size[1] : 300];
            };
        };
    }
});