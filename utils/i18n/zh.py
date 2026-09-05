"""
ComfyUI-BenNodes 中文词典（key → 中文）
"""

TRANSLATIONS = {
    # ===== 通用 =====
    "common_cat_data": "数据",
    "common_cat_image": "图像",
    "common_cat_text": "文本",
    "common_cat_control": "控制",
    "common_cat_file": "文件",
    "common_error_prefix": "错误：",

    # ===== 显示名 =====
    "display_ResolutionSelectorBen": "选择分辨率",
    "display_PromptLineBen": "提示词行处理器",
    "display_ImageScalerBen": "图像缩放",
    "display_EmptyLatentImageBen": "空Latent",
    "display_ImageBatchLoaderBen": "加载图片批次",
    "display_ImageLoaderBen": "加载图片",
    "display_TextSaverBen": "保存文本",
    "display_TextSplitterBen": "文本拆分",
    "display_JSONParserBen": "JSON解析器",
    "display_ListIndexSelectorBen": "列表索引选择器",
    "display_AdvancedListIndexSelectorBen": "索引选择(高级)",
    "display_TypeConverterBen": "类型转换器",
    "display_TextProcessorBen": "文本处理器",
    "display_TextJoinerBen": "文本连接",
    "display_FileUploaderBen": "文件选择器",
    "display_MemoryCleanupBen": "释放显存内存",
    "display_NonNullSwitchBen": "非空切换",
    "display_NodeBypasserBen": "忽略节点",
    "display_AdvancedNodeBypasserBen": "忽略节点(高级)",
    "display_AdvancedGroupBypasserBen": "忽略组(高级)",
    "display_GroupBypasserBen": "忽略组",
    "display_ParameterDistributorBen": "参数分发器",

    # ===== 图像类共用 =====
    "image_common_return_image": "图片",
    "image_common_return_mask": "遮罩",
    "image_common_return_width": "宽度",
    "image_common_return_height": "高度",
    "image_common_return_filename": "文件名",

    # ===== ImageScalerBen =====
    "image_scaler_pad_color_placeholder": "R,G,B (例如: 255,0,0)",
    "image_scaler_batch_size_mismatch": "批次内图像输出尺寸不一致（resize_mode 为 none/contain 时，原图尺寸或宽高比不同会导致输出尺寸不同），请改用 pad/crop/fill 模式或保证批次内图像一致",

    # ===== ImageBatchLoaderBen =====
    "image_batch_loader_folder_path_label": "文件夹路径",
    "image_batch_loader_no_folder": "请选择要加载的文件夹",
    "image_batch_loader_folder_not_found": "文件夹不存在: {}",
    "image_batch_loader_no_images": "文件夹中没有找到图片文件: {}",
    "image_batch_loader_load_failed": "未能成功加载任何图片",

    # ===== ImageLoaderBen =====
    "image_loader_description": "加载单张图片，支持各种常见图片格式",
    "image_loader_invalid_file": "无效的图片文件: {}",

    # ===== EmptyLatentImageBen =====
    "empty_latent_description": "创建一批具有预设分辨率和宽高比的空Latent图像。",
    "empty_latent_output_tooltip": "一批待采样的空Latent图像",

    # ===== TextSaverBen =====
    "text_saver_texts_tooltip": "要保存的文本或文本批次",
    "text_saver_prefix_tooltip": "保存文件的前缀。可以包含格式化信息，如%date:yyyy-MM-dd%或其他变量",
    "text_saver_extension_tooltip": "保存文件的后缀名，例如.txt、.md、.json等",
    "text_saver_filename_tooltip": "可选的文件名。如果是批次处理，可以输入文件名列表。如果包含文件后缀，会自动去除",
    "text_saver_description": "将输入的文本或文本批次保存到ComfyUI输出目录",

    # ===== TextSplitterBen =====
    "text_split_delimiter_tooltip": "用于拆分文本的分隔符，默认为换行符",
    "text_split_start_index_tooltip": "从第几个拆分结果开始返回",
    "text_split_max_rows_tooltip": "最多返回多少个拆分结果",
    "text_split_description": "将输入的文本或文本列表按照指定的拆分符进行拆分，并返回指定范围的结果",

    # ===== TextJoinerBen =====
    "text_join_delimiter_tooltip": "用于连接文本的分隔符，默认为空",
    "text_join_description": "将两个输入文本或文本列表按照指定的规则进行连接。支持一个输入为列表类型，另一个为字符串类型。",
    "text_join_return_result": "连接结果",
    "text_join_both_lists": "两个输入参数不能同时为列表类型",

    # ===== TextProcessorBen =====
    "text_processor_text_tooltip": "多行文本输入",
    "text_processor_type_tooltip": "文本处理类型",
    "text_processor_description": "处理多行文本，支持去除空行、空白字符等操作",
    "text_processor_failed": "文本处理失败: {}",
    "text_processor_return_text": "文本",
    "text_processor_return_list": "文本列表",

    # ===== PromptLineBen（下拉选项为工作流值，保持中文不翻译） =====

    # ===== JSONParserBen =====
    "json_parser_json_string_tooltip": "JSON字符串输入",
    "json_parser_path_tooltip": "路径表达式，用于提取特定值，留空返回整个JSON。支持多个路径，使用分号(;)分隔",
    "json_parser_output_type_tooltip": "指定输出数据类型，AUTO表示自动判断",
    "json_parser_description": "解析JSON字符串并支持路径提取和文本转换",
    "json_parser_empty_input": "JSON字符串为空",
    "json_parser_invalid_json": "无效的JSON格式: {}",
    "json_parser_path_not_found": "路径不存在: {}",
    "json_parser_index_out_of_range": "数组索引越界: {}",
    "json_parser_parse_failed": "解析失败: {}",
    "json_parser_extract_failed": "提取失败: {}",
    "json_parser_no_start_marker": "未找到JSON开始标记",
    "json_parser_no_end_marker": "未找到JSON结束标记",
    "json_parser_invalid_path": "无效的路径表达式: {}",
    "json_parser_prop_not_found": "属性不存在: {}",

    # ===== TypeConverterBen =====
    "type_converter_target_type_tooltip": "目标数据类型（选择LIST类型会将输入转换为列表）",
    "type_converter_failed": "类型转换失败: {}",
    "type_converter_invalid_int_value": "无法将'{}' 转换为整数",
    "type_converter_invalid_int_type": "无法将类型{} 转换为整数",
    "type_converter_invalid_float_value": "无法将'{}' 转换为浮点数",
    "type_converter_invalid_float_type": "无法将类型{} 转换为浮点数",

    # ===== ListIndexSelectorBen =====
    "list_index_selector_index_tooltip": "要选择的列表索引，从0开始计数，支持单个int值或逗号分隔的字符串值，如 0,1,2,3",
    "list_index_selector_empty_input": "输入数据为空，请连接输入端口",
    "list_index_selector_invalid_type": "输入类型错误，需要列表、元组或张量，当前类型 {}",
    "list_index_selector_index_out_of_range": "索引 {} 超出范围，数据长度为 {}",
    "list_index_selector_invalid_index": "无效的索引值 {}",
    "list_index_selector_failed": "获取元素失败: {}",

    # ===== AdvancedListIndexSelectorBen =====
    "adv_list_selector_start_tooltip": "起始序号，从0开始计数",
    "adv_list_selector_step_tooltip": "步长，0或1表示连续选取，2表示每隔1个取一个，3表示每隔2个取一个，以此类推",
    "adv_list_selector_length_tooltip": "要选择的元素个数",
    "adv_list_selector_empty_input": "输入列表为空，请连接输入端口",
    "adv_list_selector_length_invalid": "长度 {} 必须大于0",
    "adv_list_selector_start_out_of_range": "起始序号 {} 超出数据范围，数据长度为 {}",
    "adv_list_selector_no_elements": "从起始序号 {} 开始没有可用的元素",
    "adv_list_selector_no_elements_step": "从起始序号 {} 开始，步长 {} 时没有可用的元素",
    "adv_list_selector_unsupported_type": "不支持的数据类型: {}",
    "adv_list_selector_failed": "高级索引选择失败: {}",

    # ===== NonNullSwitchBen =====
    "non_null_switch_all_empty": "NonNullSwitch 错误：所有输入都为空！\n请确保至少连接一个有效的输入。",

    # ===== AdvancedNodeBypasserBen =====
    "adv_node_bypasser_rules_tooltip": "JSON规则格式:\n{\n  \"规则名称\": [输入ID列表],\n  ...\n}\n\n示例:\n{\n  \"规则A\": [1, 2, 3],\n  \"规则B\": [4, 5, 6]\n}\n\n说明:\n- 键: 规则的显示名称\n- 值: 要激活的输入ID数组(从1开始)\n- 选择规则后,对应ID的输入会被激活,其他输入会被禁用",

    # ===== AdvancedGroupBypasserBen =====
    "adv_group_bypasser_rules_tooltip": "JSON规则格式:\n{\n  \"规则名称\": [\"组名称列表\"],\n  ...\n}\n\n示例:\n{\n  \"规则A\": [\"组1\", \"组2\"],\n  \"规则B\": [\"组3\", \"组4\"]\n}\n\n说明:\n- 键: 规则的显示名称\n- 值: 要激活的组名称数组\n- 选择规则后,对应名称的组会被激活,其他组会被禁用",

    # ===== FileUploaderBen =====
    "file_uploader_no_file": "请选择文件",
    "file_uploader_file_not_found": "文件不存在: {}",
    "file_uploader_image_load_failed": "图片加载失败: {}",
    "file_uploader_video_load_failed": "视频加载失败: {}",
    "file_uploader_return_output": "输出",
}
