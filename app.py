import cv2
import os
import gradio as gr
import numpy as np
import pandas as pd
from add_sideborder import add_side_borders
from combine_image import composite_images_with_mask
from get_imagemetadate import get_photo_metadata
from add_bottomborder import add_bottom_border
from get_depthmap import get_photo_depth

def check_file_type(image_path):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.raw', '.DNG']
    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext not in valid_extensions:
        return False
    else:
        return True

def create_checkboxes(image_path):
    metadata = get_photo_metadata(image_path)
    metadata_list = []
    for i in metadata:
        metadata_list.append(i)
    return metadata_list

def set_metadata(image_path, metadata_list):
    metadata = get_photo_metadata(image_path)
    # 相机型号
    camera_model = metadata["相机型号"] if "相机型号" in metadata_list else ""
    # 镜头参数
    lens_params = []
    for key in ["焦距", "光圈", "快门速度", "ISO"]:
        if key in metadata_list and key in metadata:
            if key == "ISO":
                lens_params.append("ISO" + str(metadata[key]))
            else:
                lens_params.append(metadata[key])
    lens_params_str = "  ".join(lens_params)
    # 拍摄时间
    shoot_time = metadata["拍摄时间"] if "拍摄时间" in metadata_list else ""
    # 构造DataFrame
    df = pd.DataFrame([[camera_model, lens_params_str, shoot_time]], columns=["相机型号", "镜头参数", "拍摄时间"])
    return df

def rebuild_depth(depth, slider_num):
    # 转为灰度
    depth_gray = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY) if len(depth.shape) == 3 else depth
    # 归一化到0~255
    norm_depth = cv2.normalize(depth_gray, None, 0, 255, cv2.NORM_MINMAX)
    norm_depth = norm_depth.astype(np.uint8)
    # 动态分成20个分位区块
    percentiles = np.percentile(norm_depth, np.linspace(0, 100, 21))
    lower = percentiles[20-slider_num]
    upper = percentiles[20]
    mask = cv2.inRange(norm_depth, lower, upper)
    # 高斯模糊，边缘有渐变过渡
    mask_blur = cv2.GaussianBlur(mask, (21, 21), 0)
    # 归一化到0~255，形成渐变遮罩
    result = (mask_blur / mask_blur.max() * 255).astype(np.uint8) if mask_blur.max() > 0 else mask_blur
    return result

def crop_image(image_path, depth_image, up_crop, down_crop, left_crop, right_crop):
    if image_path is None:
        return None, None
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]
    cropped_image = image[up_crop:height - down_crop, left_crop:width - right_crop]
    if depth_image is not None:
        depth_image = get_photo_depth(cropped_image)
    return cropped_image, depth_image

def clear_image():
    return None, "等待上传图片..."

def combine_image(image, metadata_need, depth, depth_slider, depth_angle_slider, depth_distance_slider):
    if image is not None:
        if depth is None:
            depth = np.zeros_like(image)
            depth = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)
            side_output = add_side_borders(image, None, depth_angle_slider, depth_distance_slider)
            combine_output = composite_images_with_mask(image, side_output, depth)
            bottom_output = add_bottom_border(combine_output, metadata_need, None, depth_angle_slider, depth_distance_slider)
        else:
            depth = rebuild_depth(depth, depth_slider)
            side_output = add_side_borders(image, depth, depth_angle_slider, depth_distance_slider)
            combine_output = composite_images_with_mask(image, side_output, depth)
            bottom_output = add_bottom_border(combine_output, metadata_need, depth, depth_angle_slider, depth_distance_slider)

        return bottom_output
    else:
        return None

def upload_image(image_path, depth, depth_slider, depth_angle_slider, depth_distance_slider):
    if image_path is None:
        return (
            gr.update(choices=[], value=[]),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "等待上传图片..."
        )
    else:
        if check_file_type(image_path) is False:
            return (
                gr.update(choices=[], value=[]),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                "错误: 不支持的文件类型，请上传常见图片格式（jpg, png, gif, tiff, raw, DNG等）"
            )
        else:
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            up_crop_max = down_crop_max = image.shape[0]/2
            left_crop_max = right_crop_max = image.shape[1]/2
            metadata_list= create_checkboxes(image_path)
            metadata_need = set_metadata(image_path, metadata_list)
            bottom_output = combine_image(image, metadata_need, depth, depth_slider, depth_angle_slider, depth_distance_slider)
            return (
                gr.update(choices=metadata_list, value=metadata_list),
                bottom_output,
                image,
                gr.update(minimum=0, maximum=up_crop_max, step=10, value=0),
                gr.update(minimum=0, maximum=down_crop_max, step=10, value=0),
                gr.update(minimum=0, maximum=left_crop_max, step=10, value=0),
                gr.update(minimum=0, maximum=right_crop_max, step=10, value=0),
                metadata_need,
                "完成图片上传"
                )

def change_metadata(image_path, metadata_list):
    if image_path is None:
        return []
    else:
        metadata_need = set_metadata(image_path, metadata_list)
        return metadata_need

if __name__ == '__main__':
    with gr.Blocks(title="空间感图片边框生成器") as demo:
        gr.Markdown("# 📷 空间感图片边框生成器")
        gr.Markdown("上传图片以生成空间感图片边框\n\n"
                    "点击[生成深度]按钮以生成深度图，调整深度距离、阴影角度和阴影距离滑块以获得最佳效果。\n\n"
                    "可选：选择显示图片参数信息并调整裁剪边距。\n\n"
                    )

        with gr.Column():
            status_bar = gr.Textbox(
                label="状态栏",
                value="等待上传图片...",
                interactive=False
            )

            with gr.Row():
                # 左侧：放置图片栏
                with gr.Column(scale=1):
                    input_image = gr.File(
                        type="filepath",
                        label="上传图片",
                        height=300
                    )

                with gr.Column(scale=1):
                    info_select = gr.CheckboxGroup(
                        label="图片参数信息",
                        interactive = True
                    )

                    metadata_need = gr.Dataframe(
                        label="图片参数",
                        headers=["相机型号", "镜头参数", "拍摄时间"],
                        interactive=False,
                    )
            with gr.Row():
                with gr.Column(scale=1):
                    depth_image = gr.Image(
                        type="numpy",
                        label="深度图预览",
                        interactive=False,
                    )

                    depth_btn = gr.Button("生成深度", variant="primary")

                    depth_slider = gr.Slider(label='深度距离', minimum=1, maximum=20, step=1)

                    depth_angle_slider = gr.Slider(label='阴影角度', minimum=0, maximum=360, step=15, value=45)

                    depth_distance_slider = gr.Slider(label='阴影距离', minimum=0, maximum=100, step=10, value=30)

                with gr.Column(scale=1):
                    show_image = gr.Image(
                        type="numpy",
                        label="上传图片预览",
                        interactive=False,
                        show_download_button=False
                    )

                    up_crop = gr.Slider(label='裁剪上边距', minimum=0, maximum=200, step=10)
                    down_crop = gr.Slider(label='裁剪下边距', minimum=0, maximum=200, step=10)
                    left_crop = gr.Slider(label='裁剪左边距', minimum=0, maximum=200, step=10)
                    right_crop = gr.Slider(label='裁剪右边距', minimum=0, maximum=200, step=10)

                with gr.Column(scale=1):
                    output_image = gr.Image(
                        type="numpy",
                        format='png',
                        label="最终结果",
                        interactive = False
                    )

        input_image.change(
            fn=upload_image,
            inputs=[input_image, depth_image, depth_slider, depth_angle_slider, depth_distance_slider],
            outputs=[info_select, output_image, show_image, up_crop, down_crop, left_crop, right_crop, metadata_need, status_bar]
        )

        up_crop.change(
            fn=crop_image,
            inputs=[input_image, depth_image, up_crop, down_crop, left_crop, right_crop],
            outputs=[show_image, depth_image]
        )

        down_crop.change(
            fn=crop_image,
            inputs=[input_image, depth_image, up_crop, down_crop, left_crop, right_crop],
            outputs=[show_image, depth_image]
        )

        left_crop.change(
            fn=crop_image,
            inputs=[input_image, depth_image, up_crop, down_crop, left_crop, right_crop],
            outputs=[show_image, depth_image]
        )

        right_crop.change(
            fn=crop_image,
            inputs=[input_image, depth_image, up_crop, down_crop, left_crop, right_crop],
            outputs=[show_image, depth_image]
        )

        input_image.clear(
            fn=clear_image,
            outputs=[depth_image, status_bar]
        )

        info_select.change(
            fn=change_metadata,
            inputs=[input_image, info_select],
            outputs=[metadata_need]
        )

        show_image.change(
            fn=combine_image,
            inputs=[show_image, metadata_need, depth_image, depth_slider, depth_angle_slider, depth_distance_slider],
            outputs=[output_image]
        )

        depth_slider.change(
            fn=combine_image,
            inputs=[show_image, metadata_need, depth_image, depth_slider, depth_angle_slider, depth_distance_slider],
            outputs=[output_image]
        )

        depth_angle_slider.change(
            fn=combine_image,
            inputs=[show_image, metadata_need, depth_image, depth_slider, depth_angle_slider, depth_distance_slider],
            outputs=[output_image]
        )

        depth_distance_slider.change(
            fn=combine_image,
            inputs=[show_image, metadata_need, depth_image, depth_slider, depth_angle_slider, depth_distance_slider],
            outputs=[output_image]
        )

        depth_image.change(
            fn=combine_image,
            inputs=[show_image, metadata_need, depth_image, depth_slider, depth_angle_slider, depth_distance_slider],
            outputs=[output_image]
        )

        depth_btn.click(
            fn=get_photo_depth,
            inputs=[show_image],
            outputs=[depth_image]
        )

    demo.launch()