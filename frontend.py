import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from backend import FileOrganizer, start_monitoring, stop_monitoring # type: ignore

root = tk.Tk()
root.title("Smart File Organizer")
root.geometry("900x600")
root.configure(bg="#f0f8ff")

folder_selected = tk.StringVar()
duplicate_policy = tk.StringVar(value="Skip")
logging_var = tk.BooleanVar(value=True)

def browse_folder():
    folder_selected.set(filedialog.askdirectory())

def organize_now():
    folder = folder_selected.get()
    if not folder:
        messagebox.showerror("Error", "Please select a folder first!")
        return

    organizer = FileOrganizer(folder, duplicate_policy.get(), logging_var.get())
    progress_bar["value"] = 0

    def update_progress(i, total):
        progress_bar["value"] = (i / total) * 100
        root.update_idletasks()

    try:
        organizer.organize_files(progress_callback=update_progress)
        messagebox.showinfo("Success", "Files organized successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def undo_last():
    folder = folder_selected.get()
    organizer = FileOrganizer(folder)
    try:
        organizer.undo_last_action()
        messagebox.showinfo("Undo", "Last action undone successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- GUI Layout ---
tk.Label(root, text="Target Folder:", bg="#f0f8ff", font=("Arial", 12, "bold")).pack(pady=5)
tk.Entry(root, textvariable=folder_selected, width=60).pack(pady=5)
tk.Button(root, text="Browse", bg="#add8e6", command=browse_folder).pack(pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.pack(pady=10)

tk.Button(root, text="Organize Now", bg="#90ee90", command=organize_now).pack(pady=5)
tk.Button(root, text="Undo Last", bg="#ffa07a", command=undo_last).pack(pady=5)
tk.Button(root, text="Start Monitoring", bg="#98fb98",
          command=lambda: start_monitoring(folder_selected.get(), duplicate_policy.get(), logging_var.get())).pack(pady=5)
tk.Button(root, text="Stop Monitoring", bg="#f08080", command=stop_monitoring).pack(pady=5)

tk.Label(root, text="Duplicate Handling:", bg="#f0f8ff", font=("Arial", 11, "bold")).pack(pady=5)
ttk.Combobox(root, textvariable=duplicate_policy, values=["Skip", "Replace", "Rename"], state="readonly").pack(pady=5)

tk.Checkbutton(root, text="Enable Logging", variable=logging_var, bg="#f0f8ff").pack(pady=5)

root.mainloop()
