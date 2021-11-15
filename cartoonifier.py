import cv2  # for image processing
import easygui  # to open the filebox
import numpy as np  # to store image
import imageio  # to read image stored at particular path

import sys
import matplotlib.pyplot as plt
import os
import tkinter as tk
from PIL import ImageTk, Image
from dataclasses import dataclass


class GUI:
    box: tk.Tk

    def __init__(self):
        self.box = tk.Tk()
        self.box.geometry('400x500')
        self.box.title('Cartoonify Your Image!')
        self.box.configure(background='white')

        self.add_button(text="Choose image", command=self.upload)

        self.block_size_entry = self.add_entry('block size: 31')
        self.C_entry = self.add_entry('C: 7')

        self.add_button(text='START', command=self.start_cartoonify)

    def add_button(self, text, command, padx=20, pady=10):
        button = tk.Button(self.box, text=text, command=command, padx=padx, pady=pady)
        button.configure(background='#064116', foreground='white', font=('calibri', 15, 'bold'))
        button.pack(side=tk.TOP, pady=35)

    def add_entry(self, default_text):
        entry = tk.Entry(self.box)
        entry.insert(tk.END, default_text)
        entry.pack(side=tk.TOP, pady=2)
        return entry

    def upload(self):
        self.imgpath = easygui.fileopenbox(msg='Choose image',
                                           default='C:\\Users\\Marysia\\PycharmProjects\\Cartoonifier'
                                                   '\\images\\')

    def start_cartoonify(self):
        block_size = self.block_size_entry.get().split(':')[-1].strip()
        C = self.C_entry.get().split(':')[-1].strip()

        c = Cartoonifier(self.imgpath, int(block_size), int(C))
        cartoonified_image = c.run()
        self.add_button(text="Save cartoon image", command=lambda: self.save(cartoonified_image,
                                                                             self.imgpath),
                        padx=30, pady=5)

    def save(self, image, path):
        # saving an image using imwrite()
        imgpath, imgname = os.path.split(path)
        new_image_name = imgname.split('.')[0] + '_cartoonified.' + imgname.split('.')[1]
        path = os.path.join(imgpath, new_image_name)
        cv2.imwrite(path, image)
        I = "Image saved by name " + new_image_name + " at " + imgpath
        tk.messagebox.showinfo(title=None, message=I)

    def run(self):
        self.box.mainloop()


@dataclass
class Cartoonifier():
    imgpath: str
    block_size: int
    C: int

    def __post_init__(self):
        self.original_image, self.scale = self.read_img()

    def run(self):
        # resize and show original image
        resized1 = cv2.resize(self.original_image, self.scale)
        cv2.imshow('Original image', resized1)
        cv2.waitKey(0)

        # convert the image to grayscale
        gray_scale_image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
        resized2 = cv2.resize(gray_scale_image, self.scale)

        # apply median blur to smoothen the image
        smooth_gray_scale = cv2.medianBlur(gray_scale_image, 5)
        resized3 = cv2.resize(smooth_gray_scale, self.scale)

        # retrieve the edges for cartoon effect by using thresholding technique
        get_edge = cv2.adaptiveThreshold(smooth_gray_scale, 255,
                                         cv2.ADAPTIVE_THRESH_MEAN_C,
                                         cv2.THRESH_BINARY, self.block_size, self.C)
        resized4 = cv2.resize(get_edge, self.scale)

        # apply bilateral filter to remove noise and keep edge sharp as required
        color_image = cv2.bilateralFilter(self.original_image, 9, 300, 300)
        resized5 = cv2.resize(color_image, self.scale)

        # mask edged image with our "BEAUTIFY" image
        cartoon_image = cv2.bitwise_and(color_image, color_image, mask=get_edge)
        resized6 = cv2.resize(cartoon_image, self.scale)
        cv2.imshow('Final image', resized6)
        cv2.waitKey(0)
        # plot the whole transition
        images = [resized1, resized2, resized3, resized4, resized5, resized6]
        self.plot_step_by_step(images)

        return resized6

    def read_img(self):
        original_image = cv2.imread(self.imgpath)
        if original_image is None:
            print("Can not find any image. Choose appropriate file")
            sys.exit()
        # resize the image
        imgshape = original_image.shape
        scale = [int(960 * s) for s in (imgshape[1] / max(imgshape), imgshape[0] / max(imgshape))]
        return original_image, scale

    def plot_step_by_step(self, images):
        fig, axes = plt.subplots(3, 2, figsize=(8, 8), subplot_kw={'xticks': [], 'yticks': []},
                                 gridspec_kw=dict(hspace=0.1, wspace=0.1))
        for i, ax in enumerate(axes.flat):
            ax.imshow(images[i], cmap='gray')
        plt.show()


if __name__ == '__main__':
    cartoonifier_gui = GUI()
    cartoonifier_gui.run()
