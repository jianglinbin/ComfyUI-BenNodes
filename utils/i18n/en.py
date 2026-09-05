"""
ComfyUI-BenNodes English dictionary (key -> English)
"""

TRANSLATIONS = {
    # ===== Common =====
    "common_cat_data": "Data",
    "common_cat_image": "Image",
    "common_cat_text": "Text",
    "common_cat_control": "Control",
    "common_cat_file": "File",
    "common_error_prefix": "Error: ",

    # ===== Display names =====
    "display_ResolutionSelectorBen": "Resolution Selector",
    "display_PromptLineBen": "Prompt Line Processor",
    "display_ImageScalerBen": "Image Scaler",
    "display_EmptyLatentImageBen": "Empty Latent",
    "display_ImageBatchLoaderBen": "Load Image Batch",
    "display_ImageLoaderBen": "Load Image",
    "display_TextSaverBen": "Save Text",
    "display_TextSplitterBen": "Text Splitter",
    "display_JSONParserBen": "JSON Parser",
    "display_ListIndexSelectorBen": "List Index Selector",
    "display_AdvancedListIndexSelectorBen": "List Index Selector (Advanced)",
    "display_TypeConverterBen": "Type Converter",
    "display_TextProcessorBen": "Text Processor",
    "display_TextJoinerBen": "Text Joiner",
    "display_FileUploaderBen": "File Selector",
    "display_MemoryCleanupBen": "Memory Cleanup",
    "display_NonNullSwitchBen": "Non-Null Switch",
    "display_NodeBypasserBen": "Node Bypasser",
    "display_AdvancedNodeBypasserBen": "Node Bypasser (Advanced)",
    "display_AdvancedGroupBypasserBen": "Group Bypasser (Advanced)",
    "display_GroupBypasserBen": "Group Bypasser",
    "display_ParameterDistributorBen": "Parameter Distributor",

    # ===== Shared (image nodes) =====
    "image_common_return_image": "image",
    "image_common_return_mask": "mask",
    "image_common_return_width": "width",
    "image_common_return_height": "height",
    "image_common_return_filename": "filename",

    # ===== ImageScalerBen =====
    "image_scaler_pad_color_placeholder": "R,G,B (e.g.: 255,0,0)",

    # ===== ImageBatchLoaderBen =====
    "image_batch_loader_folder_path_label": "Folder Path",
    "image_batch_loader_no_folder": "Please select a folder to load",
    "image_batch_loader_folder_not_found": "Folder not found: {}",
    "image_batch_loader_no_images": "No image files found in folder: {}",
    "image_batch_loader_load_failed": "Failed to load any images",

    # ===== ImageLoaderBen =====
    "image_loader_description": "Load a single image, supports common image formats",
    "image_loader_invalid_file": "Invalid image file: {}",

    # ===== EmptyLatentImageBen =====
    "empty_latent_description": "Create a new batch of empty latent images with preset resolutions and aspect ratios.",

    # ===== TextSaverBen =====
    "text_saver_texts_tooltip": "The text or text batch to save",
    "text_saver_prefix_tooltip": "Filename prefix for saving. May contain formatting info such as %date:yyyy-MM-dd% or other variables",
    "text_saver_extension_tooltip": "File extension for saving, e.g. .txt, .md, .json",
    "text_saver_filename_tooltip": "Optional filename. For batch processing, a list of filenames may be provided. File extensions are stripped automatically",
    "text_saver_description": "Save the input text or text batch to the ComfyUI output directory",

    # ===== TextSplitterBen =====
    "text_split_delimiter_tooltip": "Delimiter used to split the text, defaults to newline",
    "text_split_start_index_tooltip": "Return results starting from this split index",
    "text_split_max_rows_tooltip": "Maximum number of split results to return",
    "text_split_description": "Split the input text or text list by the given delimiter and return the specified range of results",

    # ===== TextJoinerBen =====
    "text_join_delimiter_tooltip": "Delimiter used to join the texts, defaults to empty",
    "text_join_description": "Join two input texts or text lists by the given rule. Supports one input as a list and the other as a string.",
    "text_join_return_result": "joined result",
    "text_join_both_lists": "Both inputs cannot be list type at the same time",

    # ===== TextProcessorBen =====
    "text_processor_text_tooltip": "Multi-line text input",
    "text_processor_type_tooltip": "Text processing type",
    "text_processor_description": "Process multi-line text: remove empty lines, whitespace, etc.",
    "text_processor_failed": "Text processing failed: {}",
    "text_processor_return_text": "text",
    "text_processor_return_list": "text list",

    # ===== EmptyLatentImageBen =====
    "empty_latent_output_tooltip": "A batch of empty latent images to be denoised via sampling.",

    # ===== PromptLineBen (combo options are workflow values, kept in Chinese) =====

    # ===== JSONParserBen =====
    "json_parser_json_string_tooltip": "JSON string input",
    "json_parser_path_tooltip": "Path expression to extract specific values. Leave empty to return the whole JSON. Supports multiple paths separated by semicolons (;)",
    "json_parser_output_type_tooltip": "Specify the output data type. AUTO means automatic detection",
    "json_parser_description": "Parse a JSON string with path extraction and text conversion",
    "json_parser_empty_input": "JSON string is empty",
    "json_parser_invalid_json": "Invalid JSON format: {}",
    "json_parser_path_not_found": "Path not found: {}",
    "json_parser_index_out_of_range": "Array index out of range: {}",
    "json_parser_parse_failed": "Parsing failed: {}",
    "json_parser_extract_failed": "Extraction failed: {}",
    "json_parser_no_start_marker": "JSON start marker not found",
    "json_parser_no_end_marker": "JSON end marker not found",
    "json_parser_invalid_path": "Invalid path expression: {}",
    "json_parser_prop_not_found": "Property not found: {}",

    # ===== TypeConverterBen =====
    "type_converter_target_type_tooltip": "Target data type (selecting a LIST type converts the input into a list)",
    "type_converter_failed": "Type conversion failed: {}",
    "type_converter_invalid_int_value": "Cannot convert '{}' to integer",
    "type_converter_invalid_int_type": "Cannot convert type {} to integer",
    "type_converter_invalid_float_value": "Cannot convert '{}' to float",
    "type_converter_invalid_float_type": "Cannot convert type {} to float",

    # ===== ListIndexSelectorBen =====
    "list_index_selector_index_tooltip": "List index to select, starting from 0. Supports a single int or comma-separated values, e.g. 0,1,2,3",
    "list_index_selector_empty_input": "Input data is empty, please connect an input port",
    "list_index_selector_invalid_type": "Invalid input type, expected list/tuple/tensor, got {}",
    "list_index_selector_index_out_of_range": "Index {} out of range, data length is {}",
    "list_index_selector_invalid_index": "Invalid index value {}",
    "list_index_selector_failed": "Failed to get element: {}",

    # ===== AdvancedListIndexSelectorBen =====
    "adv_list_selector_start_tooltip": "Start index, counting from 0",
    "adv_list_selector_step_tooltip": "Step size: 0 or 1 selects continuously, 2 selects every other item, 3 skips two items, and so on",
    "adv_list_selector_length_tooltip": "Number of elements to select",
    "adv_list_selector_empty_input": "Input list is empty, please connect an input port",
    "adv_list_selector_length_invalid": "Length {} must be greater than 0",
    "adv_list_selector_start_out_of_range": "Start index {} is out of range, data length is {}",
    "adv_list_selector_no_elements": "No available elements starting from index {}",
    "adv_list_selector_no_elements_step": "No available elements starting from index {} with step {}",
    "adv_list_selector_unsupported_type": "Unsupported data type: {}",
    "adv_list_selector_failed": "Advanced index selection failed: {}",

    # ===== NonNullSwitchBen =====
    "non_null_switch_all_empty": "NonNullSwitch error: all inputs are empty!\nPlease connect at least one valid input.",

    # ===== AdvancedNodeBypasserBen =====
    "adv_node_bypasser_rules_tooltip": "JSON rule format:\n{\n  \"rule name\": [input ID list],\n  ...\n}\n\nExample:\n{\n  \"Rule A\": [1, 2, 3],\n  \"Rule B\": [4, 5, 6]\n}\n\nNotes:\n- Key: display name of the rule\n- Value: array of input IDs to activate (starting from 1)\n- After selecting a rule, inputs with the matching IDs are activated and the others are bypassed",

    # ===== AdvancedGroupBypasserBen =====
    "adv_group_bypasser_rules_tooltip": "JSON rule format:\n{\n  \"rule name\": [\"group name list\"],\n  ...\n}\n\nExample:\n{\n  \"Rule A\": [\"Group 1\", \"Group 2\"],\n  \"Rule B\": [\"Group 3\", \"Group 4\"]\n}\n\nNotes:\n- Key: display name of the rule\n- Value: array of group names to activate\n- After selecting a rule, groups with the matching names are activated and the others are bypassed",

    # ===== FileUploaderBen =====
    "file_uploader_no_file": "Please select a file",
    "file_uploader_file_not_found": "File not found: {}",
    "file_uploader_image_load_failed": "Image loading failed: {}",
    "file_uploader_video_load_failed": "Video loading failed: {}",
    "file_uploader_return_output": "output",
}
