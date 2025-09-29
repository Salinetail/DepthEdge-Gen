import cv2
import numpy as np
from get_color import get_dominant_colors
from add_font import add_font_to_image, get_word_length
import math
import datetime

def add_bottom_border(img, camera_params, depth, angle, distance, text_color=(30, 30, 30)):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] add_bottomborder processing...")
    """
    使用OpenCV为图片添加符合黄金比例的底部白边，并在白边左侧添加色彩样本图
    参数:
        img: 输入图片的numpy数组
        camera_params: 拍摄参数列表
        text_color: 文字颜色
        color_sample_path: 色彩样本图路径（PNG，透明背景）
    """

    # 获取原图尺寸 (高度, 宽度, 通道数)
    height, width = img.shape[:2]

    # 黄金比例约为1:1.618，计算需要添加的底部边框高度
    # 黄金比例 = (原图高度 + 边框高度) / 原图高度 = 1.618
    current_height = height
    for i in range(1, 5):
        current_height = math.ceil(current_height * 0.618)
    border_height = current_height

    block_width = width // 5

    # 创建白色边框 (BGR格式，白色为(255,255,255))
    border = np.ones((border_height, width, 3), dtype=np.uint8) * 255
    num_circles = 3

    color_list = get_dominant_colors(img, num_circles, resize=True)

    circle_radius = border_height
    for i in range(1, 6):
        circle_radius = math.ceil(circle_radius * 0.618)
    circle_diameter = circle_radius * 2
    margin = (border_height - num_circles * circle_diameter) // (num_circles + 1)

    center_x = block_width
    for i in range(1, 3):
        center_x = math.ceil(center_x * 0.618)

    if depth is not None:
        shadow_offset = int(distance)
        shadow_color = np.full_like(border, 100)
        shadow_mask = np.zeros_like(border)
        shadow_blur = 101 | 1  # 阴影高斯模糊核=圆直径，保证为奇数

        rad = math.radians(angle)
        shadow_offset_x = int(np.cos(rad) * shadow_offset)
        shadow_offset_y = int(np.sin(rad) * shadow_offset)

        shadow_border = np.zeros((border_height, width), dtype=np.uint8)
        shadow_border = np.vstack((depth, shadow_border))
        M = np.float32([[1, 0, shadow_offset_x], [0, 1, shadow_offset_y]])
        shadow_border = cv2.warpAffine(shadow_border, M, (shadow_border.shape[1], shadow_border.shape[0]), borderValue=0)
        shadow_border = cv2.GaussianBlur(shadow_border, (shadow_blur, shadow_blur), 0)

        shadow_border = shadow_border[height:border_height + height, :]
        shadow_border = shadow_border / 255.0
        shadow_border = np.expand_dims(shadow_border, axis=-1)

        border = (border * (1 - shadow_border) + shadow_color * shadow_border).astype(np.uint8)

        for color_num in range(len(color_list)):
            center_y = margin + circle_radius + color_num * (circle_diameter + margin)
            shadow_center = (center_x + int(shadow_offset_x/2), center_y + int(shadow_offset_y/2))
            cv2.circle(shadow_mask, shadow_center, circle_radius, (255, 255, 255), -1, lineType=cv2.LINE_AA)

        for i in range(1, 3):
            current_height = math.ceil(current_height * 0.618)


        shadow_mask = cv2.GaussianBlur(shadow_mask, ((int(shadow_blur/2))|1, (int(shadow_blur/2))|1), 0)
        shadow_mask = cv2.cvtColor(shadow_mask, cv2.COLOR_BGR2GRAY) / 255.0
        shadow_mask = np.expand_dims(shadow_mask, axis=-1)
        border = (border * (1 - shadow_mask) + shadow_color * shadow_mask).astype(np.uint8)

    for i, color in enumerate(color_list):
        center_y = margin + circle_radius + i * (circle_diameter + margin)
        rgb = tuple(int(x) for x in color['rgb'])
        cv2.circle(border, (center_x, center_y), circle_radius, (*rgb, 255), -1, lineType=cv2.LINE_AA)


    # 计算文字位置和内容
    text_y_len = border_height // camera_params.size  # DataFrame有三列
    right_margin = width
    for i in range(1, 7):
        right_margin = math.ceil(right_margin * 0.618)
    # 逐行添加文字
    text_y = 0

    font_size = border_height
    for i in range(1, 5):
        font_size = math.ceil(font_size * 0.618)

    word_length_1 = get_word_length(
        camera_params.loc[0, "相机型号"],
        math.ceil(font_size * 0.618)
    )

    word_length_2 = get_word_length(
        camera_params.loc[0, "镜头参数"],
        font_size
    )

    border = add_font_to_image(
        border,
        camera_params.loc[0, "相机型号"],
        width-right_margin-word_length_1[2]-word_length_1[0],
        text_y + (text_y_len // 2),
        math.ceil(font_size * 0.618)
    )

    border = add_font_to_image(
        border,
        camera_params.loc[0, "镜头参数"],
        width-right_margin-word_length_2[2]-word_length_2[0],
        (text_y + text_y_len) + (text_y_len // 2),
        font_size
    )

    border = add_font_to_image(
        border,
        camera_params.loc[0, "拍摄时间"],
        width-right_margin-word_length_2[2]-word_length_2[0],
        (text_y + 2*text_y_len) + (text_y_len // 2),
        math.ceil(font_size * 0.618)
    )

    # 将原图和边框垂直拼接
    result = np.vstack((img, border))
    return result


if __name__ == "__main__":
    # 示例用法
    input_image = r"C:\Users\ver\Desktop\IMG_1993.HEIC.JPG" # 替换为你的图片路径
    output_image = "output_polaroid.png"  # 输出图片路径，可选
    depth = cv2.imread(r"C:\Users\ver\Desktop\image_read\depth.png") # 黑白遮罩图片路径
    depth = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)
    CAMERA_PARAMS = np.array([
        "Canon EOS R5",
        "35mm  f/5.6  1/125s  ISO200",
        "2024-06-10"
    ])
    # 调用函数添加拍立得风格边框
    img = cv2.imread(input_image)
    add_bottom_border(img, CAMERA_PARAMS, depth, 45, 50, text_color=(30, 30, 30))
