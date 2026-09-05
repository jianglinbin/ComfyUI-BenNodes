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
- **测试**: `tests/test_all_nodes.py`（注册）+ `tests/test_nodes_behavior.py`（功能 28 用例）
