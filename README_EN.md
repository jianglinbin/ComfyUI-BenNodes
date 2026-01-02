# ComfyUI-BenNodes

A collection of custom nodes for ComfyUI, providing image processing, text processing, data conversion, AI analysis, and more.

[中文文档](README.md) | English

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

### Dependencies

#### Core Dependencies (Required)
```bash
pip install zhipuai Pillow psutil
```

#### Enhanced Features (Recommended)
```bash
pip install scipy
```

#### Office Document Processing (Optional)
```bash
pip install python-docx openpyxl python-pptx xlrd
```

#### Windows Specific (Optional, Windows only)
```bash
pip install pywin32
```

#### PDF and Video Processing (Optional)
```bash
pip install PyMuPDF opencv-python
```

## 📚 Node Categories

- [AI](#ai) (2 nodes)
- [Data Processing](#data-processing) (5 nodes)
- [File Operations](#file-operations) (1 node)
- [Image Processing](#image-processing) (4 nodes)
- [System Utilities](#system-utilities) (3 nodes)
- [Text Processing](#text-processing) (5 nodes)
- [Control Flow](#control-flow) (1 node)

---

## 🤖 AI

### GLM Config Node 🧠-Ben

**Category**: `BenNodes/AI`

Configure GLM model parameters including model selection, temperature, token limits, etc.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| vision_model | STRING | glm-4.6v-flash | Vision model name |
| text_model | STRING | glm-4.5-flash | Text model name |
| max_pages | INT | 0 | Max PDF pages, 0 = unlimited |
| max_tokens | INT | 8192 | Max tokens for generation |
| temperature | FLOAT | 0.3 | Output randomness, 0.1-0.3 recommended |
| top_p | FLOAT | 0.7 | Candidate word range, 0.5-0.7 recommended |
| chunk_mode | COMBO | auto | Large file processing mode |
| thinking_enabled | BOOLEAN | True | Enable thinking feature |

#### Output

- **glm_config**: GLM configuration object

#### Usage Example

```
[GLM Config Node] → [GLM Multimodal Analysis]
```

---

### GLM Multimodal Analysis 🧠-Ben

**Category**: `BenNodes/AI`

Analyze images, videos, PDFs, Office documents, or text files using GLM models.

#### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| prompt | STRING | Analysis prompt |
| system_prompt | STRING | System prompt defining model role |
| input | ANY | Supports images, videos, file paths |
| glm_config | GLM_CONFIG | GLM configuration (optional) |
| api_key | STRING | GLM API key |

#### Output

- **Analysis Result**: STRING (list)

#### Supported File Types

- **Images**: .jpg, .jpeg, .png, .bmp, .gif, .webp
- **Videos**: .mp4, .avi, .mov, .webm, .mkv
- **PDF**: .pdf
- **Word**: .docx, .doc
- **Excel**: .xlsx, .xls
- **PowerPoint**: .pptx, .ppt
- **Text**: .txt, .md, .json, .xml, .csv, .log, .py, .js, .html, .css

#### Usage Example

```
[Load Image] → [GLM Multimodal Analysis] → [Save Text]
                ↑
         [GLM Config Node]
```

---

## 📊 Data Processing

### Resolution Selector 📐-Ben

**Category**: `BenNodes/Data`

Provides preset resolutions and aspect ratios, automatically calculates output width and height.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| resolution | COMBO | 720p | Preset resolution |
| aspect_ratio | COMBO | 16:9 | Aspect ratio |
| width | INT | 1280 | Custom width |
| height | INT | 720 | Custom height |

#### Output

- **width**: INT - Calculated width
- **height**: INT - Calculated height
- **resolution_text**: STRING - Resolution description

#### Preset Resolutions

- 480p, 720p, 1080p, 2K, 4K, 8K, Custom

#### Preset Ratios

- 16:9, 4:3, 1:1, 21:9, 9:16, 3:4, Custom

---

### List Index Selector 📌-Ben

**Category**: `BenNodes/Data`

Select elements from a list by index, supports batch image processing.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| * | ANY | - | Input list |
| index | STRING | 0 | Index, supports comma-separated values |

#### Output

- **ITEM_0 ~ ITEM_19**: Up to 20 outputs

#### Usage Example

```
[Load Image Batch] → [List Index Selector] → [Save Image]
                      index: "0,2,4"
```

---

### Advanced List Index Selector 🎯-Ben

**Category**: `BenNodes/Data`

Advanced list index selection with start position, step, and length control.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| list | ANY | - | Input list |
| start_index | INT | 0 | Starting index |
| step | INT | 0 | Step value, 0 = no step |
| length | INT | 1 | Number of elements to select |

#### Output

- **SELECTED_LIST**: Selected element list

#### Usage Example

```
# Start from 5th, take every 2nd, get 3 elements
start_index: 5
step: 2
length: 3
Result: [5, 7, 9]
```

---

### JSON Parser 📋-Ben

**Category**: `BenNodes/Data`

Parse JSON strings with path extraction support.

#### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| json_string | STRING | JSON string |
| json_path | STRING | Path expression, supports multiple paths (semicolon-separated) |
| output_type | COMBO | Output data type |

#### Output

- **JSON_TEXT**: STRING - Formatted JSON text
- **PARSED_RESULT**: ANY - Parsed result

#### Path Syntax

- Simple property: `name`
- Nested property: `user.name`
- Array index: `items[0].name`
- Combined path: `data.users[1].address.city`
- Multiple paths: `name;age;address.city`

#### Usage Example

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

### Type Converter 🔄-Ben

**Category**: `BenNodes/Data`

Convert any type of input to specified data type.

#### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| * | ANY | Input data |
| target_type | COMBO | Target type |

#### Supported Types

- STRING, LIST<STRING>
- INT, LIST<INT>
- FLOAT, LIST<FLOAT>
- BOOLEAN, LIST<BOOLEAN>

#### Conversion Rules

- Single → Single: Direct conversion
- Single → List: Convert and wrap in list
- List → Single: Convert first element
- List → List: Convert each element

---

## 📁 File Operations

### File Uploader 📂-Ben

**Category**: `BenNodes/File`

Select files from filesystem, supports images, videos, documents, and more.

#### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| file_path | STRING | File path selector |

#### Output

- **file_path**: STRING - Full file path
- **file_name**: STRING - File name
- **file_extension**: STRING - File extension

---

## 🖼️ Image Processing

### Load Image 🖼️-Ben

**Category**: `BenNodes/Image`

Load a single image with support for various formats and resize modes.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | COMBO | - | Image file selection |
| resize_mode | COMBO | none | Resize mode |
| position | COMBO | center | Alignment position |
| resolution | COMBO | 720p | Target resolution |
| aspect_ratio | COMBO | 16:9 | Target ratio |
| width | INT | 1080 | Target width |
| height | INT | 720 | Target height |
| feathering | INT | 0 | Feathering amount |
| upscale_method | COMBO | bicubic | Scaling algorithm |

#### Output

- **Image**: IMAGE
- **Mask**: MASK
- **Width**: INT
- **Height**: INT
- **Filename**: STRING

#### Resize Modes

- **none**: No resize
- **fit**: Fit (maintain aspect ratio)
- **fill**: Fill (crop)
- **stretch**: Stretch (ignore aspect ratio)
- **pad**: Pad with black

---

### Load Image Batch 🗂️-Ben

**Category**: `BenNodes/Image`

Batch load all images from a folder.

#### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| folder_path | COMBO | Folder selection |
| resize_mode | COMBO | Resize mode |
| ... | ... | Other parameters same as "Load Image" |

#### Output

- **Image**: IMAGE (batch)
- **Mask**: MASK (batch)
- **Width**: INT
- **Height**: INT
- **Filename**: STRING (list)

---

### Image Scaler 🎨-Ben

**Category**: `BenNodes/Image`

Scale, crop, pad images with batch processing support.

#### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| image | IMAGE | Input image |
| resize_mode | COMBO | Resize mode |
| position | COMBO | Alignment position |
| resolution | COMBO | Target resolution |
| aspect_ratio | COMBO | Target ratio |
| width | INT | Target width |
| height | INT | Target height |
| feathering | INT | Feathering amount |
| upscale_method | COMBO | Scaling algorithm |
| pad_color | STRING | Padding color (RGB) |

#### Output

- **IMAGE**: Processed image
- **MASK**: Mask
- **width**: INT
- **height**: INT

#### Scaling Algorithms

- nearest, bilinear, bicubic, lanczos

---

### Empty Latent 🎯-Ben

**Category**: `BenNodes/Image`

Create empty latent images for image generation.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| resolution | COMBO | 1080p | Resolution |
| aspect_ratio | COMBO | 16:9 | Aspect ratio |
| width | INT | 1920 | Width |
| height | INT | 1080 | Height |
| batch_size | INT | 1 | Batch size |

#### Output

- **LATENT**: Empty latent image

---

## 🔧 System Utilities

### Memory Cleanup Dynamic 🧹-Ben

**Category**: `BenNodes/System`

Clean VRAM and RAM to optimize system resource usage.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| cleanup_mode | COMBO | All | Cleanup mode |
| input | ANY | - | Input data (passthrough) |

#### Cleanup Modes

- **None**: No cleanup
- **VRAM Only**: Clean VRAM only
- **RAM Only**: Clean RAM only
- **All**: Clean both VRAM and RAM

#### Output

- **output**: ANY - Passthrough input data

#### Use Case

Insert in workflow to clean unused models and cache:

```
[Generate Image] → [Memory Cleanup] → [Upscale Image]
```

---

### Switch NOT NULL 🔄-Ben

**Category**: `BenNodes/System`

Output default parameter if not null, otherwise output alternative.

#### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| default | ANY | Default input (optional) |
| alternative | ANY | Alternative input (optional) |

#### Output

- **output**: ANY

#### Logic

1. If default is not null, return default
2. Otherwise, if alternative is not null, return alternative
3. Otherwise, throw error

#### Use Case

Use with "Dynamic Input Bypasser" to handle missing data when nodes are bypassed:

```
[Node A] ──→ [Switch NOT NULL] ──→ [Node C]
            ↑ default
[Node B] ────┘ alternative
```

---

### Dynamic Input Bypasser 🔀-Ben

**Category**: `BenNodes/Control`

Control multiple connected nodes' execution state with a single master switch.

#### Features

- Dynamic input slot auto-management
- Single master switch controls all connected nodes
- Passthrough nodes auto-follow
- Fully independent implementation

#### Usage

1. Add "Dynamic Input Bypasser" to workflow
2. Connect nodes you want to control to the bypasser's inputs
3. Use the switch to enable/bypass all connected nodes

#### Switch States

- **yes**: Enable all connected nodes
- **no**: Bypass all connected nodes

#### Note

⚠️ When nodes are bypassed, they won't execute or produce output. If downstream nodes depend on this output, errors will occur. Recommended to use with "Switch NOT NULL" node.

---

## 📝 Text Processing

### Prompt Line Processor 📝-Ben

**Category**: `BenNodes/Text`

Process multi-line prompts, extract specified range of lines and apply operations.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| prompt | STRING | - | Multi-line text |
| start_index | INT | 0 | Starting line number |
| max_rows | INT | 1000 | Max lines to return |
| operation | COMBO | Original | Text operation |

#### Supported Operations

- Original, Uppercase, Lowercase, Capitalize, Title Case
- Strip Whitespace, Reverse, Length, Remove Empty Lines

#### Output

- **STRING**: Processed text (list)

---

### Save Text 📄-Ben

**Category**: `BenNodes/Text`

Save text or text batch to file.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| texts | STRING | - | Text to save |
| filename_prefix | STRING | ComfyUI | Filename prefix |
| file_extension | STRING | .txt | File extension |
| filename | STRING | - | Optional filename |

#### Output

- UI displays saved file list

#### Usage Example

```
[GLM Analysis] → [Save Text]
                 filename_prefix: "analysis"
                 file_extension: ".md"
```

---

### Text Split 📝-Ben

**Category**: `BenNodes/Text`

Split text by specified delimiter.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| text | STRING | - | Input text |
| delimiter | STRING | \n | Delimiter |
| start_index | INT | 0 | Starting index |
| max_rows | INT | 1000 | Max items to return |

#### Output

- **STRING**: Split text list

---

### Text Join (List Support) 📝-Ben

**Category**: `BenNodes/Text`

Join two texts or text lists.

#### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| text1 | STRING | First text |
| text2 | STRING | Second text |
| delimiter | STRING | Delimiter |

#### Join Rules

- Two strings → Direct join
- String + List → String joins with each list element
- List + String → Each list element joins with string

#### Output

- **Join Result**: STRING or STRING list

---

### Text Processor ✏️-Ben

**Category**: `BenNodes/Text`

Process multi-line text, remove empty lines, whitespace, etc.

#### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| text | STRING | - | Multi-line text |
| process_type | COMBO | none | Processing type |

#### Processing Types

- **none**: No processing
- **Remove Empty Lines**: Delete empty lines
- **Strip Whitespace**: Remove leading/trailing whitespace
- **Strip + Remove Empty**: Both operations

#### Output

- **Text**: STRING - Full text
- **Text List**: STRING - Line-split list

---

## 🔄 Control Flow

### Dynamic Input Bypasser 🔀-Ben

See [System Utilities - Dynamic Input Bypasser](#dynamic-input-bypasser--ben)

---

## 💡 Usage Tips

### 1. Batch Image Processing

```
[Load Image Batch] → [List Index Selector] → [Image Scaler] → [Save Image]
                      index: "0,2,4,6"
```

### 2. Conditional Data Flow

```
[Node A] ──→ [Switch NOT NULL] ──→ [Save]
            ↑ default
[Node B] ────┘ alternative
```

### 3. Memory Optimization

```
[Large Model Gen] → [Memory Cleanup] → [Upscale] → [Memory Cleanup] → [Save]
```

### 4. Batch Text Processing

```
[Load Text] → [Text Split] → [Prompt Processor] → [Text Join] → [Save Text]
```

### 5. AI Analysis Workflow

```
[Load Image] → [GLM Multimodal] → [JSON Parser] → [Save Text]
                ↑
         [GLM Config Node]
```

---

## 🐛 FAQ

### Q: Nodes won't load?

A: Check if dependencies are fully installed:
```bash
pip install -r requirements.txt
```

### Q: GLM node errors?

A: Ensure `zhipuai` is installed and provide a valid API key.

### Q: Can't process Office documents?

A: Install Office document processing dependencies:
```bash
pip install python-docx openpyxl python-pptx
```

Windows systems also need:
```bash
pip install pywin32
```

### Q: Poor feathering effect?

A: Install scipy for better feathering:
```bash
pip install scipy
```

### Q: Memory cleanup node errors?

A: Ensure psutil is installed:
```bash
pip install psutil
```

---

## 📄 License

MIT License

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

## 📮 Contact

- GitHub: [jianglinbin/ComfyUI-BenNodes](https://github.com/jianglinbin/ComfyUI-BenNodes)
- Issues: [Submit Issue](https://github.com/jianglinbin/ComfyUI-BenNodes/issues)

---

## 🙏 Acknowledgments

Thanks to the ComfyUI community for their support and contributions!

---

**Last Updated**: 2026
