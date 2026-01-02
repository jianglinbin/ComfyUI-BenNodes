import { app } from "../../scripts/app.js";
import { RESOLUTIONS, ASPECT_RATIOS, getWidget, hideWidget, showWidget, calcDims } from "./shared.js";

app.registerExtension({
    name: "ben.LoadImageBen",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "LoadImageBen") return;

        const origCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (origCreated) origCreated.apply(this, arguments);

            const node = this;

            const update = () => {
                try {
                    const resizeModeW = getWidget(node, "resize_mode");
                    if (!resizeModeW) return;

                    const resW = getWidget(node, "resolution");
                    const ratioW = getWidget(node, "aspect_ratio");
                    const wW = getWidget(node, "width");
                    const hW = getWidget(node, "height");
                    const featherW = getWidget(node, "feathering");
                    const upscaleMethodW = getWidget(node, "upscale_method");
                    const positionW = getWidget(node, "position");

                    if (resW) {
                        const resizeMode = resizeModeW.value;
                        const isCustom = resW.value === "自定义";

                        hideWidget(resW);
                        hideWidget(ratioW);
                        hideWidget(wW);
                        hideWidget(hW);
                        hideWidget(featherW);
                        hideWidget(upscaleMethodW);
                        hideWidget(positionW);

                        if (resizeMode !== "none") {
                            showWidget(resW);
                            
                            if (resizeMode !== "contain" && ratioW) showWidget(ratioW);
                            
                            if (isCustom && wW && hW) {
                                showWidget(wW);
                                showWidget(hW);
                                if (ratioW) hideWidget(ratioW);
                            }
                        }

                        if (resizeMode === "pad" && featherW) showWidget(featherW);

                        if (["contain", "crop", "pad"].includes(resizeMode) && upscaleMethodW) {
                            showWidget(upscaleMethodW);
                        }

                        if (["crop", "pad"].includes(resizeMode) && positionW) {
                            showWidget(positionW);
                        }

                        let d = { width: 1080, height: 720 };
                        if (resizeMode !== "none") {
                            d = calcDims(resW.value, ratioW?.value || "16:9", wW?.value || 1080, hW?.value || 720);
                        }

                        if (!isCustom && wW && hW) {
                            wW.value = d.width;
                            hW.value = d.height;
                        }
                    }

                    node.size = node.computeSize();
                    node.setDirtyCanvas(true);
                } catch (e) {
                    console.error("[LoadImageBen] update error:", e);
                }
            };

            ["resize_mode", "resolution", "aspect_ratio"].forEach(n => {
                const w = getWidget(node, n);
                if (w) {
                    const orig = w.callback;
                    w.callback = v => {
                        if (orig) orig.call(w, v);
                        update();
                    };
                }
            });

            setTimeout(update, 100);
        };

        const origComputeSize = nodeType.prototype.computeSize;
        nodeType.prototype.computeSize = function () {
            const HEADER_HEIGHT = 40;
            const WIDGET_HEIGHT = 32;
            const PADDING = 10;
            const BOTTOM_SPACE = 10;

            const visibleWidgets = (this.widgets || []).filter(w => !w.hidden && w != null);
            const wc = visibleWidgets.length;

            const widgetsAreaHeight = HEADER_HEIGHT + wc * WIDGET_HEIGHT + PADDING;
            const totalHeight = widgetsAreaHeight + BOTTOM_SPACE;

            const origSize = origComputeSize ? origComputeSize.apply(this, arguments) : [this.size ? this.size[0] : 200, totalHeight];
            return [origSize[0], totalHeight];
        };
    }
});
