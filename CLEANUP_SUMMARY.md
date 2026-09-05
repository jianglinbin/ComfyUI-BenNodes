# 项目清理总结

## 清理时间
2026-01-04

## 已删除的冗余文件

### 1. 开发脚本
- ✅ `rename_all_to_ben.bat` - 重命名脚本（已完成任务）
- ✅ `sync_and_push_local.bat` - 同步脚本（包含敏感 token）

### 2. 空文件
- ✅ `WORKFLOW_GUIDE.md` - 空的工作流指南

### 3. 冗余测试文件
- ✅ `tests/test_simple.py` - 简单测试（功能已被 test_all_nodes.py 包含）
- ✅ `tests/test_registration.py` - 注册测试（功能已被 test_all_nodes.py 包含）

### 4. 缓存目录
- ✅ `__pycache__/` - Python 字节码缓存（所有子目录）
- ✅ `.pytest_cache/` - Pytest 缓存

## 保留的文件

### 核心文件
- `__init__.py` - 主入口文件
- `requirements.txt` - 依赖列表
- `README.md` - 中文说明文档
- `README_EN.md` - 英文说明文档

### 配置文件
- `.gitignore` - Git 忽略规则（已更新）
- `comfyui-manager-submission.json` - ComfyUI Manager 配置

### 示例文件
- `example_workflow_all_nodes.json` - 包含所有节点的示例工作流

### 测试文件
- `tests/test_all_nodes.py` - 全面的测试脚本
- `tests/TEST_SUMMARY.md` - 测试总结文档

### 代码目录
- `nodes/` - 所有节点实现（24个节点）
- `js/` - 前端 JavaScript 扩展（15个文件）
- `utils/` - 工具函数

## 更新的文件

### .gitignore
- 添加了 `.pytest_cache/` 忽略规则
- 添加了测试覆盖率相关忽略规则
- 清理了冗余的忽略规则
- 移除了 `tests/` 目录的忽略（测试文件应该被提交）

## 项目结构（清理后）

```
ComfyUI-BenNodes/
├── .git/                           # Git 仓库
├── .gitignore                      # Git 忽略规则
├── __init__.py                     # 主入口
├── requirements.txt                # 依赖
├── README.md                       # 中文文档
├── README_EN.md                    # 英文文档
├── comfyui-manager-submission.json # ComfyUI Manager 配置
├── example_workflow_all_nodes.json # 示例工作流
├── CLEANUP_SUMMARY.md              # 本文件
├── nodes/                          # 节点实现
│   ├── ai/                         # AI 节点 (2个)
│   ├── data/                       # 数据节点 (5个)
│   ├── file/                       # 文件节点 (1个)
│   ├── image/                      # 图像节点 (4个)
│   ├── system/                     # 系统节点 (7个)
│   └── text/                       # 文本节点 (5个)
├── js/                             # 前端扩展 (15个文件)
├── tests/                          # 测试文件
│   ├── test_all_nodes.py          # 全面测试
│   └── TEST_SUMMARY.md            # 测试总结
└── utils/                          # 工具函数
```

## 统计信息

### 节点统计
- **总节点数**: 24 个
- **控制类**: 7 个
- **数据类**: 5 个
- **文本类**: 5 个
- **图像类**: 4 个
- **AI类**: 2 个
- **文件类**: 1 个

### 文件统计
- **Python 节点文件**: 24 个
- **JavaScript 扩展**: 15 个
- **测试文件**: 1 个
- **文档文件**: 4 个

## 清理效果

### 删除的文件数量
- 脚本文件: 2 个
- 测试文件: 2 个
- 空文件: 1 个
- 缓存目录: 所有 `__pycache__` 和 `.pytest_cache`

### 项目更整洁
- ✅ 移除了所有冗余文件
- ✅ 清理了所有缓存目录
- ✅ 更新了 .gitignore 规则
- ✅ 保留了所有必要文件
- ✅ 项目结构清晰明了

## 下一步建议

1. **提交更改**: 将清理后的项目提交到 Git
2. **测试验证**: 运行 `python tests/test_all_nodes.py` 确保所有节点正常
3. **文档更新**: 根据需要更新 README 文档
4. **发布**: 可以考虑发布到 ComfyUI Manager

## 注意事项

- 所有 `__pycache__` 目录已被 .gitignore 忽略，不会再被提交
- 敏感信息（如 token）已从项目中移除
- 测试文件保留，方便后续开发和验证

---

# 2026-09-05 深度重构与 i18n 记录

> 本节为最新状态，覆盖上文中的旧统计（24 节点 / ai 目录等已过时）。

## 移除 LLM 相关代码

- 删除 `nodes/ai/` 整个目录（GLMNodeBen、GLMConfigNodeBen 及 processors）
- 清理 `requirements.txt` 中 GLM 专属依赖（zhipuai、PyMuPDF、opencv-python 等）
- 同步清理 `__init__.py`、示例工作流、`comfyui-manager-submission.json`、README 中相关内容

## Bug 修复

- `ImageBatchLoaderBen`: 多线程批次顺序错乱 → 按原始索引回填
- `AdvancedListIndexSelectorBen`: 参数名 `list` 遮蔽内建类型导致崩溃 → `_BUILTIN_LIST/_BUILTIN_TUPLE`；步长语义与 tooltip 对齐
- `image_utils.apply_feather`: 重复计算删除；遮罩语义注释修正（255=被遮蔽）

## 死代码 / 冗余清理

- 移除重复 `AnyType` 定义、未使用函数与导入、死注册表、AI 思考注释残留
- 日志规范化：全部 `print()` → `logger`，删除模块级 `basicConfig()`

## 前端重构

- 提取 `js/shared.js`（分辨率控件联动）与 `js/bypasser_common.js`（bypasser 公共逻辑）
- 前后端常量（ASPECT_RATIOS 等）对齐

## i18n 中英双语

- 新增 `utils/i18n/`（`t()` 查表 + zh/en 词典各 106 key）
- 语言优先级：`BENNODES_LANG` 环境变量 → `ben_nodes_config.json` → 默认 `zh`
- 覆盖范围：22 个节点的显示名、CATEGORY、tooltip/placeholder、DESCRIPTION、错误消息、RETURN_NAMES
- 前端新增 `js/i18n.js`（跟随 ComfyUI Locale / 浏览器语言），覆盖上传按钮、bypasser 规则提示、内存清理描述、参数分发器开关等
- 保持不变的项（工作流兼容）：下拉选项值（"去除空行"、"仅显存"等）、NonNullSwitch 端口名（后端协议）、`RESOLUTIONS` 的"自定义"键
- 新增 `ben_nodes_config.json.example` 模板；`ben_nodes_config.json` 加入 `.gitignore`

## 当前节点统计

- **总节点数**: 22 个（控制 7 / 数据 5 / 文本 5 / 图像 4 / 文件 1，AI 类已移除）
- **测试**: `tests/test_all_nodes.py`（注册）+ `tests/test_nodes_behavior.py`（功能 37 用例）

---

# 2026-09-06 图像缩放与扩展逻辑修复记录

## 修复内容

- **P1 羽化注释修正**: `apply_feather` 注释与实现方向相反（实现/测试均为"图像区=0、补边区=255、在图像区做距离变换"），修正注释并说明 scipy EDT 无背景点时的边界晕影风险
- **P2 非 pad 模式遮罩语义统一**: contain/crop/fill/none 模式遮罩由全 255（=整幅被遮蔽，与 ComfyUI MASK 语义矛盾）改为全 0（=全部可见）；`apply_feather` 增加保护——遮罩无补边区（全 0）或无图像区（全 255）时原样返回，避免 scipy EDT 按数组边界计算产生 0~248 意外晕影
- **P3 contain 尺寸回报修正**: contain 模式输出为"长边对齐"实际尺寸（可能超出目标容器，如 4:3 图 → 16:9 目标输出 1280x960），`ImageScalerBen` 的 RETURN width/height 由目标尺寸改为实际输出尺寸，与 ui 字段及输出张量一致
- **P4 alpha 组合逻辑修复**: 源图 alpha 由"拉伸到整个输出画布 + min() 组合"改为"按缩放几何对齐到图像子矩形 + max() 组合"：
  - 修复不透明 RGBA PNG + pad 模式时补边区遮罩被清除为 0 的缺陷（outpaint 失效）
  - 修复长宽比不一致时 alpha 与内容错位
  - pad/contain/crop/fill/none 各模式分别按自身几何处理 alpha
- **P5 混合尺寸批次保护**: `ImageScalerBen` 在 `torch.stack` 前校验批次内输出尺寸一致性，不一致时抛出 i18n 双语清晰错误（新增 `image_scaler_batch_size_mismatch` key，词典 107/107）

## 行为变更说明

- MASK 输出语义变化：crop/fill/contain/none 模式的 MASK 从全 1.0 变为全 0.0（更符合 ComfyUI"1=被遮蔽"约定；pad 模式不变）
- `ImageScalerBen` 的 width/height 输出在 contain/none 模式下为实际尺寸（此前为目标尺寸）
- RGBA/P 带透明通道图像经 ImageLoaderBen 缩放时，透明区将在 MASK 中正确标记为被遮蔽

## 验证

- 功能测试 37/37 通过（新增 9 个用例：遮罩语义、羽化保护、alpha 各模式对齐、contain 尺寸回报、批次保护）
- 注册测试通过（22 节点）；词典对齐 107/107

---

# 2026-09-06 分辨率短边语义修复记录

## 问题（用户报告）

9:16 @1080p 竖屏输入（1080x1920）选 2K contain，输出仅 810x1440——比输入还小，"根本不到 2K"。

## 根本原因

`BaseResolutionNode.calculate_dimensions` 将预设基准固定作用于高度，无视画面方向：

- 横屏 16:9：高度=短边 → 2K=2560x1440 ✓
- 竖屏 9:16：高度=长边 → 2K=808x1440，短边仅 808px ✗（竖屏惯例应由短边定义档位：2K=1440x2560）

且项目内自相矛盾：ResolutionSelectorBen 重写 `BASE_DIMENSION='width'`（竖屏对、横屏错），其余 4 个分辨率节点用默认 height（横屏对、竖屏错）。

## 修复内容

- `calculate_dimensions` 改为方向感知短边语义：竖屏比例（ratio_h > ratio_w）基准作用于宽度，横屏/方形作用于高度，双维度 8 对齐
- 删除 ResolutionSelectorBen 的 `BASE_DIMENSION='width'` 重写，全节点统一语义
- `js/shared.js` calcDims 同步短边语义，并修复预览无 8 对齐导致的显示漂移（预览 810 vs 实际 808）
- 新增回归测试：竖屏 9:16 各档位（1080p=1080x1920 / 2K=1440x2560 / 4K=2160x3840 / 8K=4320x7680）、横屏行为不变、9:16@1080p 输入 2K contain 输出 1440x2560
- README 双语补充"分辨率预设说明"

## 修复后行为

| 预设 | 9:16 竖屏 | 16:9 横屏 |
|---|---|---|
| 1080p | 1080x1920（原 600x1080） | 1920x1080（不变） |
| 2K | 1440x2560（原 808x1440） | 2560x1440（不变） |
| 4K | 2160x3840（原 1208x2160） | 3840x2160（不变） |
| 8K | 4320x7680（原 2424x4320） | 7680x4320（不变） |

## 验证

- 功能测试 39/39 通过；注册测试通过（22 节点）
