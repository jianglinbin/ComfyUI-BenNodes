# ComfyUI-BenNodes

ComfyUI 自定义节点集合，提供图像处理、文本处理、数据转换、AI 分析等功能。

中文 | [English](README_EN.md)

## 📦 安装

### 方法 1：通过 ComfyUI Manager 安装（推荐）

1. 打开 ComfyUI Manager
2. 搜索 "BenNodes"
3. 点击安装

### 方法 2：手动安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/w313185710/ComfyUI-BenNodes.git
cd ComfyUI-BenNodes
pip install -r requirements.txt
```

### 依赖说明

#### 核心依赖（必需）
```bash
pip install zhipuai Pillow psutil
```

#### 增强功能依赖（推荐）
```bash
pip install scipy
```

#### Office 文档处理依赖（可选）
```bash
pip install python-docx openpyxl python-pptx xlrd
```

#### Windows 特定依赖（可选，仅 Windows）
```bash
pip install pywin32
```

#### PDF 和视频处理依赖（可选）
```bash
pip install PyMuPDF opencv-python
```

## 📚 节点分类

- [AI 相关](#ai-相关) (2个节点)
- [数据处理](#数据处理) (5个节点)
- [文件操作](#文件操作) (1个节点)
- [图像处理](#图像处理) (4个节点)
- [系统工具](#系统工具) (3个节点)
- [文本处理](#文本处理) (5个节点)
- [控制流](#控制流) (1个节点)

---

## 🤖 AI 相关

### GLM配置节点 🧠-Ben

**分类**: `BenNodes/AI`

配置 GLM 大模型的参数，包括模型选择、温度、token 限制等。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| vision_model | STRING | glm-4.6v-flash | 视觉模型名称 |
| text_model | STRING | glm-4.5-flash | 文本模型名称 |
| max_pages | INT | 0 | PDF处理最大页数，0表示不限制 |
| max_tokens | INT | 8192 | 模型生成的最大token数 |
| temperature | FLOAT | 0.3 | 控制输出随机性，建议0.1-0.3 |
| top_p | FLOAT | 0.7 | 限制候选词范围，建议0.5-0.7 |
| chunk_mode | COMBO | auto | 大文件处理模式 |
| thinking_enabled | BOOLEAN | True | 是否启用思考功能 |

#### 输出

- **glm_config**: GLM配置对象

#### 使用示例

```
[GLM配置节点] → [GLM多模态分析]
```

---

### GLM多模态分析 🧠-Ben

**分类**: `BenNodes/AI`

使用 GLM 大模型分析图片、视频、PDF、Office 文档或文本文件。

#### 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| prompt | STRING | 分析提示词 |
| system_prompt | STRING | 系统提示词，定义模型角色 |
| input | ANY | 支持图片、视频、文件路径 |
| glm_config | GLM_CONFIG | GLM配置（可选） |
| api_key | STRING | GLM API密钥 |

#### 输出

- **分析结果**: STRING（列表）

#### 支持的文件类型

- **图片**: .jpg, .jpeg, .png, .bmp, .gif, .webp
- **视频**: .mp4, .avi, .mov, .webm, .mkv
- **PDF**: .pdf
- **Word**: .docx, .doc
- **Excel**: .xlsx, .xls
- **PowerPoint**: .pptx, .ppt
- **文本**: .txt, .md, .json, .xml, .csv, .log, .py, .js, .html, .css

#### 使用示例

```
[加载图片] → [GLM多模态分析] → [保存文本]
                ↑
         [GLM配置节点]
```

---

## 📊 数据处理

### 选择分辨率 📐-Ben

**分类**: `BenNodes/数据`

提供预设分辨率和屏幕比例选择，自动计算输出宽度和高度。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| resolution | COMBO | 720p | 预设分辨率 |
| aspect_ratio | COMBO | 16:9 | 屏幕比例 |
| width | INT | 1280 | 自定义宽度 |
| height | INT | 720 | 自定义高度 |

#### 输出

- **width**: INT - 计算后的宽度
- **height**: INT - 计算后的高度
- **resolution_text**: STRING - 分辨率描述

#### 预设分辨率

- 480p, 720p, 1080p, 2K, 4K, 8K, 自定义

#### 预设比例

- 16:9, 4:3, 1:1, 21:9, 9:16, 3:4, 自定义

---

### 列表索引选择器 📌-Ben

**分类**: `BenNodes/数据`

从列表中选择指定索引的元素，支持批量图像处理。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| * | ANY | - | 输入列表 |
| index | STRING | 0 | 索引，支持逗号分隔多个值 |

#### 输出

- **ITEM_0 ~ ITEM_19**: 最多20个输出

#### 使用示例

```
[加载图片批次] → [列表索引选择器] → [保存图片]
                  index: "0,2,4"
```

---

### 索引选择(高级) 🎯-Ben

**分类**: `BenNodes/数据`

高级列表索引选择，支持起始位置、间隔、长度控制。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| list | ANY | - | 输入列表 |
| start_index | INT | 0 | 起始序号 |
| step | INT | 0 | 间隔值，0表示不间隔 |
| length | INT | 1 | 要选择的元素个数 |

#### 输出

- **SELECTED_LIST**: 选择的元素列表

#### 使用示例

```
# 从第5个开始，每隔2个取1个，共取3个
start_index: 5
step: 2
length: 3
结果: [5, 7, 9]
```

---

### JSON解析器 📋-Ben

**分类**: `BenNodes/数据`

解析 JSON 字符串并支持路径提取功能。

#### 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| json_string | STRING | JSON字符串 |
| json_path | STRING | 路径表达式，支持多个路径（分号分隔） |
| output_type | COMBO | 输出数据类型 |

#### 输出

- **JSON_TEXT**: STRING - 格式化的JSON文本
- **PARSED_RESULT**: ANY - 解析后的结果

#### 路径语法

- 简单属性: `name`
- 嵌套属性: `user.name`
- 数组索引: `items[0].name`
- 组合路径: `data.users[1].address.city`
- 多个路径: `name;age;address.city`

#### 使用示例

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

### 类型转换器 🔄-Ben

**分类**: `BenNodes/数据`

将任意类型的输入转换为指定的数据类型。

#### 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| * | ANY | 输入数据 |
| target_type | COMBO | 目标类型 |

#### 支持的类型

- STRING, LIST<STRING>
- INT, LIST<INT>
- FLOAT, LIST<FLOAT>
- BOOLEAN, LIST<BOOLEAN>

#### 转换规则

- 单值 → 单值: 直接转换
- 单值 → 列表: 转换后包装成列表
- 列表 → 单值: 取第一个元素转换
- 列表 → 列表: 对每个元素转换

---

## 📁 文件操作

### 文件选择器 📂-Ben

**分类**: `BenNodes/文件`

从文件系统选择文件，支持图片、视频、文档等多种格式。

#### 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| file_path | STRING | 文件路径选择器 |

#### 输出

- **file_path**: STRING - 文件完整路径
- **file_name**: STRING - 文件名
- **file_extension**: STRING - 文件扩展名

---

## 🖼️ 图像处理

### 加载图片 🖼️-Ben

**分类**: `BenNodes/图像`

加载单张图片，支持多种图片格式和缩放模式。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| image | COMBO | - | 图片文件选择 |
| resize_mode | COMBO | none | 缩放模式 |
| position | COMBO | center | 对齐位置 |
| resolution | COMBO | 720p | 目标分辨率 |
| aspect_ratio | COMBO | 16:9 | 目标比例 |
| width | INT | 1080 | 目标宽度 |
| height | INT | 720 | 目标高度 |
| feathering | INT | 0 | 羽化程度 |
| upscale_method | COMBO | bicubic | 缩放算法 |

#### 输出

- **图片**: IMAGE
- **遮罩**: MASK
- **宽度**: INT
- **高度**: INT
- **文件名**: STRING

#### 缩放模式

- **none**: 不缩放
- **fit**: 适应（保持比例）
- **fill**: 填充（裁剪）
- **stretch**: 拉伸（不保持比例）
- **pad**: 填充黑边

---

### 加载图片批次 🗂️-Ben

**分类**: `BenNodes/图像`

批量加载文件夹中的所有图片。

#### 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| folder_path | COMBO | 文件夹选择 |
| resize_mode | COMBO | 缩放模式 |
| ... | ... | 其他参数同"加载图片" |

#### 输出

- **图片**: IMAGE（批次）
- **遮罩**: MASK（批次）
- **宽度**: INT
- **高度**: INT
- **文件名**: STRING（列表）

---

### 图像缩放 🎨-Ben

**分类**: `BenNodes/图像`

对图像进行缩放、裁剪、填充等操作，支持批量处理。

#### 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| image | IMAGE | 输入图像 |
| resize_mode | COMBO | 缩放模式 |
| position | COMBO | 对齐位置 |
| resolution | COMBO | 目标分辨率 |
| aspect_ratio | COMBO | 目标比例 |
| width | INT | 目标宽度 |
| height | INT | 目标高度 |
| feathering | INT | 羽化程度 |
| upscale_method | COMBO | 缩放算法 |
| pad_color | STRING | 填充颜色（RGB） |

#### 输出

- **IMAGE**: 处理后的图像
- **MASK**: 遮罩
- **width**: INT
- **height**: INT

#### 缩放算法

- nearest, bilinear, bicubic, lanczos

---

### 空Latent 🎯-Ben

**分类**: `BenNodes/图像`

创建空的 Latent 图像，用于图像生成。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| resolution | COMBO | 1080p | 分辨率 |
| aspect_ratio | COMBO | 16:9 | 比例 |
| width | INT | 1920 | 宽度 |
| height | INT | 1080 | 高度 |
| batch_size | INT | 1 | 批次大小 |

#### 输出

- **LATENT**: 空的 Latent 图像

---

## 🔧 系统工具

### 释放显存内存 🧹-Ben

**分类**: `BenNodes/系统`

清理显存和内存，优化系统资源使用。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| cleanup_mode | COMBO | 全部 | 清理模式 |
| input | ANY | - | 输入数据（透传） |

#### 清理模式

- **无**: 不清理
- **仅显存**: 只清理显存
- **仅内存**: 只清理内存
- **全部**: 清理显存和内存

#### 输出

- **output**: ANY - 透传输入数据

#### 使用场景

在工作流中间插入，清理不需要的模型和缓存：

```
[生成图像] → [释放显存内存] → [放大图像]
```

---

### 非空切换 🔄-Ben

**分类**: `BenNodes/系统`

优先输出默认参数，若为空则输出备选参数。

#### 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| default | ANY | 默认输入（可选） |
| alternative | ANY | 备选输入（可选） |

#### 输出

- **output**: ANY

#### 工作逻辑

1. 如果 default 不为空，返回 default
2. 否则，如果 alternative 不为空，返回 alternative
3. 否则，抛出错误

#### 使用场景

配合"忽略节点"使用，解决前置节点被 bypass 时的数据缺失：

```
[节点A] ──→ [非空切换] ──→ [节点C]
            ↑ default
[节点B] ────┘ alternative
```

---

### 忽略节点 🔀-Ben

**分类**: `BenNodes/控制`

通过单个主开关控制多个连接节点的执行状态。

#### 特性

- 动态输入槽位自动管理
- 单一主开关控制所有连接节点
- 透传节点自动跟随
- 完全独立实现

#### 使用方法

1. 添加"忽略节点"到工作流
2. 将需要控制的节点连接到"忽略节点"的输入
3. 使用开关控制所有连接节点的启用/忽略状态

#### 开关状态

- **yes**: 启用所有连接的节点
- **no**: 忽略（bypass）所有连接的节点

#### 注意事项

⚠️ 当节点被忽略时，它不会执行，也不会产生输出。如果后续节点依赖这个输出，会报错。建议配合"非空切换"节点使用。

---

## 📝 文本处理

### 提示词行处理器 📝-Ben

**分类**: `BenNodes/文本`

处理多行提示词，支持提取指定范围的行并应用操作。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| prompt | STRING | - | 多行文本 |
| start_index | INT | 0 | 起始行号 |
| max_rows | INT | 1000 | 最多返回行数 |
| operation | COMBO | 原始 | 文本操作 |

#### 支持的操作

- 原始, 大写, 小写, 首字母大写, 标题格式
- 去除空白, 反转, 长度, 去除空行

#### 输出

- **STRING**: 处理后的文本（列表）

---

### 保存文本 📄-Ben

**分类**: `BenNodes/文本`

将文本或文本批次保存到文件。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| texts | STRING | - | 要保存的文本 |
| filename_prefix | STRING | ComfyUI | 文件名前缀 |
| file_extension | STRING | .txt | 文件扩展名 |
| filename | STRING | - | 可选的文件名 |

#### 输出

- UI 显示保存的文件列表

#### 使用示例

```
[GLM分析] → [保存文本]
            filename_prefix: "analysis"
            file_extension: ".md"
```

---

### 文本拆分 📝-Ben

**分类**: `BenNodes/文本`

按指定分隔符拆分文本。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| text | STRING | - | 输入文本 |
| delimiter | STRING | \n | 分隔符 |
| start_index | INT | 0 | 起始索引 |
| max_rows | INT | 1000 | 最多返回数量 |

#### 输出

- **STRING**: 拆分后的文本列表

---

### 文本连接（支持列表） 📝-Ben

**分类**: `BenNodes/文本`

连接两个文本或文本列表。

#### 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| text1 | STRING | 第一个文本 |
| text2 | STRING | 第二个文本 |
| delimiter | STRING | 分隔符 |

#### 连接规则

- 两个字符串 → 直接连接
- 字符串 + 列表 → 字符串与列表每个元素连接
- 列表 + 字符串 → 列表每个元素与字符串连接

#### 输出

- **连接结果**: STRING 或 STRING列表

---

### 文本处理器 ✏️-Ben

**分类**: `BenNodes/文本`

处理多行文本，支持去除空行、空白字符等操作。

#### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| text | STRING | - | 多行文本 |
| process_type | COMBO | none | 处理类型 |

#### 处理类型

- **none**: 不处理
- **去除空行**: 删除空行
- **去除空白字符**: 删除每行首尾空白
- **去除空白字符+空行**: 两者都删除

#### 输出

- **文本**: STRING - 完整文本
- **文本列表**: STRING - 按行分割的列表

---

## 🔄 控制流

### 忽略节点 🔀-Ben

详见 [系统工具 - 忽略节点](#忽略节点--ben)

---

## 💡 使用技巧

### 1. 图像批量处理

```
[加载图片批次] → [列表索引选择器] → [图像缩放] → [保存图片]
                  index: "0,2,4,6"
```

### 2. 条件数据流

```
[节点A] ──→ [非空切换] ──→ [保存]
            ↑ default
[节点B] ────┘ alternative
```

### 3. 内存优化

```
[大模型生成] → [释放显存内存] → [图像放大] → [释放显存内存] → [保存]
```

### 4. 文本批量处理

```
[加载文本] → [文本拆分] → [提示词行处理器] → [文本连接] → [保存文本]
```

### 5. AI 分析工作流

```
[加载图片] → [GLM多模态分析] → [JSON解析器] → [保存文本]
                ↑
         [GLM配置节点]
```

---

## 🐛 常见问题

### Q: 节点无法加载？

A: 检查依赖是否安装完整：
```bash
pip install -r requirements.txt
```

### Q: GLM 节点报错？

A: 确保已安装 `zhipuai` 并提供有效的 API 密钥。

### Q: Office 文档无法处理？

A: 安装 Office 文档处理依赖：
```bash
pip install python-docx openpyxl python-pptx
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

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📮 联系方式

- GitHub: [w313185710/ComfyUI-BenNodes](https://github.com/w313185710/ComfyUI-BenNodes)
- Issues: [提交问题](https://github.com/w313185710/ComfyUI-BenNodes/issues)

---

## 🙏 致谢

感谢 ComfyUI 社区的支持和贡献！

---

**最后更新**: 2024年
