import { app } from "../../scripts/app.js";
import {
    getAllGroups,
    getNodesInGroup,
    setGroupMode,
    clearPythonDefinedContent,
    bindTitleSync
} from "./bypasser_common.js";

import { t } from "./i18n.js";
app.registerExtension({
    name: "BenNodes.GroupBypasser",

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "GroupBypasserBen") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

            // 清除所有 Python 定义的内容
            clearPythonDefinedContent(this);

            // 初始化状态
            this.modeOn = 0;
            this.modeOff = 4;
            this.groupComboWidget = null;
            this.groupToggleWidget = null;
            this.selectedGroupName = "";

            // 添加组选择下拉框与开关
            this.addGroupComboWidget();
            this.addGroupToggleWidget();

            // 监听图变化以更新组列表
            this.setupGraphMonitoring();

            // 初始应用组模式
            setTimeout(() => {
                if (this.selectedGroupName) {
                    this.applyGroupMode();
                }
            }, 100);

            return r;
        };

        // 添加组选择下拉框
        nodeType.prototype.addGroupComboWidget = function () {
            const graph = this.graph || app.graph;
            const groupNames = getAllGroups(graph).map(g => g.title);

            this.groupComboWidget = this.addWidget(
                "combo",
                t("select_group"),
                groupNames.length > 0 ? groupNames[0] : "",
                (value) => {
                    this.selectedGroupName = value;
                    // 选择组后，根据当前开关状态应用
                    if (this.groupToggleWidget) {
                        this.applyGroupMode();
                    }
                },
                { values: groupNames.length > 0 ? groupNames : [""] }
            );

            if (groupNames.length > 0) {
                this.selectedGroupName = groupNames[0];
            }

            return this.groupComboWidget;
        };

        // 添加开关控件
        nodeType.prototype.addGroupToggleWidget = function () {
            const toggleName = this.title || t("group_bypasser");
            this.groupToggleWidget = this.addWidget(
                "toggle",
                toggleName,
                true,
                () => {
                    this.applyGroupMode();
                },
                { on: "yes", off: "no" }
            );

            return this.groupToggleWidget;
        };

        // 按当前选中组与开关状态应用模式
        nodeType.prototype.applyGroupMode = function () {
            if (!this.selectedGroupName || !this.groupToggleWidget) {
                return;
            }

            const graph = this.graph || app.graph;
            const targetGroup = getAllGroups(graph).find(g => g.title === this.selectedGroupName);
            if (!targetGroup) {
                return;
            }

            // value 是 boolean 类型：true = 激活，false = 忽略
            const targetMode = this.groupToggleWidget.value ? this.modeOn : this.modeOff;
            setGroupMode(graph, targetGroup, targetMode);

            // 强制更新画布
            if (graph) {
                graph.setDirtyCanvas(true, true);
            }
        };

        // 更新组下拉框选项（保留当前选择）
        nodeType.prototype.updateGroupList = function () {
            if (!this.groupComboWidget) return;

            const graph = this.graph || app.graph;
            const groupNames = getAllGroups(graph).map(g => g.title);

            const currentValue = this.groupComboWidget.value;
            this.groupComboWidget.options.values = groupNames.length > 0 ? groupNames : [""];

            // 当前选择的组还存在则保持；否则选择第一个
            if (groupNames.includes(currentValue)) {
                this.groupComboWidget.value = currentValue;
                this.selectedGroupName = currentValue;
            } else if (groupNames.length > 0) {
                this.groupComboWidget.value = groupNames[0];
                this.selectedGroupName = groupNames[0];
            } else {
                this.groupComboWidget.value = "";
                this.selectedGroupName = "";
            }

            if (graph) {
                graph.setDirtyCanvas(true, false);
            }
        };

        // 定期检查组列表变化
        nodeType.prototype.setupGraphMonitoring = function () {
            this._groupCheckInterval = setInterval(() => {
                if (this.groupComboWidget) {
                    const graph = this.graph || app.graph;
                    const currentGroupNames = getAllGroups(graph).map(g => g.title).sort().join(',');
                    const widgetGroupNames = (this.groupComboWidget.options.values || []).sort().join(',');

                    if (currentGroupNames !== widgetGroupNames) {
                        this.updateGroupList();
                    }
                }
            }, 1000);
        };

        // 清理定时器
        const origOnRemoved = nodeType.prototype.onRemoved;
        nodeType.prototype.onRemoved = function () {
            if (this._groupCheckInterval) {
                clearInterval(this._groupCheckInterval);
                this._groupCheckInterval = null;
            }
            if (origOnRemoved) {
                origOnRemoved.call(this);
            }
        };

        bindTitleSync(
            nodeType,
            function () { return this.groupToggleWidget; },
            t("group_bypasser")
        );

        // 序列化/反序列化选中的组名
        const origSerialize = nodeType.prototype.serialize;
        nodeType.prototype.serialize = function () {
            const data = origSerialize ? origSerialize.call(this) : {};
            data.selectedGroupName = this.selectedGroupName;
            return data;
        };

        const origConfigure = nodeType.prototype.configure;
        nodeType.prototype.configure = function (data) {
            if (origConfigure) {
                origConfigure.call(this, data);
            }
            if (data.selectedGroupName) {
                this.selectedGroupName = data.selectedGroupName;
                if (this.groupComboWidget) {
                    this.groupComboWidget.value = data.selectedGroupName;
                }
            }
        };
    }
});
