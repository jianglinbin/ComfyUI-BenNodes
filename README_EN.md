# ComfyUI-BenNodes

A collection of 22 practical custom nodes for ComfyUI, covering image processing, text processing, data conversion, system utilities, and workflow control.

[中文](README.md) | English

## ✨ Features

- 🖼️ **Image Processing**: Smart scaling, batch loading, multiple alignment modes
- 📝 **Text Processing**: Split, join, save, multi-line processing
- 📊 **Data Conversion**: JSON parser, type converter, list selector
- 🔧 **System Utilities**: Memory cleanup, non-null switch, file selector
- 🎮 **Workflow Control**: Node bypasser, group bypasser, parameter distributor
- 🌐 **Bilingual (zh/en)**: Node display names, tooltips and error messages in Chinese and English

## 🌐 Bilingual Support (i18n)

Node display names, categories, parameter tooltips, and error messages support both Chinese and English. Language resolution priority:

1. Environment variable `BENNODES_LANG` (`zh` / `en`, case-insensitive)
2. The `"language"` field in `ben_nodes_config.json` at the project root (copy `ben_nodes_config.json.example` as a starting point)
3. Defaults to `zh`

> Note: The language is determined once when the node package is loaded. Restart ComfyUI after changing the configuration. Combo option values (e.g. "去除空行", "仅显存") are workflow-saved values and are kept unchanged for backward compatibility.

## 📦 Installation

### Method 1: Install via ComfyUI Manager (Recommended)

1. Open ComfyUI Manager
2. Search for "BenNodes"
3. Click Install

### Method 2: Manual Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/jianglinbin/ComfyUI-BenNodes.git
cd ComfyUI-BenNodes
pip install -r requirements.txt
```

## 📚 Node List

### 📊 Data Processing (5 nodes)
- **Resolution Selector** - Preset resolution and aspect ratio selection
- **List Index Selector** - Select elements by index from list
- **Advanced List Index Selector** - Support start, step, length control
- **JSON Parser** - Parse JSON with path extraction
- **Type Converter** - Convert between any types

### 📁 File Operations (1 node)
- **File Uploader** - Select files from file system

### 🖼️ Image Processing (4 nodes)
- **Image Loader** - Load single image
- **Image Batch Loader** - Batch load images from folder
- **Image Scaler** - Scale, crop, pad images
- **Empty Latent Image** - Create empty latent image

### 🔧 System Utilities (1 node)
- **Memory Cleanup** - Clean VRAM and RAM

### 📝 Text Processing (5 nodes)
- **Prompt Line Processor** - Process multi-line prompts
- **Text Saver** - Save text to file
- **Text Splitter** - Split text by delimiter
- **Text Joiner** - Join text or lists
- **Text Processor** - Remove empty lines, whitespace

### 🎮 Workflow Control (7 nodes)
- **Non-Null Switch** - Return first non-null value
- **Node Bypasser** - Control multiple nodes execution
- **Advanced Node Bypasser** - JSON rule-based conditional activation
- **Group Bypasser** - Control group execution
- **Advanced Group Bypasser** - JSON rule-based group control
- **Parameter Distributor** - Dynamic parameter distribution

---

## 🔧 Dependencies

### Core Dependencies (Required)
```bash
pip install Pillow psutil
```

### Image Enhancement (Recommended, for feathering)
```bash
pip install scipy
```

---

## 📖 Detailed Documentation


#### Resolution Selector

**Category**: `BenNodes/Data`

Provides preset resolutions and aspect ratios, automatically calculates output width and height.

**Input Parameters**:
- `resolution` (COMBO): Preset resolution (480p/720p/1080p/2K/4K/8K/Custom)
- `aspect_ratio` (COMBO): Aspect ratio (16:9/4:3/1:1/21:9/9:16/3:4/Custom)
- `width` (INT): Custom width, default 1280
- `height` (INT): Custom height, default 720

**Output**:
- `width` (INT): Calculated width
- `height` (INT): Calculated height
- `resolution_text` (STRING): Resolution description

---

#### List Index Selector

**Category**: `BenNodes/Data`

Select elements by index from list, supports batch image processing.

**Input Parameters**:
- `*` (ANY): Input list
- `index` (STRING): Index, supports comma-separated values like "0,2,4"

**Output**:
- `ITEM_0 ~ ITEM_19`: Up to 20 outputs

**Example**:
```
[Image Batch Loader] → [List Index Selector] → [Save Image]
                        index: "0,2,4"
```

---

#### Advanced List Index Selector

**Category**: `BenNodes/Data`

Advanced list index selection with start position, step, and length control.

**Input Parameters**:
- `list` (ANY): Input list
- `start_index` (INT): Start index, default 0
- `step` (INT): Step value, 0 means no step
- `length` (INT): Number of elements to select, default 1

**Output**:
- `SELECTED_LIST`: Selected element list

**Example**:
```
# Start from 5th, take every 2nd, total 3 elements
start_index: 5
step: 2
length: 3
Result: [5, 7, 9]
```

---

#### JSON Parser

**Category**: `BenNodes/Data`

Parse JSON string with path extraction support.

**Input Parameters**:
- `json_string` (STRING): JSON string
- `json_path` (STRING): Path expression, supports multiple paths (semicolon-separated)
- `output_type` (COMBO): Output data type

**Output**:
- `JSON_TEXT` (STRING): Formatted JSON text
- `PARSED_RESULT` (ANY): Parsed result

**Path Syntax**:
- Simple property: `name`
- Nested property: `user.name`
- Array index: `items[0].name`
- Combined path: `data.users[1].address.city`
- Multiple paths: `name;age;address.city`

**Example**:
```json
{
  "user": {
    "name": "John",
    "age": 25
  }
}
```
Path: `user.name` → Output: "John"

---

#### Type Converter

**Category**: `BenNodes/Data`

Convert any type of input to specified data type.

**Input Parameters**:
- `*` (ANY): Input data
- `target_type` (COMBO): Target type

**Supported Types**:
- STRING, LIST<STRING>
- INT, LIST<INT>
- FLOAT, LIST<FLOAT>
- BOOLEAN, LIST<BOOLEAN>

**Conversion Rules**:
- Single → Single: Direct conversion
- Single → List: Convert and wrap in list
- List → Single: Convert first element
- List → List: Convert each element

---

### 📁 File Operations

#### File Uploader

**Category**: `BenNodes/File`

Select files from file system, supports images, videos, documents, etc.

**Input Parameters**:
- `file_path` (STRING): File path selector

**Output**:
- `file_path` (STRING): Full file path
- `file_name` (STRING): File name
- `file_extension` (STRING): File extension

---


### 🖼️ Image Processing

#### Image Loader

**Category**: `BenNodes/Image`

Load single image with support for multiple formats and scaling modes.

**Input Parameters**:
- `image` (COMBO): Image file selection
- `resize_mode` (COMBO): Scaling mode (none/fit/fill/stretch/pad)
- `position` (COMBO): Alignment position (center/top/bottom/left/right, etc.)
- `resolution` (COMBO): Target resolution
- `aspect_ratio` (COMBO): Target aspect ratio
- `width` (INT): Target width, default 1080
- `height` (INT): Target height, default 720
- `feathering` (INT): Feathering amount, default 0
- `upscale_method` (COMBO): Scaling algorithm (nearest/bilinear/bicubic/lanczos)

**Output**:
- `Image` (IMAGE): Processed image
- `Mask` (MASK): Mask
- `Width` (INT): Image width
- `Height` (INT): Image height
- `Filename` (STRING): File name

**Scaling Modes**:
- `none`: No scaling
- `fit`: Fit (maintain aspect ratio, may have black bars)
- `fill`: Fill (crop to fill)
- `stretch`: Stretch (don't maintain aspect ratio)
- `pad`: Pad with black bars

---

#### Image Batch Loader

**Category**: `BenNodes/Image`

Batch load all images from a folder.

**Input Parameters**:
- `folder_path` (COMBO): Folder selection
- Other parameters same as "Image Loader"

**Output**:
- `Image` (IMAGE): Image batch
- `Mask` (MASK): Mask batch
- `Width` (INT): Image width
- `Height` (INT): Image height
- `Filename` (STRING LIST): File name list

---

#### Image Scaler

**Category**: `BenNodes/Image`

Scale, crop, pad images with batch processing and multi-threading support.

**Input Parameters**:
- `image` (IMAGE): Input image
- `resize_mode` (COMBO): Scaling mode
- `position` (COMBO): Alignment position
- `resolution` (COMBO): Target resolution
- `aspect_ratio` (COMBO): Target aspect ratio
- `width` (INT): Target width
- `height` (INT): Target height
- `feathering` (INT): Feathering amount
- `upscale_method` (COMBO): Scaling algorithm
- `pad_color` (STRING): Padding color (RGB format, e.g., "127,127,127")

**Output**:
- `IMAGE`: Processed image
- `MASK`: Mask
- `width` (INT): Width
- `height` (INT): Height

**Features**:
- Batch processing support
- Multi-threading acceleration
- Custom padding color
- Feathering effect (requires scipy)

---

#### Empty Latent Image

**Category**: `BenNodes/Image`

Create empty latent image for image generation.

**Input Parameters**:
- `resolution` (COMBO): Resolution, default 1080p
- `aspect_ratio` (COMBO): Aspect ratio, default 16:9
- `width` (INT): Width, default 1920
- `height` (INT): Height, default 1080
- `batch_size` (INT): Batch size, default 1

**Output**:
- `LATENT`: Empty latent image

---

### 🔧 System Utilities

#### Memory Cleanup

**Category**: `BenNodes/Control`

Clean VRAM and RAM to optimize system resource usage.

**Input Parameters**:
- `cleanup_mode` (COMBO): Cleanup mode (None/VRAM Only/RAM Only/All), default "All"
- `input` (ANY): Input data (pass-through)

**Output**:
- `output` (ANY): Pass-through input data

**Cleanup Modes**:
- `None`: No cleanup, direct pass-through
- `VRAM Only`: Unload models, clear cache
- `RAM Only`: Clear file cache, process memory, DLLs
- `All`: Clean both VRAM and RAM

**Use Case**:
Insert in workflow to clean unnecessary models and cache:
```
[Generate Image] → [Memory Cleanup] → [Upscale Image]
```

---

### 📝 Text Processing

#### Prompt Line Processor

**Category**: `BenNodes/Text`

Process multi-line prompts with support for extracting specific line ranges and applying operations.

**Input Parameters**:
- `prompt` (STRING): Multi-line text
- `start_index` (INT): Start line number, default 0
- `max_rows` (INT): Max rows to return, default 1000
- `operation` (COMBO): Text operation

**Supported Operations**:
- Original, Uppercase, Lowercase, Capitalize, Title Case
- Strip, Reverse, Length, Remove Empty Lines

**Output**:
- `STRING`: Processed text (list)

---

#### Text Saver

**Category**: `BenNodes/Text`

Save text or text batch to file.

**Input Parameters**:
- `texts` (STRING): Text to save
- `filename_prefix` (STRING): Filename prefix, default "ComfyUI"
- `file_extension` (STRING): File extension, default ".txt"
- `filename` (STRING): Optional filename

**Output**:
- UI displays saved file list

**Example**:
```
[Text Processor] → [Text Saver]
                 filename_prefix: "analysis"
                 file_extension: ".md"
```

---

#### Text Splitter

**Category**: `BenNodes/Text`

Split text by specified delimiter.

**Input Parameters**:
- `text` (STRING): Input text
- `delimiter` (STRING): Delimiter, default "\n"
- `start_index` (INT): Start index, default 0
- `max_rows` (INT): Max items to return, default 1000

**Output**:
- `STRING`: Split text list

---

#### Text Joiner

**Category**: `BenNodes/Text`

Join two texts or text lists.

**Input Parameters**:
- `text1` (STRING): First text
- `text2` (STRING): Second text
- `delimiter` (STRING): Delimiter

**Join Rules**:
- Two strings → Direct join
- String + List → String joins with each list element
- List + String → Each list element joins with string
- List + List → Join corresponding elements

**Output**:
- `Join Result` (STRING or STRING LIST)

---

#### Text Processor

**Category**: `BenNodes/Text`

Process multi-line text with support for removing empty lines, whitespace, etc.

**Input Parameters**:
- `text` (STRING): Multi-line text
- `process_type` (COMBO): Processing type, default "none"

**Processing Types**:
- `none`: No processing
- `Remove Empty Lines`: Delete empty lines
- `Remove Whitespace`: Remove leading/trailing whitespace from each line
- `Remove Whitespace + Empty Lines`: Both

**Output**:
- `Text` (STRING): Complete text
- `Text List` (STRING): Line-split list

---


### 🎮 Workflow Control

#### Non-Null Switch

**Category**: `BenNodes/Control`

Check multiple inputs in order and return the first non-null value, supports multi-level fallback switching.

**Input Parameters**:
- `Main Source` (ANY): Primary input (optional)
- `Alternative 1` (ANY): First alternative input (optional)
- `Alternative 2~N` (ANY): More alternative inputs (dynamically added)

**Output**:
- `output` (ANY): First non-null value

**Logic**:
1. Check "Main Source", return if non-null
2. Otherwise check "Alternative 1", return if non-null
3. Continue checking "Alternative 2", "Alternative 3"...
4. If all inputs are null, throw error

**Features**:
- Dynamic input management: Automatically adds new alternative input when two inputs are connected
- Supports up to 20 inputs
- Multi-level fallback switching

**Use Case**:
Use with "Node Bypasser" to handle missing data when nodes are bypassed:
```
[Node A] ──→ [Non-Null Switch] ──→ [Node C]
            ↑ Main Source
[Node B] ────┘ Alternative 1
```

---

#### Node Bypasser

**Category**: `BenNodes/Control`

Control multiple connected nodes' execution state with a single master switch.

**Features**:
- Dynamic input slot auto-management
- Single master switch controls all connected nodes
- Pass-through nodes automatically follow
- Fully independent implementation

**Usage**:
1. Add "Node Bypasser" to workflow
2. Connect nodes you want to control to "Node Bypasser" inputs
3. Use switch to control enable/bypass state of all connected nodes

**Switch States**:
- `yes`: Enable all connected nodes
- `no`: Bypass all connected nodes

**Note**:
⚠️ When nodes are bypassed, they won't execute and won't produce output. If downstream nodes depend on this output, they will error. Recommend using with "Non-Null Switch" node.

---

#### Advanced Node Bypasser

**Category**: `BenNodes/Control`

Supports JSON rule-based conditional activation, can define multiple rule sets, each controlling different node combinations.

**Input Parameters**:
- `json_rules` (STRING): JSON rule configuration

**JSON Rule Format**:
```json
{
  "Rule A": [1, 2, 3],
  "Rule B": [4, 5, 6]
}
```

**Description**:
- Key: Rule display name
- Value: Array of input IDs to activate (starting from 1)
- When rule is selected, corresponding ID inputs are activated, others are disabled

**Use Cases**:
- Complex workflow scenario switching
- Quick switching between multiple parameter configurations
- A/B testing

---

#### Group Bypasser

**Category**: `BenNodes/Control`

Control group execution state by selecting group name and switch.

**Features**:
- COMBO selection of group name (auto-updates group list)
- BOOL switch controls group activate/bypass state
- On = Activate group, Off = Bypass group

**Usage**:
1. Create groups in workflow (select multiple nodes, right-click → Convert to Group)
2. Add "Group Bypasser" node
3. Select group to control from dropdown
4. Use switch to control group enable/bypass state

---

#### Advanced Group Bypasser

**Category**: `BenNodes/Control`

Supports JSON rule-based conditional group activation, no connection needed, automatically traverses all groups.

**Input Parameters**:
- `json_rules` (STRING): JSON rule configuration

**JSON Rule Format**:
```json
{
  "Rule A": ["Group1", "Group2"],
  "Rule B": ["Group3", "Group4"]
}
```

**Description**:
- Key: Rule display name
- Value: Array of group names to activate
- When rule is selected, corresponding named groups are activated, others are disabled

**Use Cases**:
- Multi-scenario workflow switching
- Batch control of multiple groups
- Complex workflow management

---

#### Parameter Distributor

**Category**: `BenNodes/Control`

Dynamic parameter distribution and replication, automatically replicates output parameter when connected and adds new empty output slot.

**Features**:
- Dynamic output slot auto-management
- Automatically adds new output after connection
- Supports any data type passing
- Each output independently configured
- Parameter locking feature

**Output**:
- Up to 20 dynamic outputs

**Usage**:
1. Add "Parameter Distributor" node
2. Configure parameter values on node
3. Connect output to nodes that need the parameter
4. New output slot automatically added after connection
5. Can lock parameters to prevent accidental modification

**Use Cases**:
- Distribute one parameter to multiple nodes
- Parameter reuse and management
- Centralized workflow parameter configuration

---

## 💡 Usage Tips

### 1. Batch Image Processing Workflow

```
[Image Batch Loader] → [List Index Selector] → [Image Scaler] → [Save Image]
                        index: "0,2,4,6"
```

### 2. Multi-Level Fallback Data Flow

```
[Main Node] ──→ [Non-Null Switch] ──→ [Further Processing]
               ↑ Main Source
[Alt 1] ───────┤ Alternative 1
               │
[Alt 2] ───────┘ Alternative 2
```

### 3. Memory Optimization Workflow

```
[Large Model Gen] → [Memory Cleanup] → [Upscale] → [Memory Cleanup] → [Save]
                    cleanup_mode: All              cleanup_mode: VRAM Only
```

### 4. Text Batch Processing

```
[Load Text] → [Text Splitter] → [Prompt Line Processor] → [Text Joiner] → [Text Saver]
             delimiter: \n      operation: Remove Empty Lines
```

### 5. Scenario Switching Workflow

```
[Advanced Group Bypasser]
json_rules: {
  "Scenario A": ["Gen Group", "Upscale Group"],
  "Scenario B": ["Gen Group", "Style Group"],
  "Scenario C": ["Gen Group", "Upscale Group", "Style Group"]
}
```

### 6. Centralized Parameter Management

```
[Parameter Distributor] ──→ [Node A]
                       ├──→ [Node B]
                       ├──→ [Node C]
                       └──→ [Node D]
```

---


## 🐛 FAQ

### Q: Nodes won't load?

A: Check if dependencies are fully installed:
```bash
pip install -r requirements.txt
```

### Q: Poor image feathering effect?

A: Install scipy for better feathering:
```bash
pip install scipy
```

### Q: Memory cleanup node errors?

A: Ensure psutil is installed:
```bash
pip install psutil
```

### Q: Node bypasser not working?

A: Ensure:
1. Nodes are correctly connected
2. Switch state is correctly set
3. If downstream nodes error, use "Non-Null Switch" to provide alternative data

### Q: Parameter distributor output is empty?

A: Ensure:
1. Parameter values are configured on the node
2. Output is connected to other nodes
3. Check if parameters are locked

---

## 🔄 Changelog

### v1.0.0 (2026-01-04)

**New Features**:
- ✨ Added 7 workflow control nodes
  - Non-Null Switch: Multi-level fallback switching
  - Node Bypasser: Control multiple nodes execution
  - Advanced Node Bypasser: JSON rule-based
  - Group Bypasser: Control group execution
  - Advanced Group Bypasser: JSON rule-based
  - Parameter Distributor: Dynamic parameter distribution
- 🎨 Image processing nodes support custom padding color
- 🚀 Image scaler supports multi-threaded batch processing
- 📝 Text processor supports multiple processing modes

**Improvements**:
- 🔧 Unified node naming convention (all nodes end with Ben)
- 📚 Improved node documentation and usage instructions
- 🎯 Optimized memory cleanup logic
- 🐛 Fixed known issues

---

## 📄 License

MIT License

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

### Contribution Guidelines

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📮 Contact

- GitHub: [jianglinbin/ComfyUI-BenNodes](https://github.com/jianglinbin/ComfyUI-BenNodes)
- Issues: [Submit Issue](https://github.com/jianglinbin/ComfyUI-BenNodes/issues)

---

## 🙏 Acknowledgments

Thanks to the ComfyUI community for their support and contributions!

---

**Last Updated**: January 4, 2026
