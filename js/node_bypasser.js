import { app } from "../../scripts/app.js";
import {
    getConnectedNodes,
    setNodesMode,
    clearPythonDefinedContent,
    applyWidthPreservation,
    bindTitleSync
} from "./bypasser_common.js";

import { t } from "./i18n.js";
app.registerExtension({
    name: "BenNodes.NodeBypasser",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "NodeBypasserBen") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

            // 清除所有 Python 定义的内容
            clearPythonDefinedContent(this);

            // 初始化状态
            this.modeOn = 0;
            this.modeOff = 4;
            this.masterToggle = null;

            // 添加输入与主开关
            this.addInput("", "*");
            this.addMasterToggle();

            setTimeout(() => {
                if (this.scheduleStabilize) {
                    this.scheduleStabilize(1);
                }
            }, 100);

            return r;
        };

        // 添加主开关
        nodeType.prototype.addMasterToggle = function () {
            const toggleName = this.title || t("node_bypasser");
            this.masterToggle = this.addWidget("toggle", toggleName, true, (value) => {
                // value 是 boolean 类型：true = 启用，false = 忽略
                const allNodes = this.getAllConnectedNodes();
                const targetMode = value ? this.modeOn : this.modeOff;
                setNodesMode(allNodes, targetMode);
                if (this.graph) {
                    this.graph.setDirtyCanvas(true, true);
                }
            }, { on: "yes", off: "no" });
            return this.masterToggle;
        };

        // 根据已连接节点的模式同步主开关状态
        nodeType.prototype.syncMasterToggle = function () {
            if (!this.masterToggle) return;
            const allNodes = this.getAllConnectedNodes();

            if (allNodes.length === 0) {
                this.masterToggle.value = true;
                return;
            }

            const allEnabled = allNodes.every(n => n.mode === this.modeOn);
            const allDisabled = allNodes.every(n => n.mode === this.modeOff);

            if (allEnabled) {
                this.masterToggle.value = true;
            } else if (allDisabled) {
                this.masterToggle.value = false;
            }
            // 混合状态保持当前值不变
        };

        // 稳定输入：末尾保留一个空槽，移除空槽，按连接节点命名
        nodeType.prototype.stabilizeInputs = function () {
            if (!this.inputs) return;
            const lastInput = this.inputs[this.inputs.length - 1];
            if (lastInput && lastInput.link != null) {
                this.addInput("", "*");
            }
            for (let i = this.inputs.length - 2; i >= 0; i--) {
                const input = this.inputs[i];
                if (input.link == null) {
                    this.removeInput(i);
                }
            }
            for (let i = 0; i < this.inputs.length - 1; i++) {
                const input = this.inputs[i];
                if (input.link != null) {
                    const connectedNodes = getConnectedNodes(this, i);
                    if (connectedNodes.length > 0) {
                        input.name = connectedNodes[0].title || ("Input " + (i + 1));
                    }
                } else {
                    input.name = "";
                }
            }
            if (this.inputs.length > 0) {
                this.inputs[this.inputs.length - 1].name = "";
            }
            this.size = this.computeSize();
        };

        // 获取除末尾空槽外的所有已连接节点
        nodeType.prototype.getAllConnectedNodes = function () {
            const allNodes = [];
            if (!this.inputs) return allNodes;
            for (let i = 0; i < this.inputs.length - 1; i++) {
                allNodes.push(...getConnectedNodes(this, i));
            }
            return allNodes;
        };

        // 防抖调度稳定化（合并短时间内的多次连接变化）
        nodeType.prototype.scheduleStabilize = function (ms) {
            if (ms === undefined) ms = 100;
            if (!this._schedulePromise) {
                this._schedulePromise = new Promise((resolve) => {
                    setTimeout(() => {
                        this._schedulePromise = null;
                        this.stabilizeInputs();
                        this.syncMasterToggle();
                        if (this.graph) {
                            this.graph.setDirtyCanvas(true, true);
                        }
                        resolve();
                    }, ms);
                });
            }
            return this._schedulePromise;
        };

        nodeType.prototype.onConnectionsChange = function () {
            this.scheduleStabilize(100);
        };

        applyWidthPreservation(nodeType);

        bindTitleSync(
            nodeType,
            function () { return this.masterToggle; },
            t("node_bypasser")
        );
    }
});
