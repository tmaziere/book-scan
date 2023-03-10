import os
from tkinter import *
from PIL import Image, ImageTk
import cv2
import uuid

from utils.analyse_image import is_blurred, list_ports


class MainWindow():
    def __init__(self, window, cap_l, cap_r):
        self.window = window
        self.window.title('Book Scan - an ESAM/CCC project')
        self.window.bind("<Key>", self.key_handler)
        self.cap = {}
        self.cap['l'] = cap_l
        self.cap['l'].set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap['l'].set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap['r'] = cap_r
        self.cap['r'].set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap['r'].set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.width = 480
        self.height = 640
        self.interval = 20  # Interval in ms to get the latest frame
        # Create canvas for image
        self.canvas1 = Canvas(
            self.window, width=self.width, height=self.height)
        self.canvas1.grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky=E)
        self.canvas2 = Canvas(
            self.window, width=self.width, height=self.height)
        self.canvas2.grid(row=0, column=2, columnspan=2, padx=15, pady=15, sticky=W)
        self.but_preview = Button(self.window, text="Preview (p)", command=self.handle_preview)
        self.but_preview.grid(row=1, column=0, rowspan=2, ipadx=10, ipady=10)
        self.but_save = Button(self.window, text="Save (s)", command=self.save_pages)
        self.but_save.grid(row=1, column=1, rowspan=2, ipadx=10, ipady=10)
        self.but_save['state'] = DISABLED
        label = Label(root, text='Use "preview" to freeze the images : if they are good for you, click "Save" to process the next pages.')
        label.grid(row=1, column=2, columnspan=2, padx=15, pady=15, sticky=W)
        # global attributes
        self.previz_mode = False
        self.buffer = {'l': None, 'r': None}
        self.pages = []
        self.page_count = 0
        self.temp_dir_path = 'temp/'
        self.book_uniqid = None

        self.start_new_book()
        label2 = Label(root, text=f'Current book reference: {self.book_uniqid}')        
        label2.grid(row=2, column=2, columnspan=2, padx=15, pady=15, sticky=W)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Update image on canvas
        self.update_image()

    def update_image(self):
        # LEFT : Get the latest frame and convert image format
        self.image_l = cv2.cvtColor(
            self.cap['l'].read()[1], cv2.COLOR_BGR2RGB)  # to RGB
        self.image_l = cv2.rotate(
            self.image_l, cv2.ROTATE_90_CLOCKWISE)  # rotate
        self.image_l = Image.fromarray(self.image_l)  # to PIL format
        self.image_l = ImageTk.PhotoImage(self.image_l)  # to ImageTk format
        # Update image
        self.canvas1.create_image(0, 0, anchor=NW, image=self.image_l)
        # RIGHT : Get the latest frame and convert image format
        self.image_r = cv2.cvtColor(
            self.cap['r'].read()[1], cv2.COLOR_BGR2RGB)  # to RGB
        self.image_r = cv2.rotate(
            self.image_r, cv2.ROTATE_90_CLOCKWISE)  # rotate
        self.image_r = Image.fromarray(self.image_r)  # to PIL format
        self.image_r = ImageTk.PhotoImage(self.image_r)  # to ImageTk format
        # Update image
        self.canvas2.create_image(0, 0, anchor=NW, image=self.image_r)
        # Repeat every 'interval' ms
        if self.previz_mode is False:
            self.window.after(self.interval, self.update_image)

    def buffer_image(self, index):
        if index in ("l", "r"):
            img = self.cap[index].read()[1]
            res_is_blurred, blur_val = is_blurred(img, 100)
            print(res_is_blurred, blur_val)
            self.buffer[index] = img
        else:
            raise Exception('Unknown cap index: ', index)
        
    def handle_preview(self):
        self.buffer_image('l')
        self.buffer_image('r')
        self.previz_mode = not self.previz_mode
        if self.previz_mode is False:
            self.but_save['state'] = DISABLED
            self.update_image()
        else:
            self.but_save['state'] = NORMAL

    def key_handler(self, event):
        print(event.char, event.keysym, event.keycode)
        if event.char == 'p':
            self.handle_preview()
        elif event.char == 's':
            self.save_pages()

    def save_pages(self):
        if self.buffer['l'] is not None and self.buffer['r'] is not None:
            book_files_path = os.path.join(
                self.temp_dir_path, str(self.book_uniqid))
            # left page
            self.page_count += 1
            cv2.imwrite(os.path.join(
                book_files_path, "page_"+str(self.page_count)+".jpg"), self.buffer['l'])
            # right page
            self.page_count += 1
            cv2.imwrite(os.path.join(
                book_files_path, "page_"+str(self.page_count)+".jpg"), self.buffer['r'])
            self.previz_mode = False
            self.update_image()
            self.but_save['state'] = DISABLED
        else:
            print("No pages buffered")

    def start_new_book(self):
        self.book_uniqid = uuid.uuid4()
        # create book directory
        try:
            book_files_path = os.path.join(
                self.temp_dir_path, str(self.book_uniqid))
            if not os.path.exists(book_files_path):
                os.mkdir(book_files_path)
            print("New book started: "+str(self.book_uniqid))
        except Exception as e:
            print('Error creating book temp directory: ', e)
            pass

    def on_closing(self):
        print('Closing...')
        self.cap['l'].release()
        self.cap['r'].release()
        self.window.destroy()


if __name__ == "__main__":
    root = Tk()
    # print(list_ports()[1])
    MainWindow(root, cv2.VideoCapture(0), cv2.VideoCapture(4))
    root.mainloop()
