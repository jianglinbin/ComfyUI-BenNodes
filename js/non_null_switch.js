import { app } from "../../scripts/app.js";

/**
 * SwitchNOTNULL 动态输入扩展
 * 
 * 功能：
 * - 固定显示"主数据源"和"备选1"两个输入
 * - 当两者都连接后，自动添加新的备选输入
 * - 支持无限扩展备选输入
 */

app.registerExtension({
    name: "BenNodes.NonNullSwitch",
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "NonNullSwitchBen") return;
        
        console.log("[NonNullSwitch] Registering dynamic input extension");
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            
            // 清除 Python 定义的内容
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
            
            // 初始化：添加固定的两个输入
            this.addInput("主数据源", "*");
            this.addInput("备选1", "*");
            
            // 初始化状态
            this._schedulePromise = null;
            
            console.log("[NonNullSwitch] Node created with 2 initial inputs");
            
            return r;
        };
        
        /**
         * 稳定输入列表
         * - 确保前两个输入始终存在
         * - 当所有输入都连接时，添加新的备选输入
         * - 移除末尾多余的空输入（保留一个）
         */
        nodeType.prototype.stabilizeInputs = function() {
            if (!this.inputs) return;
            
            // 确保至少有两个输入
            while (this.inputs.length < 2) {
                const index = this.inputs.length;
                const name = index === 0 ? "主数据源" : "备选1";
                this.addInput(name, "*");
            }
            
            // 检查是否所有输入都已连接
            const allConnected = this.inputs.every(input => input.link != null);
            
            if (allConnected) {
                // 所有输入都连接了，添加新的备选输入
                const nextIndex = this.inputs.length;
                const name = nextIndex === 1 ? "备选1" : `备选${nextIndex}`;
                this.addInput(name, "*");
                console.log(`[NonNullSwitch] All inputs connected, added ${name}`);
            } else {
                // 移除末尾多余的空输入，但保留至少一个空输入
                let lastConnectedIndex = -1;
                for (let i = this.inputs.length - 1; i >= 0; i--) {
                    if (this.inputs[i].link != null) {
                        lastConnectedIndex = i;
                        break;
                    }
                }
                
                // 保留到最后一个连接的输入 + 1个空输入
                const targetLength = Math.max(2, lastConnectedIndex + 2);
                while (this.inputs.length > targetLength) {
                    this.removeInput(this.inputs.length - 1);
                    console.log(`[NonNullSwitch] Removed excess empty input`);
                }
            }
            
            // 更新输入名称（确保固定名称正确）
            if (this.inputs.length > 0) {
                this.inputs[0].name = "主数据源";
            }
            if (this.inputs.length > 1) {
                this.inputs[1].name = "备选1";
            }
            for (let i = 2; i < this.inputs.length; i++) {
                this.inputs[i].name = `备选${i}`;
            }
            
            this.size = this.computeSize();
        };
        
        /**
         * 延迟执行稳定化操作
         */
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
        
        /**
         * 连接变化时触发
         */
        nodeType.prototype.onConnectionsChange = function(type, index, connected, link_info) {
            console.log(`[NonNullSwitch] Connection changed: type=${type}, index=${index}, connected=${connected}`);
            this.scheduleStabilize(100);
        };
        
        /**
         * 序列化时保存输入配置
         */
        const origSerialize = nodeType.prototype.serialize;
        nodeType.prototype.serialize = function() {
            const data = origSerialize ? origSerialize.apply(this, arguments) : {};
            data.inputs_count = this.inputs ? this.inputs.length : 2;
            return data;
        };
        
        /**
         * 反序列化时恢复输入配置
         */
        const origConfigure = nodeType.prototype.configure;
        nodeType.prototype.configure = function(info) {
            if (origConfigure) {
                origConfigure.apply(this, arguments);
            }
            
            // 恢复输入数量
            if (info.inputs_count && this.inputs) {
                while (this.inputs.length < info.inputs_count) {
                    const index = this.inputs.length;
                    const name = index === 0 ? "主数据源" : 
                                 index === 1 ? "备选1" : 
                                 `备选${index}`;
                    this.addInput(name, "*");
                }
            }
            
            // 延迟稳定化，确保连接已恢复
            setTimeout(() => {
                if (this.scheduleStabilize) {
                    this.scheduleStabilize(1);
                }
            }, 100);
        };
    }
});

console.log("[NonNullSwitch] Extension loaded");
