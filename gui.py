"""
Main GUI for the Batch File Renamer application.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List
import threading
from datetime import datetime

from config import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, RenameConfig,
    SORT_METHODS, CONFLICT_STRATEGIES, PADDING_OPTIONS,
    COLOR_SAFE, COLOR_WARNING, COLOR_ERROR
)
from validators import validate_base_name, validate_start_number, validate_separator
from renamer_engine import FileRenamer
from history_manager import HistoryManager
from theme_manager import ModernTheme
from app_settings import AppSettings


class RenamerGUI:
    """Main GUI application for batch file renaming."""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # State
        self.selected_files = []
        self.original_names = {}  # Map current path -> original import name
        self.config = RenameConfig()
        self.preview_data = []
        self.settings = AppSettings()
        self.history_manager = HistoryManager(self.settings.get_history_path())
        
        # Create UI
        self.create_widgets()
        
        # Apply Theme
        self.theme = ModernTheme(self.root)
        self.theme.apply()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Tab 1: Workspace
        self.workspace_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.workspace_frame, text="Workspace")
        self.setup_workspace_tab(self.workspace_frame)
        
        # Tab 2: History
        self.history_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.history_frame, text="History")
        self.setup_history_tab(self.history_frame)
        
        # Bind tab change to refresh history
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def setup_workspace_tab(self, parent):
        """Setup the main workspace tab."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)  # File list area
        parent.rowconfigure(4, weight=1)  # Preview area
        
        # ===== Section 1: File Selection =====
        self.create_file_selection_section(parent, row=0)
        
        # ===== Section 2: File List =====
        self.create_file_list_section(parent, row=2)
        
        # ===== Section 3: Configuration =====
        self.create_config_section(parent, row=3)
        
        # ===== Section 4: Preview =====
        self.create_preview_section(parent, row=4)
        
        # ===== Section 5: Action Buttons =====
        self.create_action_section(parent, row=5)
        
        # ===== Section 6: Status Bar =====
        self.create_status_bar(parent, row=6)

    def setup_history_tab(self, parent):
        """Setup the history tab."""
        parent.columnconfigure(0, weight=1) # Sessions list
        parent.columnconfigure(1, weight=2) # Details list
        parent.rowconfigure(1, weight=1)
        
        
        # Header
        ttk.Label(parent, text="History & Recovery", style="Header.TLabel").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Left Panel: Sessions List
        session_frame = ttk.LabelFrame(parent, text="Past Sessions", padding="5")
        session_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(0, 5))
        session_frame.columnconfigure(0, weight=1)
        session_frame.rowconfigure(0, weight=1)
        
        columns = ("date", "count")
        self.tree_sessions = ttk.Treeview(session_frame, columns=columns, show="headings", selectmode="browse")
        self.tree_sessions.heading("date", text="Date & Time")
        self.tree_sessions.heading("count", text="Files")
        self.tree_sessions.column("date", width=140)
        self.tree_sessions.column("count", width=50, anchor=tk.CENTER)
        self.tree_sessions.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        sb_sessions = ttk.Scrollbar(session_frame, orient=tk.VERTICAL, command=self.tree_sessions.yview)
        sb_sessions.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree_sessions.configure(yscrollcommand=sb_sessions.set)
        
        self.tree_sessions.bind("<<TreeviewSelect>>", self.on_session_select)
        
        # Right Panel: Session Details
        details_frame = ttk.LabelFrame(parent, text="Session Details", padding="5")
        details_frame.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.W, tk.E))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        det_columns = ("old", "arrow", "new")
        self.tree_history_details = ttk.Treeview(details_frame, columns=det_columns, show="headings")
        self.tree_history_details.heading("old", text="Original Name")
        self.tree_history_details.heading("arrow", text="")
        self.tree_history_details.heading("new", text="Renamed To")
        self.tree_history_details.column("old", width=200)
        self.tree_history_details.column("arrow", width=30, anchor=tk.CENTER)
        self.tree_history_details.column("new", width=200)
        self.tree_history_details.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        sb_details = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.tree_history_details.yview)
        sb_details.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree_history_details.configure(yscrollcommand=sb_details.set)
        
        # Action Panel
        action_frame = ttk.Frame(parent, padding="5")
        action_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        
        self.btn_undo = ttk.Button(action_frame, text="Undo Selected Session", command=self.undo_session, state=tk.DISABLED, style="Accent.TButton")
        self.btn_undo.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(action_frame, text="Refresh", command=self.load_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Change Storage Location...", command=self.change_history_location).pack(side=tk.LEFT, padx=5)

    def on_tab_change(self, event):
        """Handle tab changes."""
        if self.notebook.index("current") == 1:  # History tab
            self.load_history()

    def load_history(self):
        """Load sessions into the history list."""
        # Clear existing
        for item in self.tree_sessions.get_children():
            self.tree_sessions.delete(item)
        self.clear_history_details()
        
        sessions = self.history_manager.get_sessions()
        for session in sessions:
            # Format timestamp nicely
            try:
                dt = datetime.fromisoformat(session["timestamp"])
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                date_str = session["timestamp"]
                
            self.tree_sessions.insert("", tk.END, values=(date_str, session["count"]), iid=session["id"])

    def clear_history_details(self):
        for item in self.tree_history_details.get_children():
            self.tree_history_details.delete(item)
        self.btn_undo.config(state=tk.DISABLED)

    def on_session_select(self, event):
        """Display details for selected session."""
        selection = self.tree_sessions.selection()
        if not selection:
            return
            
        session_id = selection[0]
        session = self.history_manager.get_session_by_id(session_id)
        
        self.clear_history_details()
        if session:
            self.btn_undo.config(state=tk.NORMAL)
            for record in session["files"]:
                old_name = Path(record["old_path"]).name
                new_name = Path(record["new_path"]).name
                self.tree_history_details.insert("", tk.END, values=(old_name, "→", new_name))

    def undo_session(self):
        """Undo the selected session."""
        selection = self.tree_sessions.selection()
        if not selection:
            return
            
        session_id = selection[0]
        session = self.history_manager.get_session_by_id(session_id)
        if not session:
            return
            
        if not messagebox.askyesno("Confirm Undo", "Are you sure you want to undo this session?\nThis will rename files back to their original names."):
            return
            
        # Execute undo
        renamer = FileRenamer([], self.config, self.history_manager) # Empty init since we use session data
        results = renamer.undo_session(session)
        
        # Show results
        success_count = sum(1 for r in results if r.success)
        error_count = len(results) - success_count
        
        msg = f"Undo complete.\nRestored: {success_count}\nFailed: {error_count}"
        if error_count > 0:
            msg += "\n\nCheck logs for details or ensure files have not been moved."
            messagebox.showwarning("Undo Results", msg)
        else:
            messagebox.showinfo("Success", msg)
            
        # Refresh
        self.load_history()
        # Also refresh workspace if needed? No, user can reload.
        
    def change_history_location(self):
        """Change the location of the history file."""
        current_path = self.settings.get_history_path()
        
        # Ask user for new location (Save As dialog effectively, but we are choosing a file)
        # We can use askopenfilename to find existing, or asksaveasfilename to create new
        # But maybe just askdirectory? Then we create history.json inside?
        # User request: "choose the path". Usually implies file or folder. 
        # Let's let them choose the folder, and we assume 'history.json' inside it, 
        # OR let them point to a specific .json file. Pointing to a specific file is most flexible.
        
        new_file = filedialog.asksaveasfilename(
            title="Select History File Location",
            initialdir=current_path.parent,
            initialfile=current_path.name,
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            defaultextension=".json"
        )
        
        if new_file:
            new_path = Path(new_file)
            
            # Check if we should copy existing history
            if messagebox.askyesno("Migrate History", "Do you want to copy your current history data to the new location?"):
                try:
                    # Load current data
                    current_data = self.history_manager.history_data
                    # Save to new location (HistoryManager will handle this if we init it/save it)
                     # Creating a temp manager to save
                    temp_manager = HistoryManager(new_path)
                    temp_manager.history_data = current_data
                    temp_manager._save_history()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to migrate data: {e}")
                    return

            # Update settings
            self.settings.set_history_path(new_path)
            
            # Re-init manager
            self.history_manager = HistoryManager(new_path)
            
            # Refresh UI
            self.load_history()
            messagebox.showinfo("Success", f"History location updated to:\n{new_path}")
        
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
        self.btn_rename = ttk.Button(frame, text="Rename Files", command=self.rename_files, style="Accent.TButton")
        self.btn_rename.grid(row=0, column=0, padx=5, ipadx=10, ipady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, mode='determinate', length=300)
        self.progress.grid(row=0, column=1, padx=20)
        
        # Cancel/Reset button
        btn_reset = ttk.Button(frame, text="Reset", command=self.reset_config)
        btn_reset.grid(row=0, column=2, padx=5)
    
    def create_status_bar(self, parent, row):
        """Create status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.FLAT, anchor=tk.W, style="Status.TLabel", padding=5)
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
            new_files = [Path(f) for f in files]
            # Add to registry (only for new additions)
            for f in new_files:
                if f not in self.original_names:
                    # 1. Try to find in history (Deep Lookup)
                    historical_name = self.history_manager.trace_original_name(f)
                    if historical_name:
                         self.original_names[f] = historical_name
                    else:
                         # 2. Default to current name
                         self.original_names[f] = f.name
            
            # Combine unique files
            current_paths = set(self.selected_files)
            for f in new_files:
                if f not in current_paths:
                    self.selected_files.append(f)
            
            self.update_file_list()
            self.update_preview()
            self.status_var.set(f"Loaded {len(self.selected_files)} file(s)")
    
    def clear_files(self):
        """Clear the file list."""
        self.selected_files = []
        self.original_names = {}
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
            # Show original name if available, otherwise current name
            display_name = self.original_names.get(filepath, filepath.name)
            self.tree_files.insert("", tk.END, values=(display_name, str(filepath.parent)))
        
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
            renamer = FileRenamer(self.selected_files, self.config, self.history_manager)
            preview = renamer.preview_rename()
            self.preview_data = preview
            
            # Display preview
            for old_path, new_path, is_valid, error_msg in preview:
                # Use original name for display if available
                # But show current name in tooltip or as secondary? 
                # For now, let's show original name in "Current Name" column to satisfy user request
                display_old_name = self.original_names.get(old_path, old_path.name)
                # But keep new_name as is (the target)
                new_display = new_path.name
                
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
                                       values=(display_old_name, "→", new_display, status),
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
        stats = FileRenamer([], RenameConfig(), self.history_manager).verify_rename(results)
        
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
        
        # Refresh file list (update paths but keep selection)
        if stats['successful'] > 0:
            # Update paths in selected_files and original_names map
            new_selection = []
            
            # Create a map of successful renames: old_path -> new_path
            rename_map = {}
            for res in results:
                if res.success:
                    rename_map[res.old_path] = res.new_path
            
            # Rebuild selection list with new paths
            for f in self.selected_files:
                if f in rename_map:
                    new_path = rename_map[f]
                    # Transfer original name to new path key
                    if f in self.original_names:
                        self.original_names[new_path] = self.original_names[f]
                        # Optional: Remove old key? 
                        # del self.original_names[f] 
                        # (Safe to keep or delete, but deletion saves memory)
                        del self.original_names[f]
                    new_selection.append(new_path)
                else:
                    new_selection.append(f)
            
            self.selected_files = new_selection
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
