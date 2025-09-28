import cv2
import numpy as np
import math
import os


def add_side_borders(image, depth, angle, distance):
    # 获取图片尺寸
    height, width = image.shape[:2]
    border_size = width
    for i in range(1, 7):
        border_size = math.ceil(border_size * 0.618)
    bottom_size = border_size
    for i in range(1, 6):
        bottom_size = math.ceil(bottom_size * 0.618)
    # 确保边框尺寸不会超过图片宽度的一半
    if border_size * 2 >= width:
        raise ValueError(f"边框尺寸({border_size})过大，超过图片宽度的一半")

    border_mask = np.zeros_like(image)
    result = np.full_like(image, 255)
    # 只在底部延伸 border_size 的高度
    border_mask[border_size:height - bottom_size, border_size: width - border_size, :] = result[border_size:height - bottom_size, border_size: width - border_size, :]
    border_mask = cv2.GaussianBlur(border_mask, (10 | 1, 10 | 1), 0)
    border_mask = cv2.cvtColor(border_mask, cv2.COLOR_BGR2GRAY)
    border_mask = border_mask / 255.0
    border_mask = np.expand_dims(border_mask, axis=-1)


    # depth根据shadow_offset_x和shadow_offset_y参数位移
    if depth is not None:

        shadow_color = np.full_like(image, 100)

        rad = math.radians(angle)
        shadow_offset = int(distance)
        shadow_offset_x = int(np.cos(rad) * shadow_offset)
        shadow_offset_y = int(np.sin(rad) * shadow_offset)
        shadow_blur = 101 | 1  # 阴影高斯模糊核，保证为奇数
        # 位移depth，超出部分填充0
        M = np.float32([[1, 0, shadow_offset_x], [0, 1, shadow_offset_y]])
        shadow_mask = cv2.warpAffine(depth, M, (depth.shape[1], depth.shape[0]), borderValue=0)
        shadow_mask = cv2.GaussianBlur(shadow_mask, (shadow_blur, shadow_blur), 0)
        shadow_mask = shadow_mask / 255.0
        shadow_mask = np.expand_dims(shadow_mask, axis=-1)
        result = (result * (1 - shadow_mask) + shadow_color * shadow_mask).astype(np.uint8)


    # 即从左边border_size开始，取width - 2*border_size宽度的区域
    result = (result * (1 - border_mask) + image * border_mask).astype(np.uint8)
    return result


if __name__ == "__main__":
    # 示例用法
    input_image = r"C:\Users\ver\Desktop\IMG_1993.HEIC.JPG"  # 输入图片路径
    output_image = "output_with_borders.jpg"  # 输出图片路径
    depth = cv2.imread(r"C:\Users\ver\Desktop\image_read\depth.png") # 黑白遮罩图片路径
    depth = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)
    border_pixels = 100  # 黑边宽度
    image = cv2.imread(input_image)
    # 检查输入文件是否存在
    if not os.path.exists(input_image):
        print(f"错误: 文件不存在 - {input_image}")
        exit(1)

    # 添加左右黑边
    add_side_borders(image, depth, 45, 50)
