import { app } from "../../scripts/app.js";
import { getWidget, updateScalerWidgets, wrapWidgetCallbacks } from "./shared.js";

app.registerExtension({
    name: "ben.imageResolutionEditor.2",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "ImageScalerBen") return;

        const origCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (origCreated) origCreated.apply(this, arguments);

            this.properties = this.properties || {};
            this.properties.previewWidth = 1280;
            this.properties.previewHeight = 720;

            const node = this;

            const update = () => {
                // 创建颜色选择器UI
                if (!this.widgets.find(w => w.name === "pad_color")) {
                    this.addWidget("color", "pad_color", "#7f7f7f", () => {
                        update();
                    });
                }

                const d = updateScalerWidgets(node);
                node.properties.previewWidth = d.width;
                node.properties.previewHeight = d.height;
            };

            wrapWidgetCallbacks(node, ["resolution", "aspect_ratio", "resize_mode"], update);

            // 初始化时调用update函数，确保节点大小正确
            update();
            // 使用setTimeout再次调用，确保所有控件都已初始化
            setTimeout(update, 200);
        };

        nodeType.prototype.onExecuted = function (msg) {
            const info = msg?.resolution_info?.[0];
            if (info) {
                this.properties.previewWidth = info.width;
                this.properties.previewHeight = info.height;
            }

            this.setDirtyCanvas(true);
        };

        nodeType.prototype.onDrawForeground = function (ctx) {
            if (this.flags.collapsed) return;

            ctx.save();

            ctx.fillStyle = "#888";
            ctx.font = "12px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "bottom";
            const infoText = `${this.properties.previewWidth} x ${this.properties.previewHeight}`;
            ctx.fillText(infoText, this.size[0] / 2, this.size[1] - 8);

            ctx.restore();
        };
    }
});
