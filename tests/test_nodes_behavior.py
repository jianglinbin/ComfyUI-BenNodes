"""
功能测试：节点行为验证（不依赖 ComfyUI 运行时）

覆盖范围：
- TypeConverterBen        类型转换
- JSONParserBen           JSON 解析（含多级索引路径）
- TextSplitBen            文本拆分
- TextJoinBen             文本连接
- TextProcessorBen        文本处理
- ListIndexSelectorBen    列表索引选择（含张量）
- AdvancedListIndexSelectorBen  高级索引选择
- NonNullSwitchBen        非空切换
- ParameterDistributorBen 参数分发（构造 extra_pnginfo）
- utils.image.image_utils 缩放/羽化纯函数

运行方式：
    python tests/test_nodes_behavior.py
    或 pytest tests/test_nodes_behavior.py
"""

import importlib
import os
import sys
import types

import numpy as np
import torch
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# 导入环境构造
# 项目作为 ComfyUI custom_nodes 加载时，ComfyUI 会动态构造包链；
# 独立测试时手动构造等价包链，使节点内的相对导入 (from ...utils...) 正常工作。
# 根 __init__.py 不会被执行（其依赖 ComfyUI 的 folder_paths）。
# ---------------------------------------------------------------------------
PKG_NAME = "_ben_nodes_pkg"

_root_pkg = types.ModuleType(PKG_NAME)
_root_pkg.__path__ = [PROJECT_ROOT]
_root_pkg.__package__ = PKG_NAME
sys.modules[PKG_NAME] = _root_pkg


def load(module_path):
    """按包内路径导入模块，如 load('nodes.data.JSONParserBen')"""
    return importlib.import_module(f"{PKG_NAME}.{module_path}")


TypeConverterBen = load("nodes.data.TypeConverterBen").TypeConverterBen
JSONParserBen = load("nodes.data.JSONParserBen").JSONParserBen
ListIndexSelectorBen = load("nodes.data.ListIndexSelectorBen").ListIndexSelectorBen
AdvancedListIndexSelectorBen = load("nodes.data.AdvancedListIndexSelectorBen").AdvancedListIndexSelectorBen
NonNullSwitchBen = load("nodes.system.NonNullSwitchBen").NonNullSwitchBen
ParameterDistributorBen = load("nodes.system.ParameterDistributorBen").ParameterDistributorBen
TextSplitBen = load("nodes.text.TextSplitterBen").TextSplitBen
TextJoinBen = load("nodes.text.TextJoinerBen").TextJoinBen
TextProcessorBen = load("nodes.text.TextProcessorBen").TextProcessorBen
image_utils = load("utils.image.image_utils")
ImageScalerBen = load("nodes.image.ImageScalerBen").ImageScalerBen

any_type = load("utils.constants.constants").any_type


# ---------------------------------------------------------------------------
# TypeConverterBen
# ---------------------------------------------------------------------------

def test_type_converter_basic():
    node = TypeConverterBen()
    # str -> float
    assert node.convert(**{"*": "3.14", "target_type": "FLOAT"})[0] == 3.14
    # str -> int（支持 "3.14" 截断）
    assert node.convert(**{"*": "3.14", "target_type": "INT"})[0] == 3
    # bool -> string
    assert node.convert(**{"*": True, "target_type": "STRING"})[0] == "true"
    # str -> bool
    assert node.convert(**{"*": "yes", "target_type": "BOOLEAN"})[0] is True


def test_type_converter_list():
    node = TypeConverterBen()
    # 列表 -> LIST<INT>
    result = node.convert(**{"*": ["1", "2", "3"], "target_type": "LIST<INT>"})[0]
    assert result == [1, 2, 3]
    # 单值 -> LIST<FLOAT>
    result = node.convert(**{"*": 5, "target_type": "LIST<FLOAT>"})[0]
    assert result == [5.0]
    # 列表 -> 单值（取第一个元素）
    result = node.convert(**{"*": ["9", "8"], "target_type": "INT"})[0]
    assert result == 9
    # 空列表 -> 默认值
    result = node.convert(**{"*": [], "target_type": "STRING"})[0]
    assert result == ""


def test_type_converter_error():
    node = TypeConverterBen()
    # 非法字符串转整数 -> 返回错误字符串而不是抛异常
    result = node.convert(**{"*": "abc", "target_type": "INT"})[0]
    assert isinstance(result, str) and "类型转换失败" in result


# ---------------------------------------------------------------------------
# JSONParserBen
# ---------------------------------------------------------------------------

def test_json_parser_basic():
    node = JSONParserBen()
    json_text, parsed = node.parse_json('{"name": "ben", "age": 18}', "name")
    assert json_text == "ben"
    assert parsed == "ben"


def test_json_parser_nested_and_multi_index():
    node = JSONParserBen()
    # 嵌套 + 数组索引
    json_text, parsed = node.parse_json('{"a": {"b": [10, 20, 30]}}', "a.b[1]")
    assert json_text == "20"
    assert parsed == 20
    # 多级索引（B6 修复验证）
    json_text, parsed = node.parse_json('{"m": [[1, 2], [3, 4]]}', "m[1][0]")
    assert json_text == "3"
    assert parsed == 3
    # 组合路径
    data = '{"data": {"users": [{"city": "BJ"}, {"city": "SH"}]}}'
    json_text, parsed = node.parse_json(data, "data.users[1].city")
    assert parsed == "SH"


def test_json_parser_multi_path():
    node = JSONParserBen()
    json_text, parsed = node.parse_json('{"a": 1, "b": 2}', "a; b")
    # 多路径返回列表
    assert json_text == ["1", "2"]
    assert parsed == [1, 2]


def test_json_parser_noise_text():
    node = JSONParserBen()
    # 从噪声文本中提取 JSON
    json_text, parsed = node.parse_json('前缀 {"x": 1} 后缀', "")
    assert parsed == {"x": 1}


def test_json_parser_errors():
    node = JSONParserBen()
    # 空输入
    json_text, parsed = node.parse_json("", "")
    assert "错误" in json_text and parsed is None
    # 无效 JSON
    json_text, parsed = node.parse_json("not a json {", "")
    assert "错误" in json_text
    # 路径不存在
    json_text, parsed = node.parse_json('{"a": 1}', "b")
    assert "错误" in json_text
    # 索引越界
    json_text, parsed = node.parse_json('{"a": [1]}', "a[5]")
    assert "错误" in json_text


# ---------------------------------------------------------------------------
# TextSplitBen / TextJoinBen / TextProcessorBen
# ---------------------------------------------------------------------------

def test_text_split():
    node = TextSplitBen()
    # 基本拆分
    result = node.split_text("a\nb\nc")[0]
    assert result == ["a", "b", "c"]
    # start_index / max_rows 截取
    result = node.split_text("a\nb\nc\nd", start_index=1, max_rows=2)[0]
    assert result == ["b", "c"]
    # 自定义分隔符
    result = node.split_text("a,b,c", delimiter=",")[0]
    assert result == ["a", "b", "c"]
    # 空输入
    assert node.split_text("")[0] == []


def test_text_join():
    node = TextJoinBen()
    # str + str
    assert node.join_text("a", "b", "-")[0] == "a-b"
    # list + str
    result = node.join_text(["a", "b"], "x", "-")[0]
    assert result == ["a-x", "b-x"]
    # str + list
    result = node.join_text("x", ["a", "b"], "-")[0]
    assert result == ["x-a", "x-b"]
    # 两个列表 -> 报错
    try:
        node.join_text(["a"], ["b"])
        assert False, "两个列表输入应抛出 ValueError"
    except ValueError:
        pass


def test_text_processor():
    node = TextProcessorBen()
    text = "a\n\n  b  \nc"
    # 去除空行
    out_text, out_list = node.process_text(text, "去除空行")
    assert out_list == ["a", "  b  ", "c"]
    # 去除空白字符+空行
    out_text, out_list = node.process_text(text, "去除空白字符+空行")
    assert out_list == ["a", "b", "c"]
    # none 不处理
    out_text, out_list = node.process_text(text, "none")
    assert out_list == ["a", "", "  b  ", "c"]
    # 空输入
    out_text, out_list = node.process_text("", "none")
    assert out_text == ""


# ---------------------------------------------------------------------------
# ListIndexSelectorBen
# ---------------------------------------------------------------------------

def test_list_index_selector_basic():
    node = ListIndexSelectorBen()
    # 多索引选择
    result = node.select(["a", "b", "c", "d"], index="0,2")
    assert result[0] == "a"
    assert result[1] == "c"
    assert result[2] is None  # 填充
    # 单索引 int
    result = node.select(["a", "b"], index=1)
    assert result[0] == "b"


def test_list_index_selector_out_of_range():
    node = ListIndexSelectorBen()
    # 超范围索引 -> None
    result = node.select(["a", "b"], index="5")
    assert result[0] is None
    # 无效索引 -> None
    result = node.select(["a", "b"], index="xyz")
    assert result[0] is None
    # 空输入 -> 20 个 None
    result = node.select(None, index="0")
    assert all(r is None for r in result)
    assert len(result) == 20


def test_list_index_selector_batch_tensor():
    node = ListIndexSelectorBen()
    # 批量图像张量 [N, H, W, C]，选中后保持 batch 维度 [1, H, W, C]
    batch = torch.rand(3, 8, 8, 3)
    result = node.select(batch, index="1")
    assert result[0].shape == (1, 8, 8, 3)
    assert torch.equal(result[0][0], batch[1])


# ---------------------------------------------------------------------------
# AdvancedListIndexSelectorBen
# ---------------------------------------------------------------------------

def test_advanced_selector_continuous():
    node = AdvancedListIndexSelectorBen()
    data = list(range(10))
    # step=0 连续选取
    result = node.select_advanced(data, start_index=2, step=0, length=3)[0]
    assert result == [2, 3, 4]
    # step=1 连续选取
    result = node.select_advanced(data, start_index=2, step=1, length=3)[0]
    assert result == [2, 3, 4]
    # 长度超出自动截断
    result = node.select_advanced(data, start_index=8, step=1, length=5)[0]
    assert result == [8, 9]


def test_advanced_selector_stride():
    node = AdvancedListIndexSelectorBen()
    data = list(range(10))
    # step=2 每隔1个取一个
    result = node.select_advanced(data, start_index=1, step=2, length=3)[0]
    assert result == [1, 3, 5]
    # step=3 每隔2个取一个
    result = node.select_advanced(data, start_index=0, step=3, length=4)[0]
    assert result == [0, 3, 6, 9]
    # 间隔模式下长度超出自动截断
    result = node.select_advanced(data, start_index=5, step=3, length=10)[0]
    assert result == [5, 8]


def test_advanced_selector_errors():
    node = AdvancedListIndexSelectorBen()
    data = list(range(5))
    # 起始越界
    assert node.select_advanced(data, start_index=10, step=1, length=1)[0] is None
    # 长度 <= 0
    assert node.select_advanced(data, start_index=0, step=1, length=0)[0] is None
    # 空输入
    assert node.select_advanced(None)[0] is None
    # 不支持的类型
    assert node.select_advanced("not-a-list")[0] is None


def test_advanced_selector_tensor():
    node = AdvancedListIndexSelectorBen()
    # 批量图像张量 [N, H, W, C]
    batch = torch.rand(6, 4, 4, 3)
    result = node.select_advanced(batch, start_index=1, step=2, length=2)[0]
    assert result.shape == (2, 4, 4, 3)
    assert torch.equal(result[0], batch[1])
    assert torch.equal(result[1], batch[3])


# ---------------------------------------------------------------------------
# NonNullSwitchBen
# ---------------------------------------------------------------------------

def test_non_null_switch_priority():
    node = NonNullSwitchBen()
    # 主数据源非空 -> 返回主数据源
    assert node.switch(**{"主数据源": "a", "备选1": "b"})[0] == "a"
    # 主数据源为空 -> 返回备选1
    assert node.switch(**{"主数据源": None, "备选1": "b"})[0] == "b"
    # 按顺序取第一个非空备选
    assert node.switch(**{"主数据源": None, "备选1": None, "备选2": "c"})[0] == "c"


def test_non_null_switch_all_none():
    node = NonNullSwitchBen()
    # 全部为空 -> 抛出 ValueError
    try:
        node.switch(**{"主数据源": None, "备选1": None})
        assert False, "全部为空应抛出 ValueError"
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# ParameterDistributorBen
# ---------------------------------------------------------------------------

def _make_pnginfo(widgets_values, node_id=5):
    """构造 extra_pnginfo 与 unique_id"""
    extra_pnginfo = {
        "workflow": {
            "nodes": [
                {"id": node_id, "widgets_values": widgets_values, "outputs": []}
            ]
        }
    }
    return str(node_id), extra_pnginfo


def test_parameter_distributor_basic():
    node = ParameterDistributorBen()
    unique_id, extra_pnginfo = _make_pnginfo(["v1", "v2", "v3"])
    result = node.execute(unique_id=unique_id, extra_pnginfo=extra_pnginfo)
    assert result[0] == "v1"
    assert result[1] == "v2"
    assert result[2] == "v3"
    assert result[3] is None  # 填充到 20
    assert len(result) == 20


def test_parameter_distributor_truncation():
    node = ParameterDistributorBen()
    # 超过 20 个 widget 值 -> 截断到 20（B7 修复验证）
    values = [f"v{i}" for i in range(25)]
    unique_id, extra_pnginfo = _make_pnginfo(values)
    result = node.execute(unique_id=unique_id, extra_pnginfo=extra_pnginfo)
    assert len(result) == 20
    assert result[19] == "v19"


def test_parameter_distributor_not_found():
    node = ParameterDistributorBen()
    # 节点不存在 -> 20 个 None
    result = node.execute(unique_id="999", extra_pnginfo={"workflow": {"nodes": []}})
    assert all(r is None for r in result)
    # extra_pnginfo 为空 -> 20 个 None
    result = node.execute(unique_id="5", extra_pnginfo=None)
    assert all(r is None for r in result)


# ---------------------------------------------------------------------------
# utils.image.image_utils
# ---------------------------------------------------------------------------

def test_image_utils_resize_contain():
    img = Image.new("RGB", (100, 50), color=(255, 0, 0))
    resized, mask = image_utils.ImageScaleUtils.resize_contain(img, 200, 100, feathering=0)
    # contain 等比缩放：100x50 -> 200x100
    assert resized.size == (200, 100)
    assert mask.size == (200, 100)
    # 遮罩语义（ComfyUI MASK：255=被遮蔽）：输出全为图像内容，遮罩全 0（可见）
    mask_array = np.array(mask)
    assert mask_array.min() == 0 and mask_array.max() == 0


def test_image_utils_resize_pad():
    img = Image.new("RGB", (50, 100), color=(255, 0, 0))
    result, mask = image_utils.ImageScaleUtils.resize_pad(img, 200, 100, feathering=0)
    # pad 等比缩放再补边到目标尺寸
    assert result.size == (200, 100)
    assert mask.size == (200, 100)
    # 遮罩语义（ComfyUI MASK：255=被遮蔽）：图像区=0，补边区=255
    mask_array = np.array(mask)
    assert mask_array[50, 100] == 0  # 中心（图像区）
    assert mask_array[2, 2] == 255  # 左上角（补边区）


def test_image_utils_apply_feather():
    # 构造 mask：左半 255（补边区），右半 0（图像区）——与 resize_pad 输出语义一致
    mask_array_init = np.zeros((100, 100), dtype=np.uint8)
    mask_array_init[:, :50] = 255
    mask = Image.fromarray(mask_array_init)

    feathered = image_utils.ImageScaleUtils.apply_feather(mask, 10)
    feathered_array = np.array(feathered)
    # 补边区保持 255（被遮蔽）
    assert feathered_array[50, 5] == 255
    # 图像区靠近边缘处产生渐变（0 < 值 < 255）
    edge_value = feathered_array[50, 52]
    assert 0 < edge_value < 255
    # 图像区深处为 0（可见）
    assert feathered_array[50, 99] == 0


def test_image_utils_process_for_comfy():
    img = Image.new("RGB", (100, 50), color=(0, 255, 0))
    img_tensor, mask_tensor, fw, fh = image_utils.process_image_for_comfy(
        img, "pad", 200, 100, 0, "bicubic", "center", (127, 127, 127)
    )
    # ComfyUI 图像格式 [B, H, W, C]
    assert img_tensor.shape == (1, 100, 200, 3)
    assert mask_tensor.shape == (1, 100, 200)
    assert (fw, fh) == (200, 100)


def test_image_utils_crop_fill_none_masks_all_visible():
    # crop/fill/none 输出全为图像内容，遮罩应全 0（可见），而非全 255（被遮蔽）
    img = Image.new("RGB", (100, 50), color=(255, 0, 0))
    result, mask = image_utils.ImageScaleUtils.resize_crop(img, 200, 100, feathering=0)
    assert np.array(mask).max() == 0
    result, mask = image_utils.ImageScaleUtils.resize_fill(img, 200, 100, feathering=0)
    assert np.array(mask).max() == 0
    _, mask_none = image_utils.ImageScaleUtils.apply_scale_mode_with_mask(img, "none", 200, 100, 0)
    assert np.array(mask_none).max() == 0


def test_image_utils_apply_feather_uniform_masks():
    # 全 0（无补边区）/ 全 255（无图像区）时羽化应原样返回，不产生意外渐变
    r0 = np.array(image_utils.ImageScaleUtils.apply_feather(Image.new("L", (100, 100), 0), 40))
    r255 = np.array(image_utils.ImageScaleUtils.apply_feather(Image.new("L", (100, 100), 255), 40))
    assert r0.min() == 0 and r0.max() == 0
    assert r255.min() == 255 and r255.max() == 255


def _rgba_image(size, alpha):
    """构造 RGBA 测试图：RGB 全红，alpha 为标量或 (H, W) uint8 数组"""
    img = Image.new("RGBA", size, (255, 0, 0, 255))
    if not isinstance(alpha, int):
        img.putalpha(Image.fromarray(alpha.astype(np.uint8)))
    else:
        img.putalpha(Image.new("L", size, alpha))
    return img


def test_image_utils_alpha_pad_opaque_keeps_pad_mask():
    # 回归测试（P4）：不透明 RGBA + pad（经 process_image_for_comfy 提取 alpha），
    # 补边区遮罩必须保持 255（此前被 min() 组合清除为 0）
    img = _rgba_image((50, 100), 255)
    _, mask_tensor, _, _ = image_utils.process_image_for_comfy(img, "pad", 200, 100, 0)
    mask_array = (mask_tensor[0].numpy() * 255).round().astype(np.uint8)
    assert mask_array[50, 100] == 0   # 中心（图像区，alpha 不透明 → 可见）
    assert mask_array[2, 2] == 255    # 左上角（补边区，不被不透明 alpha 清除）


def test_image_utils_alpha_pad_transparent_region_masked():
    # 半透明 RGBA + pad：图像子矩形内透明处=255（与内容几何对齐），补边区=255
    alpha = np.full((100, 50), 255, dtype=np.uint8)
    alpha[:, 25:] = 0  # 图像右半透明
    img = _rgba_image((50, 100), alpha)
    _, mask_tensor, _, _ = image_utils.process_image_for_comfy(img, "pad", 200, 100, 0)
    mask_array = (mask_tensor[0].numpy() * 255).round().astype(np.uint8)
    # 50x100 内容等比缩放后 50x100，居中放置 x_offset=75, y_offset=0
    assert mask_array[50, 80] == 0    # 图像区不透明处（内容列 5 < 25）
    assert mask_array[50, 110] == 255  # 图像区透明处（内容列 35 ≥ 25）
    assert mask_array[2, 2] == 255    # 补边区


def test_image_utils_alpha_contain_alignment():
    # contain：alpha 随内容等比缩放，透明处=255
    alpha = np.full((100, 100), 255, dtype=np.uint8)
    alpha[:50, :] = 0  # 上半透明
    img = _rgba_image((100, 100), alpha).convert("RGB")
    result, mask = image_utils.ImageScaleUtils.resize_contain(
        img, 200, 200, feathering=0, alpha=Image.fromarray(alpha)
    )
    mask_array = np.array(mask)
    assert mask_array[25, 100] == 255  # 缩放后透明区（上半）
    assert mask_array[150, 100] == 0   # 不透明区（下半）


def test_image_utils_alpha_fill_gradient():
    # fill：alpha 拉伸到目标尺寸，遮罩 = 255 - alpha（保留渐变语义）
    alpha = np.full((100, 100), 128, dtype=np.uint8)
    img = _rgba_image((100, 100), alpha).convert("RGB")
    result, mask = image_utils.ImageScaleUtils.resize_fill(
        img, 200, 100, feathering=0, alpha=Image.fromarray(alpha)
    )
    assert (np.array(mask) == 127).all()


def test_image_utils_alpha_none_mode_via_process():
    # 通过 process_image_for_comfy 全路径验证：none 模式 + RGBA，透明处=255
    alpha = np.full((100, 100), 255, dtype=np.uint8)
    alpha[:50, :] = 0
    img = _rgba_image((100, 100), alpha)
    img_tensor, mask_tensor, fw, fh = image_utils.process_image_for_comfy(img, "none", 200, 100, 0)
    mask_array = (mask_tensor[0].numpy() * 255).round().astype(np.uint8)
    assert mask_array[10, 50] == 255  # 透明处（上半）
    assert mask_array[90, 50] == 0    # 不透明处（下半）


def test_image_scaler_return_actual_size_contain():
    # 回归测试（P3）：RETURN 的 width/height 应为实际输出尺寸而非目标尺寸
    node = ImageScalerBen()
    img_tensor = torch.zeros((1, 768, 1024, 3), dtype=torch.float32)  # 4:3 图像
    result = node.process(
        image=img_tensor, resolution="720p", aspect_ratio="16:9",
        width=1080, height=720, resize_mode="contain", position="center",
        feathering=0, upscale_method="bicubic", pad_color="127,127,127",
    )
    out_image, out_mask, out_w, out_h = result["result"]
    # contain：1024x768 -> 1280x960（长边对齐，超出 720p 16:9 容器高度）
    assert out_image.shape == (1, 960, 1280, 3)
    assert (out_w, out_h) == (1280, 960)


def test_image_scaler_batch_size_mismatch_raises():
    # 回归测试（P5）：批次内输出尺寸不一致时应给出清晰错误，而非 torch.stack 崩溃。
    # 正常张量输入尺寸一致；不一致可能来自异常兜底路径（返回 target 尺寸黑图），
    # 这里通过替身 _process_single_pil_image 直接构造不一致场景验证保护逻辑。
    node = ImageScalerBen()
    uniform = torch.zeros((2, 100, 100, 3), dtype=torch.float32)

    def fake_process(pil_image, *args, **kwargs):
        if not hasattr(fake_process, "calls"):
            fake_process.calls = 0
        fake_process.calls += 1
        if fake_process.calls == 1:
            return torch.zeros((100, 100, 3)), torch.zeros((100, 100)), 100, 100
        return torch.zeros((150, 120, 3)), torch.zeros((150, 120)), 120, 150

    node._process_single_pil_image = fake_process
    try:
        node.process(
            image=uniform, resolution="自定义", aspect_ratio="自定义",
            width=100, height=100, resize_mode="contain", position="center",
            feathering=0, upscale_method="bicubic", pad_color="127,127,127",
        )
        assert False, "应抛出 ValueError"
    except ValueError as e:
        assert "尺寸不一致" in str(e)


def test_calculate_dimensions_short_side_semantics():
    # 回归测试：分辨率预设基准作用于短边（竖屏→宽，横屏/方形→高）
    node = ImageScalerBen()
    # 竖屏 9:16：行业惯例 1080p=1080x1920、2K=1440x2560
    assert node.calculate_dimensions("1080p", "9:16", 1080, 720) == (1080, 1920)
    assert node.calculate_dimensions("2K", "9:16", 1080, 720) == (1440, 2560)
    assert node.calculate_dimensions("4K", "9:16", 1080, 720) == (2160, 3840)
    assert node.calculate_dimensions("8K", "9:16", 1080, 720) == (4320, 7680)
    # 横屏 16:9（行为不变）
    assert node.calculate_dimensions("1080p", "16:9", 1080, 720) == (1920, 1080)
    assert node.calculate_dimensions("2K", "16:9", 1080, 720) == (2560, 1440)
    assert node.calculate_dimensions("4K", "16:9", 1080, 720) == (3840, 2160)
    # 方形
    assert node.calculate_dimensions("2K", "1:1", 1080, 720) == (1440, 1440)
    # 自定义透传
    assert node.calculate_dimensions("自定义", "9:16", 123, 456) == (123, 456)


def test_image_scaler_portrait_2k_contain_not_shrink():
    # 回归测试（用户报告）：9:16@1080p 输入选 2K contain，
    # 输出应为 1440x2560（≥输入），而非修复前的 810x1440（比输入还小）
    node = ImageScalerBen()
    img = torch.zeros((1, 1920, 1080, 3), dtype=torch.float32)  # H=1920, W=1080（9:16 竖屏 1080p）
    result = node.process(
        image=img, resolution="2K", aspect_ratio="9:16",
        width=1080, height=720, resize_mode="contain", position="center",
        feathering=0, upscale_method="bicubic", pad_color="127,127,127",
    )
    out_image, _, out_w, out_h = result["result"]
    assert out_image.shape == (1, 2560, 1440, 3)
    assert (out_w, out_h) == (1440, 2560)


# ---------------------------------------------------------------------------
# any_type 常量语义
# ---------------------------------------------------------------------------

def test_any_type_semantics():
    # AlwaysEqualProxy 与任意类型相等（ComfyUI 类型推断依赖此特性）
    assert any_type == "IMAGE"
    assert any_type == "MASK"
    assert any_type == 123
    assert not (any_type != "anything")


if __name__ == "__main__":
    test_funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]

    passed = 0
    failed = []
    for fn in test_funcs:
        try:
            fn()
            print(f"✓ {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {fn.__name__}: {e}")
            failed.append((fn.__name__, e))

    print("\n" + "=" * 60)
    print(f"功能测试: {passed}/{len(test_funcs)} 通过")
    if failed:
        print("\n失败详情:")
        for name, e in failed:
            print(f"  ✗ {name}: {e}")
        sys.exit(1)
    print("🎉 全部通过")
    sys.exit(0)
