"""
全面测试：验证所有节点的 Python 和 JS 注册名是否匹配
"""
import os
import re
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_python_js_registration_match():
    """测试 Python 和 JS 注册名是否匹配"""
    print("=" * 80)
    print("测试 Python 和 JS 注册名匹配")
    print("=" * 80)
    
    # 1. 从 __init__.py 读取所有 Python 注册名
    init_path = os.path.join(project_root, "__init__.py")
    with open(init_path, 'r', encoding='utf-8') as f:
        init_content = f.read()
    
    # 提取 NODE_CLASS_MAPPINGS
    mappings_match = re.search(r'NODE_CLASS_MAPPINGS\s*=\s*\{([^}]+)\}', init_content, re.DOTALL)
    if not mappings_match:
        print("✗ 未找到 NODE_CLASS_MAPPINGS")
        return False
    
    mappings_content = mappings_match.group(1)
    mapping_pattern = r'"(\w+)":\s*(\w+)'
    python_registrations = dict(re.findall(mapping_pattern, mappings_content))
    
    print(f"\n找到 {len(python_registrations)} 个 Python 注册:")
    for reg_name in sorted(python_registrations.keys()):
        print(f"  • {reg_name}")
    
    # 2. 从 JS 文件读取所有注册名
    js_dir = os.path.join(project_root, "js")
    js_registrations = {}
    
    print(f"\n扫描 JS 文件...")
    
    for js_file in os.listdir(js_dir):
        if not js_file.endswith('.js') or js_file in ('shared.js', 'bypasser_common.js'):
            continue
        
        js_path = os.path.join(js_dir, js_file)
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # 查找 nodeData.name 匹配模式
        # 支持多种格式：nodeData.name !== "XXX" 或 nodeData.name === "XXX"
        patterns = [
            r'nodeData\.name\s*!==\s*["\'](\w+)["\']',
            r'nodeData\.name\s*===\s*["\'](\w+)["\']',
            r'node\.comfyClass\s*!==\s*["\'](\w+)["\']',
            r'node\.comfyClass\s*===\s*["\'](\w+)["\']',
        ]
        
        found_names = set()
        for pattern in patterns:
            matches = re.findall(pattern, js_content)
            found_names.update(matches)
        
        if found_names:
            for name in found_names:
                if name not in js_registrations:
                    js_registrations[name] = []
                js_registrations[name].append(js_file)
    
    print(f"\n找到 {len(js_registrations)} 个 JS 注册:")
    for reg_name in sorted(js_registrations.keys()):
        files = ', '.join(js_registrations[reg_name])
        print(f"  • {reg_name:40s} ({files})")
    
    # 3. 比对 Python 和 JS 注册名
    print("\n" + "=" * 80)
    print("比对结果")
    print("=" * 80)
    
    errors = []
    matched = []
    
    # 检查每个 Python 注册是否有对应的 JS
    for py_name in sorted(python_registrations.keys()):
        if py_name in js_registrations:
            matched.append(py_name)
            print(f"✓ {py_name:40s} - Python ✓ JS ✓")
        else:
            # 检查是否是没有 JS 的节点（某些节点可能不需要 JS）
            print(f"⚠ {py_name:40s} - Python ✓ JS ✗ (可能不需要 JS)")
    
    # 检查 JS 中是否有 Python 中没有的注册
    for js_name in sorted(js_registrations.keys()):
        if js_name not in python_registrations:
            errors.append(f"✗ {js_name:40s} - JS 中存在但 Python 中不存在")
    
    print("\n" + "=" * 80)
    print("统计")
    print("=" * 80)
    print(f"Python 注册数: {len(python_registrations)}")
    print(f"JS 注册数: {len(js_registrations)}")
    print(f"匹配数: {len(matched)}")
    print(f"错误数: {len(errors)}")
    
    if errors:
        print("\n错误详情:")
        for error in errors:
            print(error)
        return False
    
    print("\n✓ 所有 JS 注册名都与 Python 匹配")
    return True


def test_ben_suffix():
    """测试所有注册名是否包含 Ben 后缀"""
    print("\n" + "=" * 80)
    print("测试 Ben 后缀")
    print("=" * 80)
    
    init_path = os.path.join(project_root, "__init__.py")
    with open(init_path, 'r', encoding='utf-8') as f:
        init_content = f.read()
    
    mappings_match = re.search(r'NODE_CLASS_MAPPINGS\s*=\s*\{([^}]+)\}', init_content, re.DOTALL)
    if not mappings_match:
        return False
    
    mappings_content = mappings_match.group(1)
    mapping_pattern = r'"(\w+)":\s*(\w+)'
    registrations = dict(re.findall(mapping_pattern, mappings_content))
    
    errors = []
    for reg_name in sorted(registrations.keys()):
        if not reg_name.endswith("Ben"):
            errors.append(f"✗ {reg_name:40s} - 缺少 'Ben' 后缀")
            print(f"✗ {reg_name:40s} - 缺少 'Ben' 后缀")
        else:
            print(f"✓ {reg_name:40s} - 包含 'Ben' 后缀")
    
    if errors:
        print(f"\n✗ {len(errors)} 个注册名缺少 'Ben' 后缀")
        return False
    
    print(f"\n✓ 所有 {len(registrations)} 个注册名都包含 'Ben' 后缀")
    return True


def test_display_names():
    """测试显示名称是否为纯中文（不包含 Ben）"""
    print("\n" + "=" * 80)
    print("测试显示名称")
    print("=" * 80)
    
    init_path = os.path.join(project_root, "__init__.py")
    with open(init_path, 'r', encoding='utf-8') as f:
        init_content = f.read()
    
    display_match = re.search(r'NODE_DISPLAY_NAME_MAPPINGS\s*=\s*\{([^}]+)\}', init_content, re.DOTALL)
    if not display_match:
        print("✗ 未找到 NODE_DISPLAY_NAME_MAPPINGS")
        return False
    
    display_content = display_match.group(1)
    display_pattern = r'"(\w+)":\s*"([^"]+)"'
    display_names = dict(re.findall(display_pattern, display_content))
    
    errors = []
    for reg_name, display_name in sorted(display_names.items()):
        # 检查显示名称是否包含 Ben 或 -Ben
        if "Ben" in display_name or "-Ben" in display_name:
            errors.append(f"✗ {reg_name:40s} → '{display_name}' - 显示名称包含 'Ben'")
            print(f"✗ {reg_name:40s} → '{display_name}' - 显示名称包含 'Ben'")
        else:
            print(f"✓ {reg_name:40s} → '{display_name}'")
    
    assert not errors, f"{len(errors)} 个显示名称包含 'Ben'"

    print(f"\n✓ 所有 {len(display_names)} 个显示名称都不包含 'Ben'")
    return True


def test_category_structure():
    """测试所有节点的 CATEGORY 是否符合 BenNodes 结构"""
    print("\n" + "=" * 80)
    print("测试 CATEGORY 结构")
    print("=" * 80)
    
    # 获取所有节点文件
    nodes_dir = os.path.join(project_root, "nodes")
    node_files = []
    
    for root, dirs, files in os.walk(nodes_dir):
        for file in files:
            if file.endswith("Ben.py") and not file.startswith("__"):
                node_files.append(os.path.join(root, file))
    
    errors = []
    success = []
    
    for node_file in sorted(node_files):
        rel_path = os.path.relpath(node_file, project_root)
        
        with open(node_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找 CATEGORY 定义（兼容普通字符串与 f-string：f"BenNodes/{t('common_cat_x')}"）
        category_match = re.search(r'CATEGORY\s*=\s*f?["\']([^"\'{]+)', content)
        
        if not category_match:
            errors.append(f"✗ {rel_path:60s} - 未找到 CATEGORY")
            print(f"✗ {rel_path:60s} - 未找到 CATEGORY")
            continue
        
        category = category_match.group(1)
        
        if not category.startswith("BenNodes/"):
            errors.append(f"✗ {rel_path:60s} - CATEGORY '{category}' 不以 'BenNodes/' 开头")
            print(f"✗ {rel_path:60s} - CATEGORY '{category}' 不以 'BenNodes/' 开头")
        else:
            success.append(rel_path)
            print(f"✓ {rel_path:60s} - CATEGORY '{category}'")
    
    if errors:
        print(f"\n✗ {len(errors)} 个节点的 CATEGORY 不符合规范")
        return False
    
    print(f"\n✓ 所有 {len(success)} 个节点的 CATEGORY 都符合 'BenNodes/' 结构")
    return True


def test_file_names():
    """测试所有节点文件名是否包含 Ben 后缀"""
    print("\n" + "=" * 80)
    print("测试文件名 Ben 后缀")
    print("=" * 80)
    
    nodes_dir = os.path.join(project_root, "nodes")
    node_files = []
    
    # 排除辅助文件（不是节点的文件）
    exclude_files = []
    
    for root, dirs, files in os.walk(nodes_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__") and file not in exclude_files:
                node_files.append(os.path.join(root, file))
    
    errors = []
    success = []
    
    for node_file in sorted(node_files):
        rel_path = os.path.relpath(node_file, project_root)
        file_name = os.path.basename(node_file)
        
        if not file_name.endswith("Ben.py"):
            errors.append(f"✗ {rel_path:60s} - 文件名不包含 'Ben' 后缀")
            print(f"✗ {rel_path:60s} - 文件名不包含 'Ben' 后缀")
        else:
            success.append(rel_path)
            print(f"✓ {rel_path:60s}")
    
    assert not errors, f"{len(errors)} 个文件名不包含 'Ben' 后缀"

    print(f"\n✓ 所有 {len(success)} 个文件名都包含 'Ben' 后缀")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ComfyUI-BenNodes 全面测试")
    print("=" * 80 + "\n")

    test_suites = [
        ("文件名 Ben 后缀测试", test_file_names),
        ("注册名 Ben 后缀测试", test_ben_suffix),
        ("显示名称测试", test_display_names),
        ("CATEGORY 结构测试", test_category_structure),
        ("Python-JS 匹配测试", test_python_js_registration_match),
    ]

    results = {}
    for name, fn in test_suites:
        try:
            results[name] = bool(fn())
        except AssertionError as e:
            print(f"\n断言失败: {e}")
            results[name] = False

    print("\n" + "=" * 80)
    print("总体测试结果")
    print("=" * 80)
    for name, _ in test_suites:
        print(f"{name}: {'✓ 通过' if results[name] else '✗ 失败'}")

    if all(results.values()):
        print("\n" + "=" * 80)
        print("🎉 所有测试通过！")
        print("=" * 80)
        print("\n所有节点已正确配置：")
        print("  ✓ 所有文件名包含 'Ben' 后缀")
        print("  ✓ 所有注册名包含 'Ben' 后缀（可通过 'Ben' 搜索）")
        print("  ✓ 所有显示名称为纯中文（不包含 'Ben'）")
        print("  ✓ 所有 CATEGORY 符合 'BenNodes/' 结构")
        print("  ✓ Python 和 JS 注册名完全匹配")
        print("\n在 ComfyUI 中重启服务器后，所有节点应该可以正确加载。")
        exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ 部分测试失败，请检查错误信息。")
        print("=" * 80)
        exit(1)
