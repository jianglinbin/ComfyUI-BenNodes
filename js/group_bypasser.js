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
        console.log(`[GroupBypasser] setGroupMode: Invalid graph or group`);
        return;
    }
    
    console.log(`[GroupBypasser] Setting group "${group.title}" to mode ${mode}`);
    
    const nodesInGroup = getNodesInGroup(graph, group);
    console.log(`[GroupBypasser] Group has ${nodesInGroup.length} nodes`);
    
    for (const node of nodesInGroup) {
        if (node) {
            console.log(`[GroupBypasser] Setting node "${node.title}" (id: ${node.id}) mode from ${node.mode} to ${mode}`);
            node.mode = mode;
        }
    }
    
    console.log(`[GroupBypasser] ✓ Group mode set complete`);
}

app.registerExtension({
    name: "BenNodes.GroupBypasser",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "GroupBypasserBen") return;
        
        console.log("[GroupBypasser] beforeRegisterNodeDef called");
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            
            console.log("[GroupBypasser] onNodeCreated");
            
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
            this.groupComboWidget = null;
            this.groupToggleWidget = null;
            this.selectedGroupName = "";
            
            // 添加组选择下拉框
            this.addGroupComboWidget();
            
            // 添加开关
            this.addGroupToggleWidget();
            
            // 监听图变化以更新组列表
            this.setupGraphMonitoring();
            
            // 初始应用组模式
            setTimeout(() => {
                if (this.selectedGroupName) {
                    console.log("[GroupBypasser] Initial apply group mode");
                    this.applyGroupMode();
                }
            }, 100);
            
            console.log("[GroupBypasser] After setup, widgets:", this.widgets?.length);
            
            return r;
        };
        
        // 添加组选择下拉框
        nodeType.prototype.addGroupComboWidget = function() {
            const graph = this.graph || app.graph;
            const groups = getAllGroups(graph);
            const groupNames = groups.map(g => g.title);
            
            this.groupComboWidget = this.addWidget(
                "combo",
                "选择组",
                groupNames.length > 0 ? groupNames[0] : "",
                (value) => {
                    console.log("[GroupBypasser] Group selected:", value);
                    this.selectedGroupName = value;
                    // 选择组后，根据当前开关状态应用
                    if (this.groupToggleWidget) {
                        this.applyGroupMode();
                    }
                },
                {
                    values: groupNames.length > 0 ? groupNames : [""]
                }
            );
            
            if (groupNames.length > 0) {
                this.selectedGroupName = groupNames[0];
            }
            
            return this.groupComboWidget;
        };
        
        // 添加开关控件
        nodeType.prototype.addGroupToggleWidget = function() {
            const toggleName = this.title || "忽略组";
            this.groupToggleWidget = this.addWidget(
                "toggle",
                toggleName,
                true,
                (value) => {
                    console.log("[GroupBypasser] Toggle changed to:", value);
                    this.applyGroupMode();
                },
                { on: "yes", off: "no" }
            );
            
            return this.groupToggleWidget;
        };
        
        // 应用组模式
        nodeType.prototype.applyGroupMode = function() {
            console.log("[GroupBypasser] applyGroupMode called");
            console.log("[GroupBypasser] selectedGroupName:", this.selectedGroupName);
            console.log("[GroupBypasser] groupToggleWidget:", this.groupToggleWidget);
            
            if (!this.selectedGroupName || !this.groupToggleWidget) {
                console.log("[GroupBypasser] Missing selectedGroupName or groupToggleWidget");
                return;
            }
            
            const graph = this.graph || app.graph;
            console.log("[GroupBypasser] graph:", graph);
            
            const groups = getAllGroups(graph);
            console.log("[GroupBypasser] All groups:", groups.map(g => g.title));
            
            const targetGroup = groups.find(g => g.title === this.selectedGroupName);
            console.log("[GroupBypasser] Target group:", targetGroup);
            
            if (!targetGroup) {
                console.log("[GroupBypasser] Group not found:", this.selectedGroupName);
                return;
            }
            
            // value 是 boolean 类型：true = 激活，false = 忽略
            const toggleValue = this.groupToggleWidget.value;
            const targetMode = toggleValue ? this.modeOn : this.modeOff;
            console.log("[GroupBypasser] Toggle value:", toggleValue, "Target mode:", targetMode);
            
            setGroupMode(graph, targetGroup, targetMode);
            
            // 强制更新画布
            if (graph) {
                graph.setDirtyCanvas(true, true);
            }
            
            console.log("[GroupBypasser] ✓ Group mode applied");
        };
        
        // 更新组列表
        nodeType.prototype.updateGroupList = function() {
            if (!this.groupComboWidget) return;
            
            const graph = this.graph || app.graph;
            const groups = getAllGroups(graph);
            const groupNames = groups.map(g => g.title);
            
            console.log("[GroupBypasser] Updating group list:", groupNames);
            
            // 保存当前选择
            const currentValue = this.groupComboWidget.value;
            
            // 更新下拉框选项
            this.groupComboWidget.options.values = groupNames.length > 0 ? groupNames : [""];
            
            // 如果当前选择的组还存在，保持选择；否则选择第一个
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
            
            // 强制重绘
            if (graph) {
                graph.setDirtyCanvas(true, false);
            }
        };
        
        // 设置图监听
        nodeType.prototype.setupGraphMonitoring = function() {
            // 定期检查组列表变化
            this._groupCheckInterval = setInterval(() => {
                if (this.groupComboWidget) {
                    const graph = this.graph || app.graph;
                    const groups = getAllGroups(graph);
                    const currentGroupNames = groups.map(g => g.title).sort().join(',');
                    const widgetGroupNames = (this.groupComboWidget.options.values || []).sort().join(',');
                    
                    if (currentGroupNames !== widgetGroupNames) {
                        console.log("[GroupBypasser] Group list changed, updating...");
                        this.updateGroupList();
                    }
                }
            }, 1000); // 每秒检查一次
        };
        
        // 清理定时器
        const origOnRemoved = nodeType.prototype.onRemoved;
        nodeType.prototype.onRemoved = function() {
            if (this._groupCheckInterval) {
                clearInterval(this._groupCheckInterval);
                this._groupCheckInterval = null;
            }
            if (origOnRemoved) {
                origOnRemoved.call(this);
            }
        };
        
        // 监听标题变化
        const origOnPropertyChanged = nodeType.prototype.onPropertyChanged;
        nodeType.prototype.onPropertyChanged = function(name, value) {
            if (origOnPropertyChanged) {
                origOnPropertyChanged.call(this, name, value);
            }
            if ((name === "title" || name === "Node name for S&R") && this.groupToggleWidget) {
                const currentTitle = this.title || "忽略组";
                this.groupToggleWidget.name = currentTitle;
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
            if (this.groupToggleWidget && this.groupToggleWidget.name !== this.title) {
                this.groupToggleWidget.name = this.title || "忽略组";
            }
        };
        
        // 序列化
        const origSerialize = nodeType.prototype.serialize;
        nodeType.prototype.serialize = function() {
            const data = origSerialize ? origSerialize.call(this) : {};
            data.selectedGroupName = this.selectedGroupName;
            return data;
        };
        
        // 反序列化
        const origConfigure = nodeType.prototype.configure;
        nodeType.prototype.configure = function(data) {
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

console.log("[GroupBypasser] Extension loaded");
