# 设计文档

## 概述

Dynamic Input Bypasser 是一个 ComfyUI 自定义节点，通过单个主开关控制多个输入连接节点的执行状态。该节点**完全独立实现**，不依赖 rgthree 节点库，确保在任何 ComfyUI 环境中都能正常工作。

### 设计目标

1. **独立性** - 不依赖任何第三方节点库，仅依赖 ComfyUI 核心
2. **简洁性** - 使用单一主开关控制所有连接节点
3. **灵活性** - 支持动态添加/移除输入连接
4. **可读性** - 主开关名称显示节点标题
5. **兼容性** - 与 ComfyUI 框架无缝集成
6. **性能** - 使用防抖和批量更新机制

### 核心特性

- 动态输入槽位自动管理
- 单一主开关控制所有连接节点
- 主开关名称显示当前节点标题
- 透传节点（Reroute）自动跟随
- 子图节点递归处理
- 循环连接检测和阻止
- 性能优化（防抖、批量更新）
- **零外部依赖**（除 ComfyUI 核心）

## 架构

### 独立实现方案

**设计原则：** 完全独立实现，不依赖 rgthree 节点库。

### 类结构

```
DynamicInputBypasserNode
    ↓ 继承
LGraphNode (LiteGraph 基础节点类 - ComfyUI 内置)
```

### 依赖关系

```
DynamicInputBypasserNode
    ↓ 依赖
ComfyUI 核心 API:
    - app (from "../../scripts/app.js")
    - LiteGraph (全局对象)
    - LGraphNode (基类)
```

**无需额外依赖：**
- ❌ 不依赖 rgthree 节点库
- ❌ 不依赖其他第三方库
- ✅ 仅使用 ComfyUI 内置功能

## 组件和接口

### 主要组件

#### 1. DynamicInputBypasserNode 类

```javascript
class DynamicInputBypasserNode extends LGraphNode {
    constructor() {
        super();
        this.title = "Dynamic Input Bypasser";
        this.type = "DynamicInputBypasser";
        
        // 模式配置
        this.modeOn = 0;   // ALWAYS
        this.modeOff = 4;  // BYPASS
        
        // 内部状态
        this._tempWidth = null;
        this._schedulePromise = null;
        
        // 初始化
        this.addInput("", "*");
        this.addOutput("OPT_CONNECTION", "*");
        this.addMasterToggle();
    }
    
    // 核心方法（需要实现）
    addMasterToggle() { }
    getAllConnectedNodes() { }
    setNodeMode(node, mode) { }
    stabilizeInputs() { }
    scheduleStabilize(ms) { }
    onConnectionsChange() { }
    detectCircularConnection() { }
}
```

#### 2. 工具函数模块

需要实现以下独立的工具函数：

```javascript
// 获取连接的节点（跟随透传节点）
function getConnectedNodes(node, inputIndex) { }

// 判断是否为透传节点
function isPassthroughNode(node) { }

// 递归设置节点模式（包括子图）
function setNodesMode(nodes, mode) { }

// 检测循环连接
function hasCircularConnection(fromNode, toNode) { }

// 深度优先遍历子图
function traverseSubgraph(node, callback) { }
```

### 数据模型

```javascript
{
    // 节点基础属性
    id: number,
    type: "DynamicInputBypasser",
    title: string,
    
    // 输入槽位（动态）
    inputs: [
        { name: "[节点标题]", type: "*", link: number },
        // ...
        { name: "", type: "*", link: null }  // 末尾空槽位
    ],
    
    // 输出槽位
    outputs: [
        { name: "OPT_CONNECTION", type: "*", links: [] }
    ],
    
    // 控件（单一主开关）
    widgets: [
        {
            type: "toggle",
            name: "Enable [节点标题]",
            value: boolean,
            options: { on: "yes", off: "no" }
        }
    ],
    
    // 内部状态
    _tempWidth: number | null,
    _schedulePromise: Promise | null
}
```

## 正确性属性

*属性是系统应该满足的形式化规范。*

### 属性 1: 输入槽位不变量
*对于任何* Dynamic Input Bypasser 节点，最后一个输入槽位应当是空的，且只有最后一个可以为空。

**验证需求:** 1.3, 1.4

### 属性 2: 主开关唯一性
*对于任何* Dynamic Input Bypasser 节点，widgets 数组长度应当始终为 1。

**验证需求:** 2.5

### 属性 3: 主开关名称格式
*对于任何* Dynamic Input Bypasser 节点，主开关名称应当为 "[节点标题] YES/NO"。

**验证需求:** 2.6, 3.2, 3.3

### 属性 4: 批量模式设置一致性
*对于任何* Dynamic Input Bypasser 节点，当主开关启用时，所有连接节点的 mode 应当都为 0；禁用时都为 4。

**验证需求:** 2.2, 2.3, 6.1, 6.2

### 属性 5: 主开关状态反映
*对于任何* Dynamic Input Bypasser 节点，当且仅当所有连接节点都处于 mode=0 时，主开关 value 为 true。

**验证需求:** 5.1, 5.2, 5.3

### 属性 6: 透传节点跟随
*对于任何* 通过透传节点连接的输入，系统应当操作最终源节点，而不是透传节点。

**验证需求:** 4.1, 4.2, 4.3, 4.4

### 属性 7: 输入槽位名称同步
*对于任何* 已连接的输入槽位，其名称应当与源节点标题一致。

**验证需求:** 1.6, 4.3

### 属性 8: 自动扩展机制
*对于任何* Dynamic Input Bypasser 节点，当最后一个槽位被连接时，应当自动添加新的空槽位。

**验证需求:** 1.2

### 属性 9: 自动清理机制
*对于任何* Dynamic Input Bypasser 节点，当中间槽位断开时，该空槽位应当被移除。

**验证需求:** 1.3

### 属性 10: 循环连接阻止
*对于任何* Dynamic Input Bypasser 节点，循环连接应当被检测并阻止。

**验证需求:** 9.2, 9.6

### 属性 11: 子图递归处理
*对于任何* 连接的子图节点，设置模式时应当递归处理子图内所有节点。

**验证需求:** 12.1, 12.5

### 属性 12: 防抖机制
*对于任何* Dynamic Input Bypasser 节点，100ms 内的多次连接变化应当只触发一次稳定化。

**验证需求:** 10.1

### 属性 13: 临时宽度保持
*对于任何* Dynamic Input Bypasser 节点，添加/移除槽位时应当保持临时宽度至少 32ms。

**验证需求:** 8.6, 10.6

## 错误处理

### 1. 空引用错误
```javascript
const link = app.graph.links[input.link];
if (!link) continue;

const node = app.graph.getNodeById(link.origin_id);
if (!node) continue;
```

### 2. 循环连接错误
```javascript
onConnectInput(inputIndex, outputType, outputSlot, outputNode) {
    if (this.detectCircularConnection(outputNode)) {
        alert("检测到循环连接！");
        return false;
    }
    return true;
}
```

### 3. 子图无限循环
```javascript
// 使用栈而不是递归，避免栈溢出
function traverseSubgraph(node, callback) {
    const stack = [node];
    const visited = new Set();
    
    while (stack.length > 0) {
        const current = stack.pop();
        if (visited.has(current.id)) continue;
        visited.add(current.id);
        
        callback(current);
        
        if (current.subgraph) {
            stack.push(...current.subgraph.nodes);
        }
    }
}
```

## 测试策略

### 单元测试
- 节点初始化
- 输入槽位管理
- 主开关逻辑
- 工具函数

### 属性测试
- 每个属性至少 100 次迭代
- 使用 fast-check 库

### 集成测试
- 与 Reroute 节点协作
- 与子图节点协作
- 工作流保存/加载

## 实现细节

### 核心方法实现

#### 1. 添加主开关
```javascript
addMasterToggle() {
    const widget = this.addWidget(
        "toggle",
        `Enable ${this.title}`,
        false,
        (value) => {
            const nodes = this.getAllConnectedNodes();
            const mode = value ? this.modeOn : this.modeOff;
            setNodesMode(nodes, mode);
        },
        { on: "yes", off: "no" }
    );
    this.masterToggle = widget;
}
```

#### 2. 获取所有连接节点
```javascript
getAllConnectedNodes() {
    const nodes = [];
    
    // 遍历所有输入（除最后一个空槽位）
    for (let i = 0; i < this.inputs.length - 1; i++) {
        const input = this.inputs[i];
        if (!input.link) continue;
        
        const connectedNodes = getConnectedNodes(this, i);
        nodes.push(...connectedNodes);
    }
    
    return nodes;
}
```

#### 3. 稳定化输入槽位
```javascript
stabilizeInputs() {
    let changed = false;
    
    // 检查最后一个槽位
    const lastInput = this.inputs[this.inputs.length - 1];
    if (lastInput.link) {
        this.addInput("", "*");
        changed = true;
    }
    
    // 移除中间的空槽位
    for (let i = this.inputs.length - 2; i >= 0; i--) {
        const input = this.inputs[i];
        if (!input.link) {
            this.removeInput(i);
            changed = true;
        } else {
            // 更新名称
            const nodes = getConnectedNodes(this, i);
            const newName = nodes[0]?.title || "";
            if (input.name !== newName) {
                input.name = newName;
                changed = true;
            }
        }
    }
    
    return changed;
}
```

#### 4. 连接变化处理
```javascript
onConnectionsChange(type, index, connected, linkInfo) {
    this.scheduleStabilize(100);
}

scheduleStabilize(ms = 100) {
    if (!this._schedulePromise) {
        this._schedulePromise = new Promise((resolve) => {
            setTimeout(() => {
                this._schedulePromise = null;
                this.stabilizeInputs();
                this.syncMasterToggle();
                resolve();
            }, ms);
        });
    }
    return this._schedulePromise;
}
```

### 工具函数实现

#### 1. 获取连接节点（跟随透传）
```javascript
function getConnectedNodes(node, inputIndex) {
    const input = node.inputs[inputIndex];
    if (!input || !input.link) return [];
    
    const link = app.graph.links[input.link];
    if (!link) return [];
    
    let sourceNode = app.graph.getNodeById(link.origin_id);
    if (!sourceNode) return [];
    
    // 跟随透传节点
    while (isPassthroughNode(sourceNode)) {
        const sourceInput = sourceNode.inputs[0];
        if (!sourceInput || !sourceInput.link) break;
        
        const sourceLink = app.graph.links[sourceInput.link];
        if (!sourceLink) break;
        
        const nextNode = app.graph.getNodeById(sourceLink.origin_id);
        if (!nextNode) break;
        
        sourceNode = nextNode;
    }
    
    return [sourceNode];
}
```

#### 2. 判断透传节点
```javascript
function isPassthroughNode(node) {
    const type = node.type || node.constructor?.type || "";
    return type.includes("Reroute") || 
           type.includes("PrimitiveNode");
}
```

#### 3. 递归设置节点模式
```javascript
function setNodesMode(nodes, mode) {
    const stack = [...nodes];
    const visited = new Set();
    
    while (stack.length > 0) {
        const node = stack.pop();
        if (visited.has(node.id)) continue;
        visited.add(node.id);
        
        node.mode = mode;
        
        // 处理子图
        if (node.subgraph && node.subgraph.nodes) {
            stack.push(...node.subgraph.nodes);
        }
    }
}
```

#### 4. 检测循环连接
```javascript
function hasCircularConnection(fromNode, toNode) {
    const visited = new Set();
    const stack = [toNode];
    
    while (stack.length > 0) {
        const current = stack.pop();
        if (visited.has(current.id)) continue;
        if (current.id === fromNode.id) return true;
        visited.add(current.id);
        
        // 检查所有输出连接
        if (current.outputs) {
            for (const output of current.outputs) {
                if (!output.links) continue;
                for (const linkId of output.links) {
                    const link = app.graph.links[linkId];
                    if (!link) continue;
                    const nextNode = app.graph.getNodeById(link.target_id);
                    if (nextNode) stack.push(nextNode);
                }
            }
        }
    }
    
    return false;
}
```

## 部署和集成

### 文件结构
```
ComfyUI-BenNodes/
├── nodes/
│   └── dynamic_input_bypasser.js
├── __init__.py
└── README.md
```

### 节点注册
```javascript
import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ben.DynamicInputBypasser",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "DynamicInputBypasser") {
            // 注册逻辑
        }
    }
});
```

## 总结

Dynamic Input Bypasser 采用**完全独立实现**的方案，不依赖任何第三方节点库。通过参考 rgthree 的设计模式，实现了动态输入管理、单一主开关控制、透传节点跟随等核心功能。这确保了节点在任何 ComfyUI 环境中都能正常工作，无需额外安装依赖。
