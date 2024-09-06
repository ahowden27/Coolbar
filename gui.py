"""
Code for all the visuals of the gui
"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=line-too-long

import tkinter as tk
from tkinter import ttk
import psutil
from clipboards import CB, update_save
from PIL import Image, ImageTk


class ClipboardButton(tk.Button):
    """
    Class for communication
    """
    def __init__(self, master, button_id, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.button_id = button_id
        self.configure(command=self.on_button_click)
        self.tooltip = Tooltip(self, self.get_tooltip_text())

    def get_tooltip_text(self):
        """
        Fetches clipboard value for tooltip
        """
        index = self.button_id
        text = CB[index] if 1 <= index < len(CB) else ''
        return text[:50]

    def on_button_click(self):
        """
        Resets clipboard slot
        """
        index = self.button_id
        if CB[index] != '':
            CB[index] = ''
            self.configure(bg='black')
            print(f"CB{index} reset.")
            update_save()
        self.tooltip.text = self.get_tooltip_text()


class Tooltip:
    """
    Class for tooltip configuration
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """
        Shows the tooltip if a value is stored in that clipboard slot
        """
        if self.tooltip or not self.text:
            return
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        x = self.widget.winfo_pointerx()
        y = self.widget.winfo_pointery() + 20
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        """
        Hides the tooltip if no value is stored in that clipboard slot
        """
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class App(tk.Tk):
    """
    Main class for the window
    """
    def __init__(self):
        """
        Initiialization of variables and such
        """
        super().__init__()
        self.overrideredirect(True)

        self.dpi, self.screen_width, self.screen_height = self.get_screen_info()
        self.configure(bg='black')
        self.default_width = int(self.screen_width)
        self.default_height = 70
        self.geometry(f"{self.default_width}x70")

        self.padding = abs(self.default_width - 1680) / 2
        self.start_x = 0
        self.start_y = 0
        self.clipboards = ['']
        self.current_frame = 0
        self.read_percent = 0
        self.read_old = 0
        self.read_new = 0
        self.read_diff = 0
        self.read_mbps = 0
        self.write_percent = 0
        self.write_old = 0
        self.write_new = 0
        self.write_diff = 0
        self.write_mbps = 0
        self.cpu_percent = 0
        self.mem_percent = 0
        self.disk_percent = 0

        self.load_gif_frames(r'matrix.gif')
        self.bg_label = tk.Label(self)
        self.bg_label.place(relwidth=1, relheight=1)
        self.update_background()

        self.configure_styles()
        self.create_ui()
        self.update_values()

        self.bind('<ButtonPress-1>', self.on_drag_start)
        self.bind('<B1-Motion>', self.on_drag_motion)

    def configure_styles(self):
        """
        Setup for styles
        """
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Green.Horizontal.TProgressbar', foreground='green2', background='green2')
        style.configure('DarkGreen.Horizontal.TProgressbar', foreground='springgreen4', background='springgreen4')

    def load_gif_frames(self, gif_path):
        """
        Loads the gif frames
        """
        gif = Image.open(gif_path)
        self.frames = []
        while True:
            self.frames.append(ImageTk.PhotoImage(gif.copy()))
            try:
                gif.seek(gif.tell() + 1)
            except EOFError:
                break

    def update_background(self):
        """
        Updates gif background
        """
        if self.frames:
            self.bg_image = self.frames[self.current_frame]
            self.bg_label.config(image=self.bg_image)
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.after(90, self.update_background)

    def create_ui(self):
        """
        Initial creation of the window elements
        """
        read_frame = tk.Frame(self, bg='black')
        read_frame.grid(row=0, column=1, padx=[103.75 + self.padding, 20], pady=10)
        self.read_label = tk.Label(read_frame, text="Read:", fg='white', bg='black', font=('Arial', 14, 'bold'))
        self.read_label.pack()
        self.read_bar = ttk.Progressbar(read_frame, style='Green.Horizontal.TProgressbar', orient='horizontal', length=150, mode='determinate')
        self.read_bar.pack()

        write_frame = tk.Frame(self, bg='black')
        write_frame.grid(row=0, column=2, padx=[20, 88.75], pady=10)
        self.write_label = tk.Label(write_frame, text="Write:", fg='white', bg='black', font=('Arial', 14, 'bold'))
        self.write_label.pack()
        self.write_bar = ttk.Progressbar(write_frame, style='Green.Horizontal.TProgressbar', orient='horizontal', length=150, mode='determinate')
        self.write_bar.pack()

        cpu_frame = tk.Frame(self, bg='black')
        cpu_frame.grid(row=0, column=3, padx=15, pady=10)
        self.cpu_label = tk.Label(cpu_frame, text="CPU:", fg='white', bg='black', font=('Arial', 14, 'bold'))
        self.cpu_label.pack()
        self.cpu_bar = ttk.Progressbar(cpu_frame, style='Green.Horizontal.TProgressbar', orient='horizontal', length=175, mode='determinate')
        self.cpu_bar.pack()

        mem_frame = tk.Frame(self, bg='black')
        mem_frame.grid(row=0, column=4, padx=15, pady=10)
        self.mem_label = tk.Label(mem_frame, text="Memory:", fg='white', bg='black', font=('Arial', 14, 'bold'))
        self.mem_label.pack()
        self.mem_bar = ttk.Progressbar(mem_frame, style='Green.Horizontal.TProgressbar', orient='horizontal', length=175, mode='determinate')
        self.mem_bar.pack()

        disk_frame = tk.Frame(self, bg='black')
        disk_frame.grid(row=0, column=5, padx=[15, 55], pady=10)
        self.disk_label = tk.Label(disk_frame, text="Disk Usage:", fg='white', bg='black', font=('Arial', 14, 'bold'))
        self.disk_label.pack()
        self.disk_bar = ttk.Progressbar(disk_frame, style='Green.Horizontal.TProgressbar', orient='horizontal', length=175, mode='determinate')
        self.disk_bar.pack()

        for i in range(1, 11):
            self.clipboards.append(ClipboardButton(self, i, text=f"CB{i % 10}", bg='black', fg='black', activebackground='springgreen4', font=('Arial', 11, 'bold')))
            self.clipboards[i].grid(row=0, column=i+5, padx=0, pady=[7, 0])

    def update_values(self):
        """
        Updates all the values in window
        """
        io_counters = psutil.net_io_counters()
        self.read_new = io_counters.bytes_recv
        self.write_new = io_counters.bytes_sent

        if self.read_old or self.write_old:
            self.read_diff = self.read_new - self.read_old
            self.write_diff = self.write_new - self.write_old

            self.read_mbps = self.read_diff * 8 / (1024 * 1024) / 0.5
            self.write_mbps = self.write_diff * 8 / (1024 * 1024) / 0.5

            self.read_percent = (self.read_mbps / 1000.0) * 100
            self.write_percent = (self.write_mbps / 1000.0) * 100

        self.read_old = self.read_new
        self.write_old = self.write_new

        self.cpu_percent = psutil.cpu_percent()
        self.mem_percent = psutil.virtual_memory().percent
        self.disk_percent = psutil.disk_usage('/').percent

        progress_bars = {
            self.read_bar: self.read_percent,
            self.write_bar: self.write_percent,
            self.cpu_bar: self.cpu_percent,
            self.mem_bar: self.mem_percent,
            self.disk_bar: self.disk_percent
        }

        for progress_bar, value in progress_bars.items():
            progress_bar['value'] = value
            self.update_progress_bar_style(progress_bar, value)

        self.read_label.config(text=f"Read: {self.read_mbps:.1f} Mbps")
        self.write_label.config(text=f"Write: {self.write_mbps:.1f} Mbps")
        self.cpu_label.config(text=f"CPU: {self.cpu_percent}%")
        self.mem_label.config(text=f"Memory: {self.mem_percent}%")
        self.disk_label.config(text=f"Disk: {self.disk_percent}%")

        for i in range(1, 11):
            if CB[i] != '':
                self.clipboards[i].configure(bg='green2')

        self.after(500, self.update_values)

    def update_progress_bar_style(self, progress_bar, value):
        """
        Updates progress bar color
        """
        style_name = 'DarkGreen.Horizontal.TProgressbar' if value >= 50 else 'Green.Horizontal.TProgressbar'
        progress_bar.config(style=style_name)

    def on_drag_start(self, event):
        """
        Starting position of window
        """
        self.start_x = event.x
        self.start_y = event.y

    def on_drag_motion(self, event):
        """
        Moves window
        """
        x = self.winfo_x() + (event.x - self.start_x)
        y = self.winfo_y() + (event.y - self.start_y)
        self.geometry(f"+{x}+{y}")

    def get_screen_info(self):
        dpi = self.winfo_fpixels('1i')
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        return dpi, screen_width, screen_height
