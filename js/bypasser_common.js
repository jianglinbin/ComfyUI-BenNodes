// bypasser 系列节点共享逻辑
// 供 node_bypasser.js / group_bypasser.js / advanced_node_bypasser.js / advanced_group_bypasser.js 复用

import { app } from "../../scripts/app.js";

// ===== 连接遍历 =====

/**
 * 判断是否为直通节点（Reroute / PrimitiveNode）
 */
import { t } from "./i18n.js";
export function isPassthroughNode(node) {
    if (!node) return false;
    const type = node.type || node.constructor?.type || "";
    return type.includes("Reroute") || type.includes("PrimitiveNode");
}

/**
 * 获取指定输入槽连接的源节点（跳过直通节点）
 */
export function getConnectedNodes(node, inputIndex) {
    const input = node.inputs[inputIndex];
    if (!input || !input.link) return [];

    // 使用节点自己的 graph，如果不存在则使用 app.graph
    const graph = node.graph || app.graph;
    const link = graph.links[input.link];
    if (!link) return [];

    let sourceNode = graph.getNodeById(link.origin_id);
    if (!sourceNode) return [];

    const visited = new Set();
    while (isPassthroughNode(sourceNode) && !visited.has(sourceNode.id)) {
        visited.add(sourceNode.id);
        const sourceInput = sourceNode.inputs?.[0];
        if (!sourceInput || !sourceInput.link) break;

        const sourceGraph = sourceNode.graph || graph;
        const sourceLink = sourceGraph.links[sourceInput.link];
        if (!sourceLink) break;

        const nextNode = sourceGraph.getNodeById(sourceLink.origin_id);
        if (!nextNode) break;
        sourceNode = nextNode;
    }
    return [sourceNode];
}

/**
 * 批量设置节点模式（含子图内节点，按 id 去重）
 */
export function setNodesMode(nodes, mode) {
    const stack = [...nodes];
    const visited = new Set();
    while (stack.length > 0) {
        const node = stack.pop();
        if (!node || visited.has(node.id)) continue;
        visited.add(node.id);
        node.mode = mode;
        if (node.subgraph && node.subgraph._nodes) {
            stack.push(...node.subgraph._nodes);
        }
    }
}

// ===== 组操作 =====

/**
 * 获取图中所有组
 */
export function getAllGroups(graph) {
    if (!graph || !graph._groups) return [];
    return graph._groups || [];
}

/**
 * 获取组内的所有节点（节点中心点在组边界内）
 */
export function getNodesInGroup(graph, group) {
    if (!graph || !group) return [];

    const nodesInGroup = [];
    const allNodes = graph._nodes || [];

    for (const node of allNodes) {
        if (!node) continue;

        const nodeCenterX = node.pos[0] + node.size[0] / 2;
        const nodeCenterY = node.pos[1] + node.size[1] / 2;

        const groupX = group._pos[0];
        const groupY = group._pos[1];

        if (nodeCenterX >= groupX && nodeCenterX <= groupX + group._size[0] &&
            nodeCenterY >= groupY && nodeCenterY <= groupY + group._size[1]) {
            nodesInGroup.push(node);
        }
    }

    return nodesInGroup;
}

/**
 * 设置组内所有节点的模式（激活/禁用）
 */
export function setGroupMode(graph, group, mode) {
    if (!graph || !group) return;
    for (const node of getNodesInGroup(graph, group)) {
        node.mode = mode;
    }
}

// ===== 节点通用辅助 =====

/**
 * 清除 Python 端定义的 widgets / inputs / outputs（前端完全接管）
 */
export function clearPythonDefinedContent(node) {
    if (node.widgets) {
        while (node.widgets.length > 0) {
            node.widgets.pop();
        }
    }
    if (node.inputs) {
        while (node.inputs.length > 0) {
            node.removeInput(0);
        }
    }
    if (node.outputs) {
        while (node.outputs.length > 0) {
            node.removeOutput(0);
        }
    }
}

/**
 * 保持节点宽度：包装 addInput/removeInput 与 computeSize，
 * 在输入槽增删时防止宽度抖动（32ms 防抖恢复）
 */
export function applyWidthPreservation(nodeType) {
    const origAddInput = nodeType.prototype.addInput;
    nodeType.prototype.addInput = function (name, type, extra_info) {
        this._tempWidth = this.size[0];
        return origAddInput.call(this, name, type, extra_info);
    };

    const origRemoveInput = nodeType.prototype.removeInput;
    nodeType.prototype.removeInput = function (slot) {
        this._tempWidth = this.size[0];
        return origRemoveInput.call(this, slot);
    };

    const origComputeSize = nodeType.prototype.computeSize;
    nodeType.prototype.computeSize = function (out) {
        const size = origComputeSize.call(this, out);
        if (this._tempWidth) {
            size[0] = this._tempWidth;
            clearTimeout(this._debouncerTempWidth);
            this._debouncerTempWidth = setTimeout(() => {
                this._tempWidth = null;
            }, 32);
        }
        return size;
    };
}

/**
 * 按名称查找 widget
 */
export function findWidgetByName(node, name) {
    return node.widgets?.find(w => w.name === name) || null;
}

/**
 * 绑定标题同步：标题变化与每次绘制时，将指定 widget 的名称同步为节点标题
 * @param {Object} nodeType - 节点类型原型
 * @param {Function} getWidgetFn - (node) => widget
 * @param {string} fallbackName - 标题为空时的回退名称
 * @param {Function} [onTitleChanged] - (node) => void，标题变化时的额外处理
 */
export function bindTitleSync(nodeType, getWidgetFn, fallbackName, onTitleChanged) {
    const origOnPropertyChanged = nodeType.prototype.onPropertyChanged;
    nodeType.prototype.onPropertyChanged = function (name, value) {
        if (origOnPropertyChanged) {
            origOnPropertyChanged.call(this, name, value);
        }
        if (name === "title" || name === "Node name for S&R") {
            if (onTitleChanged) onTitleChanged.call(this);
            const w = getWidgetFn.call(this);
            if (w && w.name !== this.title) {
                w.name = this.title || fallbackName;
                if (this.graph) {
                    this.graph.setDirtyCanvas(true, false);
                }
            }
        }
    };

    const origOnDrawForeground = nodeType.prototype.onDrawForeground;
    nodeType.prototype.onDrawForeground = function (ctx) {
        if (origOnDrawForeground) {
            origOnDrawForeground.call(this, ctx);
        }
        const w = getWidgetFn.call(this);
        if (w && w.name !== this.title) {
            w.name = this.title || fallbackName;
        }
    };
}

/**
 * 绑定 rulesData 的序列化/反序列化（advanced 系列）
 */
export function bindRulesSerialization(nodeType) {
    const origSerialize = nodeType.prototype.serialize;
    nodeType.prototype.serialize = function () {
        const data = origSerialize ? origSerialize.call(this) : {};
        data.rulesData = this.rulesData;
        return data;
    };

    const origConfigure = nodeType.prototype.configure;
    nodeType.prototype.configure = function (data) {
        if (origConfigure) {
            origConfigure.call(this, data);
        }
        if (data.rulesData) {
            this.rulesData = data.rulesData;
            const ruleNames = Object.keys(this.rulesData);
            if (this.ruleComboWidget) {
                this.ruleComboWidget.options.values = ruleNames.length > 0 ? ruleNames : [""];
            }
        }
    };
}

// ===== JSON 规则（advanced 系列） =====

/**
 * 解析并校验规则 JSON
 * @param {string} jsonText - JSON 文本
 * @param {string} valueType - 期望的数组元素类型："number"（整数）或 "string"
 * @returns {{ok: boolean, rules?: Object, error?: string}}
 */
export function parseRulesJson(jsonText, valueType) {
    let parsed;
    try {
        parsed = JSON.parse(jsonText);
    } catch (e) {
        return { ok: false, error: e.message };
    }

    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
        return { ok: false, error: t("json_must_be_object") };
    }

    for (const key in parsed) {
        if (!Array.isArray(parsed[key])) {
            return { ok: false, error: t("rule_value_must_be_array", key) };
        }
        for (const val of parsed[key]) {
            if (valueType === "number") {
                if (typeof val !== "number" || !Number.isInteger(val)) {
                    return { ok: false, error: t("rule_non_integer", key, val) };
                }
            } else if (typeof val !== "string") {
                return { ok: false, error: t("rule_non_string", key, val) };
            }
        }
    }

    return { ok: true, rules: parsed };
}

/**
 * 重建规则选择下拉框（保留原选中值；否则选第一个规则并自动应用）
 * @param {Object} node - 节点实例
 * @param {string[]} ruleNames - 规则名列表
 * @param {string} fallbackName - 下拉框默认名称
 * @param {Function} onSelect - (ruleName) => void 选中回调
 */
export function recreateRuleCombo(node, ruleNames, fallbackName, onSelect) {
    const currentValue = node.ruleComboWidget ? node.ruleComboWidget.value : "";

    // 删除旧的 COMBO widget
    if (node.ruleComboWidget && node.widgets) {
        const index = node.widgets.indexOf(node.ruleComboWidget);
        if (index !== -1) {
            node.widgets.splice(index, 1);
        }
    }

    // 创建新的 COMBO widget
    const comboName = node.title || fallbackName;
    const defaultValue = ruleNames.length > 0 ? ruleNames[0] : "";
    node.ruleComboWidget = node.addWidget(
        "combo",
        comboName,
        defaultValue,
        onSelect,
        { values: ruleNames.length > 0 ? ruleNames : [""] }
    );

    // 恢复之前的选中值；否则选择第一个并自动应用
    if (ruleNames.includes(currentValue)) {
        node.ruleComboWidget.value = currentValue;
    } else if (ruleNames.length > 0) {
        node.ruleComboWidget.value = ruleNames[0];
        setTimeout(() => onSelect(ruleNames[0]), 50);
    }

    node.size = node.computeSize();
    return node.ruleComboWidget;
}
