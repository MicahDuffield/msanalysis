import tkinter as tk
from tkinter import filedialog

# Hide the main Tkinter window
root = tk.Tk()
root.withdraw()

# Open the file dialog and capture the selected path
def file_selector(optional_path = None):
    """
    Optional path:
    Can pass a tuple with the name of the file type, and the extension 
    you're looking for. This get's added to the list of file types
    already defined

    files you're searching without optional path:
    [("All Files", "*.*")]

    files you're searching with optional path:
    [("File Type name", "*.file extension")]

    with optional path
    """
    file_types = [("All Files", "*.*")]
    if optional_path != None:
        file_types.insert(0,optional_path)

    file_path = filedialog.askopenfilename(
        title="Select a File",
        filetypes=file_types
    )
    return file_path