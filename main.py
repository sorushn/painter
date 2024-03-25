from PIL import Image
import numpy as np
import os
from multiprocessing import Pool, cpu_count
from icecream import ic
import tkinter as tk
import tkinter.ttk as ttk
from tkcolorpicker import askcolor
import argparse


def get_dominant_color(pil_img):
    # source: https://stackoverflow.com/a/61730849
    img = pil_img.copy()
    img = img.convert("RGBA")
    img = img.resize((1, 1), resample=0)
    dominant_color = img.getpixel((0, 0))
    return dominant_color


def replace_color(pil_img, original_color, new_color):
    # source: https://stackoverflow.com/a/3753428
    data = np.array(pil_img)
    img_r, img_g, img_b = data.T  # + [None]*len(data.T)
    source_areas = (img_r == original_color[0]) & (
        img_g == original_color[1]) & (img_b == original_color[2])
    ic(source_areas.shape)
    data[source_areas.T] = new_color
    im2 = Image.fromarray(data)
    return im2


def paint_image(img_path, new_color, original_color=None):
    """Replace the pixels of original_color in the given image with the new_color. Use the most common color in the image if original_color is None"""
    ic(img_path)
    pil_img = Image.open(img_path)
    if original_color == None:
        original_color = get_dominant_color(pil_img)
    ic(original_color)
    new_img = replace_color(pil_img, original_color, new_color)
    new_img.save(img_path + ".jpeg")


def paint_all_files_in_directory(target_dir, file_extension, new_color, original_color=None, process_pool=1):
    """collect all the files in the target_dir with the given file_extension and pain them"""
    files = [file for file in os.listdir(
        target_dir) if file.endswith(file_extension)]
    files_and_args = [(os.path.join(target_dir, file),
                       new_color, original_color) for file in files]
    with Pool(process_pool) as p:
        p.starmap(paint_image, files_and_args)


def browseFiles():
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Text files",
                                                      "*.txt*"),
                                                     ("all files",
                                                      "*.*")))

    # Change label contents
    label_file_explorer.configure(text="File Opened: "+filename)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Example Argument Parser with GUI Flag")

    # Adding the GUI flag argument
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Enable graphical user interface'
    )

    parser.add_argument(
        '--new_color',
        metavar='R,G,B',
        type=str,
        default='255,0,0',
        help='New color in RGB format (e.g., --new_color 255,0,0)'
    )

    parser.add_argument(
        '--original_color',
        metavar='R,G,B',
        type=str,
        default=None,
        help='Target color in RGB format (e.g., --original_color 0,255,0)'
    )
    # Parse the arguments
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.gui:
        print("GUI enabled")
        root = tk.Tk()
        style = ttk.Style(root)
        style.theme_use('clam')
        original_color = askcolor((255, 255, 0), title="pick target color")[0]

        new_color = askcolor((255, 255, 0), title="pick target color")[0]
        if not new_color:
            new_color = (255, 255, 255)
    else:
        if args.new_color:
            try:
                new_color = [int(color) for color in args.new_color.split(',')]
                ic("New color:", new_color)
            except ValueError:
                print(
                    "Invalid new color format. Please provide RGB values separated by commas.")

        if args.original_color:
            try:
                original_color = [int(color)
                                  for color in args.original_color.split(',')]
                ic("Target color:", original_color)
            except ValueError:
                print(
                    "Invalid target color format. Please provide RGB values separated by commas.")
        else:
            original_color = None

    paint_all_files_in_directory(
        "data", ".jpg", new_color=new_color, original_color=original_color)
