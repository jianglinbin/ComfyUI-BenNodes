import { app } from "../../scripts/app.js";

function isPassthroughNode(node) {
    if (!node) return false;
    const type = node.type || node.constructor?.type || "";
    return type.includes("Reroute") || type.includes("PrimitiveNode");
}

function getConnectedNodes(node, inputIndex) {
    const input = node.inputs[inputIndex];
    if (!input || !input.link) return [];
    
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

function setNodesMode(nodes, mode) {
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

app.registerExtension({
    name: "BenNodes.AdvancedNodeBypasser",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "AdvancedNodeBypasserBen") return;
        
        console.log("[AdvancedInputBypasser] beforeRegisterNodeDef called");
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            
            console.log("[AdvancedInputBypasser] onNodeCreated");
            
            // 初始化状态
            this.modeOn = 0;
            this.modeOff = 4;
            this._tempWidth = null;
            this._debouncerTempWidth = null;
            this._schedulePromise = null;
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
            
            // 添加输入输出
            this.addInput("", "*");
            
            // 添加刷新按钮
            this.addRefreshButton();
            
            // 添加规则选择下拉框
            this.addRuleComboWidget();
            
            // 初始解析JSON
            if (this.jsonRulesWidget) {
                this.parseJsonRules();
            }
            
            console.log("[AdvancedInputBypasser] After setup, inputs:", this.inputs?.length, "outputs:", this.outputs?.length, "widgets:", this.widgets?.length);
            
            setTimeout(() => {
                if (this.scheduleStabilize) {
                    this.scheduleStabilize(1);
                }
            }, 100);
            
            return r;
        };
        
        // 添加刷新按钮
        nodeType.prototype.addRefreshButton = function() {
            this.refreshButton = this.addWidget(
                "button",
                "🔄 刷新规则",
                null,
                () => {
                    console.log("[AdvancedInputBypasser] 🔄 Refresh button clicked");
                    console.log("[AdvancedInputBypasser] Current JSON:", this.jsonRulesWidget?.value);
                    
                    if (this.parseJsonRules()) {
                        console.log("[AdvancedInputBypasser] ✓ Rules refreshed successfully");
                    }
                }
            );
            
            return this.refreshButton;
        };
        
        // 添加规则选择下拉框
        nodeType.prototype.addRuleComboWidget = function() {
            const comboName = this.title || "忽略节点";
            this.ruleComboWidget = this.addWidget(
                "combo",
                comboName,
                "",
                (value) => {
                    console.log("[AdvancedInputBypasser] Rule selected:", value);
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
            console.log("[AdvancedInputBypasser] recreateRuleComboWidget called with:", ruleNames);
            
            // 保存当前选中的值
            const currentValue = this.ruleComboWidget ? this.ruleComboWidget.value : "";
            console.log("[AdvancedInputBypasser] Current COMBO value:", currentValue);
            
            // 删除旧的COMBO widget
            if (this.ruleComboWidget && this.widgets) {
                const index = this.widgets.indexOf(this.ruleComboWidget);
                console.log("[AdvancedInputBypasser] Old COMBO widget index:", index);
                if (index !== -1) {
                    this.widgets.splice(index, 1);
                    console.log("[AdvancedInputBypasser] Old COMBO widget removed");
                }
            }
            
            // 创建新的COMBO widget
            const comboName = this.title || "忽略节点";
            const defaultValue = ruleNames.length > 0 ? ruleNames[0] : "";
            
            console.log("[AdvancedInputBypasser] Creating new COMBO:", {
                name: comboName,
                defaultValue: defaultValue,
                values: ruleNames
            });
            
            this.ruleComboWidget = this.addWidget(
                "combo",
                comboName,
                defaultValue,  // 使用第一个规则作为默认值
                (value) => {
                    console.log("[AdvancedInputBypasser] Rule selected:", value);
                    this.applyRule(value);
                },
                {
                    values: ruleNames.length > 0 ? ruleNames : [""]
                }
            );
            
            console.log("[AdvancedInputBypasser] New COMBO widget created:", {
                name: this.ruleComboWidget.name,
                value: this.ruleComboWidget.value,
                options: this.ruleComboWidget.options
            });
            
            // 恢复之前的选中值(如果还存在)
            if (ruleNames.includes(currentValue)) {
                this.ruleComboWidget.value = currentValue;
                console.log("[AdvancedInputBypasser] Restored previous value:", currentValue);
            } else if (ruleNames.length > 0) {
                // 如果之前的值不存在,选择第一个并应用
                this.ruleComboWidget.value = ruleNames[0];
                console.log("[AdvancedInputBypasser] Set to first rule:", ruleNames[0]);
                // 自动应用第一个规则
                setTimeout(() => {
                    console.log("[AdvancedInputBypasser] Auto-applying first rule...");
                    this.applyRule(ruleNames[0]);
                }, 50);
            }
            
            // 重新计算节点大小
            this.size = this.computeSize();
            console.log("[AdvancedInputBypasser] Node size recomputed:", this.size);
            
            console.log("[AdvancedInputBypasser] ✓ COMBO recreated successfully");
            console.log("[AdvancedInputBypasser] Final COMBO state:", {
                name: this.ruleComboWidget.name,
                value: this.ruleComboWidget.value,
                values: this.ruleComboWidget.options.values
            });
            
            return this.ruleComboWidget;
        };
        
        // 解析JSON规则
        nodeType.prototype.parseJsonRules = function() {
            console.log("[AdvancedInputBypasser] parseJsonRules called");
            
            if (!this.jsonRulesWidget) {
                console.log("[AdvancedInputBypasser] ✗ No jsonRulesWidget found");
                return false;
            }
            
            const jsonText = this.jsonRulesWidget.value;
            console.log("[AdvancedInputBypasser] JSON text to parse:", jsonText);
            
            try {
                const parsed = JSON.parse(jsonText);
                console.log("[AdvancedInputBypasser] JSON parsed successfully:", parsed);
                
                // 验证格式
                if (typeof parsed !== 'object' || parsed === null) {
                    throw new Error("JSON必须是对象格式");
                }
                
                for (const key in parsed) {
                    if (!Array.isArray(parsed[key])) {
                        throw new Error(`规则"${key}"的值必须是数组`);
                    }
                    // 验证数组中的值都是数字
                    for (const val of parsed[key]) {
                        if (typeof val !== 'number' || !Number.isInteger(val)) {
                            throw new Error(`规则"${key}"中包含非整数值: ${val}`);
                        }
                    }
                }
                
                this.rulesData = parsed;
                console.log("[AdvancedInputBypasser] rulesData updated:", this.rulesData);
                
                // 更新COMBO选项 - 使用重新创建的方式
                const ruleNames = Object.keys(parsed);
                console.log("[AdvancedInputBypasser] Rule names extracted:", ruleNames);
                
                if (this.ruleComboWidget) {
                    console.log("[AdvancedInputBypasser] Recreating COMBO widget...");
                    this.recreateRuleComboWidget(ruleNames);
                    
                    // 强制更新画布以刷新COMBO显示
                    if (this.graph) {
                        this.graph.setDirtyCanvas(true, true);
                        console.log("[AdvancedInputBypasser] Canvas marked as dirty");
                    }
                } else {
                    console.log("[AdvancedInputBypasser] ✗ No ruleComboWidget found");
                }
                
                console.log("[AdvancedInputBypasser] ✓ JSON parsed successfully");
                console.log("[AdvancedInputBypasser] Final COMBO values:", this.ruleComboWidget?.options?.values);
                console.log("[AdvancedInputBypasser] Final COMBO current value:", this.ruleComboWidget?.value);
                
                return true;
            } catch (e) {
                console.error("[AdvancedInputBypasser] ✗ JSON parse error:", e.message);
                console.error("[AdvancedInputBypasser] Error stack:", e.stack);
                alert(`JSON解析错误: ${e.message}`);
                return false;
            }
        };
        
        // 应用规则
        nodeType.prototype.applyRule = function(ruleName) {
            if (!ruleName || !this.rulesData[ruleName]) {
                console.log("[AdvancedInputBypasser] No valid rule selected");
                return;
            }
            
            const activeIds = this.rulesData[ruleName];
            console.log("[AdvancedInputBypasser] Applying rule:", ruleName, "Active IDs:", activeIds);
            
            // 获取所有连接的节点及其索引
            const allConnections = [];
            if (this.inputs) {
                for (let i = 0; i < this.inputs.length - 1; i++) {
                    const connectedNodes = getConnectedNodes(this, i);
                    if (connectedNodes.length > 0) {
                        allConnections.push({
                            index: i + 1, // 输入索引从1开始计数
                            nodes: connectedNodes
                        });
                    }
                }
            }
            
            console.log("[AdvancedInputBypasser] All connections:", allConnections.map(c => ({
                index: c.index,
                nodes: c.nodes.map(n => n.title)
            })));
            
            // 根据规则激活/禁用节点
            for (const conn of allConnections) {
                const shouldActivate = activeIds.includes(conn.index);
                const targetMode = shouldActivate ? this.modeOn : this.modeOff;
                
                console.log(`[AdvancedInputBypasser] Input ${conn.index}: ${shouldActivate ? 'ACTIVATE' : 'DISABLE'} (mode: ${targetMode})`);
                
                setNodesMode(conn.nodes, targetMode);
            }
            
            // 强制更新画布
            if (this.graph) {
                this.graph.setDirtyCanvas(true, true);
            }
        };
        
        // 稳定输入
        nodeType.prototype.stabilizeInputs = function() {
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
        
        nodeType.prototype.scheduleStabilize = function(ms) {
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
        
        nodeType.prototype.onConnectionsChange = function() {
            this.scheduleStabilize(100);
        };
        
        const origAddInput = nodeType.prototype.addInput;
        nodeType.prototype.addInput = function(name, type, extra_info) {
            this._tempWidth = this.size[0];
            return origAddInput.call(this, name, type, extra_info);
        };
        
        const origRemoveInput = nodeType.prototype.removeInput;
        nodeType.prototype.removeInput = function(slot) {
            this._tempWidth = this.size[0];
            return origRemoveInput.call(this, slot);
        };
        
        const origComputeSize = nodeType.prototype.computeSize;
        nodeType.prototype.computeSize = function(out) {
            let size = origComputeSize.call(this, out);
            if (this._tempWidth) {
                size[0] = this._tempWidth;
                clearTimeout(this._debouncerTempWidth);
                this._debouncerTempWidth = setTimeout(() => {
                    this._tempWidth = null;
                }, 32);
            }
            return size;
        };
        
        // 监听widget值变化后的处理
        const origOnWidgetChanged = nodeType.prototype.onWidgetChanged;
        nodeType.prototype.onWidgetChanged = function(name, value, old_value, widget) {
            if (origOnWidgetChanged) {
                origOnWidgetChanged.call(this, name, value, old_value, widget);
            }
        };
        
        // 重写 onMouseDown (保留用于调试)
        const origOnMouseDown = nodeType.prototype.onMouseDown;
        nodeType.prototype.onMouseDown = function(e, localPos, graphCanvas) {
            console.log("[AdvancedInputBypasser] onMouseDown triggered, localPos:", localPos);
            const result = origOnMouseDown ? origOnMouseDown.call(this, e, localPos, graphCanvas) : undefined;
            return result;
        };
        
        // 触发JSON解析的统一方法
        nodeType.prototype.triggerJsonParse = function() {
            if (this.parseJsonRules()) {
                if (this.ruleComboWidget && this.ruleComboWidget.value) {
                    this.applyRule(this.ruleComboWidget.value);
                }
            }
        };
        
        // 监听节点失去焦点
        const origOnDeselected = nodeType.prototype.onDeselected;
        nodeType.prototype.onDeselected = function() {
            if (origOnDeselected) {
                origOnDeselected.call(this);
            }
        };
        
        // 监听鼠标离开节点
        const origOnMouseLeave = nodeType.prototype.onMouseLeave;
        nodeType.prototype.onMouseLeave = function(e) {
            if (origOnMouseLeave) {
                origOnMouseLeave.call(this, e);
            }
        };
        
        // 监听键盘输入
        const origOnKeyDown = nodeType.prototype.onKeyDown;
        nodeType.prototype.onKeyDown = function(e) {
            if (origOnKeyDown) {
                return origOnKeyDown.call(this, e);
            }
        };
        
        // 监听标题变化
        const origOnPropertyChanged = nodeType.prototype.onPropertyChanged;
        nodeType.prototype.onPropertyChanged = function(name, value) {
            if (origOnPropertyChanged) {
                origOnPropertyChanged.call(this, name, value);
            }
            if ((name === "title" || name === "Node name for S&R") && this.ruleComboWidget) {
                // 重新创建COMBO以更新标题
                const ruleNames = Object.keys(this.rulesData || {});
                if (ruleNames.length > 0) {
                    this.recreateRuleComboWidget(ruleNames);
                } else {
                    // 如果没有规则,只更新名称
                    this.ruleComboWidget.name = this.title || "忽略节点";
                }
                // 强制重绘
                if (this.graph) {
                    this.graph.setDirtyCanvas(true, false);
                }
            }
        };
        
        // 在每次绘制时更新控件名称
        const origOnDrawForeground2 = nodeType.prototype.onDrawForeground;
        nodeType.prototype.onDrawForeground = function(ctx) {
            if (origOnDrawForeground2) {
                origOnDrawForeground2.call(this, ctx);
            }
            if (this.ruleComboWidget && this.ruleComboWidget.name !== this.title) {
                this.ruleComboWidget.name = this.title || "忽略节点";
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
                // 更新COMBO选项
                const ruleNames = Object.keys(this.rulesData);
                if (this.ruleComboWidget) {
                    this.ruleComboWidget.options.values = ruleNames.length > 0 ? ruleNames : [""];
                }
            }
        };
    }
});

console.log("[AdvancedInputBypasser] Extension loaded");
