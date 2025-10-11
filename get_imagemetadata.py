import exifread
import os
import datetime
import piexif
from PIL import Image

def get_photo_metadata(image_path):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] get_photo_metadata processing...")

    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
    except Exception as e:
        print(f"读取文件时出错")
        return None

    metadata = {}

    # 相机品牌和型号
    metadata['相机型号'] = tags.get('Image Model', '未知').values if 'Image Model' in tags else '未知'

    # 焦距
    if 'EXIF FocalLengthIn35mmFilm' in tags:
        focal_length = tags['EXIF FocalLengthIn35mmFilm'].values
        metadata['焦距'] = f"{int(round(focal_length[0], 0))}mm"
    else:
        metadata['焦距'] = '未知'

    # 光圈
    if 'EXIF FNumber' in tags:
        f_number = tags['EXIF FNumber'].values[0]
        metadata['光圈'] = f"f/{round(float(f_number), 1)}"
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

    gps_params = ""
    if 'GPS GPSLatitude' in tags:
        gps_params = gps_params + str((float(tags['GPS GPSLatitude'].values[2]))) + "°"
    else:
        gps_params = gps_params + '未知'

    if "GPS GPSLatitudeRef" in tags:
        gps_params = gps_params + str(tags['GPS GPSLatitudeRef'].values)
    else:
        gps_params = gps_params + '未知'

    if 'GPS GPSLongitude' in tags:
        gps_params = gps_params + "    " + str((float(tags['GPS GPSLongitude'].values[2]))) + "°"
    else:
        gps_params = gps_params + '未知'

    if 'GPS GPSLongitudeRef' in tags:
        gps_params = gps_params + str(tags['GPS GPSLongitudeRef'].values)
    else:
        gps_params = gps_params + '未知'

    metadata['地理位置'] = gps_params
    return metadata

def deliver_metadata(image_path, output_path):
    try:
        # 读取原图的EXIF数据
        exif_dict = piexif.load(image_path)
        # 打开输出图片
        image = Image.open(output_path)
        icc_profile = image.info.get('icc_profile')
        # 保存时写入EXIF
        image.save(output_path, exif=piexif.dump(exif_dict), quality=100, subsampling=0, compress_level=1, icc_profile=icc_profile)
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] deliver_metadata: EXIF已写入输出图片")
    except Exception as e:
        print(f"deliver_metadata出错: {e}")

if __name__ == "__main__":
    # 示例用法
    # 替换为你的照片路径
    photo_path = r"C:\Users\ver\Desktop\IMG_1993.HEIC.JPG"

    # 读取并显示元数据
    metadata = get_photo_metadata(photo_path)
