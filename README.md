# ComfyUI-BenNodes

ComfyUI 自定义节点集合，提供 25 个实用节点，涵盖图像处理、文本处理、数据转换、AI 分析、系统工具和工作流控制等功能。

中文 | [English](README_EN.md)

## ✨ 特性

- 🖼️ **图像处理**: 智能缩放、批量加载、多种对齐模式
- 📝 **文本处理**: 拆分、连接、保存、多行处理
- 📊 **数据转换**: JSON 解析、类型转换、列表选择器
- 🤖 **AI 分析**: GLM 多模态分析，支持图片、视频、PDF、Office 文档
- 🔧 **系统工具**: 内存清理、非空切换、文件选择器
- 🎮 **工作流控制**: 节点忽略、组忽略、参数分发器

## 📦 安装

### 方法 1：通过 ComfyUI Manager 安装（推荐）

1. 打开 ComfyUI Manager
2. 搜索 "BenNodes"
3. 点击安装

### 方法 2：手动安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/jianglinbin/ComfyUI-BenNodes.git
cd ComfyUI-BenNodes
pip install -r requirements.txt
```

## 📚 节点列表

### 🤖 AI 相关 (2个)
- **GLM配置** - 配置 GLM 模型参数
- **GLM多模态分析** - 分析图片、视频、PDF、Office 文档

### 📊 数据处理 (5个)
- **选择分辨率** - 预设分辨率和比例选择
- **列表索引选择器** - 从列表中选择指定索引元素
- **索引选择(高级)** - 支持起始、间隔、长度控制
- **JSON解析器** - 解析 JSON 并支持路径提取
- **类型转换器** - 任意类型转换

### 📁 文件操作 (1个)
- **文件选择器** - 从文件系统选择文件

### 🖼️ 图像处理 (4个)
- **加载图片** - 加载单张图片
- **加载图片批次** - 批量加载文件夹图片
- **图像缩放** - 缩放、裁剪、填充
- **空Latent** - 创建空 Latent 图像

### 🔧 系统工具 (1个)
- **释放显存内存** - 清理显存和内存


### 📝 文本处理 (5个)
- **提示词行处理器** - 处理多行提示词
- **保存文本** - 保存文本到文件
- **文本拆分** - 按分隔符拆分文本
- **文本连接** - 连接文本或列表
- **文本处理器** - 去除空行、空白字符

### 🎮 工作流控制 (7个)
- **非空切换** - 优先输出非空值
- **忽略节点** - 控制多个节点的执行状态
- **忽略节点(高级)** - 基于 JSON 规则的条件激活
- **忽略组** - 控制组的执行状态
- **忽略组(高级)** - 基于 JSON 规则的组控制
- **参数分发器** - 动态参数分发和复制

---

## 🔧 依赖说明

### 核心依赖（必需）
```bash
pip install Pillow psutil
```

### AI 功能依赖（使用 GLM 节点时需要）
```bash
pip install zhipuai
```

### 图像增强依赖（推荐，用于羽化效果）
```bash
pip install scipy
```

### Office 文档处理依赖（可选）
```bash
pip install python-docx openpyxl python-pptx xlrd
```

### Windows 特定依赖（可选，仅 Windows）
```bash
pip install pywin32
```

### PDF 和视频处理依赖（可选）
```bash
pip install PyMuPDF opencv-python
```

---

## 📖 详细文档


### 🤖 AI 相关

#### GLM配置

**分类**: `BenNodes/AI`

配置 GLM 大模型的参数，包括模型选择、温度、token 限制等。

**输入参数**:
- `vision_model` (STRING): 视觉模型名称，默认 "glm-4.6v-flash"
- `text_model` (STRING): 文本模型名称，默认 "glm-4.5-flash"
- `max_pages` (INT): PDF 处理最大页数，0 表示不限制
- `max_tokens` (INT): 模型生成的最大 token 数，默认 8192
- `temperature` (FLOAT): 控制输出随机性，建议 0.1-0.3
- `top_p` (FLOAT): 限制候选词范围，建议 0.5-0.7
- `chunk_mode` (COMBO): 大文件处理模式（auto/manual）
- `thinking_enabled` (BOOLEAN): 是否启用思考功能

**输出**:
- `glm_config`: GLM 配置对象

**使用示例**:
```
[GLM配置] → [GLM多模态分析]
```

---

#### GLM多模态分析

**分类**: `BenNodes/AI`

使用 GLM 大模型分析图片、视频、PDF、Office 文档或文本文件，支持大文件分块处理。

**输入参数**:
- `prompt` (STRING): 分析提示词
- `system_prompt` (STRING): 系统提示词，定义模型角色和行为
- `input` (ANY): 支持 ComfyUI 图片、视频数据类型，或文件路径字符串
- `glm_config` (GLM_CONFIG): GLM 配置节点（可选）
- `api_key` (STRING): GLM API 密钥

**输出**:
- `分析结果` (STRING LIST): 分析结果列表

**支持的文件类型**:
- 图片: .jpg, .jpeg, .png, .bmp, .gif, .webp
- 视频: .mp4, .avi, .mov, .webm, .mkv
- PDF: .pdf
- Word: .docx, .doc
- Excel: .xlsx, .xls
- PowerPoint: .pptx, .ppt
- 文本: .txt, .md, .json, .xml, .csv, .log, .py, .js, .html, .css

**使用示例**:
```
[加载图片] → [GLM多模态分析] → [保存文本]
                ↑
         [GLM配置节点]
```

---


### 📊 数据处理

#### 选择分辨率

**分类**: `BenNodes/数据`

提供预设分辨率和屏幕比例选择，自动计算输出宽度和高度。

**输入参数**:
- `resolution` (COMBO): 预设分辨率（480p/720p/1080p/2K/4K/8K/自定义）
- `aspect_ratio` (COMBO): 屏幕比例（16:9/4:3/1:1/21:9/9:16/3:4/自定义）
- `width` (INT): 自定义宽度，默认 1280
- `height` (INT): 自定义高度，默认 720

**输出**:
- `width` (INT): 计算后的宽度
- `height` (INT): 计算后的高度
- `resolution_text` (STRING): 分辨率描述

---

#### 列表索引选择器

**分类**: `BenNodes/数据`

从列表中选择指定索引的元素，支持批量图像处理。

**输入参数**:
- `*` (ANY): 输入列表
- `index` (STRING): 索引，支持逗号分隔多个值，如 "0,2,4"

**输出**:
- `ITEM_0 ~ ITEM_19`: 最多 20 个输出

**使用示例**:
```
[加载图片批次] → [列表索引选择器] → [保存图片]
                  index: "0,2,4"
```

---

#### 索引选择(高级)

**分类**: `BenNodes/数据`

高级列表索引选择，支持起始位置、间隔、长度控制。

**输入参数**:
- `list` (ANY): 输入列表
- `start_index` (INT): 起始序号，默认 0
- `step` (INT): 间隔值，0 表示不间隔
- `length` (INT): 要选择的元素个数，默认 1

**输出**:
- `SELECTED_LIST`: 选择的元素列表

**使用示例**:
```
# 从第 5 个开始，每隔 2 个取 1 个，共取 3 个
start_index: 5
step: 2
length: 3
结果: [5, 7, 9]
```

---

#### JSON解析器

**分类**: `BenNodes/数据`

解析 JSON 字符串并支持路径提取功能。

**输入参数**:
- `json_string` (STRING): JSON 字符串
- `json_path` (STRING): 路径表达式，支持多个路径（分号分隔）
- `output_type` (COMBO): 输出数据类型

**输出**:
- `JSON_TEXT` (STRING): 格式化的 JSON 文本
- `PARSED_RESULT` (ANY): 解析后的结果

**路径语法**:
- 简单属性: `name`
- 嵌套属性: `user.name`
- 数组索引: `items[0].name`
- 组合路径: `data.users[1].address.city`
- 多个路径: `name;age;address.city`

**使用示例**:
```json
{
  "user": {
    "name": "张三",
    "age": 25
  }
}
```
路径: `user.name` → 输出: "张三"

---

#### 类型转换器

**分类**: `BenNodes/数据`

将任意类型的输入转换为指定的数据类型。

**输入参数**:
- `*` (ANY): 输入数据
- `target_type` (COMBO): 目标类型

**支持的类型**:
- STRING, LIST<STRING>
- INT, LIST<INT>
- FLOAT, LIST<FLOAT>
- BOOLEAN, LIST<BOOLEAN>

**转换规则**:
- 单值 → 单值: 直接转换
- 单值 → 列表: 转换后包装成列表
- 列表 → 单值: 取第一个元素转换
- 列表 → 列表: 对每个元素转换

---


### 📁 文件操作

#### 文件选择器

**分类**: `BenNodes/文件`

从文件系统选择文件，支持图片、视频、文档等多种格式。

**输入参数**:
- `file_path` (STRING): 文件路径选择器

**输出**:
- `file_path` (STRING): 文件完整路径
- `file_name` (STRING): 文件名
- `file_extension` (STRING): 文件扩展名

---

### 🖼️ 图像处理

#### 加载图片

**分类**: `BenNodes/图像`

加载单张图片，支持多种图片格式和缩放模式。

**输入参数**:
- `image` (COMBO): 图片文件选择
- `resize_mode` (COMBO): 缩放模式（none/fit/fill/stretch/pad）
- `position` (COMBO): 对齐位置（center/top/bottom/left/right 等）
- `resolution` (COMBO): 目标分辨率
- `aspect_ratio` (COMBO): 目标比例
- `width` (INT): 目标宽度，默认 1080
- `height` (INT): 目标高度，默认 720
- `feathering` (INT): 羽化程度，默认 0
- `upscale_method` (COMBO): 缩放算法（nearest/bilinear/bicubic/lanczos）

**输出**:
- `图片` (IMAGE): 处理后的图片
- `遮罩` (MASK): 遮罩
- `宽度` (INT): 图片宽度
- `高度` (INT): 图片高度
- `文件名` (STRING): 文件名

**缩放模式说明**:
- `none`: 不缩放
- `fit`: 适应（保持比例，可能有黑边）
- `fill`: 填充（裁剪以填满）
- `stretch`: 拉伸（不保持比例）
- `pad`: 填充黑边

---

#### 加载图片批次

**分类**: `BenNodes/图像`

批量加载文件夹中的所有图片。

**输入参数**:
- `folder_path` (COMBO): 文件夹选择
- 其他参数同"加载图片"

**输出**:
- `图片` (IMAGE): 图片批次
- `遮罩` (MASK): 遮罩批次
- `宽度` (INT): 图片宽度
- `高度` (INT): 图片高度
- `文件名` (STRING LIST): 文件名列表

---

#### 图像缩放

**分类**: `BenNodes/图像`

对图像进行缩放、裁剪、填充等操作，支持批量处理和多线程加速。

**输入参数**:
- `image` (IMAGE): 输入图像
- `resize_mode` (COMBO): 缩放模式
- `position` (COMBO): 对齐位置
- `resolution` (COMBO): 目标分辨率
- `aspect_ratio` (COMBO): 目标比例
- `width` (INT): 目标宽度
- `height` (INT): 目标高度
- `feathering` (INT): 羽化程度
- `upscale_method` (COMBO): 缩放算法
- `pad_color` (STRING): 填充颜色（RGB 格式，如 "127,127,127"）

**输出**:
- `IMAGE`: 处理后的图像
- `MASK`: 遮罩
- `width` (INT): 宽度
- `height` (INT): 高度

**特性**:
- 支持批量处理
- 多线程加速
- 自定义填充颜色
- 羽化效果（需要 scipy）

---

#### 空Latent

**分类**: `BenNodes/图像`

创建空的 Latent 图像，用于图像生成。

**输入参数**:
- `resolution` (COMBO): 分辨率，默认 1080p
- `aspect_ratio` (COMBO): 比例，默认 16:9
- `width` (INT): 宽度，默认 1920
- `height` (INT): 高度，默认 1080
- `batch_size` (INT): 批次大小，默认 1

**输出**:
- `LATENT`: 空的 Latent 图像

---


### 🔧 系统工具

#### 释放显存内存

**分类**: `BenNodes/控制`

清理显存和内存，优化系统资源使用。

**输入参数**:
- `cleanup_mode` (COMBO): 清理模式（无/仅显存/仅内存/全部），默认"全部"
- `input` (ANY): 输入数据（透传）

**输出**:
- `output` (ANY): 透传输入数据

**清理模式说明**:
- `无`: 不执行任何清理，直接透传
- `仅显存`: 卸载模型、清空缓存
- `仅内存`: 清理文件缓存、进程内存、DLL
- `全部`: 同时清理显存和内存

**使用场景**:
在工作流中间插入，清理不需要的模型和缓存：
```
[生成图像] → [释放显存内存] → [放大图像]
```

---

### 📝 文本处理

#### 提示词行处理器

**分类**: `BenNodes/文本`

处理多行提示词，支持提取指定范围的行并应用操作。

**输入参数**:
- `prompt` (STRING): 多行文本
- `start_index` (INT): 起始行号，默认 0
- `max_rows` (INT): 最多返回行数，默认 1000
- `operation` (COMBO): 文本操作

**支持的操作**:
- 原始, 大写, 小写, 首字母大写, 标题格式
- 去除空白, 反转, 长度, 去除空行

**输出**:
- `STRING`: 处理后的文本（列表）

---

#### 保存文本

**分类**: `BenNodes/文本`

将文本或文本批次保存到文件。

**输入参数**:
- `texts` (STRING): 要保存的文本
- `filename_prefix` (STRING): 文件名前缀，默认 "ComfyUI"
- `file_extension` (STRING): 文件扩展名，默认 ".txt"
- `filename` (STRING): 可选的文件名

**输出**:
- UI 显示保存的文件列表

**使用示例**:
```
[GLM分析] → [保存文本]
            filename_prefix: "analysis"
            file_extension: ".md"
```

---

#### 文本拆分

**分类**: `BenNodes/文本`

按指定分隔符拆分文本。

**输入参数**:
- `text` (STRING): 输入文本
- `delimiter` (STRING): 分隔符，默认 "\n"
- `start_index` (INT): 起始索引，默认 0
- `max_rows` (INT): 最多返回数量，默认 1000

**输出**:
- `STRING`: 拆分后的文本列表

---

#### 文本连接

**分类**: `BenNodes/文本`

连接两个文本或文本列表。

**输入参数**:
- `text1` (STRING): 第一个文本
- `text2` (STRING): 第二个文本
- `delimiter` (STRING): 分隔符

**连接规则**:
- 两个字符串 → 直接连接
- 字符串 + 列表 → 字符串与列表每个元素连接
- 列表 + 字符串 → 列表每个元素与字符串连接
- 列表 + 列表 → 对应位置元素连接

**输出**:
- `连接结果` (STRING 或 STRING LIST)

---

#### 文本处理器

**分类**: `BenNodes/文本`

处理多行文本，支持去除空行、空白字符等操作。

**输入参数**:
- `text` (STRING): 多行文本
- `process_type` (COMBO): 处理类型，默认 "none"

**处理类型**:
- `none`: 不处理
- `去除空行`: 删除空行
- `去除空白字符`: 删除每行首尾空白
- `去除空白字符+空行`: 两者都删除

**输出**:
- `文本` (STRING): 完整文本
- `文本列表` (STRING): 按行分割的列表

---


### 🎮 工作流控制

#### 非空切换

**分类**: `BenNodes/控制`

按顺序检查多个输入，返回第一个非空值，支持多级容错切换。

**输入参数**:
- `主数据源` (ANY): 主要输入（可选）
- `备选1` (ANY): 第一个备选输入（可选）
- `备选2~备选N` (ANY): 更多备选输入（动态添加）

**输出**:
- `output` (ANY): 第一个非空值

**工作逻辑**:
1. 检查"主数据源"，如果非空则返回
2. 否则检查"备选1"，如果非空则返回
3. 继续检查"备选2"、"备选3"...
4. 如果所有输入都为空，抛出错误

**特性**:
- 动态输入管理：当两个输入都连接后，自动添加新的备选输入
- 支持最多 20 个输入
- 多级容错切换

**使用场景**:
配合"忽略节点"使用，解决前置节点被 bypass 时的数据缺失：
```
[节点A] ──→ [非空切换] ──→ [节点C]
            ↑ 主数据源
[节点B] ────┘ 备选1
```

---

#### 忽略节点

**分类**: `BenNodes/控制`

通过单个主开关控制多个连接节点的执行状态。

**特性**:
- 动态输入槽位自动管理
- 单一主开关控制所有连接节点
- 透传节点自动跟随
- 完全独立实现

**使用方法**:
1. 添加"忽略节点"到工作流
2. 将需要控制的节点连接到"忽略节点"的输入
3. 使用开关控制所有连接节点的启用/忽略状态

**开关状态**:
- `yes`: 启用所有连接的节点
- `no`: 忽略（bypass）所有连接的节点

**注意事项**:
⚠️ 当节点被忽略时，它不会执行，也不会产生输出。如果后续节点依赖这个输出，会报错。建议配合"非空切换"节点使用。

---

#### 忽略节点(高级)

**分类**: `BenNodes/控制`

支持基于 JSON 规则的条件激活，可以定义多个规则集，每个规则集控制不同的节点组合。

**输入参数**:
- `json_rules` (STRING): JSON 规则配置

**JSON 规则格式**:
```json
{
  "规则A": [1, 2, 3],
  "规则B": [4, 5, 6]
}
```

**说明**:
- 键: 规则的显示名称
- 值: 要激活的输入 ID 数组（从 1 开始）
- 选择规则后，对应 ID 的输入会被激活，其他输入会被禁用

**使用场景**:
- 复杂工作流的场景切换
- 多套参数配置快速切换
- A/B 测试

---

#### 忽略组

**分类**: `BenNodes/控制`

通过选择组名和开关控制组的执行状态。

**特性**:
- COMBO 选择组名（自动更新组列表）
- BOOL 开关控制组的激活/忽略状态
- 开启 = 激活组，关闭 = 忽略组

**使用方法**:
1. 在工作流中创建组（选中多个节点右键 → Convert to Group）
2. 添加"忽略组"节点
3. 从下拉列表选择要控制的组
4. 使用开关控制组的启用/忽略状态

---

#### 忽略组(高级)

**分类**: `BenNodes/控制`

支持基于 JSON 规则的条件激活组，无需连接，自动遍历所有组。

**输入参数**:
- `json_rules` (STRING): JSON 规则配置

**JSON 规则格式**:
```json
{
  "规则A": ["组1", "组2"],
  "规则B": ["组3", "组4"]
}
```

**说明**:
- 键: 规则的显示名称
- 值: 要激活的组名称数组
- 选择规则后，对应名称的组会被激活，其他组会被禁用

**使用场景**:
- 多场景工作流切换
- 批量控制多个组
- 复杂工作流管理

---

#### 参数分发器

**分类**: `BenNodes/控制`

动态参数分发和复制，当输出被连接时自动复制该输出参数，并添加新的空输出槽位。

**特性**:
- 动态输出槽位自动管理
- 输出被连接后自动添加新输出
- 支持任意类型的数据传递
- 每个输出独立配置
- 参数锁定功能

**输出**:
- 最多 20 个动态输出

**使用方法**:
1. 添加"参数分发器"节点
2. 在节点上配置参数值
3. 连接输出到需要该参数的节点
4. 连接后会自动添加新的输出槽位
5. 可以锁定参数防止意外修改

**使用场景**:
- 一个参数分发给多个节点
- 参数复用和管理
- 工作流参数集中配置

---


## 💡 使用技巧

### 1. 图像批量处理工作流

```
[加载图片批次] → [列表索引选择器] → [图像缩放] → [保存图片]
                  index: "0,2,4,6"
```

### 2. 多级容错数据流

```
[主节点] ──→ [非空切换] ──→ [后续处理]
            ↑ 主数据源
[备选1] ────┤ 备选1
            │
[备选2] ────┘ 备选2
```

### 3. 内存优化工作流

```
[大模型生成] → [释放显存内存] → [图像放大] → [释放显存内存] → [保存]
              cleanup_mode: 全部          cleanup_mode: 仅显存
```

### 4. 文本批量处理

```
[加载文本] → [文本拆分] → [提示词行处理器] → [文本连接] → [保存文本]
            delimiter: \n   operation: 去除空行
```

### 5. AI 分析工作流

```
[文件选择器] → [GLM多模态分析] → [JSON解析器] → [保存文本]
                    ↑
              [GLM配置节点]
              api_key: "your_key"
```

### 6. 场景切换工作流

```
[忽略组(高级)]
json_rules: {
  "场景A": ["生成组", "放大组"],
  "场景B": ["生成组", "风格化组"],
  "场景C": ["生成组", "放大组", "风格化组"]
}
```

### 7. 参数集中管理

```
[参数分发器] ──→ [节点A]
            ├──→ [节点B]
            ├──→ [节点C]
            └──→ [节点D]
```

---

## 🐛 常见问题

### Q: 节点无法加载？

A: 检查依赖是否安装完整：
```bash
pip install -r requirements.txt
```

### Q: GLM 节点报错？

A: 确保已安装 `zhipuai` 并提供有效的 API 密钥：
```bash
pip install zhipuai
```

### Q: Office 文档无法处理？

A: 安装 Office 文档处理依赖：
```bash
pip install python-docx openpyxl python-pptx xlrd
```

Windows 系统还需要：
```bash
pip install pywin32
```

### Q: 图像羽化效果不佳？

A: 安装 scipy 以获得更好的羽化效果：
```bash
pip install scipy
```

### Q: 内存清理节点报错？

A: 确保已安装 psutil：
```bash
pip install psutil
```

### Q: 忽略节点不工作？

A: 确保：
1. 节点已正确连接
2. 开关状态正确设置
3. 如果后续节点报错，使用"非空切换"节点提供备选数据

### Q: 参数分发器输出为空？

A: 确保：
1. 在节点上配置了参数值
2. 输出已连接到其他节点
3. 检查参数是否被锁定

---

## 🔄 更新日志

### v1.0.0 (2026-01-04)

**新增功能**:
- ✨ 新增 7 个工作流控制节点
  - 非空切换：多级容错切换
  - 忽略节点：控制多个节点执行
  - 忽略节点(高级)：基于 JSON 规则
  - 忽略组：控制组执行
  - 忽略组(高级)：基于 JSON 规则
  - 参数分发器：动态参数分发
- 🎨 图像处理节点支持自定义填充颜色
- 🚀 图像缩放支持多线程批量处理
- 📝 文本处理器支持多种处理模式

**改进**:
- 🔧 统一节点命名规范（所有节点以 Ben 结尾）
- 📚 完善节点文档和使用说明
- 🎯 优化内存清理逻辑
- 🐛 修复已知问题

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📮 联系方式

- GitHub: [jianglinbin/ComfyUI-BenNodes](https://github.com/jianglinbin/ComfyUI-BenNodes)
- Issues: [提交问题](https://github.com/jianglinbin/ComfyUI-BenNodes/issues)

---

## 🙏 致谢

感谢 ComfyUI 社区的支持和贡献！

---

**最后更新**: 2026年1月4日
