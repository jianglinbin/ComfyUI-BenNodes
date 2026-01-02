import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ben.FileUploaderBen",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "FileUploaderBen") return;

        const origCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (origCreated) origCreated.apply(this, arguments);

            const node = this;
            
            // 隐藏原始的文件路径输入框
            const fileWidget = node.widgets.find(w => w.name === "file");
            if (fileWidget) {
                fileWidget.type = "hidden";
            }

            // 添加文件选择按钮
            const uploadButton = node.addWidget("button", "选择文件", "select_file", () => {
                const input = document.createElement("input");
                input.type = "file";
                input.multiple = false;
                input.style.display = "none";

                input.onchange = async (e) => {
                    const file = e.target.files[0];
                    if (!file) return;

                    const originalLabel = uploadButton.label;
                    uploadButton.label = "上传中...";
                    node.setDirtyCanvas(true);

                    try {
                        // 上传文件到 ComfyUI 的 input 目录
                        const formData = new FormData();
                        formData.append("image", file, file.name);
                        formData.append("overwrite", "true");

                        const response = await fetch("/upload/image", {
                            method: "POST",
                            body: formData
                        });

                        if (response.ok) {
                            const result = await response.json();
                            // 获取上传后的文件路径
                            const uploadedPath = result.name || file.name;
                            
                            // 更新文件路径 widget
                            if (fileWidget) {
                                fileWidget.value = uploadedPath;
                            }

                            // 更新按钮显示文件名
                            uploadButton.label = `已选择: ${file.name}`;
                            node.setDirtyCanvas(true);
                        } else {
                            throw new Error("上传失败");
                        }

                    } catch (error) {
                        alert("上传失败: " + error);
                        uploadButton.label = originalLabel;
                    }
                };

                document.body.appendChild(input);
                input.click();
                document.body.removeChild(input);
            });

            node.setSize([300, 100]);
        };
    }
});

app.registerExtension({
    name: "ben.FileUploaderMultiBen",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "FileUploaderMultiBen") return;

        const origCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (origCreated) origCreated.apply(this, arguments);

            const node = this;
            
            // 隐藏原始的文件夹路径输入框
            const folderWidget = node.widgets.find(w => w.name === "folder_path");
            if (folderWidget) {
                folderWidget.type = "hidden";
            }

            // 添加文件夹选择按钮
            const uploadButton = node.addWidget("button", "选择文件夹", "select_folder", () => {
                const input = document.createElement("input");
                input.type = "file";
                input.webkitdirectory = true;
                input.multiple = true;
                input.style.display = "none";

                input.onchange = async (e) => {
                    const files = Array.from(e.target.files);
                    if (!files.length) return;

                    // 获取文件夹名称
                    let folderName = "uploaded_folder";
                    if (files[0].webkitRelativePath) {
                        folderName = files[0].webkitRelativePath.split("/")[0];
                    }

                    const originalLabel = uploadButton.label;
                    uploadButton.label = `上传中 0/${files.length}...`;
                    node.setDirtyCanvas(true);

                    try {
                        let uploadedCount = 0;
                        for (const file of files) {
                            const formData = new FormData();
                            formData.append("image", file, file.name);
                            formData.append("subfolder", folderName);
                            formData.append("overwrite", "true");

                            await fetch("/upload/image", {
                                method: "POST",
                                body: formData
                            });

                            uploadedCount++;
                            uploadButton.label = `上传中 ${uploadedCount}/${files.length}...`;
                            node.setDirtyCanvas(true);

                            // 小延迟避免请求过快
                            await new Promise(r => setTimeout(r, 50));
                        }

                        // 更新文件夹路径 widget
                        if (folderWidget) {
                            folderWidget.value = folderName;
                        }

                        uploadButton.label = `已选择: ${folderName} (${files.length}个文件)`;
                        node.setDirtyCanvas(true);

                    } catch (error) {
                        alert("上传失败: " + error);
                        uploadButton.label = originalLabel;
                    }
                };

                document.body.appendChild(input);
                input.click();
                document.body.removeChild(input);
            });

            node.setSize([300, 120]);
        };
    }
});
