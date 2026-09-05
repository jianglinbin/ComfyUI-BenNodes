import { app } from "../../scripts/app.js";
import {
    getConnectedNodes,
    setNodesMode,
    applyWidthPreservation,
    findWidgetByName,
    bindTitleSync,
    bindRulesSerialization,
    parseRulesJson,
    recreateRuleCombo
} from "./bypasser_common.js";

import { t } from "./i18n.js";
app.registerExtension({
    name: "BenNodes.AdvancedNodeBypasser",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "AdvancedNodeBypasserBen") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

            // 初始化状态
            this.modeOn = 0;
            this.modeOff = 4;
            this.jsonRulesWidget = null;
            this.ruleComboWidget = null;
            this.refreshButton = null;
            this.rulesData = {};

            // 查找 Python 定义的 json_rules widget
            this.jsonRulesWidget = findWidgetByName(this, "json_rules");

            // 添加输入与控件
            this.addInput("", "*");
            this.addRefreshButton();
            this.addRuleComboWidget();

            // 初始解析 JSON
            if (this.jsonRulesWidget) {
                this.parseJsonRules();
            }

            setTimeout(() => {
                if (this.scheduleStabilize) {
                    this.scheduleStabilize(1);
                }
            }, 100);

            return r;
        };

        // 添加刷新按钮
        nodeType.prototype.addRefreshButton = function () {
            this.refreshButton = this.addWidget(
                "button",
                t("refresh_rules"),
                null,
                () => {
                    this.parseJsonRules();
                }
            );

            return this.refreshButton;
        };

        // 添加规则选择下拉框
        nodeType.prototype.addRuleComboWidget = function () {
            const comboName = this.title || t("node_bypasser");
            this.ruleComboWidget = this.addWidget(
                "combo",
                comboName,
                "",
                (value) => {
                    this.applyRule(value);
                },
                { values: [""] }
            );

            return this.ruleComboWidget;
        };

        // 解析 JSON 规则并重建下拉框
        nodeType.prototype.parseJsonRules = function () {
            if (!this.jsonRulesWidget) return false;

            // 规则值为整数数组（输入索引，从 1 开始）
            const result = parseRulesJson(this.jsonRulesWidget.value, "number");
            if (!result.ok) {
                console.error("[AdvancedInputBypasser] JSON parse error:", result.error);
                alert(t("json_parse_error", result.error));
                return false;
            }

            this.rulesData = result.rules;

            if (this.ruleComboWidget) {
                recreateRuleCombo(this, Object.keys(this.rulesData), t("node_bypasser"), (value) => {
                    this.applyRule(value);
                });

                // 强制更新画布以刷新 COMBO 显示
                if (this.graph) {
                    this.graph.setDirtyCanvas(true, true);
                }
            }

            return true;
        };

        // 应用规则：激活规则中列出的输入索引对应的节点，禁用其余
        nodeType.prototype.applyRule = function (ruleName) {
            if (!ruleName || !this.rulesData[ruleName]) {
                return;
            }

            const activeIds = this.rulesData[ruleName];

            // 收集所有已连接输入（索引从 1 开始计数）
            const allConnections = [];
            if (this.inputs) {
                for (let i = 0; i < this.inputs.length - 1; i++) {
                    const connectedNodes = getConnectedNodes(this, i);
                    if (connectedNodes.length > 0) {
                        allConnections.push({
                            index: i + 1,
                            nodes: connectedNodes
                        });
                    }
                }
            }

            // 根据规则激活/禁用节点
            for (const conn of allConnections) {
                const shouldActivate = activeIds.includes(conn.index);
                setNodesMode(conn.nodes, shouldActivate ? this.modeOn : this.modeOff);
            }

            // 强制更新画布
            if (this.graph) {
                this.graph.setDirtyCanvas(true, true);
            }
        };

        // 稳定输入：末尾保留一个空槽，移除空槽，按 `[序号] 节点名` 命名
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
                        input.name = `[${i + 1}] ${connectedNodes[0].title || "Input"}`;
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

        // 防抖调度稳定化（合并短时间内的多次连接变化）
        nodeType.prototype.scheduleStabilize = function (ms) {
            if (ms === undefined) ms = 100;
            if (!this._schedulePromise) {
                this._schedulePromise = new Promise((resolve) => {
                    setTimeout(() => {
                        this._schedulePromise = null;
                        this.stabilizeInputs();
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
            function () { return this.ruleComboWidget; },
            t("node_bypasser"),
            function () {
                // 标题变化时重建 COMBO 以更新名称
                const ruleNames = Object.keys(this.rulesData || {});
                if (ruleNames.length > 0) {
                    recreateRuleCombo(this, ruleNames, t("node_bypasser"), (value) => {
                        this.applyRule(value);
                    });
                }
            }
        );

        // 触发 JSON 解析并应用当前选中的规则
        nodeType.prototype.triggerJsonParse = function () {
            if (this.parseJsonRules() && this.ruleComboWidget?.value) {
                this.applyRule(this.ruleComboWidget.value);
            }
        };

        bindRulesSerialization(nodeType);
    }
});
