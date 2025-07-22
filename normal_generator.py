import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import sys
import urllib.request
import zipfile
import shutil

class NormalGenerator:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("Normal Generator")
            self.root.geometry("500x400")
            
            self.file_path = ""
            self.strength = 2
            self.format = "png"
            
            self.setup_ui()
        except Exception as e:
            print(f"Error initializing: {e}")
            input("Press Enter to exit...")
        
    def setup_ui(self):
        # Title
        tk.Label(self.root, text="Normal Generator", font=("Arial", 16, "bold")).pack(pady=15)
        
        # Update button
        update_btn = tk.Button(self.root, text="📥 Update Repository", 
                              command=self.download_repo, width=25, height=2,
                              bg="#28a745", fg="white", font=("Arial", 10))
        update_btn.pack(pady=10)
        
        # File selection area
        file_frame = tk.Frame(self.root, relief="solid", bd=2)
        file_frame.pack(pady=15, padx=20, fill="x")
        
        tk.Label(file_frame, text="Select Image File:", font=("Arial", 10, "bold")).pack(pady=5)
        
        select_btn = tk.Button(file_frame, text="📁 Browse File", 
                              command=self.select_file, width=20)
        select_btn.pack(pady=5)
        
        # File path display
        self.path_label = tk.Label(file_frame, text="No file selected", 
                                  wraplength=400, bg="white", relief="sunken", 
                                  height=3, font=("Arial", 9))
        self.path_label.pack(pady=5, padx=10, fill="x")
        
        # Controls frame
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=15)
        
        # Strength selection
        strength_frame = tk.Frame(controls_frame)
        strength_frame.pack(side="left", padx=20)
        
        tk.Label(strength_frame, text="Strength:", font=("Arial", 10, "bold")).pack()
        self.strength_var = tk.StringVar(value="2")
        strength_combo = ttk.Combobox(strength_frame, textvariable=self.strength_var, 
                                     values=[str(i) for i in range(1, 11)], width=10, state="readonly")
        strength_combo.pack(pady=5)
        strength_combo.bind('<<ComboboxSelected>>', self.update_strength)
        
        # Format selection
        format_frame = tk.Frame(controls_frame)
        format_frame.pack(side="right", padx=20)
        
        tk.Label(format_frame, text="Format:", font=("Arial", 10, "bold")).pack()
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, 
                                   values=["png", "exr"], width=10, state="readonly")
        format_combo.pack(pady=5)
        format_combo.bind('<<ComboboxSelected>>', self.update_format)
        
        # Run button
        self.run_btn = tk.Button(self.root, text="🚀 Generate Normal Map", 
                               command=self.run_script, width=25, height=2,
                               bg="#0078d7", fg="white", font=("Arial", 12, "bold"),
                               state="disabled")
        self.run_btn.pack(pady=20)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tga"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_path = file_path
            self.path_label.config(text=file_path)
            self.run_btn.config(state="normal")
            
    def update_strength(self, event):
        self.strength = int(self.strength_var.get())
        
    def update_format(self, event):
        self.format = self.format_var.get()
        
    def download_repo(self):
        try:
            repo_url = "https://github.com/MircoWerner/BumpToNormalMap/archive/refs/heads/main.zip"
            target_dir = "BumpToNormalMap"
            output_dir = "output"
            
            # Create output directory
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            
            # Download and extract if not exists
            if not os.path.exists(target_dir):
                messagebox.showinfo("Downloading", "Downloading repository... Please wait.")
                
                # Download zip file
                zip_path = "repo.zip"
                urllib.request.urlretrieve(repo_url, zip_path)
                
                # Extract zip
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall()
                
                # Rename extracted folder
                if os.path.exists("BumpToNormalMap-main"):
                    shutil.move("BumpToNormalMap-main", target_dir)
                
                # Clean up
                os.remove(zip_path)
                
                messagebox.showinfo("Success", "Repository downloaded successfully!")
            else:
                messagebox.showinfo("Info", "Repository already exists!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")
            
    def run_script(self):
        if not self.file_path:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
            
        script_path = os.path.join("BumpToNormalMap", "bumptonormalmap.py")
        
        if not os.path.exists(script_path):
            messagebox.showerror("Error", "Please download repository first!")
            return
            
        try:
            # Create output filename
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            output_path = os.path.join("output", f"{base_name}_normal.{self.format}")
            
            # Run the script
            cmd = [sys.executable, script_path, self.file_path, str(self.strength), self.format]
            
            messagebox.showinfo("Processing", "Generating normal map... Please wait.")
            
            result = subprocess.run(cmd, cwd="BumpToNormalMap", capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", f"Normal map generated successfully!\nCheck the BumpToNormalMap folder for output.")
            else:
                messagebox.showerror("Error", f"Script failed:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Execution failed: {str(e)}")
            
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
