"""
Main GUI for the Batch File Renamer application.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List
import threading

from config import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, RenameConfig,
    SORT_METHODS, CONFLICT_STRATEGIES, PADDING_OPTIONS,
    COLOR_SAFE, COLOR_WARNING, COLOR_ERROR
)
from validators import validate_base_name, validate_start_number, validate_separator
from renamer_engine import FileRenamer


class RenamerGUI:
    """Main GUI application for batch file renaming."""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # State
        self.selected_files = []
        self.config = RenameConfig()
        self.preview_data = []
        
        # Create UI
        self.create_widgets()
        self.update_preview()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # File list area
        main_frame.rowconfigure(4, weight=1)  # Preview area
        
        # ===== Section 1: File Selection =====
        self.create_file_selection_section(main_frame, row=0)
        
        # ===== Section 2: File List =====
        self.create_file_list_section(main_frame, row=2)
        
        # ===== Section 3: Configuration =====
        self.create_config_section(main_frame, row=3)
        
        # ===== Section 4: Preview =====
        self.create_preview_section(main_frame, row=4)
        
        # ===== Section 5: Action Buttons =====
        self.create_action_section(main_frame, row=5)
        
        # ===== Section 6: Status Bar =====
        self.create_status_bar(main_frame, row=6)
    
    def create_file_selection_section(self, parent, row):
        """Create file selection controls."""
        frame = ttk.LabelFrame(parent, text="File Selection", padding="5")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        # Browse button
        btn_browse = ttk.Button(frame, text="Browse Files...", command=self.browse_files)
        btn_browse.grid(row=0, column=0, padx=5)
        
        # Clear button
        btn_clear = ttk.Button(frame, text="Clear All", command=self.clear_files)
        btn_clear.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # File count label
        self.lbl_file_count = ttk.Label(frame, text="No files selected")
        self.lbl_file_count.grid(row=0, column=2, padx=5)
    
    def create_file_list_section(self, parent, row):
        """Create file list display."""
        frame = ttk.LabelFrame(parent, text="Selected Files", padding="5")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Treeview for file list
        columns = ("filename", "path")
        self.tree_files = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        self.tree_files.heading("filename", text="Filename")
        self.tree_files.heading("path", text="Directory")
        self.tree_files.column("filename", width=300)
        self.tree_files.column("path", width=400)
        self.tree_files.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_files.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree_files.configure(yscrollcommand=scrollbar.set)
    
    def create_config_section(self, parent, row):
        """Create configuration controls."""
        frame = ttk.LabelFrame(parent, text="Rename Configuration", padding="5")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Grid layout for configuration fields
        # Row 0: Base Name
        ttk.Label(frame, text="Base Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.entry_base_name = ttk.Entry(frame, width=30)
        self.entry_base_name.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.entry_base_name.bind('<KeyRelease>', lambda e: self.on_config_change())
        
        # Row 0: Separator
        ttk.Label(frame, text="Separator:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.entry_separator = ttk.Entry(frame, width=10)
        self.entry_separator.insert(0, self.config.separator)
        self.entry_separator.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        self.entry_separator.bind('<KeyRelease>', lambda e: self.on_config_change())
        
        # Row 1: Start Number
        ttk.Label(frame, text="Start Number:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.spin_start_number = ttk.Spinbox(frame, from_=0, to=999999, width=15)
        self.spin_start_number.set(self.config.start_number)
        self.spin_start_number.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        self.spin_start_number.bind('<KeyRelease>', lambda e: self.on_config_change())
        self.spin_start_number.bind('<<Increment>>', lambda e: self.on_config_change())
        self.spin_start_number.bind('<<Decrement>>', lambda e: self.on_config_change())
        
        # Row 1: Padding
        ttk.Label(frame, text="Zero Padding:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.combo_padding = ttk.Combobox(frame, values=list(PADDING_OPTIONS.values()), 
                                          state="readonly", width=20)
        self.combo_padding.set(PADDING_OPTIONS[self.config.padding])
        self.combo_padding.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        self.combo_padding.bind('<<ComboboxSelected>>', lambda e: self.on_config_change())
        
        # Row 2: Sort Method
        ttk.Label(frame, text="Sort By:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.combo_sort = ttk.Combobox(frame, values=list(SORT_METHODS.values()), 
                                       state="readonly", width=28)
        self.combo_sort.set(SORT_METHODS[self.config.sort_method])
        self.combo_sort.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.combo_sort.bind('<<ComboboxSelected>>', lambda e: self.on_config_change())
        
        # Row 2: Conflict Resolution
        ttk.Label(frame, text="If Conflict:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        self.combo_conflict = ttk.Combobox(frame, values=list(CONFLICT_STRATEGIES.values()),
                                           state="readonly", width=20)
        self.combo_conflict.set(CONFLICT_STRATEGIES[self.config.conflict_resolution])
        self.combo_conflict.grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)
        self.combo_conflict.bind('<<ComboboxSelected>>', lambda e: self.on_config_change())
        
        # Configure column weights
        frame.columnconfigure(1, weight=1)
    
    def create_preview_section(self, parent, row):
        """Create preview display."""
        frame = ttk.LabelFrame(parent, text="Preview (Old → New)", padding="5")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Treeview for preview
        columns = ("old_name", "arrow", "new_name", "status")
        self.tree_preview = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        self.tree_preview.heading("old_name", text="Current Name")
        self.tree_preview.heading("arrow", text="")
        self.tree_preview.heading("new_name", text="New Name")
        self.tree_preview.heading("status", text="Status")
        
        self.tree_preview.column("old_name", width=300)
        self.tree_preview.column("arrow", width=30, anchor=tk.CENTER)
        self.tree_preview.column("new_name", width=300)
        self.tree_preview.column("status", width=150)
        
        self.tree_preview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_preview.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree_preview.configure(yscrollcommand=scrollbar.set)
        
        # Configure tags for color coding
        self.tree_preview.tag_configure("safe", foreground=COLOR_SAFE)
        self.tree_preview.tag_configure("warning", foreground=COLOR_WARNING)
        self.tree_preview.tag_configure("error", foreground=COLOR_ERROR)
    
    def create_action_section(self, parent, row):
        """Create action buttons."""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Rename button (large, prominent)
        self.btn_rename = ttk.Button(frame, text="Rename Files", command=self.rename_files)
        self.btn_rename.grid(row=0, column=0, padx=5, ipadx=20, ipady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, mode='determinate', length=300)
        self.progress.grid(row=0, column=1, padx=20)
        
        # Cancel/Reset button
        btn_reset = ttk.Button(frame, text="Reset", command=self.reset_config)
        btn_reset.grid(row=0, column=2, padx=5)
    
    def create_status_bar(self, parent, row):
        """Create status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=row, column=0, sticky=(tk.W, tk.E))
    
    # ===== Event Handlers =====
    
    def browse_files(self):
        """Open file dialog to select files."""
        files = filedialog.askopenfilenames(
            title="Select Files to Rename",
            filetypes=[
                ("All Files", "*.*"),
                ("Video Files", "*.mp4 *.mov *.avi *.mkv"),
                ("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Audio Files", "*.mp3 *.wav *.flac *.aac")
            ]
        )
        
        if files:
            self.selected_files = [Path(f) for f in files]
            self.update_file_list()
            self.update_preview()
            self.status_var.set(f"Loaded {len(self.selected_files)} file(s)")
    
    def clear_files(self):
        """Clear the file list."""
        self.selected_files = []
        self.update_file_list()
        self.update_preview()
        self.status_var.set("Ready")
    
    def on_config_change(self):
        """Handle configuration changes."""
        # Update config object from UI
        self.update_config_from_ui()
        # Regenerate preview
        self.update_preview()
    
    def update_config_from_ui(self):
        """Update the config object from UI values."""
        self.config.base_name = self.entry_base_name.get().strip()
        self.config.separator = self.entry_separator.get()
        
        # Start number
        try:
            self.config.start_number = int(self.spin_start_number.get())
        except ValueError:
            self.config.start_number = 1
        
        # Padding - reverse lookup
        padding_display = self.combo_padding.get()
        for key, value in PADDING_OPTIONS.items():
            if value == padding_display:
                self.config.padding = key
                break
        
        # Sort method - reverse lookup
        sort_display = self.combo_sort.get()
        for key, value in SORT_METHODS.items():
            if value == sort_display:
                self.config.sort_method = key
                break
        
        # Conflict resolution - reverse lookup
        conflict_display = self.combo_conflict.get()
        for key, value in CONFLICT_STRATEGIES.items():
            if value == conflict_display:
                self.config.conflict_resolution = key
                break
    
    def update_file_list(self):
        """Update the file list display."""
        # Clear existing items
        for item in self.tree_files.get_children():
            self.tree_files.delete(item)
        
        # Add files
        for filepath in self.selected_files:
            self.tree_files.insert("", tk.END, values=(filepath.name, str(filepath.parent)))
        
        # Update count label
        count = len(self.selected_files)
        self.lbl_file_count.config(text=f"{count} file(s) selected")
    
    def update_preview(self):
        """Update the preview display."""
        # Clear existing preview
        for item in self.tree_preview.get_children():
            self.tree_preview.delete(item)
        
        if not self.selected_files:
            self.btn_rename.config(state=tk.DISABLED)
            return
        
        # Validate configuration
        is_valid, error = validate_base_name(self.config.base_name)
        if not is_valid:
            self.status_var.set(f"Error: {error}")
            self.btn_rename.config(state=tk.DISABLED)
            return
        
        is_valid, error = validate_separator(self.config.separator)
        if not is_valid:
            self.status_var.set(f"Error: {error}")
            self.btn_rename.config(state=tk.DISABLED)
            return
        
        # Generate preview
        try:
            renamer = FileRenamer(self.selected_files, self.config)
            preview = renamer.preview_rename()
            self.preview_data = preview
            
            # Display preview
            for old_path, new_path, is_valid, error_msg in preview:
                old_name = old_path.name
                new_name = new_path.name
                
                if is_valid:
                    status = "✓ Ready"
                    tag = "safe"
                elif error_msg and "conflict" in error_msg.lower():
                    status = "⚠ Conflict"
                    tag = "warning"
                else:
                    status = f"✗ {error_msg if error_msg else 'Error'}"
                    tag = "error"
                
                self.tree_preview.insert("", tk.END, 
                                       values=(old_name, "→", new_name, status),
                                       tags=(tag,))
            
            # Check if any files can be renamed
            valid_count = sum(1 for _, _, is_valid, _ in preview if is_valid)
            if valid_count > 0:
                self.btn_rename.config(state=tk.NORMAL)
                self.status_var.set(f"Ready to rename {valid_count} file(s)")
            else:
                self.btn_rename.config(state=tk.DISABLED)
                self.status_var.set("No valid files to rename")
                
        except Exception as e:
            self.status_var.set(f"Preview error: {str(e)}")
            self.btn_rename.config(state=tk.DISABLED)
    
    def rename_files(self):
        """Execute the rename operation."""
        if not self.selected_files or not self.preview_data:
            messagebox.showwarning("No Files", "Please select files to rename first.")
            return
        
        # Confirm action
        valid_count = sum(1 for _, _, is_valid, _ in self.preview_data if is_valid)
        response = messagebox.askyesno(
            "Confirm Rename",
            f"Rename {valid_count} file(s)?\n\nThis action cannot be undone.",
            icon=messagebox.WARNING
        )
        
        if not response:
            return
        
        # Disable UI during operation
        self.btn_rename.config(state=tk.DISABLED)
        self.status_var.set("Renaming files...")
        self.progress['value'] = 0
        self.progress['maximum'] = len(self.preview_data)
        
        # Run rename in thread to keep UI responsive
        thread = threading.Thread(target=self.execute_rename_thread)
        thread.start()
    
    def execute_rename_thread(self):
        """Execute rename in background thread."""
        def progress_callback(current, total, filename):
            self.root.after(0, lambda: self.progress.config(value=current))
            self.root.after(0, lambda: self.status_var.set(f"Renaming: {filename}"))
        
        try:
            renamer = FileRenamer(self.selected_files, self.config)
            renamer.preview_rename()  # Regenerate plan
            results = renamer.execute_rename(progress_callback)
            
            # Show results
            self.root.after(0, lambda: self.show_results(results))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Rename failed: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
        finally:
            self.root.after(0, lambda: self.btn_rename.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress.config(value=0))
    
    def show_results(self, results):
        """Display rename operation results."""
        stats = FileRenamer([], RenameConfig()).verify_rename(results)
        
        # Build message
        message = f"Rename Complete!\n\n"
        message += f"Total: {stats['total']}\n"
        message += f"Successful: {stats['successful']}\n"
        message += f"Failed: {stats['failed']}\n"
        message += f"Success Rate: {stats['success_rate']:.1f}%\n"
        
        if stats['errors']:
            message += f"\nErrors:\n"
            for result in stats['errors'][:5]:  # Show first 5 errors
                message += f"  • {result.old_path.name}: {result.error}\n"
            if len(stats['errors']) > 5:
                message += f"  ... and {len(stats['errors']) - 5} more\n"
        
        if stats['successful'] > 0:
            messagebox.showinfo("Rename Complete", message)
        else:
            messagebox.showerror("Rename Failed", message)
        
        # Refresh file list (clear renamed files)
        if stats['successful'] > 0:
            self.selected_files = [r.old_path for r in results if not r.success]
            self.update_file_list()
            self.update_preview()
        
        self.status_var.set(f"Renamed {stats['successful']} file(s)")
    
    def reset_config(self):
        """Reset configuration to defaults."""
        self.config = RenameConfig()
        self.entry_base_name.delete(0, tk.END)
        self.entry_separator.delete(0, tk.END)
        self.entry_separator.insert(0, self.config.separator)
        self.spin_start_number.set(self.config.start_number)
        self.combo_padding.set(PADDING_OPTIONS[self.config.padding])
        self.combo_sort.set(SORT_METHODS[self.config.sort_method])
        self.combo_conflict.set(CONFLICT_STRATEGIES[self.config.conflict_resolution])
        self.update_preview()
        self.status_var.set("Configuration reset")


def start():
    """Start the GUI application."""
    root = tk.Tk()
    app = RenamerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    start()
