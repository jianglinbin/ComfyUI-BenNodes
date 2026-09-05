# ComfyUI-BenNodes 重构执行计划

> 生成日期：2026-09-05
> 范围：移除 LLM 相关代码 → Bug 修复 → 死代码清理 → 日志规范化 → 前端去重 → 深度重构 → i18n 中英双语
> 原则：不改变任何节点的注册名（`*Ben`）、输入输出端口数量与类型；所有修改保持向后兼容（已有工作流加载不受影响，除被删除的 GLM 节点外）。

---

## 阶段 1：移除 LLM 相关代码（最先执行）

### 1.1 删除文件（整个 nodes/ai 目录）
| 文件 | 说明 |
|---|---|
| `nodes/ai/GLMNodeBen.py` | GLM 主节点 |
| `nodes/ai/GLMConfigNodeBen.py` | GLM 配置节点 |
| `nodes/ai/text_processor.py` | 文本处理模块（仅被 GLM 使用） |
| `nodes/ai/vision_processor.py` | 视觉处理模块（仅被 GLM 使用） |
| `nodes/ai/office_processor.py` | Office 处理模块（仅被 GLM 使用） |
| `nodes/ai/__init__.py` | 空文件，随目录删除 |

### 1.2 修改文件
| 文件 | 改动 |
|---|---|
| `__init__.py` | 删除 L22-L23 两条 import；删除 L50-L51（NODE_CLASS_MAPPINGS）与 L78-L79（NODE_DISPLAY_NAME_MAPPINGS）中的 GLM 两项 |
| `requirements.txt` | 删除 GLM 专属依赖：`zhipuai`、`PyMuPDF`、`opencv-python`、`python-docx`、`openpyxl`、`python-pptx`、`xlrd`、`pywin32`。保留：`Pillow`（图像节点）、`scipy`（羽化）、`psutil`（内存清理） |
| `nodes/file/FileUploaderBen.py` | 更新类 docstring：删除"输出可以直接连接到 GLMNodeBen"字样。VIDEO 输出能力**保留**（可接 SaveVideo 等节点） |
| `tests/test_all_nodes.py` | L246 `exclude_files` 列表中删除 3 个 processor 文件名（文件已不存在，保留会误导） |
| `tests/TEST_SUMMARY.md` | 移除 GLM 相关条目，节点总数 24 → 22 |
| `README.md` / `README_EN.md` | 删除"AI 相关"章节、GLM 依赖说明、GLM FAQ；节点统计 25/24 → 22（阶段 7 i18n 时会全面重写，此处先做删除性同步） |
| `comfyui-manager-submission.json` | description 移除 GLM/AI 文案；`pip` 数组移除 `zhipuai`、`python-docx`、`openpyxl`、`python-pptx`、`xlrd`、`PyMuPDF`、`opencv-python` |
| `example_workflow_all_nodes.json` | 移除 `GLMNodeBen`、`GLMConfigNodeBen` 节点及其连线/分组（`test.json` 不含 GLM，不动） |

### 1.3 验证
- 全局搜索 `GLM|zhipuai|ZhipuAI|vision_processor|text_processor|office_processor` 结果为 0
- `__init__.py` 可被 import（节点数 22）

---

## 阶段 2：Bug 修复

| # | 文件 | 问题 | 修复方案 |
|---|---|---|---|
| B1 | `nodes/image/ImageBatchLoaderBen.py` L95-L113 | 多线程 `as_completed` 按完成顺序 append，批次/文件名顺序错乱 | futures 记录原始索引，结果按索引回填后依序组装 |
| B2 | `nodes/data/AdvancedListIndexSelectorBen.py` L35、L46 | tooltip 说"step=1 每隔1个取一个"但代码 step=1 为连续取；INPUT_TYPES 默认 step=0 与函数签名 step=1 不一致 | 以现有代码行为为准（step=N 表示每隔 N-1 个取一个，即索引步长 N）：改 tooltip 描述为"步长，1=连续取，2=每隔1个取一个"；函数签名默认值改为 0 与 UI 一致 |
| B3 | `utils/image/image_utils.py` L241-L264 | `apply_feather` 中 `image_mask`/`distance_transform_edt` 重复计算两次，第一次结果丢弃 | 删除第一组计算（L241-L242） |
| B6 | `nodes/data/JSONParserBen.py` L154-L173 | 路径提取不支持多级索引 `a[0][1]`，`int()` 无容错 | 重写为正则解析 `name[idx1][idx2]` 形式，索引转换失败抛出可读错误 |
| B7 | `nodes/system/ParameterDistributorBen.py` L71-L80 | widgets_values 超过 20 个时返回元组超长 | `result = list(widgets_values[:20])` 截断 |

阶段 1 已顺带消除 B4、B5（GLM 相关，随 LLM 移除消失）。

---

## 阶段 3：死代码 / 冗余清理

| # | 位置 | 改动 |
|---|---|---|
| R1 | ListIndexSelectorBen / AdvancedListIndexSelectorBen / TypeConverterBen / NonNullSwitchBen / ParameterDistributorBen / MemoryCleanupBen | 删除各自文件内的 `AlwaysEqualProxy/AnyType` 类定义，统一改为 `from ...utils.constants.constants import any_type` |
| R2 | NodeBypasserBen / AdvancedNodeBypasserBen / GroupBypasserBen / AdvancedGroupBypasserBen / NonNullSwitchBen / ParameterDistributorBen / MemoryCleanupBen | 删除文件底部从未被使用的 `NODE_CLASS_MAPPINGS` / `NODE_DISPLAY_NAME_MAPPINGS`（注册统一在根 `__init__.py`） |
| R3 | `nodes/data/TypeConverterBen.py` L207-L237 | 删除无调用方的 `_to_list()` |
| R4 | `utils/image/image_utils.py` L463-L476 | 删除半成品函数 `tensor_to_base64()`（只有 docstring，无函数体，无调用方） |
| R6 | （GLMNodeBen 已随阶段 1 删除） | — |
| R7 | GLMConfigNodeBen(os)已删；FileUploaderBen 删 `Tuple`；ImageBatchLoaderBen 删 `List/Tuple`；ImageScalerBen 删 `List/Tuple`；ImageLoaderBen 删 `ImageOps/ImageSequence`；TextSaverBen 删 `time/logging/json/torch` | 清理未使用 import |
| R8 | PromptLineBen / TextSplitBen / TextJoinBen | 删除声明但未使用的 hidden 参数 `workflow_prompt`、`my_unique_id`（连带函数签名中的对应形参） |
| R9 | `js/image_scaler.js`、`js/load_image.js` | 移除未使用的 `updateResolutionControls` 导入（阶段 5 会用上新函数后再评估） |
| R10 | `utils/image/image_utils.py` L217-L256、L341-L429 | 删除约 130 行 AI 思考过程注释，压缩为简短中文注释说明遮罩语义（255=图像区，0=补边区） |
| R11 | `nodes/image/ImageBatchLoaderBen.py` L130-L135 | 删除死赋值与自言自语注释 |

---

## 阶段 4：日志规范化

| # | 位置 | 改动 |
|---|---|---|
| C1 | TypeConverterBen / JSONParserBen / TextProcessorBen / NonNullSwitchBen / ParameterDistributorBen / ImageBatchLoaderBen / MemoryCleanupBen / FileUploaderBen | 执行路径的 `print()` 全部改为模块级 `logger.debug()`；错误路径改 `logger.error()`；保留节点 UI 回显（ui 字段）不变 |
| C2 | ListIndexSelectorBen / AdvancedListIndexSelectorBen / TypeConverterBen / TextProcessorBen | 删除模块级 `logging.basicConfig(...)` 调用（库代码不配置全局日志），统一模式：`logger = logging.getLogger(__name__)` |

---

## 阶段 5：前端去重与常量对齐（方案 B）

| # | 位置 | 改动 |
|---|---|---|
| C3 | `js/shared.js` vs `utils/constants/constants.py` | ASPECT_RATIOS 对齐：JS 补齐 `2:3、32:9、9:18、9:19、9:19.5、9:20、5:4、3:4`，删除 Python 没有的 `18:9`；`calcDims` 补 8 倍数向下取整对齐，与后端 `calculate_dimensions` 一致 |
| C4 | `js/shared.js` + `empty_latent_image_ben.js` + `load_image_single.js` + `load_image.js` + `image_scaler.js` | 在 shared.js 新增 `configureResizeWidgets(node, options)` 通用函数（处理 resolution/aspect_ratio/width/height/feather/upscale/position/pad_color 的显隐与联动），各文件改为调用；`empty_latent_image_ben.js`、`resolution_selector.js` 的内联重复逻辑同样收敛 |
| C5 | `nodes/text/TextSaverBen.py` L87-L106 | 简化：统一交给 `folder_paths.get_save_image_path` 处理子目录，删除手动路径二次解析（保留行为：前缀含子目录时能正确落盘） |
| R5 | `js/file_uploader.js` L79 起 | 删除 `FileUploaderMultiBen` 死扩展注册（后端无此节点）；同步删除 `tests/test_all_nodes.py` L93 的 exclusion hack |

---

## 阶段 6：深度重构（方案 C）

| # | 位置 | 改动 |
|---|---|---|
| D1 | `js/node_bypasser.js`、`js/group_bypasser.js`、`js/advanced_node_bypasser.js`、`js/advanced_group_bypasser.js` | 提取公共逻辑到 `js/bypasser_common.js`：onNodeCreated 包装、widget 重建防抖、规则解析/校验、定时器注册与 onRemoved 清理。四个文件保留各自差异化逻辑 |
| D2 | `tests/test_all_nodes.py` | 1) `return False/True` 改为 `assert`，保证 pytest 下真实生效；2) 新增功能测试 `tests/test_nodes_behavior.py`（不依赖 ComfyUI 运行时）：TypeConverter、JSONParser、TextSplit/Join/Processor、ListIndexSelector（含张量）、AdvancedListIndexSelector、NonNullSwitch、ParameterDistributor（mock extra_pnginfo）、image_utils 的纯函数部分 |
| D3 | 全部节点 | 错误返回结构统一约定：可恢复错误 → 返回空值/None 并 `logger.error`（不中断队列）；参数/路径类硬错误 → raise ValueError（中文/英文随 i18n）。逐节点核对并在 docstring 标注 |

### D3 核对结果（2026-09-05 执行）

统一约定：
- **可恢复错误**（数据内容问题，节点仍可继续服务后续请求）：返回空值/None/错误说明字符串 + `logger.error`，不中断队列
- **硬错误**（参数/路径/前提条件不满足，无法产出有意义输出）：`raise ValueError`
- 下拉选项等前端约定导致的错误提示用中文；i18n 阶段（阶段 7）统一走 `t()`

| 节点 | 错误处理 | 分类 | 结论 |
|---|---|---|---|
| TypeConverterBen | 转换失败返回错误说明字符串 + logger.error | 可恢复 | ✓ 保留字符串（用户可在输出端直接看到失败原因，历史行为） |
| JSONParserBen | 空输入/无效JSON/路径不存在 → ("错误：...", ...) | 可恢复 | ✓ 同上 |
| TextProcessorBen | 处理失败返回 ("错误: ...", []) | 可恢复 | ✓ |
| TextSplitBen | 空输入返回 [] | 可恢复 | ✓ |
| TextJoinBen | 双列表输入 raise ValueError | 硬错误 | ✓（参数组合非法） |
| ListIndexSelectorBen | 输入空/类型错/索引越界 → 20×None + logger.error | 可恢复 | ✓ |
| AdvancedListIndexSelectorBen | 输入空/参数非法/类型不支持 → (None,) + logger.error | 可恢复 | ✓（另修复参数名 list 遮蔽内建类型导致的崩溃 bug） |
| NonNullSwitchBen | 全部输入为空 raise ValueError | 硬错误 | ✓ |
| ParameterDistributorBen | 找不到节点/无值 → 20×None + logger.debug | 可恢复 | ✓ |
| MemoryCleanupBen | 清理失败 logger.error 继续 | 可恢复 | ✓（清理失败不应中断工作流） |
| ImageScalerBen | 单图处理失败 → 黑图占位 + logger.error | 可恢复 | ✓ |
| ImageBatchLoaderBen | 单图失败跳过 + logger.error | 可恢复 | ✓ |
| ImageLoaderBen / TextSaverBen / PromptLineBen | 无显式异常处理（异常由 ComfyUI 队列捕获） | 硬错误 | ✓（文件IO类失败属硬错误，交由队列报错） |
| FileUploaderBen | 文件未选/不存在/加载失败 raise ValueError | 硬错误 | ✓（路径/参数类） |
| ListIndexSelector 的张量分支 | batch 张量保持 [1,H,W,C] 输出 | — | ✓ 有测试覆盖 |

---

## 阶段 7：i18n 中英双语（最后执行，覆盖前面所有文案）

### 7.1 语言模块
```
utils/i18n/__init__.py   # t(key) 函数 + 当前语言解析
utils/i18n/zh.py         # 中文词典（key → 中文）
utils/i18n/en.py         # 英文词典（key → 英文）
```
- 语言解析优先级：环境变量 `BENNODES_LANG`（zh/en，大小写不敏感）→ 项目根 `ben_nodes_config.json` 的 `"language"` 字段 → 默认 `zh`
- 模块加载时确定语言一次，`t()` 为纯查表；缺失 key 回退到 key 本身并 `logger.warning` 一次
- 新增 `ben_nodes_config.json.example` 模板；`ben_nodes_config.json` 加入 `.gitignore`

### 7.2 应用范围（key 命名规范 `<节点>_<用途>` / `common_<用途>`）
1. **根 `__init__.py`**：`NODE_DISPLAY_NAME_MAPPINGS` 全部 22 项改为 `t("...")`（如 zh: "选择分辨率" / en: "Resolution Selector"）
2. **CATEGORY**：`"BenNodes/数据"` → `f"BenNodes/{t('common_cat_data')}"`（en: Data / Image / Text / Control / File）。保持 `BenNodes/` 前缀（tests 依赖）
3. **各节点 INPUT_TYPES**：所有 `tooltip`、`placeholder`、下拉框选项文案（如 去除空行、仅显存 等中文选项值）双语化。**注意：下拉框选项属于 widget 值，会存入工作流 JSON——选项文案双语化会导致旧工作流值不匹配**，因此下拉选项保持 key 化：选项内部值不变，仅 `label` 层面双语（ComfyUI combo 无 label 机制，故下拉选项文本保持现状不改，仅在计划内标注此约束）。处理策略：**下拉选项保持中文不变**（保证旧工作流兼容），tooltip/显示名/DESCRIPTION/错误消息双语化
4. **错误消息**：各节点 `raise ValueError` 与错误返回字符串改走 `t()`
5. **前端 JS**：`console` 日志不动；节点前端动态添加的按钮/提示文本（如 file_uploader 上传按钮、bypasser 规则提示）通过后端 `INPUT_TYPES` 传递或 JS 内简单 `zh/en` 双字段处理（JS 端读取同一 `ben_nodes_config.json` 不现实，采用"双语并显"或跟随 `window` 上 ComfyUI locale API `app.ui.settings` 若可用则跟随，否则默认中文）

### 7.3 文档双语
- `README.md`（中文）：同步最终节点清单（22 个）、i18n 使用说明、依赖变更
- `README_EN.md`（英文）：同步
- `tests/TEST_SUMMARY.md`、`CLEANUP_SUMMARY.md`：追加本次重构记录

---

## 验证方案（每阶段结束执行）

1. **语法检查**：`<python> -m compileall nodes utils __init__.py`（无全局 python，执行时探测 ComfyUI 自带解释器 / conda / venv）
2. **注册测试**：`<python> tests/test_all_nodes.py`（阶段 6 后可加 `pytest tests/`）
3. **功能测试**：`<python> tests/test_nodes_behavior.py`（阶段 6 新增）
4. **残留搜索**：阶段 1 后搜 `GLM|zhipuai|processor`；阶段 3/4 后搜 `basicConfig|AlwaysEqualProxy|AnyType(str)`（应只剩 constants.py 一处）
5. **JS 检查**：`node --check` 逐文件语法校验（如有 node 环境）；否则人工核对 import/导出一致性
6. **最终**：git diff 全量 review，确认无行为变化后提交（是否提交由用户决定）

## 风险与回滚
- 每阶段独立可验证，阶段间用 git 状态隔离；出错可按阶段回滚
- 下拉选项文案不改（见 7.2.3 约束），保证旧工作流兼容
- 删除 `nodes/ai` 后旧工作流中的 GLM 节点会显示为缺失节点（预期行为，用户已确认移除）

## 预计改动清单
- 删除：6 个文件（nodes/ai 整目录）
- 新增：`utils/i18n/__init__.py`、`utils/i18n/zh.py`、`utils/i18n/en.py`、`ben_nodes_config.json.example`、`tests/test_nodes_behavior.py`、`js/bypasser_common.js`、本计划文档
- 修改：Python 节点 16 个、JS 10 个、根 `__init__.py`、requirements.txt、README×2、submission.json、示例工作流、tests×2
