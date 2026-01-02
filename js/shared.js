// 分辨率预设
export const RESOLUTIONS = { 
    "270p": 270, 
    "360p": 360, 
    "480p": 480, 
    "720p": 720, 
    "1080p": 1080, 
    "2K": 1440, 
    "4K": 2160, 
    "5K": 2880, 
    "8K": 4320 
};

// 宽高比预设
export const ASPECT_RATIOS = { 
    "16:9": [16, 9], 
    "4:3": [4, 3], 
    "1:1": [1, 1], 
    "3:2": [3, 2], 
    "9:16": [9, 16], 
    "21:9": [21, 9], 
    "18:9": [18, 9], 
    "5:4": [5, 4], 
    "3:4": [3, 4] 
};

/**
 * 获取节点的控件
 * @param {Object} node - 节点对象
 * @param {string} name - 控件名称
 * @returns {Object|null} 找到的控件或 null
 */
export function getWidget(node, name) {
    return node.widgets ? node.widgets.find(w => w.name === name) : null;
}

/**
 * 隐藏控件
 * @param {Object} widget - 控件对象
 */
export function hideWidget(widget) {
    if (widget) {
        widget.hidden = true;
        widget.computeSize = () => [0, -4];
    }
}

/**
 * 显示控件
 * @param {Object} widget - 控件对象
 */
export function showWidget(widget) {
    if (widget) {
        widget.hidden = false;
        delete widget.computeSize;
    }
}

/**
 * 计算分辨率
 * @param {string} res - 分辨率预设名称
 * @param {string} ratio - 宽高比预设名称
 * @param {number} width - 自定义宽度
 * @param {number} height - 自定义高度
 * @returns {Object} 计算后的宽度和高度
 */
export function calcDims(res, ratio, width, height) {
    if (res === "自定义") return { width: width, height: height };
    const h = RESOLUTIONS[res] || 720;
    const r = ASPECT_RATIOS[ratio] || [16, 9];
    return { width: Math.round(h * r[0] / r[1]), height: h };
}

/**
 * 更新分辨率相关控件的显示状态
 * @param {Object} node - 节点对象
 */
export function updateResolutionControls(node) {
    const resW = getWidget(node, "resolution");
    const ratioW = getWidget(node, "aspect_ratio");
    const widthW = getWidget(node, "width");
    const heightW = getWidget(node, "height");

    if (!resW) return;

    // 获取当前值
    const resolution = resW.value;
    const isCustom = resolution === "自定义";

    // 隐藏或显示控件
    if (ratioW) {
        if (isCustom) {
            // 自定义分辨率时隐藏宽高比
            hideWidget(ratioW);
        } else {
            // 非自定义分辨率时显示宽高比
            showWidget(ratioW);
        }
    }
    
    // 处理宽高控件的显示/隐藏
    if (widthW && heightW) {
        if (isCustom) {
            // 自定义分辨率时显示宽高
            showWidget(widthW);
            showWidget(heightW);
        } else {
            // 非自定义分辨率时隐藏宽高
            hideWidget(widthW);
            hideWidget(heightW);
        }
    }

    node.size = node.computeSize();
    node.setDirtyCanvas(true);
}
