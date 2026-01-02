import { app } from "../../scripts/app.js";

function isPassthroughNode(node) {
    if (!node) return false;
    const type = node.type || node.constructor?.type || "";
    return type.includes("Reroute") || type.includes("PrimitiveNode");
}

function getConnectedNodes(node, inputIndex) {
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
        
        // 同样使用 sourceNode 的 graph
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

// 移除循环检测函数，因为 DynamicInputBypasser 是控制节点，不传递数据流
// 不需要检测循环连接

app.registerExtension({
    name: "BenNodes.DynamicInputBypasser",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "DynamicInputBypasser") return;
        
        console.log("[DynamicInputBypasser] beforeRegisterNodeDef called");
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            
            console.log("[DynamicInputBypasser] onNodeCreated, inputs:", this.inputs?.length, "outputs:", this.outputs?.length, "widgets:", this.widgets?.length);
            
            // 清除所有 Python 定义的内容
            if (this.widgets) {
                while (this.widgets.length > 0) {
                    this.widgets.pop();
                }
            }
            if (this.inputs) {
                while (this.inputs.length > 0) {
                    this.removeInput(0);
                }
            }
            if (this.outputs) {
                while (this.outputs.length > 0) {
                    this.removeOutput(0);
                }
            }
            
            // 初始化状态
            this.modeOn = 0;
            this.modeOff = 4;
            this._tempWidth = null;
            this._debouncerTempWidth = null;
            this._schedulePromise = null;
            this.masterToggle = null;
            
            // 添加输入输出
            this.addInput("", "*");
            this.addOutput("OPT_CONNECTION", "*");
            
            // 添加主开关
            this.addMasterToggle();
            
            console.log("[DynamicInputBypasser] After setup, inputs:", this.inputs?.length, "outputs:", this.outputs?.length, "widgets:", this.widgets?.length);
            
            setTimeout(() => {
                if (this.scheduleStabilize) {
                    this.scheduleStabilize(1);
                }
            }, 100);
            
            return r;
        };
        
        // 添加所有方法到原型
        nodeType.prototype.addMasterToggle = function() {
            const toggleName = this.title || "忽略节点";
            this.masterToggle = this.addWidget("toggle", toggleName, true, (value) => {
                console.log("[DynamicInputBypasser] Toggle changed to:", value, "type:", typeof value);
                const allNodes = this.getAllConnectedNodes();
                console.log("[DynamicInputBypasser] Connected nodes:", allNodes.length);
                // value 是 boolean 类型：true = 启用，false = 忽略
                const targetMode = value ? this.modeOn : this.modeOff;
                console.log("[DynamicInputBypasser] Setting mode to:", targetMode, "(modeOn:", this.modeOn, "modeOff:", this.modeOff, ")");
                setNodesMode(allNodes, targetMode);
                // 强制更新画布
                if (this.graph) {
                    this.graph.setDirtyCanvas(true, true);
                }
            }, { on: "yes", off: "no" });
            return this.masterToggle;
        };
        
        nodeType.prototype.syncMasterToggle = function() {
            if (!this.masterToggle) return;
            const allNodes = this.getAllConnectedNodes();
            
            if (allNodes.length === 0) {
                this.masterToggle.value = true;
                return;
            }
            
            // 检查所有节点的模式
            const allEnabled = allNodes.every(n => n.mode === this.modeOn);
            const allDisabled = allNodes.every(n => n.mode === this.modeOff);
            
            if (allEnabled) {
                this.masterToggle.value = true;
            } else if (allDisabled) {
                this.masterToggle.value = false;
            }
            // 如果是混合状态，保持当前值不变
        };
        
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
                    console.log(`[DynamicInputBypasser] Input ${i} connected nodes:`, connectedNodes.map(n => n.title));
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
        
        nodeType.prototype.getAllConnectedNodes = function() {
            const allNodes = [];
            if (!this.inputs) return allNodes;
            for (let i = 0; i < this.inputs.length - 1; i++) {
                const connectedNodes = getConnectedNodes(this, i);
                allNodes.push(...connectedNodes);
            }
            return allNodes;
        };
        
        nodeType.prototype.scheduleStabilize = function(ms) {
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
        
        const origOnPropertyChanged = nodeType.prototype.onPropertyChanged;
        nodeType.prototype.onPropertyChanged = function(name, value) {
            if (origOnPropertyChanged) {
                origOnPropertyChanged.call(this, name, value);
            }
            if ((name === "title" || name === "Node name for S&R") && this.masterToggle) {
                // 使用 this.title 获取当前标题
                const currentTitle = this.title || "忽略节点";
                this.masterToggle.name = currentTitle;
                // 强制重绘
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
            if (this.masterToggle && this.masterToggle.name !== this.title) {
                this.masterToggle.name = this.title || "忽略节点";
            }
        };
    }
});

console.log("[DynamicInputBypasser] Extension loaded");
