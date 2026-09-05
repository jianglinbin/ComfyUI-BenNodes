import { app } from "../../scripts/app.js";
import { updateScalerWidgets, wrapWidgetCallbacks, applyFixedComputeSize } from "./shared.js";

app.registerExtension({
    name: "ben.ImageLoader",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "ImageLoaderBen") return;

        const origCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (origCreated) origCreated.apply(this, arguments);

            const node = this;

            const update = () => updateScalerWidgets(node);

            wrapWidgetCallbacks(node, ["resize_mode", "resolution", "aspect_ratio"], update);

            setTimeout(update, 100);
        };

        applyFixedComputeSize(nodeType);
    }
});
