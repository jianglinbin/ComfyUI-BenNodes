import { app } from "../../scripts/app.js";
import {
    getAllGroups,
    setGroupMode,
    findWidgetByName,
    bindTitleSync,
    bindRulesSerialization,
    parseRulesJson,
    recreateRuleCombo
} from "./bypasser_common.js";

import { t } from "./i18n.js";
app.registerExtension({
    name: "BenNodes.AdvancedGroupBypasser",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "AdvancedGroupBypasserBen") return;

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

            // 添加控件
            this.addRefreshButton();
            this.addRuleComboWidget();

            // 初始解析 JSON
            if (this.jsonRulesWidget) {
                this.parseJsonRules();
            }

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
            const comboName = this.title || t("group_bypasser");
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

            // 规则值为字符串数组（组名称）
            const result = parseRulesJson(this.jsonRulesWidget.value, "string");
            if (!result.ok) {
                console.error("[AdvancedGroupBypasser] JSON parse error:", result.error);
                alert(t("json_parse_error", result.error));
                return false;
            }

            this.rulesData = result.rules;

            if (this.ruleComboWidget) {
                recreateRuleCombo(this, Object.keys(this.rulesData), t("group_bypasser"), (value) => {
                    this.applyRule(value);
                });

                if (this.graph) {
                    this.graph.setDirtyCanvas(true, true);
                }
            }

            return true;
        };

        // 应用规则：按名称匹配激活规则中列出的组，禁用其余
        nodeType.prototype.applyRule = function (ruleName) {
            if (!ruleName || !this.rulesData[ruleName]) {
                return;
            }

            const activeGroupNames = this.rulesData[ruleName];
            const graph = this.graph || app.graph;

            // 遍历所有组，根据名称匹配激活/禁用
            for (const group of getAllGroups(graph)) {
                const shouldActivate = activeGroupNames.includes(group.title);
                setGroupMode(graph, group, shouldActivate ? this.modeOn : this.modeOff);
            }

            // 强制更新画布
            if (graph) {
                graph.setDirtyCanvas(true, true);
            }
        };

        bindTitleSync(
            nodeType,
            function () { return this.ruleComboWidget; },
            t("group_bypasser"),
            function () {
                // 标题变化时重建 COMBO 以更新名称
                const ruleNames = Object.keys(this.rulesData || {});
                if (ruleNames.length > 0) {
                    recreateRuleCombo(this, ruleNames, t("group_bypasser"), (value) => {
                        this.applyRule(value);
                    });
                }
            }
        );

        bindRulesSerialization(nodeType);
    }
});
