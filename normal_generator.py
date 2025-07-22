import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import sys
import urllib.request
import zipfile
import shutil
import threading

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

class NormalGenerator:
    def __init__(self):
        try:
            if DND_AVAILABLE:
                self.root = TkinterDnD.Tk()
            else:
                self.root = tk.Tk()
                
            self.root.title("Normal Map Generator")
            self.root.geometry("480x420")
            self.root.configure(bg="#ecf0f1")
            
            self.file_path = ""
            self.strength = 2
            self.format = "png"
            
            self.setup_ui()
        except Exception as e:
            print(f"Error initializing: {e}")
            input("Press Enter to exit...")
        
    def setup_ui(self):
        title_label = tk.Label(self.root, text="Normal Map Generator", 
                              font=("Segoe UI", 18, "bold"), fg="#2c3e50")
        title_label.pack(pady=(20, 30))
        
        file_frame = tk.Frame(self.root, relief="solid", bd=1, bg="#f8f9fa")
        file_frame.pack(pady=20, padx=30, fill="x")
        
        tk.Label(file_frame, text="Drag image here or browse", 
                font=("Segoe UI", 11), fg="#34495e", bg="#f8f9fa").pack(pady=(15, 10))
        
        select_btn = tk.Button(file_frame, text="📁 Browse File", 
                              command=self.select_file, width=15, height=1,
                              bg="#3498db", fg="white", font=("Segoe UI", 10),
                              relief="flat", bd=0, activebackground="#2980b9",
                              activeforeground="white", cursor="hand2")
        select_btn.pack(pady=(0, 10))
        
        self.path_label = tk.Label(file_frame, text="No file selected", 
                                  wraplength=400, bg="white", relief="solid", 
                                  height=2, font=("Segoe UI", 9), fg="#7f8c8d",
                                  bd=1)
        self.path_label.pack(pady=(0, 15), padx=15, fill="x")
        
        # Setup drag and drop
        self.setup_drag_drop(file_frame)
        
        controls_frame = tk.Frame(self.root, bg="#ecf0f1")
        controls_frame.pack(pady=20, padx=30, fill="x")
        
        strength_frame = tk.Frame(controls_frame, bg="#ecf0f1")
        strength_frame.pack(side="left", padx=20)
        
        tk.Label(strength_frame, text="Strength:", font=("Segoe UI", 10, "bold"), 
                bg="#ecf0f1", fg="#2c3e50").pack()
        self.strength_var = tk.StringVar(value="2")
        strength_combo = ttk.Combobox(strength_frame, textvariable=self.strength_var, 
                                     values=[str(i) for i in range(1, 11)], width=8, state="readonly")
        strength_combo.pack(pady=5)
        strength_combo.bind('<<ComboboxSelected>>', self.update_strength)
        
        format_frame = tk.Frame(controls_frame, bg="#ecf0f1")
        format_frame.pack(side="right", padx=20)
        
        tk.Label(format_frame, text="Format:", font=("Segoe UI", 10, "bold"), 
                bg="#ecf0f1", fg="#2c3e50").pack()
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, 
                                   values=["png", "exr"], width=8, state="readonly")
        format_combo.pack(pady=5)
        format_combo.bind('<<ComboboxSelected>>', self.update_format)
        
        self.run_btn = tk.Button(self.root, text="Generate Normal Map", 
                               command=self.run_script, width=20, height=2,
                               bg="#27ae60", fg="white", font=("Segoe UI", 12, "bold"),
                               relief="flat", bd=0, activebackground="#229954",
                               activeforeground="white", cursor="hand2",
                               state="disabled")
        self.run_btn.pack(pady=20)
        
        threading.Thread(target=self.download_repo, daemon=True).start()
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tga"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.set_file_path(file_path)
            
    def set_file_path(self, file_path):
        self.file_path = file_path
        # Show full absolute path
        absolute_path = os.path.abspath(file_path)
        self.path_label.config(text=absolute_path, fg="#27ae60")
        self.run_btn.config(state="normal")
        
    def setup_drag_drop(self, widget):
        """Setup drag and drop functionality"""
        if not DND_AVAILABLE:
            return
            
        def on_drag_enter(event):
            widget.config(bg="#e8f4fd")
            
        def on_drag_leave(event):
            widget.config(bg="#f8f9fa")
            
        def on_drop(event):
            widget.config(bg="#f8f9fa")
            # Get the dropped file path
            files = event.data.split()
            if files:
                file_path = files[0].strip('{}')  # Remove braces if present
                # Validate if it's an image file
                valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga')
                if file_path.lower().endswith(valid_extensions):
                    self.set_file_path(file_path)
                else:
                    messagebox.showerror("Invalid File", "Please select a valid image file.")
        
        # Enable drag and drop if available
        try:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<DropEnter>>', on_drag_enter)
            widget.dnd_bind('<<DropLeave>>', on_drag_leave)
            widget.dnd_bind('<<Drop>>', on_drop)
        except:
            pass
        
    def update_strength(self, event):
        self.strength = int(self.strength_var.get())
        
    def update_format(self, event):
        self.format = self.format_var.get()
        
    def download_repo(self):
        try:
            repo_url = "https://github.com/MircoWerner/BumpToNormalMap/archive/refs/heads/main.zip"
            target_dir = "BumpToNormalMap"
            
            if not os.path.exists(target_dir):
                zip_path = "repo.zip"
                urllib.request.urlretrieve(repo_url, zip_path)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall()
                
                if os.path.exists("BumpToNormalMap-main"):
                    shutil.move("BumpToNormalMap-main", target_dir)
                
                os.remove(zip_path)
                
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "numpy", "opencv-python"], 
                                 check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    pass
                
        except Exception as e:
            pass





            
            
    def run_script(self):
        if not self.file_path:
            return
            
        script_path = os.path.join("BumpToNormalMap", "bumptonormalmap.py")
        
        if not os.path.exists(script_path):
            messagebox.showerror("Error", "Repository not found!")
            return
            
        try:
            script_full_path = os.path.abspath(script_path)
            input_file_path = os.path.abspath(self.file_path)
            
            cmd = [sys.executable, script_full_path, input_file_path, str(self.strength), self.format]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                input_dir = os.path.dirname(input_file_path)
                input_name = os.path.splitext(os.path.basename(input_file_path))[0]
                output_name = f"{input_name}_N.{self.format}"
                output_path = os.path.join(input_dir, output_name)
                
                messagebox.showinfo("Success", f"Normal map saved to:\n{output_path}")
            else:
                messagebox.showerror("Error", "Generation failed")
                
        except Exception as e:
            messagebox.showerror("Error", "Execution failed")
            
    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error running application: {e}")
            input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        app = NormalGenerator()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        input("Press Enter to exit...")
