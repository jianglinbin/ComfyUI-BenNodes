import { app } from "../../scripts/app.js";

// 获取节点输入的配置信息
import { t } from "./i18n.js";
function getInputConfig(node, inputIndex) {
    if (!node || !node.inputs || !node.inputs[inputIndex]) return null;
    
    const input = node.inputs[inputIndex];
    const inputName = input.name;
    
    // 从节点定义中获取输入配置
    const nodeType = node.constructor;
    const nodeDef = nodeType.nodeData;
    
    if (!nodeDef || !nodeDef.input) return null;
    
    // 查找输入定义
    let inputDef = null;
    if (nodeDef.input.required && nodeDef.input.required[inputName]) {
        inputDef = nodeDef.input.required[inputName];
    } else if (nodeDef.input.optional && nodeDef.input.optional[inputName]) {
        inputDef = nodeDef.input.optional[inputName];
    }
    
    return inputDef;
}

// 创建对应类型的 widget（不创建输入）
function createWidgetForOutput(node, outputIndex, targetNode, targetInputIndex) {
    const inputConfig = getInputConfig(targetNode, targetInputIndex);
    if (!inputConfig) {
        console.log("[DynamicOutputReplicator] No input config found");
        return null;
    }
    
    const targetInput = targetNode.inputs[targetInputIndex];
    const widgetName = `${targetNode.title || targetNode.type}.${targetInput.name}`;
    
    console.log("[DynamicOutputReplicator] Creating widget:", widgetName, "config:", inputConfig);
    
    // 检查是否是 COMBO 类型
    if (Array.isArray(inputConfig[0])) {
        // COMBO 类型
        const options = inputConfig[0];
        const widget = node.addWidget("combo", widgetName, options[0], (value) => {
            console.log("[DynamicOutputReplicator] Widget value changed:", value);
        }, { values: options });
        
        return widget;
    }
    
    // 其他类型
    const type = inputConfig[0];
    const config = inputConfig[1] || {};
    
    let widget = null;
    if (type === "INT") {
        widget = node.addWidget("number", widgetName, config.default || 0, (value) => {
            console.log("[DynamicOutputReplicator] Widget value changed:", value);
        }, {
            min: config.min,
            max: config.max,
            step: config.step || 1,
            precision: 0
        });
    } else if (type === "FLOAT") {
        widget = node.addWidget("number", widgetName, config.default || 0.0, (value) => {
            console.log("[DynamicOutputReplicator] Widget value changed:", value);
        }, {
            min: config.min,
            max: config.max,
            step: config.step || 0.01,
            precision: 2
        });
    } else if (type === "STRING") {
        widget = node.addWidget("text", widgetName, config.default || "", (value) => {
            console.log("[DynamicOutputReplicator] Widget value changed:", value);
        }, {
            multiline: config.multiline || false
        });
    } else if (type === "BOOLEAN") {
        widget = node.addWidget("toggle", widgetName, config.default || false, (value) => {
            console.log("[DynamicOutputReplicator] Widget value changed:", value);
        });
    }
    
    return widget;
}

app.registerExtension({
    name: "BenNodes.ParameterDistributor",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "ParameterDistributorBen") return;
        
        console.log("[ParameterDistributor] beforeRegisterNodeDef called");
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            
            console.log("[DynamicOutputReplicator] onNodeCreated, inputs:", this.inputs?.length, "outputs:", this.outputs?.length);
            
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
            
            // 添加第一个输出
            this.addOutput("*", "*");
            
            // 初始化状态
            this._tempWidth = null;
            this._debouncerTempWidth = null;
            this._schedulePromise = null;
            this._outputCounter = 1;
            this._outputWidgets = {}; // 存储每个输出对应的 widget
            this._paramsLocked = false; // 参数锁状态
            this.lockWidget = null; // 锁定开关 widget 引用
            
            // 添加锁定开关（会在最后）
            this.addLockWidget();
            
            console.log("[DynamicOutputReplicator] After setup, inputs:", this.inputs?.length, "outputs:", this.outputs?.length);
            
            // 延迟初始化，等待可能的 configure 调用
            setTimeout(() => {
                console.log("[DynamicOutputReplicator] Delayed init, widgets_values from properties:", this.properties?.widgets_values);
                
                if (this.scheduleStabilize) {
                    this.scheduleStabilize(1);
                }
            }, 100);
            
            return r;
        };
        
        // 添加锁定开关 widget
        nodeType.prototype.addLockWidget = function() {
            if (!this.lockWidget) {
                this.lockWidget = this.addWidget("toggle", t("lock_params"), this._paramsLocked || false, (value) => {
                    console.log("[DynamicOutputReplicator] Lock toggled:", value);
                    this._paramsLocked = value;
                    if (this.graph) {
                        this.graph.setDirtyCanvas(true, false);
                    }
                }, { on: t("locked"), off: t("unlocked") });
            }
        };
        
        // 确保锁定开关在最下方
        nodeType.prototype.ensureLockWidgetAtBottom = function() {
            if (this.lockWidget && this.widgets) {
                const lockIndex = this.widgets.indexOf(this.lockWidget);
                if (lockIndex >= 0 && lockIndex < this.widgets.length - 1) {
                    // 锁定开关不在最后，移动它
                    this.widgets.splice(lockIndex, 1);
                    this.widgets.push(this.lockWidget);
                }
            }
        };
        
        // 重写 getExtraMenuOptions 添加刷新选项
        const origGetExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
        nodeType.prototype.getExtraMenuOptions = function(_, options) {
            if (origGetExtraMenuOptions) {
                origGetExtraMenuOptions.apply(this, arguments);
            }
            
            options.unshift({
                content: t("refresh_outputs"),
                callback: () => {
                    this.scheduleStabilize(1);
                }
            });
        };
        
        // 稳定输出状态
        nodeType.prototype.stabilizeOutputs = function() {
            console.log("[DynamicOutputReplicator] ===== stabilizeOutputs called =====");
            console.log("[DynamicOutputReplicator] outputs:", this.outputs?.length);
            console.log("[DynamicOutputReplicator] widgets:", this.widgets?.length);
            console.log("[DynamicOutputReplicator] _pendingWidgetsValues:", this._pendingWidgetsValues);
            console.log("[DynamicOutputReplicator] _paramsLocked:", this._paramsLocked);
            
            if (!this.outputs) return;
            
            const graph = this.graph || app.graph;
            
            // 如果参数已锁定
            if (this._paramsLocked) {
                console.log("[DynamicOutputReplicator] Params locked");
                
                // 如果有待恢复的 widget 信息，需要先恢复 widget
                if (this._pendingWidgetsValues && this._pendingOutputWidgets) {
                    console.log("[DynamicOutputReplicator] Restoring widgets in locked state");
                    
                    // 根据保存的映射信息恢复 widget
                    for (let key in this._pendingOutputWidgets) {
                        const outputIndex = parseInt(key);
                        const widgetInfo = this._pendingOutputWidgets[key];
                        
                        // 检查这个输出是否已经有 widget
                        if (!this._outputWidgets || !this._outputWidgets[outputIndex]) {
                            // 需要创建 widget，使用保存的信息直接创建
                            console.log(`[DynamicOutputReplicator] Restoring widget for output ${outputIndex}:`, widgetInfo);
                            
                            let widget = null;
                            if (widgetInfo.type === "combo" && widgetInfo.options && widgetInfo.options.values) {
                                widget = this.addWidget("combo", widgetInfo.name, widgetInfo.value, null, { values: widgetInfo.options.values });
                            } else if (widgetInfo.type === "number") {
                                widget = this.addWidget("number", widgetInfo.name, widgetInfo.value, null, widgetInfo.options || {});
                            } else if (widgetInfo.type === "text") {
                                widget = this.addWidget("text", widgetInfo.name, widgetInfo.value, null, widgetInfo.options || {});
                            } else if (widgetInfo.type === "toggle") {
                                widget = this.addWidget("toggle", widgetInfo.name, widgetInfo.value, null, widgetInfo.options || {});
                            }
                            
                            if (widget) {
                                if (!this._outputWidgets) {
                                    this._outputWidgets = {};
                                }
                                this._outputWidgets[outputIndex] = widget;
                                console.log(`[DynamicOutputReplicator] Restored widget for output ${outputIndex}`);
                                
                                // 确保锁定开关在最下方
                                this.ensureLockWidgetAtBottom();
                            }
                        }
                    }
                    
                    // 清除待恢复的信息
                    this._pendingWidgetsValues = null;
                    this._pendingOutputWidgets = null;
                }
                
                // 更新输出名称
                for (let i = 0; i < this.outputs.length; i++) {
                    const output = this.outputs[i];
                    if (i === this.outputs.length - 1) {
                        output.name = "*";
                    } else {
                        if (output.links && output.links.length > 0) {
                            const link = graph.links[output.links[0]];
                            if (link) {
                                const targetNode = graph.getNodeById(link.target_id);
                                if (targetNode && targetNode.inputs && targetNode.inputs[link.target_slot]) {
                                    const targetInput = targetNode.inputs[link.target_slot];
                                    const targetNodeName = targetNode.title || targetNode.type;
                                    const inputName = targetInput.name || `input_${link.target_slot}`;
                                    output.name = `${targetNodeName}.${inputName}`;
                                }
                            }
                        }
                    }
                }
                
                this.size = this.computeSize();
                return;
            }
            
            // 未锁定时的正常逻辑
            // 为所有已连接但没有 widget 的输出创建 widget
            for (let i = 0; i < this.outputs.length - 1; i++) {  // 排除最后一个输出
                const output = this.outputs[i];
                if (output.links && output.links.length > 0) {
                    // 这个输出已连接，检查是否有 widget
                    if (!this._outputWidgets || !this._outputWidgets[i]) {
                        // 没有 widget，创建一个
                        const link = graph.links[output.links[0]];
                        if (link) {
                            const targetNode = graph.getNodeById(link.target_id);
                            if (targetNode) {
                                console.log(`[DynamicOutputReplicator] Creating widget for existing output ${i}`);
                                const widget = createWidgetForOutput(this, i, targetNode, link.target_slot);
                                
                                if (widget) {
                                    if (!this._outputWidgets) {
                                        this._outputWidgets = {};
                                    }
                                    this._outputWidgets[i] = widget;
                                    console.log("[DynamicOutputReplicator] Created widget for output", i, "widget name:", widget.name);
                                    
                                    // 确保锁定开关在最下方
                                    this.ensureLockWidgetAtBottom();
                                    
                                    // 如果有待恢复的值，立即恢复
                                    // 注意：锁定开关现在在最后，参数 widget 的索引不需要调整
                                    if (this._pendingWidgetsValues) {
                                        const widgetIndex = this.widgets.indexOf(widget);
                                        console.log("[DynamicOutputReplicator] Widget index:", widgetIndex, "pending values length:", this._pendingWidgetsValues.length);
                                        if (widgetIndex >= 0 && widgetIndex < this._pendingWidgetsValues.length) {
                                            const oldValue = widget.value;
                                            widget.value = this._pendingWidgetsValues[widgetIndex];
                                            console.log(`[DynamicOutputReplicator] Immediately restored widget ${widgetIndex} value from ${oldValue} to:`, this._pendingWidgetsValues[widgetIndex]);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // 检查最后一个输出是否被连接
            const lastOutput = this.outputs[this.outputs.length - 1];
            if (lastOutput && lastOutput.links && lastOutput.links.length > 0) {
                // 最后一个输出被连接了
                const link = graph.links[lastOutput.links[0]];
                if (link) {
                    const targetNode = graph.getNodeById(link.target_id);
                    if (targetNode) {
                        const outputIndex = this.outputs.length - 1;
                        
                        // 检查是否已经有 widget
                        if (!this._outputWidgets || !this._outputWidgets[outputIndex]) {
                            // 为这个输出创建 widget
                            const widget = createWidgetForOutput(this, outputIndex, targetNode, link.target_slot);
                            
                            if (widget) {
                                // 存储引用
                                if (!this._outputWidgets) {
                                    this._outputWidgets = {};
                                }
                                this._outputWidgets[outputIndex] = widget;
                                console.log("[DynamicOutputReplicator] Created widget for output", outputIndex, "widget name:", widget.name);
                                
                                // 确保锁定开关在最下方
                                this.ensureLockWidgetAtBottom();
                                
                                // 如果有待恢复的值，立即恢复
                                // 注意：锁定开关现在在最后，参数 widget 的索引不需要调整
                                if (this._pendingWidgetsValues) {
                                    const widgetIndex = this.widgets.indexOf(widget);
                                    console.log("[DynamicOutputReplicator] Widget index:", widgetIndex, "pending values length:", this._pendingWidgetsValues.length);
                                    if (widgetIndex >= 0 && widgetIndex < this._pendingWidgetsValues.length) {
                                        const oldValue = widget.value;
                                        widget.value = this._pendingWidgetsValues[widgetIndex];
                                        console.log(`[DynamicOutputReplicator] Immediately restored widget ${widgetIndex} value from ${oldValue} to:`, this._pendingWidgetsValues[widgetIndex]);
                                    }
                                }
                            }
                        }
                    }
                }
                
                // 添加新输出
                this._outputCounter++;
                this.addOutput("*", "*");
                console.log("[DynamicOutputReplicator] Added new output:", `output_${this._outputCounter}`);
            }
            
            // 移除未连接的中间输出（保留最后一个）
            for (let i = this.outputs.length - 2; i >= 0; i--) {
                const output = this.outputs[i];
                if (!output.links || output.links.length === 0) {
                    console.log("[DynamicOutputReplicator] Removing unconnected output at index:", i);
                    
                    // 移除对应的 widget
                    if (this._outputWidgets && this._outputWidgets[i]) {
                        const widget = this._outputWidgets[i];
                        const widgetIndex = this.widgets.indexOf(widget);
                        if (widgetIndex >= 0) {
                            this.widgets.splice(widgetIndex, 1);
                        }
                        delete this._outputWidgets[i];
                    }
                    
                    this.removeOutput(i);
                }
            }
            
            // 更新输出名称 - 显示目标节点和输入槽位信息
            for (let i = 0; i < this.outputs.length; i++) {
                const output = this.outputs[i];
                if (i === this.outputs.length - 1) {
                    // 最后一个输出显示为 *
                    output.name = "*";
                } else {
                    // 已连接的输出显示目标节点和输入信息
                    if (output.links && output.links.length > 0) {
                        const link = graph.links[output.links[0]];
                        if (link) {
                            const targetNode = graph.getNodeById(link.target_id);
                            if (targetNode && targetNode.inputs && targetNode.inputs[link.target_slot]) {
                                const targetInput = targetNode.inputs[link.target_slot];
                                const targetNodeName = targetNode.title || targetNode.type;
                                const inputName = targetInput.name || `input_${link.target_slot}`;
                                output.name = `${targetNodeName}.${inputName}`;
                            }
                        }
                    }
                }
            }
            
            // 清除待恢复的值（已经恢复完成）
            if (this._pendingWidgetsValues) {
                console.log("[DynamicOutputReplicator] Clearing pending widgets values");
                this._pendingWidgetsValues = null;
            }
            
            this.size = this.computeSize();
        };
        
        // 调度稳定化
        nodeType.prototype.scheduleStabilize = function(ms) {
            if (ms === undefined) ms = 100;
            if (!this._schedulePromise) {
                this._schedulePromise = new Promise((resolve) => {
                    setTimeout(() => {
                        this._schedulePromise = null;
                        this.stabilizeOutputs();
                        if (this.graph) {
                            this.graph.setDirtyCanvas(true, true);
                        }
                        resolve();
                    }, ms);
                });
            }
            return this._schedulePromise;
        };
        
        // 连接变化时触发
        nodeType.prototype.onConnectionsChange = function(type, index, connected, link_info) {
            console.log("[DynamicOutputReplicator] onConnectionsChange:", type, index, connected);
            this.scheduleStabilize(100);
        };
        
        // 保持宽度稳定
        const origAddOutput = nodeType.prototype.addOutput;
        nodeType.prototype.addOutput = function(name, type, extra_info) {
            this._tempWidth = this.size[0];
            return origAddOutput.call(this, name, type, extra_info);
        };
        
        const origRemoveOutput = nodeType.prototype.removeOutput;
        nodeType.prototype.removeOutput = function(slot) {
            this._tempWidth = this.size[0];
            return origRemoveOutput.call(this, slot);
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
        
        // 序列化时保存输出计数器和 widget 值
        const origSerialize = nodeType.prototype.serialize;
        nodeType.prototype.serialize = function() {
            const data = origSerialize ? origSerialize.call(this) : {};
            data.outputCounter = this._outputCounter;
            data.paramsLocked = this._paramsLocked;  // 保存锁定状态
            
            // 保存 widget 值 - 这些值会被发送到后端
            // 注意：最后一个 widget 是锁定开关，需要排除
            if (this.widgets && this.widgets.length > 0) {
                const paramWidgets = this.widgets.filter(w => w !== this.lockWidget);
                data.widgets_values = paramWidgets.map(w => w.value);
                console.log("[DynamicOutputReplicator] serialize: saving widgets_values:", data.widgets_values);
            }
            
            // 保存输出信息
            if (this.outputs && this.outputs.length > 0) {
                data.outputs_info = this.outputs.map(o => ({
                    name: o.name,
                    type: o.type,
                    links: o.links
                }));
            }
            
            // 保存 widget 的详细信息（包括类型和配置）
            if (this._outputWidgets) {
                data.outputWidgets = {};
                for (let key in this._outputWidgets) {
                    const widget = this._outputWidgets[key];
                    if (widget) {
                        const widgetIndex = this.widgets.indexOf(widget);
                        data.outputWidgets[key] = {
                            widgetIndex: widgetIndex,
                            name: widget.name,
                            type: widget.type,
                            value: widget.value,
                            options: widget.options  // 保存 widget 的配置选项
                        };
                    }
                }
                console.log("[DynamicOutputReplicator] serialize: saving outputWidgets:", data.outputWidgets);
            }
            
            console.log("[DynamicOutputReplicator] serialize complete, data:", data);
            return data;
        };
        
        // 配置时恢复输出计数器和 widget 值
        const origConfigure = nodeType.prototype.configure;
        nodeType.prototype.configure = function(info) {
            console.log("[DynamicOutputReplicator] ===== configure called =====");
            console.log("[DynamicOutputReplicator] info:", JSON.stringify(info, null, 2));
            console.log("[DynamicOutputReplicator] info.widgets_values:", info.widgets_values);
            console.log("[DynamicOutputReplicator] Current widgets:", this.widgets?.length);
            
            if (origConfigure) {
                origConfigure.call(this, info);
            }
            
            if (info.outputCounter !== undefined) {
                this._outputCounter = info.outputCounter;
                console.log("[DynamicOutputReplicator] Restored outputCounter:", this._outputCounter);
            }
            
            // 恢复锁定状态
            if (info.paramsLocked !== undefined) {
                this._paramsLocked = info.paramsLocked;
                if (this.lockWidget) {
                    this.lockWidget.value = info.paramsLocked;
                }
                console.log("[DynamicOutputReplicator] Restored paramsLocked:", this._paramsLocked);
            }
            
            // 保存 widgets_values 以便稍后恢复
            this._pendingWidgetsValues = info.widgets_values;
            this._pendingOutputWidgets = info.outputWidgets;
            
            console.log("[DynamicOutputReplicator] Saved pending widgets_values:", this._pendingWidgetsValues);
            
            // 延迟稳定化和恢复 widget 值
            setTimeout(() => {
                console.log("[DynamicOutputReplicator] ===== Delayed restore =====");
                console.log("[DynamicOutputReplicator] widgets count:", this.widgets?.length);
                console.log("[DynamicOutputReplicator] pending values:", this._pendingWidgetsValues);
                
                // 恢复 widget 值
                // 注意：最后一个 widget 是锁定开关，不需要恢复值
                if (this._pendingWidgetsValues && this.widgets) {
                    const paramWidgets = this.widgets.filter(w => w !== this.lockWidget);
                    for (let i = 0; i < Math.min(this._pendingWidgetsValues.length, paramWidgets.length); i++) {
                        if (paramWidgets[i]) {
                            paramWidgets[i].value = this._pendingWidgetsValues[i];
                            console.log(`[DynamicOutputReplicator] Restored widget ${i} value:`, this._pendingWidgetsValues[i]);
                        }
                    }
                    this._pendingWidgetsValues = null;
                }
                
                // 恢复 widget 到输出的映射
                if (this._pendingOutputWidgets) {
                    this._outputWidgets = {};
                    for (let key in this._pendingOutputWidgets) {
                        const widgetInfo = this._pendingOutputWidgets[key];
                        if (widgetInfo && widgetInfo.widgetIndex >= 0 && widgetInfo.widgetIndex < this.widgets.length) {
                            const widget = this.widgets[widgetInfo.widgetIndex];
                            if (widget !== this.lockWidget) {
                                this._outputWidgets[key] = widget;
                                console.log(`[DynamicOutputReplicator] Restored outputWidget mapping ${key} -> widget ${widgetInfo.widgetIndex}`);
                            }
                        }
                    }
                    this._pendingOutputWidgets = null;
                }
                
                if (this.scheduleStabilize) {
                    this.scheduleStabilize(1);
                }
            }, 200);
        };
    }
});

console.log("[DynamicOutputReplicator] Extension loaded");
