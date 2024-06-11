import customtkinter as customtk
from customtkinter import filedialog
import os
import json
from PIL import Image, ImageTk




class homeui(customtk.CTk):
    def __init__(self):
        super().__init__()

        self.title('Manhua-Martial Peak')
        self.geometry('1250x1000')  # size of window    
        self.geometry('+10+10')     # Coordinate of window

        customtk.set_appearance_mode('dark')

        self.side_frame = customtk.CTkFrame(self, width=375, height=630)
        self.side_frame.place(x=865, y=10)

        data = self.load_json('last_view.json')
        self.directory = data['directory']
        self.folder_name = data['folder']

        self.heading = customtk.CTkLabel(self.side_frame, text=self.folder_name)
        self.heading.place(x=600, y=2)

        # Change the current working directory
        os.chdir(self.directory)

        # Create a dropdown menu (option menu) with the folder names
        folder_names = [name for name in os.listdir(self.directory) if os.path.isdir(os.path.join(self.directory, name))]

        self.manga_name = customtk.StringVar(self.side_frame)

        if folder_names:
            self.manga_name.set(self.folder_name)
            dropdown = customtk.CTkOptionMenu(self.side_frame, variable=self.manga_name, values=folder_names, command=self.change_manga)
            dropdown.place(x=20, y=20)
        else:
            no_folders_label = customtk.CTkLabel(self.side_frame, text="No folders found in the directory.")
            no_folders_label.place(x=20, y=20)


        self.directory_entry = customtk.CTkButton(self.side_frame, text='Choose Directory', command=self.change_directory)
        self.directory_entry.place(x=150, y=200)

        self.chapter_btn = customtk.CTkButton(self.side_frame, text='Get Chapter', command=self.submit_chapter)
        self.chapter_btn.place(x=150, y=100)

        self.chapter_entry = customtk.CTkEntry(self.side_frame, width=100)
        self.chapter_entry.place(x=20, y=100)
        # Bind the Enter key to the entry field
        self.chapter_entry.bind("<Return>", self.submit_chapter)

        self.scrollable_frame = customtk.CTkScrollableFrame(self, width=800, height=630)
        self.scrollable_frame.place(x=25, y=10)

        # Scroll-Controls
        self.scrollable_frame.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.scrollable_frame.bind_all("<Up>", lambda e: self.on_mouse_wheel(e, -1))
        self.scrollable_frame.bind_all("<Down>", lambda e: self.on_mouse_wheel(e, 1))
        self.scrollable_frame.bind_all("<Home>", lambda e: self.scrollable_frame._parent_canvas.yview_moveto(0.0))
        self.scrollable_frame.bind_all("<End>", lambda e: self.scrollable_frame._parent_canvas.yview_moveto(1.0))

        # # Default Images Size
        # self.img_width = 750
        # self.img_height = 1250
        self.scale_factor = 1

        self.scale_entry = customtk.CTkEntry(self.side_frame, width=50,  placeholder_text='Scale-Factor')
        self.scale_entry.place(x=20, y=250)
        self.scale_entry.bind('<Return>', command= self.scale_func)

        # Bind ctrl + and ctrl - for resizing images
        self.bind_all("<Control-plus>", self.increase_image_size)
        self.bind_all("<Control-minus>", self.decrease_image_size)

        # Load last viewed chapter and page
        self.load_last_view()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    

    def scale_func(self, event):
        self.scale_factor = float(self.scale_entry.get())
        self.submit_chapter()

    def change_manga(self, f_name):
        # print(event)
        self.chapter_entry.delete(0, 'end')
        # Loading Chapter
        chapter_data = self.load_json(f'{f_name}/last_chapter.json')
        self.chapter_entry.insert(0, chapter_data['chapter'])
        # -- Save Scroll position
        chapter_data['scroll_val'] = self.scrollable_frame._parent_canvas.yview()
        self.save_json(f'{f_name}/last_chapter.json', chapter_data)

        self.submit_chapter()

        # Load Scroll position
        self.scrollable_frame._parent_canvas.yview_moveto(chapter_data['scroll_val'][0])

    # Smooth & Fast scroll
    def on_mouse_wheel(self, event, *move_val):
        # Custom scroll speed for smoother scrolling

        if 1 in move_val or -1 in move_val:
            direction = move_val[0]
        else:
            direction = -1 if event.delta > 0 else 1

        for i in range(30):  # for loop for smoothness while having small increments
            self.scrollable_frame._parent_canvas.yview_scroll(int(direction * 5), "units")    

        self.on_scroll_load(self.img_dir)
        

             
    
    # Gets All img of Chapter & saves ch.no to json (save_last_view())
    def submit_chapter(self, *event):

        manga = self.manga_name.get()
        chapter_number = self.chapter_entry.get()
        file_location = f"{self.directory}/{manga}/last_chapter.json"
        
        # Create json file in folders
        if os.path.exists(file_location) == False:
            self.create_last_chapter_file(manga)

        # Retrieve previous read chapter.no
        if chapter_number == '':
            last_chapter_file = self.load_json(file_location)
            chapter_number = last_chapter_file['chapter']

        if chapter_number.isdigit():
            chapter_path = os.path.join(manga, f'Chapter-{chapter_number}')

            if os.path.exists(chapter_path):
                self.img_dir = self.load_img_list(chapter_path)
                self.save_last_chapter(chapter_number)
                self.on_scroll_load(self.img_dir)

            else:
                self.heading.configure(text=f"Chapter {chapter_number} does not exist.")

        else:
            self.heading.configure(text="Please enter a valid chapter number.")

    # Loads all the images in folder to the frame
    def load_img_list(self, folder_path):
        # Clear any existing images in the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Function to return page.no from filename for ordering with sorted(key=)
        def extract_pg_number(filename):
            parts = filename.split('_')
            pg_part = parts[-1].split('.')[0]
            pg_number = int(pg_part.replace('pg', ''))
            return pg_number

        img_list = [filename for filename in sorted(os.listdir(folder_path), key=extract_pg_number) if filename.endswith(('.png', '.jpg', '.jpeg'))]
        open_img_list = []

        for i, img in enumerate(img_list):
            file_path = os.path.join(folder_path, img_list[i])
            # Opened Image
            img = Image.open(file_path)
            # ctk_img = customtk.CTkImage(light_image=img)
            open_img_list.append(img)

        # Transfer to function where chapter loads
        current_scroll_val = self.scrollable_frame._parent_canvas.yview()[0]

        total_height = sum(height.height for i, height in enumerate(open_img_list) )
        self.page_and_scroll = {}
        self.empty_labels = []

        # Running total of the scroll value
        accumulated_scroll = 0
        
        for pg_no, img in enumerate(open_img_list):
            # Calculate & add to dict, the scroll value for the current image based on its height
            img_scroll_value = img.height / total_height
            self.page_and_scroll[pg_no] = accumulated_scroll
            
            # Add Empty Areas
            blank_label = customtk.CTkLabel(self.scrollable_frame, height=img.height, text='')
            self.empty_labels.append(blank_label)
            blank_label.pack()

            accumulated_scroll += img_scroll_value
        
        return open_img_list

        # Load and display each image in the folder
        # for filename in sorted(os.listdir(folder_path), key=extract_pg_number):
        # for filename in os.listdir(folder_path):


        """        
            if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):

                file_path = os.path.join(folder_path, filename)
                
                # Use CTkImage
                img = Image.open(file_path)
                ctk_img = customtk.CTkImage(light_image=img)

                original_size = img.size
                self.scale_factor = 750/original_size[0]
                ctk_img.configure(size=(original_size[0]*self.scale_factor, original_size[1]*self.scale_factor))
                

                # Attach the CTkImage to a CTkLabel
                label = customtk.CTkLabel(self.scrollable_frame, image=ctk_img, text='')
                label.pack()

        
        # Scroll back to top after entering submit chapter button
        self.scrollable_frame._parent_canvas.yview_moveto(0)

        self.btn_frame = customtk.CTkFrame(self.scrollable_frame,border_width=2)
        self.btn_frame.pack(pady=20)

        prev_btn = customtk.CTkButton(self.btn_frame, text='<-Previous', command=lambda: self.prev_or_next(-1))
        prev_btn.grid(padx=10, row=0, column=0)

        next_btn = customtk.CTkButton(self.btn_frame, text='Next->', command=lambda: self.prev_or_next(1))
        next_btn.grid(padx=10, row=0, column=1)"""

    def on_scroll_load(self, img_list):
        self.scrollable_frame.update()
        
        # Transfer to function where chapter loads
        current_scroll_val = self.scrollable_frame._parent_canvas.yview()[0]

        # last_pg = 8
        # current_page = 0
        # Get right values for current and last page
        for pg, scroll in self.page_and_scroll.items():
            last_pg = list(self.page_and_scroll.keys())[-1]
            
            try:
                if current_scroll_val >= scroll and current_scroll_val <= self.page_and_scroll[pg+1] :
                    current_page = pg
                    break
            except:
                current_page = last_pg
                break

        # Load the Images
        def img_label(i_list=[0, 1, 2, 3]):
            """-1 prev, 0 current & 1 next page"""
            for i, value in enumerate(i_list):

                idx = current_page + value
                label_to_fill = self.empty_labels[idx]
                
                if label_to_fill.cget('image') == None:
                    ctk_img = customtk.CTkImage(light_image= img_list[idx] )

                    original_size = img_list[idx].size
                    self.scale_factor = 750/original_size[0]
                    ctk_img.configure(size=(original_size[0]*self.scale_factor, original_size[1]*self.scale_factor))
                    
                    # Attach the CTkImage to a CTkLabel
                    label_to_fill.configure(image=ctk_img, height=original_size[1]*self.scale_factor)
                    label_to_fill._update_image
        
        def blank_label(i_list):
            """-1 prev, 0 current & 1 next page"""
            for i, value in enumerate(i_list):
                idx = current_page + value
                label_to_empty = self.empty_labels[idx]
                
                if label_to_empty.cget('image') != None:
                    label_to_empty.configure(image=None)

        if current_page-1 < last_pg: 
            img_label()    # Load 3 img
            blank_label([-1])
            self.scrollable_frame.update_idletasks()

        elif current_page < last_pg: img_label([0])     # Load 2 img

        elif current_page == last_pg: # load 1 img
            img_label([0])
            self.btn_frame = customtk.CTkFrame(self.scrollable_frame,border_width=2)
            self.btn_frame.pack(pady=20)

            prev_btn = customtk.CTkButton(self.btn_frame, text='<-Previous', command=lambda: self.prev_or_next(-1))
            prev_btn.grid(padx=10, row=0, column=0)

            next_btn = customtk.CTkButton(self.btn_frame, text='Next->', command=lambda: self.prev_or_next(1))
            next_btn.grid(padx=10, row=0, column=1)
    
        print(current_page, last_pg)

        # print(self.page_and_scroll)



        """file_path = os.path.join(folder_path, img_list[0])
                
        # Use CTkImage
        img = Image.open(file_path)
        ctk_img = customtk.CTkImage(light_image=img)"""

        # print(scroll_value)
        # print(total_scroll)


        pass



    # Save the Chapter.no to json
    def save_last_chapter(self, chapter_number):
        # Save the last viewed chapter and page
        directory = f"{self.manga_name.get()}/last_chapter.json"
        
        last_chapter_data = self.load_json(directory)
        last_chapter_data['chapter'] = chapter_number
        last_chapter_data['scroll_val'] = self.scrollable_frame._parent_canvas.yview()

        self.save_json(directory, last_chapter_data)

    # Load the last viewed chapter and page
    def load_last_view(self):
        if os.path.exists('last_view.json'):
            
            # Create variables from previous values
            manga = self.folder_name

            last_chapter = self.load_json(f"{manga}/last_chapter.json")

            chapter_number = last_chapter.get('chapter')
            scrollvalue = last_chapter.get('scroll_val')

            self.chapter_entry.insert(0, chapter_number)
            chapter_path = os.path.join(manga, f'Chapter-{chapter_number}')

            self.img_dir = self.load_img_list(chapter_path)

            if os.path.exists(chapter_path):
                # self.after to wait for widgets to fully load
                self.load_img_list(chapter_path)
                self.on_scroll_load(self.img_dir)
                self.after(100, lambda: self.scrollable_frame._parent_canvas.yview_moveto(scrollvalue[0]))

    # Change to new directory
    def change_directory(self, event):
        directory = filedialog.askdirectory()
        if directory:
            self.directory = directory

        # if self.directory == '':
        #     self.directory = 'C:/Users/user/Documents/Code/New Codes/Project 03 - Manga Reader'

        try:
            os.chdir(self.directory)
            print(self.directory)

            data = self.load_json()
            data['directory'] = self.directory
            self.save_json('last_view.json', data)

            self.chapter_entry.delete(0, 'end')
            self.load_last_view()

        except:
            print('No directory Found')

    # Button for going next & previous chapter
    def prev_or_next(self, number):
        ch_no = self.chapter_entry.get()
        self.chapter_entry.delete(0,'end')
        self.chapter_entry.insert(0, int(ch_no)+number)
        self.submit_chapter()

    # Read last.json
    def load_json(self, json_file):
        with open(json_file, 'r') as file:
            return json.load(file)

    # Dump last.json
    def save_json(self, json_file, data):
        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)

    # Save Scroll on closing
    def on_closing(self):
        # scrollbar_value = self.scrollable_frame._parent_canvas.yview()
        try:
            self.save_last_chapter(self.chapter_entry.get())         # Save the last viewed page (scroll value)
            data = self.load_json('last_view.json')
            data['folder'] = self.manga_name.get()
            self.save_json('last_view.json', data)
        except: pass

        self.destroy()

    # Create last_chapter.json
    def create_last_chapter_file(self, folder_name):

        directory = self.directory
        file_path = os.path.join(directory, folder_name, 'last_chapter.json')

        chapters_path = os.listdir(os.path.join(directory, folder_name))
        # Find lowest numbered folder
        # List all items in the directory
        # items = os.listdir(directory)
        # folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]

        folder_names = [name for name in chapters_path if os.path.isdir(os.path.join(f'{directory}/{folder_name}', name))]
        print(folder_names)

        lowest_number = 0

        for folder in folder_names:
            # Split the folder name to find the number part
            numbered_str = folder.replace('Chapter-', '')
            
            try:
                number = int(numbered_str)

                if lowest_number == 0:
                    lowest_number = number

                elif number < lowest_number:
                    lowest_number = number


            except ValueError:
                # Ignore folders where the number part is not an integer
                pass



        data = {
            "chapter": str(lowest_number),
            "scroll_val": [
                0.0,
                0.041810459251393685
            ]
        }  

        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Created last_chapter.json in {file_path}")

    # Using Ctrl+ & Ctrl- to adjust img size
    def increase_image_size(self, event):
        self.img_width += 50
        self.img_height += 83.333333333
        self.submit_chapter()

    def decrease_image_size(self, event):
        self.img_width = max(50, self.img_width - 50)  # Ensure width is at least 50
        self.img_height = max(83.33333333, self.img_height - 83.3333333)  # Ensure height is at least 50
        self.submit_chapter()
                    
if __name__ == '__main__':
    app = homeui()
    app.mainloop()