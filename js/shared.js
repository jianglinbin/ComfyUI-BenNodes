// 分辨率预设（与 utils/constants/constants.py 保持一致）
export const RESOLUTIONS = {
    "270p": 270,
    "360p": 360,
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
    "2K": 1440,
    "4K": 2160,
    "5K": 2880,
    "8K": 4320,
    "自定义": null
};

// 宽高比预设（与 utils/constants/constants.py 保持一致）
export const ASPECT_RATIOS = {
    "16:9": [16, 9],
    "4:3": [4, 3],
    "1:1": [1, 1],
    "3:2": [3, 2],
    "2:3": [2, 3],
    "9:16": [9, 16],
    "21:9": [21, 9],
    "32:9": [32, 9],
    "9:18": [9, 18],
    "9:19": [9, 19],
    "9:19.5": [9, 19.5],
    "9:20": [9, 20],
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

/**
 * 为指定控件包装回调，在原回调后执行 update
 * @param {Object} node - 节点对象
 * @param {string[]} names - 控件名称列表
 * @param {Function} update - 回调后执行的更新函数
 */
export function wrapWidgetCallbacks(node, names, update) {
    names.forEach(n => {
        const w = getWidget(node, n);
        if (w) {
            const orig = w.callback;
            w.callback = v => {
                if (orig) orig.call(w, v);
                update();
            };
        }
    });
}

/**
 * 更新缩放系列节点的控件显示/隐藏与宽高联动
 * 适用于包含 resize_mode/resolution/aspect_ratio/width/height/
 * feathering/upscale_method/position（可选 pad_color）控件的节点
 * @param {Object} node - 节点对象
 * @returns {Object} 计算后的 { width, height }
 */
export function updateScalerWidgets(node) {
    try {
        const resizeModeW = getWidget(node, "resize_mode");
        if (!resizeModeW) return { width: 1080, height: 720 };

        const resW = getWidget(node, "resolution");
        if (!resW) return { width: 1080, height: 720 };

        const ratioW = getWidget(node, "aspect_ratio");
        const wW = getWidget(node, "width");
        const hW = getWidget(node, "height");
        const featherW = getWidget(node, "feathering");
        const upscaleMethodW = getWidget(node, "upscale_method");
        const positionW = getWidget(node, "position");
        const padColorW = getWidget(node, "pad_color");

        const resizeMode = resizeModeW.value;
        const isCustom = resW.value === "自定义";

        // 先全部隐藏，再按模式显示
        hideWidget(resW);
        hideWidget(ratioW);
        hideWidget(wW);
        hideWidget(hW);
        hideWidget(featherW);
        hideWidget(upscaleMethodW);
        hideWidget(positionW);
        hideWidget(padColorW);

        if (resizeMode !== "none") {
            showWidget(resW);
            if (resizeMode !== "contain" && ratioW) showWidget(ratioW);
            if (isCustom && wW && hW) {
                showWidget(wW);
                showWidget(hW);
                hideWidget(ratioW);
            }
        }

        if (resizeMode === "pad") {
            if (featherW) showWidget(featherW);
            if (padColorW) showWidget(padColorW);
        }

        if (["contain", "crop", "pad"].includes(resizeMode) && upscaleMethodW) {
            showWidget(upscaleMethodW);
        }

        if (["crop", "pad"].includes(resizeMode) && positionW) {
            showWidget(positionW);
        }

        // 计算尺寸并同步到宽高控件
        let d = { width: 1080, height: 720 };
        if (resizeMode !== "none") {
            d = calcDims(resW.value, ratioW?.value || "16:9", wW?.value || 1080, hW?.value || 720);
        }

        if (!isCustom && wW && hW) {
            wW.value = d.width;
            hW.value = d.height;
        }

        node.size = node.computeSize();
        node.setDirtyCanvas(true);
        return d;
    } catch (e) {
        console.error("[BenNodes] updateScalerWidgets error:", e);
        return { width: 1080, height: 720 };
    }
}

/**
 * 覆盖节点类型的 computeSize，按可见控件数量计算固定高度
 * @param {Object} nodeType - 节点类型原型
 */
export function applyFixedComputeSize(nodeType) {
    const origComputeSize = nodeType.prototype.computeSize;
    nodeType.prototype.computeSize = function () {
        const HEADER_HEIGHT = 40;
        const WIDGET_HEIGHT = 32;
        const PADDING = 10;
        const BOTTOM_SPACE = 10;

        const visibleWidgets = (this.widgets || []).filter(w => !w.hidden && w != null);
        const widgetsAreaHeight = HEADER_HEIGHT + visibleWidgets.length * WIDGET_HEIGHT + PADDING;
        const totalHeight = widgetsAreaHeight + BOTTOM_SPACE;

        const origSize = origComputeSize ? origComputeSize.apply(this, arguments) : [this.size ? this.size[0] : 200, totalHeight];
        return [origSize[0], totalHeight];
    };
}
