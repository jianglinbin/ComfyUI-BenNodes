import { app } from "../../scripts/app.js";
import { getWidget, hideWidget, showWidget } from "./shared.js";

app.registerExtension({
    name: "ben.latentResolutionPreset.2",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "EmptyLatentImageBen") return;

        const origCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (origCreated) origCreated.apply(this, arguments);

            const node = this;

            const update = () => {
                const resW = getWidget(node, "resolution");
                const ratioW = getWidget(node, "aspect_ratio");
                const widthW = getWidget(node, "width");
                const heightW = getWidget(node, "height");

                if (!resW) return;

                // 获取当前值
                const resolution = resW.value;
                const isCustom = resolution === "自定义";

                // 隐藏或显示控件
                if (ratioW) {
                    if (isCustom) {
                        // 自定义分辨率时隐藏宽高比
                        hideWidget(ratioW);
                    } else {
                        // 非自定义分辨率时显示宽高比
                        showWidget(ratioW);
                    }
                }
                
                // 处理宽高控件的显示/隐藏
                if (widthW && heightW) {
                    if (isCustom) {
                        // 自定义分辨率时显示宽高
                        showWidget(widthW);
                        showWidget(heightW);
                    } else {
                        // 非自定义分辨率时隐藏宽高
                        hideWidget(widthW);
                        hideWidget(heightW);
                    }
                }

                node.size = node.computeSize();
                node.setDirtyCanvas(true);
            };

            // 添加回调函数
            ["resolution"].forEach(n => {
                const w = getWidget(node, n);
                if (w) {
                    const orig = w.callback;
                    w.callback = v => {
                        if (orig) orig.call(w, v);
                        update();
                    };
                }
            });

            // 初始化时更新一次
            setTimeout(update, 200);
        };
    }
});
