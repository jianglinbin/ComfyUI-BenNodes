import { app } from "../../scripts/app.js";
import { t } from "./i18n.js";

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
            const uploadButton = node.addWidget("button", t("select_file"), "select_file", () => {
                const input = document.createElement("input");
                input.type = "file";
                input.multiple = false;
                input.style.display = "none";

                input.onchange = async (e) => {
                    const file = e.target.files[0];
                    if (!file) return;

                    const originalLabel = uploadButton.label;
                    uploadButton.label = t("uploading");
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
                            uploadButton.label = t("selected", file.name);
                            node.setDirtyCanvas(true);
                        } else {
                            throw new Error(t("upload_failed"));
                        }

                    } catch (error) {
                        alert(t("upload_failed_with_error", error));
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

