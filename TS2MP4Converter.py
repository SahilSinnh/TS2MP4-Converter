"""
This script is a GUI application that converts TS (Transport Stream) video files to MP4 format.
It provides a user interface where the user can select an input folder containing TS files, choose whether to convert the files or just list them, and view the conversion progress and log.

The TSConverterApp class represents the main application window and contains methods for setting up the user interface, handling user interactions, and processing the files.
"""

import os
import math
import ffmpeg
import threading
import subprocess
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext, font

class TSConverterApp:
    def __init__(self, root):
        """
        Initializes the TSConverterApp object.

        Parameters:
            root (tk.Tk): The root Tkinter window object.

        Returns:
            None
        """
        self.root = root
        self.root.title("TS To MP4 Video Converter - by sahil_sinnh")
        self.root.geometry("800x650")
        self.root.config(bg='cyan4')
        
        self.forbidden_folders = ["Program Files/", "AppData/", "CrossDevice/", "Program Files\\", "AppData\\", "CrossDevice\\", "VS-Code", "vscode"]
        
        self.input_folder = tk.StringVar()
        self.convert_mode = tk.BooleanVar(value=False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        Sets up the user interface of the application.

        Parameters:
            None

        Returns:
            None
        """
        # Destroy all existing widgets in root
        for widget in root.winfo_children():
            widget.destroy()
        # Header
        tk.Label(self.root, text="TS To MP4 Video Converter", bg='DeepSkyBlue4', fg='cyan2', width=100, font=f'TkDefaultFont {math.ceil(font.nametofont('TkDefaultFont').actual()['size']*3)} bold').pack(side="top", fill="x")
        
        # File Selector
        self.input_label = tk.Label(self.root, text="Select Input Folder:", bg='cyan4', font=f'TkDefaultFont {math.ceil(font.nametofont('TkDefaultFont').actual()['size']*1.1)} bold')
        self.input_label.pack(padx=1, pady=5)
        self.input_label.pack()
        self.input_folder_box = tk.Entry(self.root, bg='DarkSlateGray4', textvariable=self.input_folder, width=80)
        self.input_folder_box.pack()
        self.browse_folder_button = tk.Button(self.root, text="Browse", bg='SeaGreen4', width=8, command=self.select_folder)
        self.browse_folder_button.pack(padx=1, pady=1)
        
        # Forbidden Folders [Folders which are discarded from processing]
        self.forbidden_label = tk.Label(self.root, text="Forbidden Folders: [" + ", ".join(set(s.replace("/", "").replace("\\", "") for s in self.forbidden_folders)) + "]", bg='cyan4', font=f'TkDefaultFont {math.ceil(font.nametofont('TkDefaultFont').actual()['size']*0.85)} italic')
        self.forbidden_label.pack()
        
        # Backup Folder and Log File Location
        self.log_label = tk.Button(self.root, bg='cyan4', font=f'TkDefaultFont {math.ceil(font.nametofont('TkDefaultFont').actual()['size'])} bold', text="", command=self.open_log_folder)
        
        # Conversion Mode [Weather to convert files or just list them]
        self.convert_checkbox = tk.Checkbutton(self.root, text="Enable Conversion Mode", bg='cyan4', font=f'TkDefaultFont {math.ceil(font.nametofont('TkDefaultFont').actual()['size'])} bold', variable=self.convert_mode)
        self.convert_checkbox.pack()
        
        # Run Button
        self.run_button = tk.Button(self.root, text="Run", bg='SeaGreen3', width=12, command=self.start_process)
        self.run_button.pack(padx=10, pady=10)
        
        # Output Box Console
        self.output_box = scrolledtext.ScrolledText(self.root, bg='DarkSlateGray4', width=80, height=15)
        self.output_box.pack()

        # Progress bar
        self.progress_label = tk.Label(self.root, text="Progress:", bg='cyan4', font=f'TkDefaultFont {math.ceil(font.nametofont('TkDefaultFont').actual()['size']*1.1)} bold')
        self.progress = ttk.Progressbar(self.root, length=400, mode='determinate', maximum=100)
        
        # Return to Home button
        self.home_button = tk.Button(self.root, text="Back to Home", bg='SeaGreen3', command=self.back_to_home)
        
        # Help and About button
        help_button = tk.Button(root, text="Help", bg='turquoise4', fg='cyan1', command=self.show_help)
        help_button.pack(side="left", padx=10, pady=10)
        about_button = tk.Button(root, text="About", bg='turquoise4', fg='cyan1', command=self.show_about)
        about_button.pack(side="right", padx=10, pady=10)
        # By Line
        tk.Label(self.root, text="Created By - sahil_sinnh", bg='cyan4', fg='cyan1', width=100, font=f'TkDefaultFont {math.ceil(font.nametofont('TkDefaultFont').actual()['size'])} bold').pack(side="bottom", fill="x")
        
        
    def select_folder(self):
        """
        Opens a file dialog to select an input folder and sets the selected folder path to the input_folder variable.

        Parameters:
            None

        Returns:
            None
        """
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)
            self.log_label.config(text=f"Log Folder:  {(os.path.join(folder, 'TS_to_MP4_Logs/')).replace('/', '\\')}")
    
    def start_process(self):
        """
        Starts the file processing in a separate thread.

        Parameters:
            None

        Returns:
            None
        """
        self.run_button['state'] = tk.DISABLED
        self.input_folder_box['state'] = tk.DISABLED
        self.browse_folder_button['state'] = tk.DISABLED
        self.convert_checkbox['state'] = tk.DISABLED
        threading.Thread(target=self.process_files, daemon=True).start()
    
    def process_files(self):
        """
        Processes the TS files in the selected input folder.

        Parameters:
            None

        Returns:
            None
        """
        file_count = 0
        input_folder = self.input_folder.get()
        if not input_folder:
            messagebox.showerror("Error", "Please select an input folder")
            self.home_button.pack(padx=10, pady=10)
            self.back_to_home() #return back to home
            return
        
        self.progress_label.pack(padx=1, pady=1)
        self.progress.pack()
        
        backup_folder = os.path.join(input_folder, 'TS_to_MP4_Logs')
        log_file = os.path.join(backup_folder, 'conversion_log.csv')
        os.makedirs(backup_folder, exist_ok=True)
        
        log_data = self.load_log(log_file)
        ts_files = self.find_ts_files(input_folder)
        
        total_files = len(ts_files)
        
        for idx, ts_file in enumerate(ts_files):
            self.update_progress(idx, total_files)
            if not any(sub in ts_file for sub in self.forbidden_folders):
                mp4_file = ts_file.replace(".ts", "_ts2mp4.mp4")
                if ts_file in log_data and log_data[ts_file]['Status'] == 'Success':
                    continue
                file_count +=1
                if self.convert_mode.get():
                    success, error = self.convert_ts_to_mp4(ts_file, mp4_file)
                    
                    log_data[ts_file] = {
                        'Original TS File': ts_file.replace('/', '\\'),
                        'Original Size': f'{os.path.getsize(ts_file)/1024/1024} MB',
                        'Status': 'Success' if success else 'Failed',
                        'Converted MP4 File': mp4_file.replace('/', '\\') if success else None,
                        'New Size': f'{os.path.getsize(mp4_file)/1024/1024} MB' if success else None,
                        'Timestamp': pd.Timestamp.now(),
                        'Backup TS File': ts_file.replace(input_folder, backup_folder).replace('/', '\\'),
                        'Error Message': error
                    }
                    self.output_box.insert(tk.END, str(file_count) + ". " +  log_data[ts_file]['Status'].upper() + " - " + ts_file.replace('\\', '/') + "\n")
                    if success:
                        self.move_ts_file(ts_file, backup_folder)
                    self.update_log(log_file, log_data)
                else:
                    self.output_box.insert(tk.END, str(file_count) + ". " + ts_file.replace('/', '\\') + "\n")
                    continue
        
        self.output_box.insert(tk.END, "\n\nProcessed " + str(file_count) + " Files. \n")
            
        if not self.convert_mode.get():
            self.update_progress(total_files, total_files)  # Ensure progress bar reaches 100%
            messagebox.showinfo("Done", "Listed all unconverted .ts files.")
            self.home_button.pack(padx=10, pady=10)
            return
        
        self.update_progress(total_files, total_files)  # Ensure progress bar reaches 100%
        if self.convert_mode.get():
            self.log_label.pack()
        messagebox.showinfo("Done", "Processing complete.")
        self.home_button.pack(padx=10, pady=10)
    
    def find_ts_files(self, folder):
        """
        Finds all TS files in the given folder and its subfolders.

        Parameters:
            folder (str): The path of the folder to search for TS files.

        Returns:
            list: A list of paths to the found TS files.
        """
        ts_files = []
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".ts"):
                    ts_path = os.path.join(root, file)
                    if "Program Files" not in ts_path and "VS-Code" not in ts_path and "vscode" not in ts_path and "AppData" not in ts_path and "CrossDevice" not in ts_path:
                        ts_files.append(ts_path)
        return ts_files
    
    def convert_ts_to_mp4(self, ts_file, mp4_file):
        """
        Converts a TS file to MP4 format using FFmpeg.

        Parameters:
            ts_file (str): The path of the TS file to convert.
            mp4_file (str): The path to save the converted MP4 file.

        Returns:
            tuple: A tuple containing a boolean indicating the success of the conversion and an error message (if any).
        """
        try:
            ffmpeg_path = r"ffmpeg.exe"
            process = (
                ffmpeg
                .input(ts_file)
                .output(mp4_file, vcodec='copy', **{"y": None, "loglevel": "quiet"})  # 'y' = overwrite, 'loglevel' = quiet
                .compile(cmd=ffmpeg_path)  # Get the raw command
            )
            # Suppress console window on Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # Run using subprocess.Popen
            proc = subprocess.Popen(process, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()  # Ensures it completes before moving forward
            return True, None
        except RuntimeError as e:
            self.update_output_box(f"Error converting {ts_file}: {e}")
            return False, str(e)
    
    def move_ts_file(self, ts_file, backup_folder):
        """
        Moves a TS file to the backup folder.

        Parameters:
            ts_file (str): The path of the TS file to move.
            backup_folder (str): The path of the backup folder.

        Returns:
            None
        """
        relative_path = os.path.relpath(ts_file, self.input_folder.get())
        backup_path = os.path.join(backup_folder, relative_path)
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        os.rename(ts_file, backup_path)
    
    def load_log(self, log_file):
        """
        Loads the conversion log from an Excel file.

        Parameters:
            log_file (str): The path of the log file.

        Returns:
            dict: A dictionary representing the log data.
        """
        if os.path.exists(log_file):
            return pd.read_csv(log_file).to_dict(orient = 'index')
        return {}
    
    def update_log(self, log_file, data):
        """
        Updates the conversion log in the Excel file.

        Parameters:
            log_file (str): The path of the log file.
            data (dict): The updated log data.

        Returns:
            None
        """
        df = pd.DataFrame.from_dict(data, orient='index')
        df.reset_index(drop=True, inplace=True)
        df.to_csv(log_file, index=False)
    
    def update_progress(self, current, total):
        """
        Updates the progress bar.

        Parameters:
            current (int): The current progress value.
            total (int): The total progress value.

        Returns:
            None
        """
        if total == 0:
            progress = 100
        elif current == 0:
            progress = 1
        else:
            progress = (current / total) * 100
        
        self.root.after(0, self.progress.config, {'value': progress})  # Update progress bar
    
    def update_output_box(self, message):
        """
        Updates the output box console with a message.

        Parameters:
            message (str): The message to display.

        Returns:
            None
        """
        self.root.after(0, self.output_box.insert, tk.END, message + "\n")
    
    def open_log_folder(self):
        """
        Executes on Log Folder button click and opens the directory with log file and backups.

        Parameters:
            None

        Returns:
            None
        """
        os.startfile(os.path.join(self.input_folder.get(), 'TS_to_MP4_Logs'))
        
    def back_to_home(self):
        """
        Executes on Back to Home button click and refreshes the app window.

        Parameters:
            None

        Returns:
            None
        """
        self.__init__(self.root)
        
    def show_help(self):
        """
        Executes on Help button click and displays the README.md file in a new window.

        Parameters:
            None

        Returns:
            None
        """
        help_window = tk.Toplevel()
        help_window.title("Help")
        help_window.geometry("600x400")
        text_area = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=("Arial", 10))
        text_area.config(bg='cyan4', fg='white')
        text_area.pack(expand=True, fill="both")
        
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md'), "r", encoding="utf-8") as file:
                text_area.insert(tk.END, file.read())
        except FileNotFoundError:
            text_area.insert(tk.END, "README.md not found!")

        text_area.config(state="disabled")  # Make text read-only
    
    def show_about(self):
        """
        Executes on About button click and displays the version_info.txt file in a new window.

        Parameters:
            None

        Returns:
            None
        """
        help_window = tk.Toplevel()
        help_window.title("About")
        help_window.geometry("600x400")
        text_area = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=("Arial", 10))
        text_area.config(bg='cyan4', fg='white')
        text_area.pack(expand=True, fill="both")

        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version_info.txt'), "r", encoding="utf-8") as file:
                text_area.insert(tk.END, file.read())
        except FileNotFoundError:
            text_area.insert(tk.END, "version_info.txt not found!")

        text_area.config(state="disabled")  # Make text read-only

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap(default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TS2MP4Converter_icon.ico'))
    app = TSConverterApp(root)
    root.mainloop()
