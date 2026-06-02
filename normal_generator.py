import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    import ctypes
    ctypes.windll.user32.MessageBoxW(
        0,
        "Python tkinter no esta instalado.\nInstala Python desde python.org marcando 'tcl/tk'.",
        "Error - Normal Map Generator", 0x10
    )
    sys.exit(1)

import subprocess
import urllib.request
import zipfile
import shutil
import threading

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


def _show_error(msg):
    try:
        messagebox.showerror("Error - Normal Map Generator", msg)
    except Exception:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "Error - Normal Map Generator", 0x10)


class NormalGenerator:
    def __init__(self):
        self.root = None
        try:
            if DND_AVAILABLE:
                self.root = TkinterDnD.Tk()
            else:
                self.root = tk.Tk()

            self.root.title("Normal Map Generator")
            self.root.minsize(460, 300)
            self.root.configure(bg="#ecf0f1")

            self.files = []
            self.strength = 2
            self.format = "jpg"

            self.setup_ui()
        except Exception as e:
            _show_error(f"Error al iniciar:\n{e}")

    def setup_ui(self):
        content = tk.Frame(self.root, bg="#ecf0f1")
        content.pack(fill="x", pady=(6, 0))

        tk.Label(content, text="Normal Map Generator", font=("Segoe UI", 15, "bold"),
                 fg="#2c3e50", bg="#ecf0f1").pack(pady=(8, 6))

        file_frame = tk.Frame(content, relief="solid", bd=1, bg="#f8f9fa")
        file_frame.pack(pady=6, padx=12, fill="x")

        tk.Label(file_frame, text="Drag image(s) here or browse",
                 font=("Segoe UI", 10), fg="#34495e", bg="#f8f9fa").pack(pady=(8, 6))

        buttons = tk.Frame(file_frame, bg="#f8f9fa")
        buttons.pack()
        tk.Button(buttons, text="Browse Files", command=self.select_file, width=14,
                  bg="#3498db", fg="white", font=("Segoe UI", 9), relief="flat", bd=0,
                  activebackground="#2980b9", activeforeground="white",
                  cursor="hand2").pack(side="left", padx=4, pady=(0, 6))
        tk.Button(buttons, text="Select Folder", command=self.select_folder, width=14,
                  bg="#1abc9c", fg="white", font=("Segoe UI", 9), relief="flat", bd=0,
                  activebackground="#16a085", activeforeground="white",
                  cursor="hand2").pack(side="left", padx=4, pady=(0, 6))

        self.path_label = tk.Label(file_frame, text="No file selected", wraplength=420,
                                   bg="white", relief="solid", font=("Segoe UI", 9),
                                   fg="#7f8c8d", bd=1, anchor="w", padx=6)
        self.path_label.pack(pady=(0, 8), padx=10, fill="x")

        self.setup_drag_drop(file_frame)

        controls = tk.Frame(content, bg="#ecf0f1")
        controls.pack(pady=6, padx=12, fill="x")

        self.strength_var = tk.StringVar(value="2")
        tk.Label(controls, text="Strength", font=("Segoe UI", 9, "bold"),
                 bg="#ecf0f1", fg="#2c3e50").pack(side="left", padx=(0, 6))
        sc = ttk.Combobox(controls, textvariable=self.strength_var,
                          values=[str(i) for i in range(1, 11)], width=6, state="readonly")
        sc.pack(side="left")
        sc.bind('<<ComboboxSelected>>', self.update_strength)

        tk.Label(controls, text="Format", font=("Segoe UI", 9, "bold"),
                 bg="#ecf0f1", fg="#2c3e50").pack(side="left", padx=(16, 6))
        self.format_var = tk.StringVar(value="jpg")
        fc = ttk.Combobox(controls, textvariable=self.format_var,
                          values=["png", "jpg", "exr"], width=6, state="readonly")
        fc.pack(side="left")
        fc.bind('<<ComboboxSelected>>', self.update_format)

        footer = tk.Frame(self.root, bg="#ecf0f1")
        footer.pack(side="bottom", fill="x")
        self.run_btn = tk.Button(footer, text="Generate Normal Map", command=self.run_script,
                                 height=1, bg="#27ae60", fg="white",
                                 font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                                 activebackground="#229954", activeforeground="white",
                                 cursor="hand2", state="disabled")
        self.run_btn.pack(padx=12, pady=8, fill="x")

        # Download repo only if not already present
        threading.Thread(target=self.ensure_repo, daemon=True).start()

    def select_file(self):
        paths = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tga"),
                       ("All files", "*.*")]
        )
        if paths:
            self.set_files(list(paths))

    def set_file_path(self, file_path):
        self.set_files([file_path])

    def set_files(self, file_paths):
        valid_ext = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga')
        cleaned = []
        for p in file_paths:
            if not p:
                continue
            ap = os.path.abspath(p.strip().strip('{}'))
            fname = os.path.basename(ap).lower()
            if ap.lower().endswith(valid_ext) and not fname.startswith('_normal'):
                cleaned.append(ap)
        self.files = cleaned

        if not self.files:
            self.path_label.config(text="No file selected", fg="#7f8c8d")
            self.run_btn.config(state="disabled")
            return

        if len(self.files) == 1:
            self.path_label.config(text=self.files[0], fg="#27ae60")
        else:
            more = len(self.files) - 1
            self.path_label.config(text=f"{self.files[0]}\n+ {more} more file(s)", fg="#27ae60")
        self.run_btn.config(state="normal")

    def select_folder(self):
        folder = filedialog.askdirectory(title="Selecciona una carpeta")
        if folder:
            self.set_files(self.get_files_from_folder(folder))

    def get_files_from_folder(self, folder_path):
        valid_ext = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga')
        result = []
        for root, _, files in os.walk(folder_path):
            for f in files:
                fl = f.lower()
                if fl.startswith('_normal') or fl.endswith('.uasset'):
                    continue
                if fl.endswith(valid_ext):
                    result.append(os.path.abspath(os.path.join(root, f)))
        return result

    def setup_drag_drop(self, widget):
        if not DND_AVAILABLE:
            return

        def on_enter(_e): widget.config(bg="#e8f4fd")
        def on_leave(_e): widget.config(bg="#f8f9fa")
        def on_drop(event):
            widget.config(bg="#f8f9fa")
            try:
                paths = list(self.root.tk.splitlist(event.data))
            except Exception:
                paths = event.data.split()
            valid_ext = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tga')
            selected = [p.strip().strip('{}') for p in paths if p.lower().endswith(valid_ext)]
            if selected:
                self.set_files(selected)
            else:
                messagebox.showerror("Invalid File", "Please drop valid image files.")

        try:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<DropEnter>>', on_enter)
            widget.dnd_bind('<<DropLeave>>', on_leave)
            widget.dnd_bind('<<Drop>>', on_drop)
        except Exception:
            pass

    def update_strength(self, _e):
        self.strength = int(self.strength_var.get())

    def update_format(self, _e):
        self.format = self.format_var.get()

    def ensure_repo(self):
        """Download BumpToNormalMap only if not already present."""
        target_dir = os.path.join(SCRIPT_DIR, "BumpToNormalMap")
        script = os.path.join(target_dir, "bumptonormalmap.py")

        if os.path.exists(script):
            # Already there — just make sure deps are installed
            self._install_deps()
            return

        try:
            repo_url = "https://github.com/MircoWerner/BumpToNormalMap/archive/refs/heads/main.zip"
            zip_path = os.path.join(SCRIPT_DIR, "repo.zip")

            urllib.request.urlretrieve(repo_url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(SCRIPT_DIR)

            extracted = os.path.join(SCRIPT_DIR, "BumpToNormalMap-main")
            if os.path.exists(extracted):
                shutil.move(extracted, target_dir)

            try:
                os.remove(zip_path)
            except Exception:
                pass

            self._install_deps()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"No se pudo descargar el repositorio:\n{e}"))

    def _install_deps(self):
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "numpy", "opencv-python"],
                check=True, capture_output=True
            )
        except Exception:
            pass

    def run_script(self):
        if not self.files:
            return
        self.run_btn.config(state="disabled")

        def _worker():
            script_path = os.path.join(SCRIPT_DIR, "BumpToNormalMap", "bumptonormalmap.py")
            if not os.path.exists(script_path):
                messagebox.showerror("Error", "Repositorio no encontrado. Verifica tu conexion a internet.")
                self.run_btn.config(state="normal")
                return

            successes, failures = [], []

            for input_path in self.files:
                try:
                    input_path = os.path.abspath(input_path)
                    sel_fmt = self.format
                    script_fmt = 'png' if sel_fmt == 'jpg' else sel_fmt
                    cmd = [sys.executable, script_path, input_path, str(self.strength), script_fmt]
                    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

                    if result.returncode == 0:
                        out = result.stdout or ""
                        output_path = None
                        if "Wrote '" in out:
                            try:
                                output_path = out.split("Wrote '", 1)[1].split("'", 1)[0]
                            except Exception:
                                pass
                        if not output_path:
                            base = os.path.splitext(os.path.basename(input_path))[0]
                            output_path = os.path.join(os.path.dirname(input_path),
                                                       f"{base}_normal.{script_fmt}")

                        final = output_path
                        if sel_fmt == 'jpg':
                            try:
                                try:
                                    from PIL import Image
                                except ImportError:
                                    subprocess.run([sys.executable, "-m", "pip", "install", "pillow"],
                                                   check=True, capture_output=True)
                                    from PIL import Image
                                jpg = os.path.splitext(output_path)[0] + ".jpg"
                                with Image.open(output_path) as im:
                                    im.convert('RGB').save(jpg, 'JPEG', quality=95)
                                if os.path.exists(output_path):
                                    os.remove(output_path)
                                final = jpg
                            except Exception:
                                final = output_path

                        successes.append(final)
                    else:
                        failures.append(input_path)
                except Exception:
                    failures.append(input_path)

            if successes and not failures:
                msg = f"Guardado:\n{successes[0]}" if len(successes) == 1 \
                      else f"Generados {len(successes)} normal maps."
                messagebox.showinfo("Exito", msg)
            elif successes:
                messagebox.showwarning("Parcial", f"{len(successes)} ok, {len(failures)} fallaron.")
            else:
                messagebox.showerror("Error", "Fallo la generacion.")

            self.run_btn.config(state="normal")

        threading.Thread(target=_worker, daemon=True).start()

    def run(self):
        if self.root is None:
            return
        self.root.lift()
        self.root.focus_force()
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = NormalGenerator()
        app.run()
    except Exception as e:
        _show_error(f"No se pudo iniciar:\n{e}")

# https://github.com/JuanMaldini/Normal_creator
