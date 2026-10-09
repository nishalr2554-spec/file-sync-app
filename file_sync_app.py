import os
import shutil
import fnmatch
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import customtkinter as ctk

# ── Appearance ─────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")          # "dark" | "light" | "system"
ctk.set_default_color_theme("blue")      # "blue" | "green" | "dark-blue"


class FileTransferApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Advanced File Transfer")
        self.geometry("680x560")
        self.resizable(True, True)

        # ── File Type Definitions ───────────────────────────────────────────────
        self.file_type_map = {
            "All Files (*.*)": "*.*",
            "Images (*.jpg, *.png, *.gif)": "*.jpg;*.jpeg;*.png;*.gif;*.bmp",
            "Documents (*.pdf, *.docx, *.txt)": "*.pdf;*.docx;*.doc;*.txt;*.odt",
            "Audio (*.mp3, *.wav, *.flac)": "*.mp3;*.wav;*.flac;*.aac",
            "Video (*.mp4, *.mkv, *.avi)": "*.mp4;*.mkv;*.avi;*.mov",
            "Scripts (*.py, *.js, *.sh)": "*.py;*.js;*.sh;*.bat",
            "Archives (*.zip, *.rar, *.7z)": "*.zip;*.rar;*.7z;*.tar.gz",
        }

        self.app_bg_color = "#1f1f1f"
        self.panel_bg_color = "#2b2b2b"
        self.accent_color = "#1f6aa5"
        self.progress_color = "#22c55e"

        self._build_ui()

    # ── UI Construction ─────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)   # source list grows

        main = self.main_frame
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)   # source list grows

        # ── Header ──────────────────────────────────────────────────────────────
        ctk.CTkLabel(
            main,
            text="Advanced File Transfer",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        # ── Source Group ────────────────────────────────────────────────────────
        src_frame = ctk.CTkFrame(main, corner_radius=10)
        src_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        src_frame.grid_columnconfigure(0, weight=1)
        src_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(src_frame, text="Source Files & Folders",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        # Listbox (native tk) inside a CTk container
        list_container = ctk.CTkFrame(src_frame, fg_color=("#d9d9d9", self.panel_bg_color), corner_radius=6)
        self.list_container = list_container
        list_container.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 6))
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)

        self.source_listbox = tk.Listbox(
            list_container,
            selectmode=tk.EXTENDED,
            bg=self.panel_bg_color, fg="#dcdcdc",
            selectbackground=self.accent_color,
            highlightthickness=0,
            borderwidth=0,
            activestyle="none",
            font=("Segoe UI", 10),
            height=10,
        )
        scrollbar = ctk.CTkScrollbar(list_container, command=self.source_listbox.yview)
        self.source_listbox.configure(yscrollcommand=scrollbar.set)
        self.source_listbox.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(2, 4), pady=6)

        # Right-click context menu
        self._context_menu = tk.Menu(self, tearoff=0,
                                     bg=self.panel_bg_color, fg="#dcdcdc",
                                     activebackground=self.accent_color, activeforeground="white",
                                     font=("Segoe UI", 10))
        self._context_menu.add_command(label="✖  Remove from List",
                                       command=self._remove_from_list)
        self.source_listbox.bind("<Button-3>", self._show_context_menu)

        # Source buttons
        src_btns = ctk.CTkFrame(src_frame, fg_color="transparent")
        src_btns.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))

        self.add_files_btn = ctk.CTkButton(src_btns, text="➕  Add Files", width=130,
                      command=self.add_files, fg_color=self.accent_color, hover_color=self.accent_color)
        self.add_files_btn.pack(side="left", padx=(0, 8))
        self.add_folder_btn = ctk.CTkButton(src_btns, text="📁  Add Folder", width=130,
                      command=self.add_folder, fg_color=self.accent_color, hover_color=self.accent_color)
        self.add_folder_btn.pack(side="left", padx=(0, 8))
        ctk.CTkButton(src_btns, text="🗑  Clear", width=100,
                      fg_color="#c0392b", hover_color="#922b21",
                      command=lambda: self.source_listbox.delete(0, tk.END)).pack(side="left")

        # ── Options Group ───────────────────────────────────────────────────────
        opt_frame = ctk.CTkFrame(main, corner_radius=10)
        opt_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        opt_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(opt_frame, text="Options for Folder Transfer",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 6))

        ctk.CTkLabel(opt_frame, text="File Type:").grid(row=1, column=0, padx=(12, 8), pady=(0, 10), sticky="w")
        self.file_type_var = tk.StringVar(value=list(self.file_type_map.keys())[0])
        self.file_type_combo = ctk.CTkOptionMenu(
            opt_frame,
            variable=self.file_type_var,
            values=list(self.file_type_map.keys()),
            width=340,
        )
        self.file_type_combo.grid(row=1, column=1, padx=(0, 12), pady=(0, 10), sticky="w")

        ctk.CTkLabel(opt_frame, text="If file exists:").grid(row=2, column=0, padx=(12, 8), pady=(0, 10), sticky="w")
        self.duplicate_mode_var = tk.StringVar(value="skip")
        self.duplicate_mode_combo = ctk.CTkOptionMenu(
            opt_frame,
            variable=self.duplicate_mode_var,
            values=["skip", "overwrite", "rename"],
            width=180,
        )
        self.duplicate_mode_combo.grid(row=2, column=1, padx=(0, 12), pady=(0, 10), sticky="w")

        ctk.CTkLabel(opt_frame, text="Appearance:").grid(row=3, column=0, padx=(12, 8), pady=(0, 10), sticky="w")
        self.appearance_mode_var = tk.StringVar(value="Dark")
        self.appearance_mode_combo = ctk.CTkOptionMenu(
            opt_frame,
            variable=self.appearance_mode_var,
            values=["Light", "Dark", "System"],
            width=180,
            command=self._change_appearance_mode,
        )
        self.appearance_mode_combo.grid(row=3, column=1, padx=(0, 12), pady=(0, 10), sticky="w")

        ctk.CTkLabel(opt_frame, text="Colors:").grid(row=4, column=0, padx=(12, 8), pady=(0, 10), sticky="w")
        color_btns = ctk.CTkFrame(opt_frame, fg_color="transparent")
        color_btns.grid(row=4, column=1, padx=(0, 12), pady=(0, 10), sticky="w")
        ctk.CTkButton(color_btns, text="App BG", width=90, command=lambda: self._pick_and_apply_color("app_bg")).pack(side="left", padx=(0, 6))
        ctk.CTkButton(color_btns, text="Panel BG", width=90, command=lambda: self._pick_and_apply_color("panel_bg")).pack(side="left", padx=(0, 6))
        ctk.CTkButton(color_btns, text="Accent", width=90, command=lambda: self._pick_and_apply_color("accent")).pack(side="left", padx=(0, 6))
        ctk.CTkButton(color_btns, text="Progress", width=90, command=lambda: self._pick_and_apply_color("progress")).pack(side="left")

        # ── Destination Group ───────────────────────────────────────────────────
        dest_frame = ctk.CTkFrame(main, corner_radius=10)
        dest_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        dest_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(dest_frame, text="Destination",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 6))

        self.dest_path_var = tk.StringVar()
        ctk.CTkEntry(dest_frame, textvariable=self.dest_path_var,
                     placeholder_text="Select a destination folder…").grid(
            row=1, column=0, sticky="ew", padx=(12, 8), pady=(0, 12))
        self.browse_dest_btn = ctk.CTkButton(dest_frame, text="Browse…", width=110,
                      command=self.browse_destination, fg_color=self.accent_color, hover_color=self.accent_color)
        self.browse_dest_btn.grid(row=1, column=1, padx=(0, 12), pady=(0, 12))

        # ── Transfer Button ─────────────────────────────────────────────────────
        self.transfer_btn = ctk.CTkButton(
            main,
            text="⬆  Transfer Items",
            height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.transfer_items,
            fg_color=self.accent_color,
            hover_color=self.accent_color,
        )
        self.transfer_btn.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ctk.CTkProgressBar(main, variable=self.progress_var, mode="determinate")
        self.progress_bar.configure(progress_color=self.progress_color)
        self.progress_bar.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        self.progress_bar.set(0.0)

        # ── Status Bar ──────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            anchor="w",
            font=ctk.CTkFont(size=11),
            fg_color=("#c8c8c8", "#1a1a1a"),
            corner_radius=0,
            height=24,
        )
        status_bar.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

    # ── Handlers ────────────────────────────────────────────────────────────────

    def _show_context_menu(self, event):
        """Select the item under the cursor, then show the context menu."""
        index = self.source_listbox.nearest(event.y)
        if index < 0:
            return
        # If the clicked item isn't already selected, set selection to it
        if index not in self.source_listbox.curselection():
            self.source_listbox.selection_clear(0, tk.END)
            self.source_listbox.selection_set(index)
        self._context_menu.tk_popup(event.x_root, event.y_root)

    def _remove_from_list(self):
        """Remove all selected entries from the source list (does NOT touch disk)."""
        for index in reversed(self.source_listbox.curselection()):
            self.source_listbox.delete(index)

    def _delete_from_disk(self):
        """Permanently delete selected files/folders from disk, then remove from list."""
        indices = self.source_listbox.curselection()
        if not indices:
            return
        paths = [self.source_listbox.get(i) for i in indices]
        names = "\n".join(f"  • {os.path.basename(p)}" for p in paths)
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Permanently delete the following from disk?\n\n{names}\n\nThis cannot be undone.",
            icon="warning",
        )
        if not confirmed:
            return
        errors = []
        for i, path in zip(reversed(indices), reversed(paths)):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                self.source_listbox.delete(i)
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")
        if errors:
            messagebox.showerror("Delete Errors", "\n".join(errors))
        else:
            self.status_var.set(f"Deleted {len(paths)} item(s) from disk.")

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Select Files")
        for p in paths:
            self.source_listbox.insert(tk.END, p)

    def add_folder(self):
        path = filedialog.askdirectory(title="Select Folder")
        if path:
            self.source_listbox.insert(tk.END, path)

    def browse_destination(self):
        path = filedialog.askdirectory(title="Select Destination Folder")
        if path:
            self.dest_path_var.set(path)

    def _change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode.lower())

    def _pick_and_apply_color(self, target):
        color = colorchooser.askcolor(title="Choose Color", color=self._get_current_color(target))[1]
        if not color:
            return
        if target == "app_bg":
            self.app_bg_color = color
        elif target == "panel_bg":
            self.panel_bg_color = color
        elif target == "accent":
            self.accent_color = color
        elif target == "progress":
            self.progress_color = color
        self._apply_custom_colors()

    def _get_current_color(self, target):
        if target == "app_bg":
            return self.app_bg_color
        if target == "panel_bg":
            return self.panel_bg_color
        if target == "accent":
            return self.accent_color
        if target == "progress":
            return self.progress_color
        return "#1f6aa5"

    def _apply_custom_colors(self):
        self.configure(fg_color=self.app_bg_color)
        self.main_frame.configure(fg_color="transparent")
        self.list_container.configure(fg_color=self.panel_bg_color)
        self.source_listbox.configure(bg=self.panel_bg_color, selectbackground=self.accent_color)
        self._context_menu.configure(bg=self.panel_bg_color, activebackground=self.accent_color)
        self.progress_bar.configure(progress_color=self.progress_color)
        self.add_files_btn.configure(fg_color=self.accent_color, hover_color=self.accent_color)
        self.add_folder_btn.configure(fg_color=self.accent_color, hover_color=self.accent_color)
        self.transfer_btn.configure(fg_color=self.accent_color, hover_color=self.accent_color)
        self.browse_dest_btn.configure(fg_color=self.accent_color, hover_color=self.accent_color)

        for child in self.main_frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                child.configure(fg_color=self.panel_bg_color)

    def _resolve_destination_path(self, dest_file):
        mode = self.duplicate_mode_var.get()
        if mode == "skip":
            return None if os.path.exists(dest_file) else dest_file
        if mode == "overwrite":
            return dest_file
        if mode == "rename":
            base, ext = os.path.splitext(dest_file)
            counter = 1
            candidate = dest_file
            while os.path.exists(candidate):
                candidate = f"{base} ({counter}){ext}"
                counter += 1
            return candidate
        return None

    def transfer_items(self):
        source_items = list(self.source_listbox.get(0, tk.END))
        dest_folder = self.dest_path_var.get().strip()

        pattern_string = self.file_type_map.get(self.file_type_var.get(), "*.*")
        patterns = [p.strip() for p in pattern_string.split(";")]

        if not source_items:
            messagebox.showerror("Error", "No source files or folders selected.")
            return
        if not dest_folder or not os.path.isdir(dest_folder):
            messagebox.showerror("Error", "Please select a valid destination folder.")
            return

        planned_files = []
        for item_path in source_items:
            if not os.path.exists(item_path):
                continue
            if os.path.isfile(item_path):
                planned_files.append((item_path, dest_folder, os.path.basename(item_path)))
            elif os.path.isdir(item_path):
                for dirpath, _, filenames in os.walk(item_path):
                    for filename in filenames:
                        if any(fnmatch.fnmatch(filename, p) for p in patterns):
                            src_file = os.path.join(dirpath, filename)
                            rel_dir = os.path.relpath(dirpath, item_path)
                            if rel_dir == ".":
                                dest_dir = os.path.join(dest_folder, os.path.basename(item_path))
                            else:
                                dest_dir = os.path.join(dest_folder, os.path.basename(item_path), rel_dir)
                            planned_files.append((src_file, dest_dir, filename))

        total_files = len(planned_files)
        if total_files == 0:
            messagebox.showinfo("Transfer", "No matching files were found to transfer.")
            return

        success_count = 0
        skip_count = 0
        fail_count = 0
        errors = []

        self.progress_var.set(0.0)
        self.progress_bar.set(0.0)
        self.update_idletasks()

        for index, (src_file, dest_dir, filename) in enumerate(planned_files, start=1):
            self.status_var.set(f"Processing {index}/{total_files}: {os.path.basename(src_file)}")
            self.update_idletasks()

            try:
                os.makedirs(dest_dir, exist_ok=True)
                dest_file = os.path.join(dest_dir, filename)
                resolved_dest = self._resolve_destination_path(dest_file)

                if resolved_dest is None:
                    skip_count += 1
                else:
                    shutil.copy2(src_file, resolved_dest)
                    success_count += 1

            except Exception as e:
                fail_count += 1
                errors.append(f"Error on '{os.path.basename(src_file)}': {e}")

            self.progress_var.set(index / total_files)
            self.progress_bar.set(self.progress_var.get())
            self.update_idletasks()

        self.progress_var.set(1.0)
        self.progress_bar.set(1.0)
        self.status_var.set("Transfer complete.")

        title = "Success" if fail_count == 0 else "Transfer Complete with Errors"
        msg = (
            f"Files Transferred : {success_count}\n"
            f"Skipped (duplicates): {skip_count}\n"
            f"Failed Operations : {fail_count}"
        )
        if errors:
            msg += "\n\nErrors:\n- " + "\n- ".join(errors)

        (messagebox.showinfo if fail_count == 0 else messagebox.showwarning)(title, msg)


if __name__ == "__main__":
    app = FileTransferApp()
    app.mainloop()
