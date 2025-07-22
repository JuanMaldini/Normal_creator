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
        # Auto-download repository on startup
        self.download_repo()
        
        # Title
        title_label = tk.Label(self.root, text="Normal Map Generator", 
                              font=("Segoe UI", 18, "bold"), fg="#2c3e50")
        title_label.pack(pady=(20, 30))
        
        # File selection area
        file_frame = tk.Frame(self.root, relief="solid", bd=1, bg="#f8f9fa")
        file_frame.pack(pady=20, padx=30, fill="x")
        
        tk.Label(file_frame, text="Drop image file here or browse", 
                font=("Segoe UI", 11), fg="#34495e", bg="#f8f9fa").pack(pady=(15, 10))
        
        select_btn = tk.Button(file_frame, text="📁 Browse File", 
                              command=self.select_file, width=15, height=1,
                              bg="#3498db", fg="white", font=("Segoe UI", 10),
                              relief="flat", bd=0, activebackground="#2980b9",
                              activeforeground="white", cursor="hand2")
        select_btn.pack(pady=(0, 10))
        
        # File path display
        self.path_label = tk.Label(file_frame, text="No file selected", 
                                  wraplength=400, bg="white", relief="flat", 
                                  height=2, font=("Segoe UI", 9), fg="#7f8c8d",
                                  bd=1, relief="solid")
        self.path_label.pack(pady=(0, 15), padx=15, fill="x")
        
        # Setup drag and drop
        self.setup_drag_drop(file_frame)
        
        # Controls frame
        controls_frame = tk.Frame(self.root, bg="#ecf0f1")
        controls_frame.pack(pady=20, padx=30, fill="x")
        
        # Strength selection
        strength_frame = tk.Frame(controls_frame, bg="#ecf0f1")
        strength_frame.pack(side="left", padx=20)
        
        tk.Label(strength_frame, text="Strength:", font=("Segoe UI", 10, "bold"), 
                bg="#ecf0f1", fg="#2c3e50").pack()
        self.strength_var = tk.StringVar(value="2")
        strength_combo = ttk.Combobox(strength_frame, textvariable=self.strength_var, 
                                     values=[str(i) for i in range(1, 11)], width=8, state="readonly")
        strength_combo.pack(pady=5)
        strength_combo.bind('<<ComboboxSelected>>', self.update_strength)
        
        # Format selection
        format_frame = tk.Frame(controls_frame, bg="#ecf0f1")
        format_frame.pack(side="right", padx=20)
        
        tk.Label(format_frame, text="Format:", font=("Segoe UI", 10, "bold"), 
                bg="#ecf0f1", fg="#2c3e50").pack()
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, 
                                   values=["png", "exr"], width=8, state="readonly")
        format_combo.pack(pady=5)
        format_combo.bind('<<ComboboxSelected>>', self.update_format)
        
        # Run button
        self.run_btn = tk.Button(self.root, text="Generate Normal Map", 
                               command=self.run_script, width=20, height=2,
                               bg="#27ae60", fg="white", font=("Segoe UI", 12, "bold"),
                               relief="flat", bd=0, activebackground="#229954",
                               activeforeground="white", cursor="hand2",
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
            self.execute_btn.config(state="normal")
            
    def update_strength(self, event):
        self.strength = int(self.strength_var.get())
        
    def update_format(self, event):
        self.format = self.format_var.get()
        
    def download_repo(self):
        try:
            repo_url = "https://github.com/MircoWerner/BumpToNormalMap/archive/refs/heads/main.zip"
            target_dir = "BumpToNormalMap"
            
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
                
                # Install required dependencies
                messagebox.showinfo("Installing", "Installing required dependencies (numpy, opencv-python)...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "numpy", "opencv-python"], 
                                 check=True, capture_output=True)
                    messagebox.showinfo("Success", "Repository downloaded and dependencies installed successfully!")
                except subprocess.CalledProcessError:
                    messagebox.showwarning("Warning", "Repository downloaded but dependency installation failed.\nPlease install manually: pip install numpy opencv-python")
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
            # Get absolute paths
            script_full_path = os.path.abspath(script_path)
            input_file_path = os.path.abspath(self.file_path)
            
            # Run the script from current working directory (not BumpToNormalMap)
            # This ensures the output will be saved in the same folder as the input image
            cmd = [sys.executable, script_full_path, input_file_path, str(self.strength), self.format]
            
            messagebox.showinfo("Processing", "Generating normal map... Please wait.")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Get the expected output path
                input_dir = os.path.dirname(input_file_path)
                input_name = os.path.splitext(os.path.basename(input_file_path))[0]
                output_name = f"{input_name}_normal.{self.format}"
                output_path = os.path.join(input_dir, output_name)
                
                messagebox.showinfo("Success", f"Normal map generated successfully!\nSaved to: {output_path}\n\nOutput:\n{result.stdout}")
            else:
                messagebox.showerror("Error", f"Script failed:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Execution failed: {str(e)}")
            
    def execute_command(self):
        if not self.file_path:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
            
        script_path = os.path.join("BumpToNormalMap", "bumptonormalmap.py")
        
        if not os.path.exists(script_path):
            messagebox.showerror("Error", "Please download repository first!")
            return
            
        try:
            # Get absolute paths
            script_full_path = os.path.abspath(script_path)
            input_file_path = os.path.abspath(self.file_path)
            
            # Build the command with absolute paths
            cmd = f'python "{script_full_path}" "{input_file_path}" {self.strength} {self.format}'
            
            # Get the expected output path for display
            input_dir = os.path.dirname(input_file_path)
            input_name = os.path.splitext(os.path.basename(input_file_path))[0]
            output_name = f"{input_name}_normal.{self.format}"
            output_path = os.path.join(input_dir, output_name)
            
            # Show the command that will be executed
            command_info = f"Executing command:\n\n{cmd}\n\nOutput will be saved to:\n{output_path}\n\nProceed?"
            
            if messagebox.askyesno("Execute Command", command_info):
                # Execute the command from current working directory
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"Command executed successfully!\nSaved to: {output_path}\n\nOutput:\n{result.stdout}")
                else:
                    messagebox.showerror("Error", f"Command failed!\n\nError:\n{result.stderr}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Command execution failed: {str(e)}")
            
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
