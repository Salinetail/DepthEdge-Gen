import numpy as np
from sklearn.cluster import KMeans
import os
import cv2

def get_dominant_colors(img, num_colors=5, resize=True):
    """
    提取图片中的主要色彩

    参数:
        image_path: 图片路径
        num_colors: 要提取的主要色彩数量
        resize: 是否调整图片大小以加快处理速度

    返回:
        包含主要色彩信息的列表，每个元素是一个字典
    """

    # 调整图片大小以加快处理速度
    if resize:
        # 保持比例，最大边长为200像素
        max_size = 200
        img = cv2.resize(img, (max_size, max_size), interpolation=cv2.INTER_AREA)

    # 转换为RGB模式（处理透明图片）

    # 重塑数组以便聚类
    pixels = img.reshape(-1, 3)

    # 使用K-means聚类找出主要色彩
    kmeans = KMeans(n_clusters=num_colors, random_state=42)
    kmeans.fit(pixels)

    # 获取聚类中心（主要色彩）
    colors = kmeans.cluster_centers_
    colors = np.round(colors).astype(int)  # 转换为整数RGB值

    # 计算每个色彩的占比
    counts = np.bincount(kmeans.labels_)
    percentages = counts / counts.sum() * 100

    # 整理结果
    result = []
    for i in range(num_colors):
        r, g, b = colors[i]
        # 转换为十六进制
        hex_color = f"#{r:02x}{g:02x}{b:02x}"

        result.append({
            "index": i + 1,
            "rgb": (r, g, b),
            "hex": hex_color,
            "percentage": round(percentages[i], 2)
        })

    # 按占比排序
    result.sort(key=lambda x: x["percentage"], reverse=True)

    return result


if __name__ == "__main__":
    image_path = r"C:\Users\ver\Desktop\IMG_0192.HEIC.JPG"  # 替换为你的图片路径
    num_colors = 5  # 要提取的色彩数量

    try:
        dominant_colors = get_dominant_colors(image_path, num_colors)
        display_colors(dominant_colors)
        plot_colors(dominant_colors, "color_samples_cv2.png")

    except Exception as e:
        print(f"发生错误: {str(e)}")