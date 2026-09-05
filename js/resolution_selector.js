import { app } from '../../scripts/app.js';
import { updateResolutionControls, wrapWidgetCallbacks } from './shared.js';

app.registerExtension({
    name: 'BenNodes.ResolutionSelector',
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== 'ResolutionSelectorBen') return;

        const origCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (origCreated) origCreated.apply(this, arguments);

            const node = this;

            const update = () => updateResolutionControls(node);

            wrapWidgetCallbacks(node, ['resolution'], update);

            // 初始化时更新一次
            setTimeout(update, 200);
        };
    }
});
