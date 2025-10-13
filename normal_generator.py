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
            # Compact: let Tk auto-size; set a modest minimum
            self.root.minsize(460, 300)
            self.root.configure(bg="#ecf0f1")
            
            # Support multiple files
            self.files = []  # list of absolute file paths
            self.strength = 2
            self.format = "jpg"
            
            self.setup_ui()
        except Exception as e:
            print(f"Error initializing: {e}")
            input("Press Enter to exit...")
        
    def setup_ui(self):
        # Main content that expands
        content = tk.Frame(self.root, bg="#ecf0f1")
        content.pack(fill="x", pady=(6, 0))

        title = tk.Label(content, text="Normal Map Generator", font=("Segoe UI", 15, "bold"), fg="#2c3e50", bg="#ecf0f1")
        title.pack(pady=(8, 6))

        # File area (DnD target)
        file_frame = tk.Frame(content, relief="solid", bd=1, bg="#f8f9fa")
        file_frame.pack(pady=6, padx=12, fill="x")

        tk.Label(file_frame, text="Drag image(s) here or browse", font=("Segoe UI", 10), fg="#34495e", bg="#f8f9fa").pack(pady=(8, 6))

        buttons = tk.Frame(file_frame, bg="#f8f9fa")
        buttons.pack()
        tk.Button(buttons, text="📁 Browse Files", command=self.select_file, width=14, bg="#3498db", fg="white",
                 font=("Segoe UI", 9), relief="flat", bd=0, activebackground="#2980b9", activeforeground="white",
                 cursor="hand2").pack(side="left", padx=4, pady=(0, 6))
        tk.Button(buttons, text="📂 Select Folder", command=self.select_folder, width=14, bg="#1abc9c", fg="white",
                 font=("Segoe UI", 9), relief="flat", bd=0, activebackground="#16a085", activeforeground="white",
                 cursor="hand2").pack(side="left", padx=4, pady=(0, 6))

        self.path_label = tk.Label(file_frame, text="No file selected", wraplength=420, bg="white", relief="solid",
                                   height=1, font=("Segoe UI", 9), fg="#7f8c8d", bd=1, anchor="w", padx=6)
        self.path_label.pack(pady=(0, 8), padx=10, fill="x")

        # Enable drag & drop on the file frame
        self.setup_drag_drop(file_frame)

        # Controls
        controls = tk.Frame(content, bg="#ecf0f1")
        controls.pack(pady=6, padx=12, fill="x")

        # Compact inline controls
        self.strength_var = tk.StringVar(value="2")
        tk.Label(controls, text="Strength", font=("Segoe UI", 9, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(side="left", padx=(0,6))
        strength_combo = ttk.Combobox(controls, textvariable=self.strength_var, values=[str(i) for i in range(1, 11)], width=6, state="readonly")
        strength_combo.pack(side="left")
        strength_combo.bind('<<ComboboxSelected>>', self.update_strength)

        tk.Label(controls, text="Format", font=("Segoe UI", 9, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(side="left", padx=(16,6))
        self.format_var = tk.StringVar(value="jpg")
        format_combo = ttk.Combobox(controls, textvariable=self.format_var, values=["png", "jpg", "exr"], width=6, state="readonly")
        format_combo.pack(side="left")
        format_combo.bind('<<ComboboxSelected>>', self.update_format)

        # Footer with primary action pinned to bottom
        footer = tk.Frame(self.root, bg="#ecf0f1")
        footer.pack(side="bottom", fill="x")
        self.run_btn = tk.Button(footer, text="Generate Normal Map", command=self.run_script, height=1, bg="#27ae60",
                                 fg="white", font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                                 activebackground="#229954", activeforeground="white", cursor="hand2", state="disabled")
        self.run_btn.pack(padx=12, pady=8, fill="x")

        # Download repo in background (keeps UI responsive)
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
            # Excluir .uasset y archivos con prefijo _normal
            fname = os.path.basename(ap)
            if ap.lower().endswith(valid_extensions) and not ap.lower().endswith('.uasset') and not fname.lower().startswith('_normal'):
                cleaned.append(ap)
        self.files = cleaned

        # Minimal UX: no popups here; update label only
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

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Selecciona una carpeta")
        if folder_path:
            files = self.get_files_from_folder(folder_path)
            self.set_files(files)

    def get_files_from_folder(self, folder_path):
        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga')
        result = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.uasset'):
                    continue
                if file.lower().startswith('_normal'):
                    continue
                if file.lower().endswith(valid_extensions):
                    result.append(os.path.abspath(os.path.join(root, file)))
        return result
        
    def setup_drag_drop(self, widget):
        """Setup drag and drop functionality"""
        if not DND_AVAILABLE:
            return

        def on_drag_enter(_event):
            widget.config(bg="#e8f4fd")

        def on_drag_leave(_event):
            widget.config(bg="#f8f9fa")

        def on_drop(event):
            widget.config(bg="#f8f9fa")
            # Get dropped file path(s)
            try:
                paths = list(self.root.tk.splitlist(event.data))
            except Exception:
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
        except Exception:
            pass
        
    def update_strength(self, event):
        self.strength = int(self.strength_var.get())
        
    def update_format(self, event):
        self.format = self.format_var.get()
        
    def download_repo(self):
        try:
            repo_url = "https://github.com/MircoWerner/BumpToNormalMap/archive/refs/heads/main.zip"
            target_dir = "BumpToNormalMap"
            
            # Always ensure a fresh copy: delete existing folder if present
            try:
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir, ignore_errors=True)
            except Exception:
                pass

            # Remove any previous zip artifact
            zip_path = "repo.zip"
            try:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
            except Exception:
                pass

            # Download fresh zip
            urllib.request.urlretrieve(repo_url, zip_path)
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall()
            
            # Rename extracted folder
            if os.path.exists("BumpToNormalMap-main"):
                shutil.move("BumpToNormalMap-main", target_dir)
            
            # Clean zip
            try:
                os.remove(zip_path)
            except Exception:
                pass
            
            # Ensure dependencies (silent)
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
                    selected_format = self.format
                    script_format = 'png' if selected_format == 'jpg' else selected_format
                    cmd = [sys.executable, script_full_path, input_file_path, str(self.strength), script_format]
                    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                    if result.returncode == 0:
                        # Try to read the written path from stdout
                        output_path = None
                        out = result.stdout or ""
                        marker = "Wrote '"
                        if marker in out:
                            try:
                                after = out.split(marker, 1)[1]
                                output_path = after.split("'", 1)[0]
                            except Exception:
                                output_path = None
                        if not output_path:
                            # Fallback to common naming '*_normal.ext'
                            input_dir = os.path.dirname(input_file_path)
                            input_name = os.path.splitext(os.path.basename(input_file_path))[0]
                            output_path = os.path.join(input_dir, f"{input_name}_normal.{script_format}")

                        final_path = output_path
                        if selected_format == 'jpg':
                            # Convert PNG -> JPG
                            try:
                                try:
                                    from PIL import Image  # type: ignore
                                except Exception:
                                    subprocess.run([sys.executable, "-m", "pip", "install", "pillow"], check=True, capture_output=True)
                                    from PIL import Image  # type: ignore
                                jpg_path = os.path.splitext(output_path)[0] + ".jpg"
                                with Image.open(output_path) as im:
                                    im.convert('RGB').save(jpg_path, 'JPEG', quality=95)
                                try:
                                    if script_format == 'png' and os.path.exists(output_path):
                                        os.remove(output_path)
                                except Exception:
                                    pass
                                final_path = jpg_path
                            except Exception:
                                final_path = output_path

                        successes.append(final_path)
                    else:
                        failures.append(input_file_path)
                except Exception:
                    failures.append(input_file_path)

            # Minimal summary
            if successes and not failures:
                if len(successes) == 1:
                    messagebox.showinfo("Success", f"Saved:\n{successes[0]}")
                else:
                    messagebox.showinfo("Success", f"Generated {len(successes)} normal maps.")
            elif successes and failures:
                messagebox.showwarning("Partial Success", f"Generated {len(successes)} file(s), {len(failures)} failed.")
            else:
                messagebox.showerror("Error", "Generation failed for all files.")

            # Re-enable run
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

#https://github.com/JuanMaldini/Normal_creator