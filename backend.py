
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

FILE_TYPES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".ppt", ".pptx", ".xls", ".xlsx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".mpeg"],
}

moved_files_log = []
observer = None

class FileOrganizer:
    def __init__(self, folder_path, duplicate_policy="Skip", logging_enabled=True):
        self.folder_path = folder_path
        self.duplicate_policy = duplicate_policy
        self.logging_enabled = logging_enabled

    def organize_files(self, single_file=None, progress_callback=None):
        if not os.path.exists(self.folder_path):
            raise FileNotFoundError("Target folder does not exist!")

        files = [single_file] if single_file else [
            f for f in os.listdir(self.folder_path)
            if os.path.isfile(os.path.join(self.folder_path, f))
        ]
        total = len(files)
        for i, file in enumerate(files, 1):
            file_path = os.path.join(self.folder_path, file)
            if not os.path.isfile(file_path):
                continue

            ext = os.path.splitext(file)[1].lower()
            moved = False

            for category, extensions in FILE_TYPES.items():
                if ext in extensions:
                    dest_folder = os.path.join(self.folder_path, category)
                    os.makedirs(dest_folder, exist_ok=True)
                    dest_path = self.handle_duplicates(dest_folder, file)
                    shutil.move(file_path, dest_path)
                    moved_files_log.append((os.path.basename(dest_path), category))
                    moved = True
                    break

            if not moved:
                dest_folder = os.path.join(self.folder_path, "Others")
                os.makedirs(dest_folder, exist_ok=True)
                dest_path = self.handle_duplicates(dest_folder, file)
                shutil.move(file_path, dest_path)
                moved_files_log.append((os.path.basename(dest_path), "Others"))

            if progress_callback:
                progress_callback(i, total)

        if self.logging_enabled:
            self.save_log()

    def handle_duplicates(self, folder, file):
        dest_path = os.path.join(folder, file)
        if os.path.exists(dest_path):
            if self.duplicate_policy == "Skip":
                return dest_path
            elif self.duplicate_policy == "Replace":
                os.remove(dest_path)
            elif self.duplicate_policy == "Rename":
                base, ext = os.path.splitext(file)
                counter = 1
                new_file = f"{base}({counter}){ext}"
                dest_path = os.path.join(folder, new_file)
                while os.path.exists(dest_path):
                    counter += 1
                    new_file = f"{base}({counter}){ext}"
                    dest_path = os.path.join(folder, new_file)
        return dest_path

    def save_log(self):
        log_path = os.path.join(self.folder_path, "organizer_log.txt")
        with open(log_path, "a") as log_file:
            for file, category in moved_files_log:
                log_file.write(f"Moved: {file} → {category}\n")
        moved_files_log.clear()

    def undo_last_action(self):
        if not moved_files_log:
            raise ValueError("No actions to undo!")
        last_file, folder = moved_files_log.pop()
        shutil.move(os.path.join(self.folder_path, folder, last_file), self.folder_path)

class WatchdogHandler(FileSystemEventHandler):
    def __init__(self, organizer):
        self.organizer = organizer

    def on_created(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            self.organizer.organize_files(single_file=filename)

def start_monitoring(folder, duplicate_policy, logging_enabled=True):
    global observer
    organizer = FileOrganizer(folder, duplicate_policy, logging_enabled)
    event_handler = WatchdogHandler(organizer)
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=False)
    observer.start()

def stop_monitoring():
    global observer
    if observer:
        observer.stop()
        observer = None
