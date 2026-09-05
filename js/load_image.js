import { app } from "../../scripts/app.js";
import { getWidget, updateScalerWidgets, wrapWidgetCallbacks, applyFixedComputeSize } from "./shared.js";

import { t } from "./i18n.js";
app.registerExtension({
    name: "ben.ImageBatchLoader",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "ImageBatchLoaderBen") return;

        const origCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (origCreated) origCreated.apply(this, arguments);

            const node = this;

            // 添加上传文件夹按钮
            const uploadButton = node.addWidget("button", t("upload_folder"), "upload_folder", () => {
                const input = document.createElement("input");
                input.type = "file";
                input.webkitdirectory = true;
                input.multiple = true;
                input.style.display = "none";

                input.onchange = async (e) => {
                    const files = Array.from(e.target.files);
                    if (!files.length) return;

                    let folderName = "uploaded_folder";
                    if (files[0].webkitRelativePath) {
                        folderName = files[0].webkitRelativePath.split("/")[0];
                    }

                    const originalLabel = uploadButton.label;
                    uploadButton.label = t("uploading_progress", 0, files.length);
                    node.setDirtyCanvas(true);

                    try {
                        let uploadedCount = 0;
                        for (const file of files) {
                            if (!file.type.startsWith("image/")) continue;

                            const formData = new FormData();
                            formData.append("image", file, file.name || "image.png");
                            formData.append("subfolder", folderName);
                            formData.append("overwrite", "true");

                            await fetch("/upload/image", {
                                method: "POST",
                                body: formData
                            });

                            uploadedCount++;
                            uploadButton.label = t("uploading_progress", uploadedCount, files.length);
                            node.setDirtyCanvas(true);

                            await new Promise(r => setTimeout(r, 50));
                        }

                        const folderW = getWidget(node, "folder_path");
                        if (folderW) {
                            folderW.value = folderName;
                            folderW.options.values = [folderName, ...folderW.options.values.filter(v => v !== folderName)];
                            if (folderW.callback) {
                                folderW.callback(folderName);
                            }
                        }

                        update();
                        node.setDirtyCanvas(true);

                    } catch (error) {
                        alert(t("upload_failed_with_error", error));
                    } finally {
                        uploadButton.label = originalLabel;
                        node.setDirtyCanvas(true);
                    }
                };

                document.body.appendChild(input);
                input.click();
                document.body.removeChild(input);
            });

            const update = () => updateScalerWidgets(node);

            // 批量绑定回调
            wrapWidgetCallbacks(node, ["folder_path", "resize_mode", "resolution", "aspect_ratio"], update);

            // 初始化
            setTimeout(update, 100);
        };

        applyFixedComputeSize(nodeType);
    }
});
