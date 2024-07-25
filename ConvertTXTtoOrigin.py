import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def process_file(file_path, output_folder):
    # Read the file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Find the start of the data
    for i, line in enumerate(lines):
        if line.startswith('Wave   ;Sample   ;Dark     ;Reference;Transmittance'):
            start_idx = i + 2  # Data starts after the header and units line
            break
    
    # Read the data into a DataFrame
    df = pd.read_csv(file_path, sep=';', skiprows=start_idx, names=["Wave", "Sample", "Dark", "Reference", "Transmittance"])
    
    # Extract only the columns "Wave" and "Transmittance"
    df_short = df[['Wave', 'Transmittance']]
    
    # Replace semicolons with spaces in all string columns
    df_short = df_short.astype(str).apply(lambda x: x.str.replace(';', ' ', regex=False))
    
    # Save to a new file in the output folder
    new_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_short.txt"
    new_file_path = os.path.join(output_folder, new_filename)
    df_short.to_csv(new_file_path, sep=' ', index=False)
    print(f"Processed {file_path} -> {new_file_path}")

def process_all_files_in_folder(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith('.TXT'):  # Process only .TXT files
            file_path = os.path.join(input_folder, filename)
            process_file(file_path, output_folder)
    messagebox.showinfo("Success", "Processing complete!")

def select_input_folder():
    folder_selected = filedialog.askdirectory()
    input_folder_var.set(folder_selected)

def select_output_folder():
    folder_selected = filedialog.askdirectory()
    output_folder_var.set(folder_selected)

def run_processing():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()
    
    if not input_folder or not output_folder:
        messagebox.showwarning("Input Error", "Please select both input and output folders.")
        return
    
    os.makedirs(output_folder, exist_ok=True)
    process_all_files_in_folder(input_folder, output_folder)

# Create the main window
root = tk.Tk()
root.title("File Processor for Spectrometer Data")

# Input folder selection
tk.Label(root, text="Input Folder:").grid(row=0, column=0, padx=10, pady=5)
input_folder_var = tk.StringVar()
tk.Entry(root, textvariable=input_folder_var, width=50).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse...", command=select_input_folder).grid(row=0, column=2, padx=10, pady=5)

# Output folder selection
tk.Label(root, text="Output Folder:").grid(row=1, column=0, padx=10, pady=5)
output_folder_var = tk.StringVar()
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse...", command=select_output_folder).grid(row=1, column=2, padx=10, pady=5)

# Run button
tk.Button(root, text="Run", command=run_processing, bg="green", fg="white").grid(row=2, columnspan=3, pady=20)

# Start the main event loop
root.mainloop()

