import cv2
import numpy as np
import os
import datetime


def composite_images_with_mask(img1, img2, depth):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] combine_image porcessing...")
    # 确保depth是单通道
    if len(depth.shape) != 2:
        raise ValueError("depth遮罩必须是单通道灰度图像")

    # 确保所有图片尺寸相同
    if img1.shape[:2] != img2.shape[:2] or img1.shape[:2] != depth.shape[:2]:
        # 调整尺寸以匹配第一张图片
        h, w = img1.shape[:2]
        img2 = cv2.resize(img2, (w, h), interpolation=cv2.INTER_AREA)
        depth = cv2.resize(depth, (w, h), interpolation=cv2.INTER_AREA)
        print("警告: 图片尺寸不匹配，已自动调整")

    # 归一化depth到0-1范围，保留完整过渡效果
    depth_normalized = depth / 255.0

    # 扩展维度以匹配彩色图片 (H, W) -> (H, W, 1)
    depth_normalized = np.expand_dims(depth_normalized, axis=-1)

    # 应用depth遮罩合成图片
    # depth值为255(1.0)的区域显示img1，0的区域显示img2，中间值平滑过渡
    result = img1 * depth_normalized + img2 * (1 - depth_normalized)

    # 转换为整数类型
    result = result.astype(np.uint8)

    return result


if __name__ == "__main__":
    # 示例用法
    # 请替换为实际的图片路径
    image1_path = r"C:\Users\ver\Desktop\IMG_1498.DNG"
    image2_path = r"C:\Users\ver\Desktop\image_read\output_with_borders.jpg"
    mask_path = r"C:\Users\ver\Desktop\image_read\output\depth.jpg"  # 黑白遮罩图片
    output_path = "composite_result.jpg"

    # 检查输入文件是否存在
    for path in [image1_path, image2_path, mask_path]:
        if not os.path.exists(path):
            print(f"错误: 文件不存在 - {path}")
            exit(1)

    # 执行合成
    composite_images_with_mask(image1_path, image2_path, mask_path, output_path)
