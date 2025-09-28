import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import datetime

def add_font_to_image(botton_image, word, word_x, word_y, font_size):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] add_font processing...")
    font_path = 'font/SmileySans-Oblique.ttf'
    font = ImageFont.truetype(font_path, font_size)
    img_pil = Image.fromarray(cv2.cvtColor(botton_image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    draw.text((word_x, word_y), word, font=font, fill=(0,0,0))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def get_word_length(word, font_size):
    font_path = 'font/SmileySans-Oblique.ttf'
    font = ImageFont.truetype(font_path, font_size)
    return font.getbbox(word)