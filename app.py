import cv2
import gradio as gr
import numpy as np
from add_side import add_side_borders
from combine_image import composite_images_with_mask
from get_imagemetadate import get_photo_metadata
from add_bottonside import add_polaroid_border
from get_depthmap import get_photo_depth

def create_checkboxes(image_path):
    metadata = get_photo_metadata(image_path)
    metadata_list = []
    for i in metadata:
        metadata_list.append(i)
    return metadata_list

def set_metadata(image_path, metadata_list):
    metadata = get_photo_metadata(image_path)
    if "相机型号" in metadata_list:
        metadata_need = [metadata["相机型号"]]
    else:
        metadata_need = [""]

    data = []
    for metadata_name in metadata:
        if metadata_name in metadata_list:
            if metadata_name == "焦距":
                data.append(metadata[metadata_name])

            if metadata_name == "光圈":
                data.append(metadata[metadata_name])

            if metadata_name == "快门速度":
                data.append(metadata[metadata_name])

            if metadata_name == "ISO":
                data.append("ISO"+str(metadata[metadata_name]))

    data_str = ""
    for data_need in data:
        data_str += data_need + " "
    metadata_need.append(data_str)

    if "拍摄时间" in metadata_list:
        metadata_need.append(metadata["拍摄时间"])
    else:
        metadata_need.append("")

    return metadata_need

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

def clear_image():
    return None

def combine_img(image_path, depth, depth_slider, depth_angle_slider, depth_distance_slider):
    if image_path is None:
        return gr.update(choices=[], value=[]), None
    else:
        metadata_list = create_checkboxes(image_path)
        metadata_need = set_metadata(image_path, metadata_list)
        if depth is None:
            image = cv2.imread(image_path)
            depth = np.zeros_like(image)
            depth = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)
            side_output = add_side_borders(image_path, None, depth_angle_slider, depth_distance_slider)
            combine_output = composite_images_with_mask(image_path, side_output, depth)
            bottom_output = add_polaroid_border(combine_output, metadata_need, None, depth_angle_slider, depth_distance_slider)
        else:
            depth = rebuild_depth(depth, depth_slider)
            side_output = add_side_borders(image_path, depth, depth_angle_slider, depth_distance_slider)
            combine_output = composite_images_with_mask(image_path, side_output, depth)
            bottom_output = add_polaroid_border(combine_output, metadata_need, depth, depth_angle_slider, depth_distance_slider)

        return gr.update(choices=metadata_list, value=metadata_list), bottom_output

def change_info_select(image_path, depth, depth_slider, metadata_list, depth_angle_slider, depth_distance_slider):
    if image_path is None:
        return None
    else:
        metadata_need = set_metadata(image_path, metadata_list)

        if depth is None:
            image = cv2.imread(image_path)
            depth = np.zeros_like(image)
            depth = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)
            side_output = add_side_borders(image_path, None,depth_angle_slider, depth_distance_slider)
            combine_output = composite_images_with_mask(image_path, side_output, depth)
            bottom_output = add_polaroid_border(combine_output, metadata_need, None, depth_angle_slider, depth_distance_slider)
        else:
            depth = rebuild_depth(depth, depth_slider)
            side_output = add_side_borders(image_path, depth, depth_angle_slider, depth_distance_slider)
            combine_output = composite_images_with_mask(image_path, side_output, depth)
            bottom_output = add_polaroid_border(combine_output, metadata_need, depth, depth_angle_slider, depth_distance_slider)

        return bottom_output

def change_depth_slider(image_path, depth, depth_slider, metadata_list, depth_angle_slider, depth_distance_slider):
    if image_path is None:
        return None
    else:
        metadata_need = set_metadata(image_path, metadata_list)

        if depth is None:
            image = cv2.imread(image_path)
            depth = np.zeros_like(image)
            depth = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)
            side_output = add_side_borders(image_path, None, depth_angle_slider, depth_distance_slider)
            combine_output = composite_images_with_mask(image_path, side_output, depth)
            bottom_output = add_polaroid_border(combine_output, metadata_need, None, depth_angle_slider, depth_distance_slider)
        else:
            depth = rebuild_depth(depth, depth_slider)
            side_output = add_side_borders(image_path, depth, depth_angle_slider, depth_distance_slider)
            combine_output = composite_images_with_mask(image_path, side_output, depth)
            bottom_output = add_polaroid_border(combine_output, metadata_need, depth, depth_angle_slider, depth_distance_slider)

        return bottom_output

if __name__ == '__main__':
    with gr.Blocks(title="空间感图片边框生成器") as demo:
        gr.Markdown("# 📷 空间感图片边框生成器")
        gr.Markdown("上传图片以生成空间感图片边框")

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

            with gr.Column(scale=1):
                depth_image = gr.Image(
                    type="numpy",
                    label="预览图片",
                    interactive=False
                )

                depth_btn = gr.Button("生成深度", variant="primary")

                depth_slider = gr.Slider(label='深度距离', minimum=1, maximum=20, step=1)

                depth_angel_slider = gr.Slider(label='阴影角度', minimum=0, maximum=360, step=15, value=45)

                depth_distance_slider = gr.Slider(label='阴影距离', minimum=0, maximum=100, step=10, value=30)

            with gr.Column(scale=1):
                output_image = gr.Image(
                    type="numpy",
                    format='png',
                    label="预览图片",
                    interactive = False
                )

        input_image.change(
            fn=combine_img,
            inputs=[input_image, depth_image, depth_slider],
            outputs=[info_select, output_image],
        )

        input_image.clear(
            fn=clear_image,
            outputs=[depth_image]
        )

        info_select.change(
            fn=change_info_select,
            inputs=[input_image, depth_image, depth_slider, info_select, depth_angel_slider, depth_distance_slider],
            outputs=[output_image]
        )

        depth_slider.change(
            fn=change_depth_slider,
            inputs=[input_image, depth_image, depth_slider, info_select, depth_angel_slider, depth_distance_slider],
            outputs=[output_image]
        )

        depth_angel_slider.change(
            fn=change_depth_slider,
            inputs=[input_image, depth_image, depth_slider, info_select, depth_angel_slider, depth_distance_slider],
            outputs=[output_image]
        )

        depth_distance_slider.change(
            fn=change_depth_slider,
            inputs=[input_image, depth_image, depth_slider, info_select, depth_angel_slider, depth_distance_slider],
            outputs=[output_image]
        )

        depth_image.change(
            fn=combine_img,
            inputs=[input_image, depth_image, depth_slider, depth_angel_slider, depth_distance_slider],
            outputs=[info_select, output_image]
        )

        depth_btn.click(
            fn=get_photo_depth,
            inputs=[input_image],
            outputs=[depth_image]
        )

    demo.launch()