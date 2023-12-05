from PIL import Image
import numpy as np
import os
from multiprocessing import Pool, cpu_count
from icecream import ic


def get_dominant_color(pil_img):
    # source: https://stackoverflow.com/a/61730849
    img = pil_img.copy()
    img = img.convert("RGBA")
    img = img.resize((1, 1), resample=0)
    dominant_color = img.getpixel((0, 0))
    return dominant_color


def replace_color(pil_img, source_color, target_color):
    # source: https://stackoverflow.com/a/3753428
    data = np.array(pil_img)
    img_r, img_g, img_b = data.T  # + [None]*len(data.T)
    source_areas = (img_r == source_color[0]) & (
        img_g == source_color[1]) & (img_b == source_color[2])
    ic(source_areas.shape)
    data[source_areas.T] = target_color
    im2 = Image.fromarray(data)
    return im2


def paint_image(img_path, target_color, source_color=None):
    pil_img = Image.open(img_path)
    if source_color == None:
        source_color = get_dominant_color(pil_img)
    new_img = replace_color(pil_img, source_color, target_color)
    new_img.save(img_path + ".jpeg")


def paint_all_files_in_directory(target_dir, file_extension, target_color, source_color=None, process_pool=1):
    files = [file for file in os.listdir(
        target_dir) if file.endswith(file_extension)]
    files_and_args = [(os.path.join(target_dir, file),
                       target_color, source_color) for file in files]
    with Pool(process_pool) as p:
        p.starmap(paint_image, files_and_args)
