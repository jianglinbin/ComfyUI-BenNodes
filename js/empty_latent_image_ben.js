import { app } from "../../scripts/app.js";
import { updateResolutionControls, wrapWidgetCallbacks } from "./shared.js";

app.registerExtension({
    name: "ben.latentResolutionPreset.2",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "EmptyLatentImageBen") return;

        const origCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (origCreated) origCreated.apply(this, arguments);

            const node = this;

            const update = () => updateResolutionControls(node);

            wrapWidgetCallbacks(node, ["resolution"], update);

            // 初始化时更新一次
            setTimeout(update, 200);
        };
    }
});
