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
            
            # Support multiple files
            self.files = []  # list of absolute file paths
            self.strength = 2
            self.format = "png"
            
            self.setup_ui()
        except Exception as e:
            print(f"Error initializing: {e}")
            input("Press Enter to exit...")
        
    def setup_ui(self):
        title_label = tk.Label(self.root, text="Normal Map Generator", font=("Segoe UI", 18, "bold"), fg="#2c3e50")
        title_label.pack(pady=(20, 30))

        file_frame = tk.Frame(self.root, relief="solid", bd=1, bg="#f8f9fa")
        file_frame.pack(pady=20, padx=30, fill="x")

        tk.Label(file_frame, text="Browse Files", font=("Segoe UI", 11), fg="#34495e", bg="#f8f9fa").pack(pady=(15, 10))

        select_btn = tk.Button(
            file_frame,
            text="📁 Browse Files",
            command=self.select_file,
            width=15,
            height=1,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            activebackground="#2980b9",
            activeforeground="white",
            cursor="hand2",
        )
        select_btn.pack(pady=(0, 10))

        self.path_label = tk.Label(
            file_frame,
            text="No file selected",
            wraplength=400,
            bg="white",
            relief="solid",
            height=2,
            font=("Segoe UI", 9),
            fg="#7f8c8d",
            bd=1,
        )
        self.path_label.pack(pady=(0, 15), padx=15, fill="x")

        # Setup drag and drop
        self.setup_drag_drop(file_frame)

        controls_frame = tk.Frame(self.root, bg="#ecf0f1")
        controls_frame.pack(pady=20, padx=30, fill="x")

        strength_frame = tk.Frame(controls_frame, bg="#ecf0f1")
        strength_frame.pack(side="left", padx=20)

        tk.Label(strength_frame, text="Strength:", font=("Segoe UI", 10, "bold"), bg="#ecf0f1", fg="#2c3e50").pack()
        self.strength_var = tk.StringVar(value="2")
        strength_combo = ttk.Combobox(
            strength_frame,
            textvariable=self.strength_var,
            values=[str(i) for i in range(1, 11)],
            width=8,
            state="readonly",
        )
        strength_combo.pack(pady=5)
        strength_combo.bind('<<ComboboxSelected>>', self.update_strength)

        format_frame = tk.Frame(controls_frame, bg="#ecf0f1")
        format_frame.pack(side="right", padx=20)

        tk.Label(format_frame, text="Format:", font=("Segoe UI", 10, "bold"), bg="#ecf0f1", fg="#2c3e50").pack()
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            values=["png", "exr"],
            width=8,
            state="readonly",
        )
        format_combo.pack(pady=5)
        format_combo.bind('<<ComboboxSelected>>', self.update_format)

        self.run_btn = tk.Button(
            self.root,
            text="Generate Normal Map",
            command=self.run_script,
            width=20,
            height=2,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            bd=0,
            activebackground="#229954",
            activeforeground="white",
            cursor="hand2",
            state="disabled",
        )
        self.run_btn.pack(pady=20)

        threading.Thread(target=self.download_repo, daemon=True).start()
        
    def select_file(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tga"),
                ("All files", "*.*")
            ]
        )
        if file_paths:
            self.set_files(list(file_paths))
            
    def set_file_path(self, file_path):
        """Backward-compatible single-file setter."""
        self.set_files([file_path])

    def set_files(self, file_paths):
        # Normalize and filter valid image files
        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga')
        cleaned = []
        for p in file_paths:
            if not p:
                continue
            ap = os.path.abspath(p.strip().strip('{}'))
            if ap.lower().endswith(valid_extensions):
                cleaned.append(ap)
        self.files = cleaned
        if not self.files:
            self.path_label.config(text="No file selected", fg="#7f8c8d")
            self.run_btn.config(state="disabled")
            return
        # Update label
        if len(self.files) == 1:
            self.path_label.config(text=self.files[0], fg="#27ae60")
        else:
            first = self.files[0]
            more = len(self.files) - 1
            self.path_label.config(text=f"{first}\n+ {more} more file(s)…", fg="#27ae60")
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
            # Get dropped file path(s)
            paths = []
            try:
                # Robust parsing for Tcl/Tk list format: handles spaces with braces
                paths = list(self.root.tk.splitlist(event.data))
            except Exception:
                # Fallback: naive split
                paths = event.data.split()
            # Filter only valid image files and set
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga')
            selected = [p.strip().strip('{}') for p in paths if p.lower().endswith(valid_extensions)]
            if selected:
                self.set_files(selected)
            else:
                messagebox.showerror("Invalid File", "Please select valid image file(s).")
        
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
        if not self.files:
            return

        # Disable run button during processing
        self.run_btn.config(state="disabled")

        def _worker():
            script_path = os.path.join("BumpToNormalMap", "bumptonormalmap.py")
            if not os.path.exists(script_path):
                messagebox.showerror("Error", "Repository not found!")
                self.run_btn.config(state="normal")
                return

            script_full_path = os.path.abspath(script_path)
            successes = []
            failures = []

            for input_file_path in self.files:
                try:
                    input_file_path = os.path.abspath(input_file_path)
                    cmd = [sys.executable, script_full_path, input_file_path, str(self.strength), self.format]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        input_dir = os.path.dirname(input_file_path)
                        input_name = os.path.splitext(os.path.basename(input_file_path))[0]
                        output_name = f"{input_name}_N.{self.format}"
                        output_path = os.path.join(input_dir, output_name)
                        successes.append(output_path)
                    else:
                        failures.append(input_file_path)
                except Exception:
                    failures.append(input_file_path)

            # Show summary
            if successes and not failures:
                if len(successes) == 1:
                    messagebox.showinfo("Success", f"Normal map saved to:\n{successes[0]}")
                else:
                    messagebox.showinfo("Success", f"Generated {len(successes)} normal maps.")
            elif successes and failures:
                messagebox.showwarning(
                    "Partial Success",
                    f"Generated {len(successes)} normal map(s), {len(failures)} failed."
                )
            else:
                messagebox.showerror("Error", "Generation failed for all files.")

            # Re-enable run and keep selection
            self.run_btn.config(state="normal")

        # Run without blocking UI
        threading.Thread(target=_worker, daemon=True).start()
            
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
