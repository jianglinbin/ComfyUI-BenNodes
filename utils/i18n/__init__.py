"""
ComfyUI-BenNodes i18n 中英双语支持

语言解析优先级（模块加载时确定一次）：
1. 环境变量 BENNODES_LANG（zh/en，大小写不敏感）
2. 项目根 ben_nodes_config.json 的 "language" 字段
3. 默认 zh

用法：
    from ...utils.i18n import t
    CATEGORY = f"BenNodes/{t('common_cat_data')}"
    "tooltip": t("type_converter_target_type_tooltip")
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

# 项目根目录（utils/i18n/__init__.py 向上两级）
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SUPPORTED_LANGUAGES = ("zh", "en")
DEFAULT_LANGUAGE = "zh"


def _detect_language():
    """按优先级解析当前语言，返回 'zh' 或 'en'"""
    # 1. 环境变量
    env_lang = os.environ.get("BENNODES_LANG", "").strip().lower()
    if env_lang in SUPPORTED_LANGUAGES:
        return env_lang
    if env_lang:
        logger.warning("BENNODES_LANG='%s' 不受支持（可用: %s），尝试配置文件", env_lang, "/".join(SUPPORTED_LANGUAGES))

    # 2. 配置文件
    config_path = os.path.join(_PROJECT_ROOT, "ben_nodes_config.json")
    try:
        if os.path.isfile(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            config_lang = str(config.get("language", "")).strip().lower()
            if config_lang in SUPPORTED_LANGUAGES:
                return config_lang
            if config_lang:
                logger.warning("ben_nodes_config.json 的 language='%s' 不受支持（可用: %s）",
                               config_lang, "/".join(SUPPORTED_LANGUAGES))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("读取 ben_nodes_config.json 失败: %s", e)

    # 3. 默认
    return DEFAULT_LANGUAGE


# 模块加载时确定语言一次
CURRENT_LANGUAGE = _detect_language()

if CURRENT_LANGUAGE == "en":
    from .en import TRANSLATIONS
else:
    from .zh import TRANSLATIONS

# 缺失 key 只告警一次
_warned_keys = set()


def t(key):
    """查表翻译。缺失 key 回退为 key 本身并告警一次。"""
    value = TRANSLATIONS.get(key)
    if value is None:
        if key not in _warned_keys:
            _warned_keys.add(key)
            logger.warning("i18n 缺失翻译 key: %s (语言: %s)", key, CURRENT_LANGUAGE)
        return key
    return value


def get_current_language():
    """返回当前语言代码"""
    return CURRENT_LANGUAGE
