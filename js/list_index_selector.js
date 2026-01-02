import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ben.listIndexSelector",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 只处理ListIndexSelectorBen节点
        if (nodeData.name !== "ListIndexSelectorBen") return;
        
        // 解析索引值，处理ADD和ADD5指令
        function parseIndexValue(indexValue, listLength = 0) {
            // 转换为小写并去除空格
            const cleanValue = indexValue.toLowerCase().trim();
            
            // 检查是否是ADD指令
            if (cleanValue === "add") {
                // 基础ADD指令，初始默认值为0
                return "add,0";
            }
            
            // 检查是否是ADD5指令
            if (cleanValue === "add5") {
                // ADD5指令，初始默认值为5
                return "add,5";
            }
            
            // 检查是否是add开头的指令
            if (cleanValue.startsWith("add,")) {
                const parts = cleanValue.split(",").map(p => p.trim()).filter(p => p !== "");
                if (parts.length === 1) {
                    // 只有add前缀，没有参数，默认为add,0
                    return "add,0";
                }
                
                // 解析数值参数
                const numericParts = parts.slice(1).map(p => {
                    const num = parseInt(p);
                    return isNaN(num) ? 0 : num;
                });
                
                // 处理索引越界
                if (listLength > 0) {
                    numericParts.forEach((num, index) => {
                        if (num >= listLength) {
                            numericParts[index] = num - listLength;
                        }
                    });
                }
                
                return [parts[0], ...numericParts].join(",");
            }
            
            // 非ADD/ADD5指令，保持原样
            return indexValue;
        }
        
        // 计算下一个索引值
        function calculateNextIndexValue(currentIndex, listLength = 0) {
            const cleanValue = currentIndex.toLowerCase().trim();
            
            // 检查是否是add开头的指令
            if (!cleanValue.startsWith("add,")) {
                return currentIndex;
            }
            
            const parts = cleanValue.split(",").map(p => p.trim()).filter(p => p !== "");
            if (parts.length === 1) {
                return "add,0";
            }
            
            // 解析当前数值参数
            const currentNumbers = parts.slice(1).map(p => {
                const num = parseInt(p);
                return isNaN(num) ? 0 : num;
            });
            
            // 计算基准值（最大数值）
            const baseValue = Math.max(...currentNumbers);
            
            if (currentNumbers.length === 1) {
                // 单参数情况：初始默认值为0，每次执行后自增1
                let nextValue = baseValue + 1;
                // 处理索引越界
                if (listLength > 0 && nextValue >= listLength) {
                    nextValue = nextValue - listLength;
                }
                return `add,${nextValue}`;
            } else {
                // 多参数情况
                const nextNumbers = [];
                let interval = 0;
                
                // 计算间隔值：使用前两个数值参数之间的差值
                if (currentNumbers.length >= 2) {
                    interval = currentNumbers[1] - currentNumbers[0];
                }
                
                // 计算新的数值参数
                for (let i = 0; i < currentNumbers.length; i++) {
                    let nextValue = baseValue + (i + 1) + (i * interval);
                    // 处理索引越界
                    if (listLength > 0) {
                        while (nextValue >= listLength) {
                            nextValue -= listLength;
                        }
                    }
                    nextNumbers.push(nextValue);
                }
                
                return `add,${nextNumbers.join(",")}`;
            }
        }
        
        // 更新输出端口的函数
        function updateOutputs(node, indexValue) {
            if (!node.outputs) {
                node.outputs = [];
            }
            
            // 解析索引数量
            const indices = indexValue
                .split(",")
                .map(i => i.trim())
                .filter(i => i !== "");
            
            // 处理ADD指令
            const processedIndices = indices[0].toLowerCase() === "add" ? indices.slice(1) : indices;
            
            const target_number_of_outputs = Math.max(1, processedIndices.length);
            // 限制最大输出数量为20（与Python端保持一致）
            const max_outputs = Math.min(target_number_of_outputs, 20);
            const num_outputs = node.outputs.length;
            
            if (max_outputs === num_outputs) {
                return; // already set, do nothing
            }
            
            // 更新输出端口
            if (max_outputs < num_outputs) {
                // 移除多余的输出端口
                const outputs_to_remove = num_outputs - max_outputs;
                for (let i = 0; i < outputs_to_remove; i++) {
                    node.removeOutput(node.outputs.length - 1);
                }
            } else {
                // 添加新的输出端口
                for (let i = num_outputs; i < max_outputs; ++i) {
                    const output_name = `ITEM_${i}`;
                    node.addOutput(output_name, node._type);
                }
            }
            
            // 刷新节点大小
            node.size = node.computeSize();
            if (node.setSizeForOutputs) {
                node.setSizeForOutputs();
                node.size = node.computeSize(); // 再次计算确保大小正确
            }
            
            // 标记画布为脏
            if (node.setDirtyCanvas) {
                node.setDirtyCanvas(true);
            } else if (app.graph.setDirtyCanvas) {
                app.graph.setDirtyCanvas(true);
            }
            
            // 标记节点为脏
            if (node.setDirtyNode) {
                node.setDirtyNode(true);
            } else if (app.graph.setDirtyNode) {
                app.graph.setDirtyNode(node, true);
            }
        }
        
        // 添加列表长度预览元素
        function addListLengthPreview(node) {
            // 检查是否已经有预览元素
            if (node._listLengthPreview) {
                return;
            }
            
            const preview = document.createElement("div");
            preview.className = "list-length-preview";
            preview.style.cssText = `
                position: absolute;
                bottom: 5px;
                right: 5px;
                font-size: 10px;
                color: #666;
                background-color: rgba(0, 0, 0, 0.1);
                padding: 2px 5px;
                border-radius: 3px;
            `;
            
            node._listLengthPreview = preview;
            
            // 安全地添加预览元素，确保容器存在且是有效的DOM元素
            try {
                // 尝试找到合适的容器添加预览元素
                if (node.widgets_container && typeof node.widgets_container.appendChild === 'function') {
                    node.widgets_container.appendChild(preview);
                } else if (node.container && typeof node.container.appendChild === 'function') {
                    node.container.appendChild(preview);
                } else if (node.element && typeof node.element.appendChild === 'function') {
                    node.element.appendChild(preview);
                } else {
                    // 如果没有找到合适的容器，使用setTimeout延迟重试
                    setTimeout(() => addListLengthPreview(node), 100);
                }
            } catch (error) {
                console.error('Failed to add list length preview:', error);
                // 发生错误时延迟重试
                setTimeout(() => addListLengthPreview(node), 100);
            }
        }
        
        // 更新列表长度预览
        function updateListLengthPreview(node, listLength) {
            if (!node._listLengthPreview) {
                addListLengthPreview(node);
            }
            
            node._listLengthPreview.textContent = `列表长度: ${listLength}`;
        }
        
        // 保存原始的执行函数（如果存在）
        const originalExecute = nodeType.prototype.execute;
        
        // 创建索引更新函数
        function updateIndexAfterExecution(node) {
            const indexWidget = node.widgets.find(w => w.name === "index");
            if (indexWidget) {
                const currentIndex = indexWidget.value;
                console.log('执行后索引值:', currentIndex);
                
                // 获取列表长度（需要从输入连接获取，这里先设为0）
                let listLength = 0;
                
                // 先解析索引值，确保格式正确
                const parsedIndex = parseIndexValue(currentIndex, listLength);
                // 计算下一个索引值
                const nextIndex = calculateNextIndexValue(parsedIndex, listLength);
                console.log('解析后的索引值:', parsedIndex);
                console.log('计算的下一个索引值:', nextIndex);
                
                // 更新索引值
                indexWidget.value = nextIndex;
                console.log('更新后的索引值:', indexWidget.value);
                
                // 强制触发widget的更新事件
                if (indexWidget.callback) {
                    indexWidget.callback(nextIndex);
                }
                
                // 更新输出端口
                updateOutputs(node, nextIndex);
                
                // 确保节点状态正确更新
                if (node.setDirtyCanvas) {
                    node.setDirtyCanvas(true);
                } else if (app.graph.setDirtyCanvas) {
                    app.graph.setDirtyCanvas(true);
                }
                
                // 重新渲染节点
                if (app.canvas) {
                    app.canvas.draw(true);
                } else if (app.graph.render) {
                    app.graph.render();
                }
            }
        }
        
        // 覆盖execute方法，处理执行前后的索引值
        nodeType.prototype.execute = function () {
            const indexWidget = this.widgets.find(w => w.name === "index");
            let originalIndex = null;
            
            if (indexWidget) {
                // 保存原始索引值
                originalIndex = indexWidget.value;
                console.log('执行前索引值:', originalIndex);
                
                // 解析并转换索引值（去掉add前缀）
                const parts = originalIndex.split(",").map(p => p.trim()).filter(p => p !== "");
                if (parts[0].toLowerCase() === "add") {
                    const convertedIndex = parts.slice(1).join(",");
                    indexWidget.value = convertedIndex;
                    console.log('传递给后端的索引值:', convertedIndex);
                }
            }
            
            // 执行原始的execute方法
            let result;
            if (originalExecute) {
                result = originalExecute.apply(this, arguments);
            }
            
            // 恢复原始索引值
            if (indexWidget && originalIndex) {
                indexWidget.value = originalIndex;
                console.log('恢复后的索引值:', originalIndex);
            }
            
            return result;
        };
        
        // 在扩展注册完成后，添加全局事件监听器
        app.registerExtension({name: 'ben.listIndexSelector.update', async setup() {
            // 使用更可靠的方式监听工作流执行完成事件
            if (app.onAfterExecution) {
                app.onAfterExecution(async () => {
                    // 遍历所有ListIndexSelectorBen节点
                    const selectorNodes = app.graph._nodes.filter(node => node.comfyClass === 'ListIndexSelectorBen');
                    selectorNodes.forEach(node => {
                        // 更新每个节点的索引
                        updateIndexAfterExecution(node);
                    });
                });
            } else {
                // 备用方式
                app.graph.onAfterExecute = function() {
                    // 遍历所有ListIndexSelectorBen节点
                    const selectorNodes = app.graph._nodes.filter(node => node.comfyClass === 'ListIndexSelectorBen');
                    selectorNodes.forEach(node => {
                        // 更新每个节点的索引
                        updateIndexAfterExecution(node);
                    });
                };
            }
        }});
        
        nodeType.prototype.onNodeCreated = function () {
            const node = this;
            node._type = "*";
            
            // 初始化输出端口
            const indexWidget = this.widgets.find(w => w.name === "index");
            if (indexWidget) {
                // 解析初始索引值（处理ADD/ADD5指令）
                let initialValue = indexWidget.value;
                
                // 特殊处理ADD5指令，初始值为5
                if (initialValue.toLowerCase().trim() === "add5") {
                    initialValue = "add,5";
                    indexWidget.value = initialValue;
                } else {
                    // 解析其他索引值
                    const parsedIndex = parseIndexValue(initialValue);
                    indexWidget.value = parsedIndex;
                    initialValue = parsedIndex;
                }
                
                // 更新输出端口
                updateOutputs(node, initialValue);
                
                // 监听index参数变化，自动更新输出端口数量
                const origOnChange = indexWidget.callback;
                indexWidget.callback = function (value) {
                    let processedValue = value;
                    
                    // 处理ADD5指令
                    if (processedValue.toLowerCase().trim() === "add5") {
                        processedValue = "add,5";
                        this.value = processedValue;
                    } else {
                        // 解析索引值
                        processedValue = parseIndexValue(value);
                        this.value = processedValue;
                    }
                    
                    // 调用原始回调
                    if (origOnChange) {
                        origOnChange(processedValue);
                    }
                    
                    // 更新输出端口数量
                    updateOutputs(node, processedValue);
                };
            }
            
            // 延迟添加列表长度预览，确保DOM结构已完全创建
            setTimeout(() => addListLengthPreview(node), 200);
        };
        
        // 监听参数变化事件，确保端口数量正确
        const originalOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            if (originalOnConfigure) {
                originalOnConfigure.apply(this, arguments);
            }
            
            // 确保输出端口数量正确
            const indexWidget = this.widgets.find(w => w.name === "index");
            if (indexWidget) {
                const parsedIndex = parseIndexValue(indexWidget.value);
                indexWidget.value = parsedIndex;
                updateOutputs(this, parsedIndex);
            }
        };
    }
});
