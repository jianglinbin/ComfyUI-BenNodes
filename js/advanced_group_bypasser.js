import { app } from "../../scripts/app.js";

// 获取图中所有组
function getAllGroups(graph) {
    if (!graph || !graph._groups) return [];
    return graph._groups || [];
}

// 获取组内的所有节点
function getNodesInGroup(graph, group) {
    if (!graph || !group) return [];
    
    const nodesInGroup = [];
    const allNodes = graph._nodes || [];
    
    for (const node of allNodes) {
        if (!node) continue;
        
        // 检查节点是否在组的边界内
        const nodeX = node.pos[0];
        const nodeY = node.pos[1];
        const nodeWidth = node.size[0];
        const nodeHeight = node.size[1];
        
        const groupX = group._pos[0];
        const groupY = group._pos[1];
        const groupWidth = group._size[0];
        const groupHeight = group._size[1];
        
        // 节点中心点在组内
        const nodeCenterX = nodeX + nodeWidth / 2;
        const nodeCenterY = nodeY + nodeHeight / 2;
        
        if (nodeCenterX >= groupX && nodeCenterX <= groupX + groupWidth &&
            nodeCenterY >= groupY && nodeCenterY <= groupY + groupHeight) {
            nodesInGroup.push(node);
        }
    }
    
    return nodesInGroup;
}

// 设置组的模式(激活/禁用组内所有节点)
function setGroupMode(graph, group, mode) {
    if (!graph || !group) {
        console.log(`[AdvancedGroupBypasser] setGroupMode: Invalid graph or group`);
        return;
    }
    
    console.log(`[AdvancedGroupBypasser] Setting group "${group.title}" to mode ${mode}`);
    
    const nodesInGroup = getNodesInGroup(graph, group);
    console.log(`[AdvancedGroupBypasser] Group has ${nodesInGroup.length} nodes`);
    
    for (const node of nodesInGroup) {
        if (node) {
            node.mode = mode;
        }
    }
}

app.registerExtension({
    name: "BenNodes.AdvancedGroupBypasser",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "AdvancedGroupBypasserBen") return;
        
        console.log("[AdvancedGroupBypasser] beforeRegisterNodeDef called");
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            
            console.log("[AdvancedGroupBypasser] onNodeCreated");
            
            // 初始化状态
            this.modeOn = 0;
            this.modeOff = 4;
            this.jsonRulesWidget = null;
            this.ruleComboWidget = null;
            this.refreshButton = null;
            this.rulesData = {};
            
            // 查找Python定义的json_rules widget
            if (this.widgets) {
                for (let widget of this.widgets) {
                    if (widget.name === "json_rules") {
                        this.jsonRulesWidget = widget;
                        break;
                    }
                }
            }
            
            // 添加刷新按钮
            this.addRefreshButton();
            
            // 添加规则选择下拉框
            this.addRuleComboWidget();
            
            // 初始解析JSON
            if (this.jsonRulesWidget) {
                this.parseJsonRules();
            }
            
            console.log("[AdvancedGroupBypasser] After setup, widgets:", this.widgets?.length);
            
            return r;
        };
        
        // 添加刷新按钮
        nodeType.prototype.addRefreshButton = function() {
            this.refreshButton = this.addWidget(
                "button",
                "🔄 刷新规则",
                null,
                () => {
                    console.log("[AdvancedGroupBypasser] 🔄 Refresh button clicked");
                    console.log("[AdvancedGroupBypasser] Current JSON:", this.jsonRulesWidget?.value);
                    
                    if (this.parseJsonRules()) {
                        console.log("[AdvancedGroupBypasser] ✓ Rules refreshed successfully");
                    }
                }
            );
            
            return this.refreshButton;
        };
        
        // 添加规则选择下拉框
        nodeType.prototype.addRuleComboWidget = function() {
            const comboName = this.title || "忽略组";
            this.ruleComboWidget = this.addWidget(
                "combo",
                comboName,
                "",
                (value) => {
                    console.log("[AdvancedGroupBypasser] Rule selected:", value);
                    this.applyRule(value);
                },
                {
                    values: [""]
                }
            );
            
            return this.ruleComboWidget;
        };
        
        // 重新创建规则选择下拉框
        nodeType.prototype.recreateRuleComboWidget = function(ruleNames) {
            const currentValue = this.ruleComboWidget ? this.ruleComboWidget.value : "";
            
            if (this.ruleComboWidget && this.widgets) {
                const index = this.widgets.indexOf(this.ruleComboWidget);
                if (index !== -1) {
                    this.widgets.splice(index, 1);
                }
            }
            
            const comboName = this.title || "忽略组";
            const defaultValue = ruleNames.length > 0 ? ruleNames[0] : "";
            
            this.ruleComboWidget = this.addWidget(
                "combo",
                comboName,
                defaultValue,
                (value) => {
                    console.log("[AdvancedGroupBypasser] Rule selected:", value);
                    this.applyRule(value);
                },
                {
                    values: ruleNames.length > 0 ? ruleNames : [""]
                }
            );
            
            if (ruleNames.includes(currentValue)) {
                this.ruleComboWidget.value = currentValue;
            } else if (ruleNames.length > 0) {
                this.ruleComboWidget.value = ruleNames[0];
                setTimeout(() => {
                    this.applyRule(ruleNames[0]);
                }, 50);
            }
            
            this.size = this.computeSize();
            
            return this.ruleComboWidget;
        };
        
        // 解析JSON规则
        nodeType.prototype.parseJsonRules = function() {
            if (!this.jsonRulesWidget) return false;
            
            const jsonText = this.jsonRulesWidget.value;
            
            try {
                const parsed = JSON.parse(jsonText);
                
                if (typeof parsed !== 'object' || parsed === null) {
                    throw new Error("JSON必须是对象格式");
                }
                
                // 验证规则格式：值必须是字符串数组（组名称）
                for (const key in parsed) {
                    if (!Array.isArray(parsed[key])) {
                        throw new Error(`规则"${key}"的值必须是数组`);
                    }
                    for (const val of parsed[key]) {
                        if (typeof val !== 'string') {
                            throw new Error(`规则"${key}"中包含非字符串值: ${val}`);
                        }
                    }
                }
                
                this.rulesData = parsed;
                
                const ruleNames = Object.keys(parsed);
                
                if (this.ruleComboWidget) {
                    this.recreateRuleComboWidget(ruleNames);
                    
                    if (this.graph) {
                        this.graph.setDirtyCanvas(true, true);
                    }
                }
                
                return true;
            } catch (e) {
                console.error("[AdvancedGroupBypasser] JSON parse error:", e.message);
                alert(`JSON解析错误: ${e.message}`);
                return false;
            }
        };
        
        // 应用规则 - 遍历所有组并按名称匹配
        nodeType.prototype.applyRule = function(ruleName) {
            if (!ruleName || !this.rulesData[ruleName]) {
                console.log("[AdvancedGroupBypasser] No valid rule selected");
                return;
            }
            
            const activeGroupNames = this.rulesData[ruleName];
            console.log("[AdvancedGroupBypasser] Applying rule:", ruleName, "Active group names:", activeGroupNames);
            
            // 获取图中所有组
            const graph = this.graph || app.graph;
            const allGroups = getAllGroups(graph);
            
            console.log("[AdvancedGroupBypasser] Total groups in graph:", allGroups.length);
            console.log("[AdvancedGroupBypasser] Group names:", allGroups.map(g => g.title));
            
            // 遍历所有组，根据名称匹配激活/禁用
            for (const group of allGroups) {
                const shouldActivate = activeGroupNames.includes(group.title);
                const targetMode = shouldActivate ? this.modeOn : this.modeOff;
                
                console.log(`[AdvancedGroupBypasser] Group "${group.title}": ${shouldActivate ? 'ACTIVATE' : 'DISABLE'}`);
                setGroupMode(graph, group, targetMode);
            }
            
            // 强制更新画布
            if (graph) {
                graph.setDirtyCanvas(true, true);
            }
        };
        
        // 监听标题变化
        const origOnPropertyChanged = nodeType.prototype.onPropertyChanged;
        nodeType.prototype.onPropertyChanged = function(name, value) {
            if (origOnPropertyChanged) {
                origOnPropertyChanged.call(this, name, value);
            }
            if ((name === "title" || name === "Node name for S&R") && this.ruleComboWidget) {
                const ruleNames = Object.keys(this.rulesData || {});
                if (ruleNames.length > 0) {
                    this.recreateRuleComboWidget(ruleNames);
                } else {
                    this.ruleComboWidget.name = this.title || "忽略组";
                }
                if (this.graph) {
                    this.graph.setDirtyCanvas(true, false);
                }
            }
        };
        
        // 在每次绘制时更新控件名称
        const origOnDrawForeground = nodeType.prototype.onDrawForeground;
        nodeType.prototype.onDrawForeground = function(ctx) {
            if (origOnDrawForeground) {
                origOnDrawForeground.call(this, ctx);
            }
            if (this.ruleComboWidget && this.ruleComboWidget.name !== this.title) {
                this.ruleComboWidget.name = this.title || "忽略组";
            }
        };
        
        // 序列化
        const origSerialize = nodeType.prototype.serialize;
        nodeType.prototype.serialize = function() {
            const data = origSerialize ? origSerialize.call(this) : {};
            data.rulesData = this.rulesData;
            return data;
        };
        
        // 反序列化
        const origConfigure = nodeType.prototype.configure;
        nodeType.prototype.configure = function(data) {
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
});

console.log("[AdvancedGroupBypasser] Extension loaded");
