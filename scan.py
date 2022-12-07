import os
from tkinter import *
from PIL import Image, ImageTk
import cv2
import uuid

class MainWindow():
    def __init__(self, window, cap):
        self.window = window
        self.window.title('Book Scan')
        self.window.bind("<Key>", self.key_handler)
        self.cap = cap
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.interval = 20 # Interval in ms to get the latest frame
        # Create canvas for image
        self.canvas1 = Canvas(self.window, width=self.width, height=self.height)
        self.canvas1.grid(row=0, column=0)
        self.canvas2 = Canvas(self.window, width=self.width, height=self.height)
        self.canvas2.grid(row=0, column=1)
        self.previz_mode = False
        self.buffer = {}
        self.pages = []
        self.page_count = 0
        self.temp_dir_path = 'temp/'
        self.book_uniqid = None
        
        self.start_new_book()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Update image on canvas
        self.update_image()

    def update_image(self):
        # Get the latest frame and convert image format
        self.image = cv2.cvtColor(self.cap.read()[1], cv2.COLOR_BGR2RGB) # to RGB
        self.image = Image.fromarray(self.image) # to PIL format
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format
        # Update image
        self.canvas1.create_image(0, 0, anchor=NW, image=self.image)
        self.canvas2.create_image(0, 0, anchor=NW, image=self.image)
        # Repeat every 'interval' ms
        if self.previz_mode is False:
            self.window.after(self.interval, self.update_image)

    def buffer_image(self, index):
        self.buffer[index] = self.cap.read()[1]
    
    def key_handler(self, event):
        print(event.char, event.keysym, event.keycode)
        if event.char == 'p':
            self.buffer_image('left')
            self.buffer_image('right')
            self.previz_mode = not self.previz_mode
            if self.previz_mode is False:
                self.update_image()
        elif event.char == 's':
            self.save_pages()
            
    def save_pages(self):
        if self.buffer['left'] is not None and self.buffer['right'] is not None:
            book_files_path = os.path.join(
            self.temp_dir_path, str(self.book_uniqid))
            # left page
            self.page_count += 1
            cv2.imwrite(os.path.join(
                    book_files_path, "page_"+str(self.page_count)+".jpg"), self.buffer['left'])
            # right page
            self.page_count += 1
            cv2.imwrite(os.path.join(
                    book_files_path, "page_"+str(self.page_count)+".jpg"), self.buffer['right'])
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
        self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    root = Tk()
    MainWindow(root, cv2.VideoCapture(-1))
    root.mainloop()