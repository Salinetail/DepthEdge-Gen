import exifread
import os


def get_photo_metadata(image_path):
    """
    读取照片的EXIF元数据，提取关键相机参数

    参数:
        image_path: 照片文件路径

    返回:
        包含相机参数的字典
    """
    # 检查文件是否存在
    print("get_photo_metadata processing...")
    if not os.path.exists(image_path):
        print(f"错误: 文件 '{image_path}' 不存在")
        return None

    # 检查文件是否为图片格式
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.raw', 'DNG']
    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext not in valid_extensions:
        print(f"错误: 文件 '{image_path}' 不是支持的图片格式")
        return None

    # 打开文件并读取EXIF数据
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
    except Exception as e:
        print(f"读取文件时出错: {str(e)}")
        return None

    # 提取我们关心的参数
    metadata = {}

    # 相机品牌和型号
    metadata['相机品牌'] = tags.get('Image Make', '未知').values if 'Image Make' in tags else '未知'
    metadata['相机型号'] = tags.get('Image Model', '未知').values if 'Image Model' in tags else '未知'

    # 焦距
    if 'EXIF FocalLength' in tags:
        focal_length = tags['EXIF FocalLength'].values
        metadata['焦距'] = f"{focal_length[0]} mm"
    else:
        metadata['焦距'] = '未知'

    # 光圈
    if 'EXIF FNumber' in tags:
        f_number = tags['EXIF FNumber'].values[0]
        metadata['光圈'] = f"f/{f_number}"
    else:
        metadata['光圈'] = '未知'

    # 快门速度
    if 'EXIF ExposureTime' in tags:
        exposure_time = tags['EXIF ExposureTime'].values[0]
        metadata['快门速度'] = f"{exposure_time}s"
    else:
        metadata['快门速度'] = '未知'

    # ISO
    if 'EXIF ISOSpeedRatings' in tags:
        metadata['ISO'] = tags['EXIF ISOSpeedRatings'].values[0]
    else:
        metadata['ISO'] = '未知'

    # 拍摄日期时间
    if 'EXIF DateTimeOriginal' in tags:
        metadata['拍摄时间'] = tags['EXIF DateTimeOriginal'].values
    else:
        metadata['拍摄时间'] = '未知'

    return metadata


def print_metadata(metadata):
    """打印照片的元数据信息"""
    if not metadata:
        return

    print("\n照片参数信息:")
    print("-" * 30)
    for key, value in metadata.items():
        print(f"{key}: {value}")
    print("-" * 30)


if __name__ == "__main__":
    # 示例用法
    # 替换为你的照片路径
    photo_path = r"C:\Users\ver\Desktop\IMG_0192.HEIC.JPG"

    # 读取并显示元数据
    metadata = get_photo_metadata(photo_path)
    print_metadata(metadata)

