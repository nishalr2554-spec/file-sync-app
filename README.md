# Advanced File Transfer

A simple desktop app for copying files and folders to another location, with a graphical interface built using Python and CustomTkinter.

## Features

* Add individual files or whole folders to a transfer list
* Filter folder transfers by file type (images, documents, audio, video, scripts, archives, or all files)
* Choose what happens when a file already exists at the destination: **skip**, **overwrite**, or **rename** (adds `(1)`, `(2)`, ...)
* Keeps the original folder structure when copying folders
* Progress bar and live status messages during the transfer
* Summary at the end showing files transferred, skipped, and failed
* Right-click an item in the list to remove it (this never deletes anything from your disk)
* Light, dark, and system appearance modes, plus custom colors for the background, panels, accent, and progress bar

## Requirements

* Python 3.8 or newer
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

Tkinter comes with the standard Python installer on Windows and macOS. On some Linux systems you may need to install it separately (for example `sudo apt install python3-tk`).

## Installation

```bash
git clone https://github.com/nishalr2554-spec/file-sync-app.git
cd file-sync-app
pip install -r requirements.txt
```

## Usage

```bash
python file\_sync\_app.py
```

1. Click **Add Files** or **Add Folder** to build your list.
2. Pick a **File Type** filter and an **If file exists** option.
3. Click **Browse...** and choose the destination folder.
4. Click **Transfer Items**.

## Notes

* The file type filter applies only to files found inside folders. Files you add one by one are always copied.
* Files are copied, not moved, so the originals stay where they are.
* The interface uses the Segoe UI font, so it looks best on Windows. Other systems will fall back to a default font.

## License

Add a license of your choice (for example MIT).

