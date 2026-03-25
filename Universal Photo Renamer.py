import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from collections import defaultdict

def reverse_rename_photos(folder_path, extensions_str, log_widget):
   
    def log_message(message):
        log_widget.insert(tk.END, message + "\n"); log_widget.see(tk.END); log_widget.update_idletasks()

    try:
        log_message("Starting Intelligent Reverse Rename process...")
        extensions = [ext.strip().lower() for ext in extensions_str.split(',') if ext.strip()]
        if not extensions:
            log_message("❌ ERROR: No file types selected."); messagebox.showerror("Error", "Please select a file type."); return

        pattern_extensions = '|'.join(extensions)
        # --- THE CRITICAL FIX IS HERE ---
        # This new, universal pattern looks for ANY characters at the start (non-greedy),
        # followed by the numbers at the VERY END of the filename stem.
        # It captures: 1. The entire base name (e.g., "My-Trip_IMG_") 2. The number part 3. The file extension
        file_pattern = re.compile(rf"^(.*?)(\d+)\.({pattern_extensions})$", re.IGNORECASE)

        files_by_prefix = defaultdict(list)
        log_message(f"Searching for files like 'any_name_ending_in_numbers.({pattern_extensions})'...")

        for filename in os.listdir(folder_path):
            match = file_pattern.match(filename)
            if match:
                # The "prefix" is now defined as the part of the name that is consistent across a sequence.
                # For "IMG_01", "IMG_02", the prefix is "IMG_".
                # For "photo1", "photo2", the prefix is "photo".
                base_name = match.group(1)
                number_part = match.group(2)

                m = re.match(r'^(.*?)(\D+)$', base_name)
                if m:
                    sequence_prefix = m.group(1) + m.group(2)
                else:
                    sequence_prefix = base_name

                files_by_prefix[sequence_prefix].append({
                    'original_name': filename,
                    'base_name': base_name,
                    'number': int(number_part),
                    'extension': match.group(3)
                })

        if not files_by_prefix:
            log_message("No files found matching a 'name_ending_in_numbers' pattern."); messagebox.showinfo("Finished", "No files matching a recognized sequence (e.g., IMG_1234.jpg) were found."); return

        total_renamed = 0
        for prefix, files_to_rename in files_by_prefix.items():
            if len(files_to_rename) < 2: continue

            log_message(f"\n--- Found sequence with base name '{prefix or '[none]'}'. Reversing {len(files_to_rename)} files... ---")
            files_to_rename.sort(key=lambda x: x['number'])

            original_full_names = [f['base_name'] + str(f['number']) for f in files_to_rename]
            new_full_names = original_full_names[::-1]

            for file_info in files_to_rename:
                temp_name = f"{file_info['base_name']}{file_info['number']}_temp.{file_info['extension']}"
                os.rename(os.path.join(folder_path, file_info['original_name']), os.path.join(folder_path, temp_name))

            for i, file_info in enumerate(files_to_rename):
                temp_name = f"{file_info['base_name']}{file_info['number']}_temp.{file_info['extension']}"
                final_new_name = f"{new_full_names[i]}.{file_info['extension']}"
                os.rename(os.path.join(folder_path, temp_name), os.path.join(folder_path, final_new_name))
                log_message(f" {file_info['original_name']} -> {final_new_name}")
            total_renamed += len(files_to_rename)

        if total_renamed > 0:
            log_message("\n✅ Reverse Rename complete!"); messagebox.showinfo("Success!", f"{total_renamed} photos were successfully renamed in reverse order.")
        else:
            log_message("No sequences with 2 or more files were found to reverse."); messagebox.showinfo("Finished", "No sequences with 2 or more files were found to reverse.")
    except Exception as e:
        log_message(f"\n❌ ERROR: {e}"); messagebox.showerror("Error", f"An error occurred: {e}")

def batch_rename_photos(folder_path, extensions_str, new_prefix, log_widget):
    def log_message(message):
        log_widget.insert(tk.END, message + "\n"); log_widget.see(tk.END); log_widget.update_idletasks()
    try:
        log_message("Starting Batch Rename process...")
        extensions = [ext.strip().lower() for ext in extensions_str.split(',') if ext.strip()]
        if not extensions: log_message("❌ ERROR: No file types selected."); messagebox.showerror("Error", "Please select a file type."); return
        files_to_rename = [fn for fn in os.listdir(folder_path) if os.path.splitext(fn)[1][1:].lower() in extensions]
        if not files_to_rename: log_message("No files found with the selected extensions."); messagebox.showinfo("Finished", "No matching files were found."); return
        files_to_rename.sort()
        log_message(f"Found {len(files_to_rename)} files to rename.")
        num_digits = len(str(len(files_to_rename)))
        log_message("\n--- Renaming files ---")
        for i, filename in enumerate(files_to_rename):
            old_path = os.path.join(folder_path, filename)
            new_name = f"{new_prefix}_{str(i+1).zfill(num_digits)}{os.path.splitext(filename)[1]}"
            new_path = os.path.join(folder_path, new_name)
            if os.path.exists(new_path):
                temp_name = f"temp_{i}_{filename}"; os.rename(old_path, os.path.join(folder_path, temp_name)); old_path = os.path.join(folder_path, temp_name)
            os.rename(old_path, new_path)
            log_message(f" {filename} -> {new_name}")
        log_message("\n✅ Batch Rename complete!"); messagebox.showinfo("Success!", "All files were successfully renamed.")
    except Exception as e:
        log_message(f"\n❌ ERROR: {e}"); messagebox.showerror("Error", f"An error occurred: {e}")

class RenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Photo Renamer Published by - Pau Garcia")
        self.root.geometry("650x550")
        self.folder_path = ""
        self.folder_frame = tk.Frame(root, padx=10, pady=10); self.folder_frame.pack(fill=tk.X)
        self.select_button = tk.Button(self.folder_frame, text="1. Select Folder...", command=self.select_folder)
        self.select_button.pack(side=tk.LEFT, padx=(0, 10))
        self.folder_label = tk.Label(self.folder_frame, text="No folder selected", fg="grey", anchor="w")
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ext_frame = tk.LabelFrame(root, text=" 2. Select File Types to Process ", padx=10, pady=10); self.ext_frame.pack(fill=tk.X, padx=10)
        self.ext_vars = {}
        COMMON_EXTENSIONS = [("JPG", "jpg"), ("JPEG", "jpeg"), ("PNG", "png"), ("Nikon (.NEF)", "nef"), ("Sony (.ARW)", "arw"), ("Canon (.CR2)", "cr2"), ("Adobe (.DNG)", "dng"), ("Olympus (.ORF)", "orf"), ("Fujifilm (.RAF)", "raf")]
        for i, (display, ext) in enumerate(COMMON_EXTENSIONS):
            var = tk.IntVar(value=1 if ext in ['jpg', 'jpeg', 'png'] else 0)
            cb = tk.Checkbutton(self.ext_frame, text=display, variable=var); self.ext_vars[ext] = var
            cb.grid(row=i // 3, column=i % 3, sticky="w")
        tk.Label(self.ext_frame, text="Other:").grid(row=(len(COMMON_EXTENSIONS) // 3) + 1, column=0, sticky="w", pady=(10,0))
        self.other_ext_entry = tk.Entry(self.ext_frame); self.other_ext_entry.grid(row=(len(COMMON_EXTENSIONS) // 3) + 1, column=1, columnspan=2, sticky="we", pady=(10,0))
        self.notebook = ttk.Notebook(root, padding=10); self.notebook.pack(fill="both", expand=True)
        self.tab1 = ttk.Frame(self.notebook); self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Reverse Rename (Intelligent Mode)")
        self.notebook.add(self.tab2, text="Batch Rename (e.g., image_1, image_2)")
        tk.Label(self.tab1, text="This mode finds any files that end in numbers (e.g., 'Vacation_001', 'IMG_1234') and reverses each sequence automatically.", wraplength=550, justify="left").pack(pady=10)
        self.reverse_rename_button = tk.Button(self.tab1, text="Run Reverse Rename!", command=self.start_reverse_rename, state=tk.DISABLED, font=('Helvetica', 10, 'bold'))
        self.reverse_rename_button.pack(pady=20, padx=20, fill=tk.X)
        batch_frame = tk.Frame(self.tab2); batch_frame.pack(pady=10, fill=tk.X, padx=10)
        tk.Label(batch_frame, text="New Filename Prefix:").pack(side=tk.LEFT)
        self.prefix_entry = tk.Entry(batch_frame); self.prefix_entry.insert(0, "image"); self.prefix_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.batch_rename_button = tk.Button(self.tab2, text="Run Batch Rename!", command=self.start_batch_rename, state=tk.DISABLED, font=('Helvetica', 10, 'bold'))
        self.batch_rename_button.pack(pady=20, padx=20, fill=tk.X)
        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10); self.log_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.log_area.insert(tk.END, "Welcome! Please select a folder and choose a renaming mode from the tabs above.")
    def select_folder(self):
        path = filedialog.askdirectory(title="Select your photo folder")
        if path:
            self.folder_path = path; self.folder_label.config(text=path, fg="black")
            self.reverse_rename_button.config(state=tk.NORMAL); self.batch_rename_button.config(state=tk.NORMAL)
            self.log_area.delete(1.0, tk.END); self.log_area.insert(tk.END, f"Folder selected: {path}\n\nReady to rename. Choose an option from the tabs.")
    def get_selected_extensions(self):
        selected = [ext for ext, var in self.ext_vars.items() if var.get() == 1]
        other_exts = [ext.strip().lower().replace('.', '') for ext in self.other_ext_entry.get().split(',') if ext.strip()]
        return ", ".join(list(dict.fromkeys(selected + other_exts)))
    def start_reverse_rename(self):
        extensions_str = self.get_selected_extensions()
        if not extensions_str: messagebox.showwarning("Warning", "Please select at least one file type."); return
        if messagebox.askyesno("Are you sure?", f"This will REVERSE RENAME any photo sequences found in the folder.\n\nA backup is highly recommended. Continue?"):
            self.log_area.delete(1.0, tk.END); reverse_rename_photos(self.folder_path, extensions_str, self.log_area)
    def start_batch_rename(self):
        extensions_str = self.get_selected_extensions(); new_prefix = self.prefix_entry.get().strip()
        if not extensions_str: messagebox.showwarning("Warning", "Please select at least one file type."); return
        if not new_prefix: messagebox.showwarning("Warning", "Please enter a prefix for the new filenames."); return
        if messagebox.askyesno("Are you sure?", f"This will BATCH RENAME all files to '{new_prefix}_1', '{new_prefix}_2', etc.\n\nThis cannot be undone. Continue?"):
            self.log_area.delete(1.0, tk.END); batch_rename_photos(self.folder_path, extensions_str, new_prefix, self.log_area)

if __name__ == "__main__":
    root = tk.Tk()
    app = RenamerApp(root)
    root.mainloop()