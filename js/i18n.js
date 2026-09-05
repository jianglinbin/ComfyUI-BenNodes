/**
 * BenNodes 前端 i18n 中英双语支持
 *
 * 语言检测优先级：
 * 1. ComfyUI 设置 Comfy.Locale（如 zh-CN / en-US）
 * 2. 浏览器语言 navigator.language
 * 3. 默认 zh
 *
 * 注意：与后端工作流值耦合的文本（下拉选项、端口名等）保持中文，不进入本词典。
 */

import { app } from "../../scripts/app.js";

const ZH = {
    // 文件上传（file_uploader / load_image）
    "select_file": "选择文件",
    "upload_folder": "上传文件夹",
    "uploading": "上传中...",
    "uploading_progress": "上传中 {0}/{1}...",
    "selected": "已选择: {0}",
    "upload_failed": "上传失败",
    "upload_failed_with_error": "上传失败: {0}",

    // bypasser 系列
    "refresh_rules": "🔄 刷新规则",
    "node_bypasser": "忽略节点",
    "group_bypasser": "忽略组",
    "select_group": "选择组",
    "json_parse_error": "JSON解析错误: {0}",
    "json_must_be_object": "JSON必须是对象格式",
    "rule_value_must_be_array": "规则\"{0}\"的值必须是数组",
    "rule_non_integer": "规则\"{0}\"中包含非整数值: {1}",
    "rule_non_string": "规则\"{0}\"中包含非字符串值: {1}",

    // 内存清理
    "cleanup_mode_label": "清理模式",
    "cleanup_desc_none": "⏭️ 不执行清理\n• 直接传递数据\n• 不清理任何内存\n\n适用：调试或跳过清理",
    "cleanup_desc_vram_only": "💾 只清理显存\n• 卸载模型\n• 清空VRAM缓存\n\n适用：显存不足时",
    "cleanup_desc_ram_only": "🧠 只清理内存\n• 清理文件缓存\n• 清理进程内存\n• 清理未使用DLL\n\n适用：内存不足时",
    "cleanup_desc_all": "🔥 深度清理\n• 显存：卸载模型+清空缓存\n• 内存：全部清理\n\n适用：严重内存不足",

    // 参数分发器
    "lock_params": "🔒 锁定参数",
    "locked": "已锁定",
    "unlocked": "未锁定",
    "refresh_outputs": "刷新输出",

    // 列表索引选择器
    "list_length": "列表长度: {0}",
};

const EN = {
    "select_file": "Select File",
    "upload_folder": "Upload Folder",
    "uploading": "Uploading...",
    "uploading_progress": "Uploading {0}/{1}...",
    "selected": "Selected: {0}",
    "upload_failed": "Upload failed",
    "upload_failed_with_error": "Upload failed: {0}",

    "refresh_rules": "🔄 Refresh Rules",
    "node_bypasser": "Node Bypasser",
    "group_bypasser": "Group Bypasser",
    "select_group": "Select Group",
    "json_parse_error": "JSON parse error: {0}",
    "json_must_be_object": "JSON must be an object",
    "rule_value_must_be_array": "Value of rule \"{0}\" must be an array",
    "rule_non_integer": "Rule \"{0}\" contains a non-integer value: {1}",
    "rule_non_string": "Rule \"{0}\" contains a non-string value: {1}",

    "cleanup_mode_label": "Cleanup Mode",
    "cleanup_desc_none": "⏭️ No cleanup\n• Pass data through directly\n• No memory cleaned\n\nUse case: debugging or skipping cleanup",
    "cleanup_desc_vram_only": "💾 VRAM only\n• Unload models\n• Clear VRAM cache\n\nUse case: low VRAM",
    "cleanup_desc_ram_only": "🧠 RAM only\n• Clear file cache\n• Clean process memory\n• Clean unused DLLs\n\nUse case: low RAM",
    "cleanup_desc_all": "🔥 Deep cleanup\n• VRAM: unload models + clear cache\n• RAM: full cleanup\n\nUse case: severely low memory",

    "lock_params": "🔒 Lock Params",
    "locked": "Locked",
    "unlocked": "Unlocked",
    "refresh_outputs": "Refresh Outputs",

    "list_length": "List length: {0}",
};

function detectLang() {
    // 1. ComfyUI Locale 设置
    try {
        const locale = app?.ui?.settings?.getSettingValue?.("Comfy.Locale");
        if (typeof locale === "string" && locale.length > 0) {
            return locale.toLowerCase().startsWith("zh") ? "zh" : "en";
        }
    } catch (e) { /* 忽略 */ }

    // 2. 浏览器语言
    try {
        const nav = (navigator.language || "").toLowerCase();
        if (nav) {
            return nav.startsWith("zh") ? "zh" : "en";
        }
    } catch (e) { /* 忽略 */ }

    // 3. 默认
    return "zh";
}

const LANG = detectLang();
const DICT = LANG === "en" ? EN : ZH;

/**
 * 查表翻译。支持 {0}/{1} 位置参数替换。缺失 key 回退为 key 本身。
 * @param {string} key
 * @param {...*} args - 位置参数，替换 {0} {1} ...
 * @returns {string}
 */
export function t(key, ...args) {
    let value = DICT[key];
    if (value === undefined) {
        console.warn(`[BenNodes i18n] missing key: ${key} (${LANG})`);
        value = key;
    }
    return value.replace(/\{(\d+)\}/g, (m, i) => (args[i] !== undefined ? String(args[i]) : m));
}

export function getLang() {
    return LANG;
}
