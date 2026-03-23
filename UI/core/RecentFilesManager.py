import json
import os

class RecentFilesManager:
    def __init__(self, process_callback, max_files=10):
        self.recent_files = []
        self.max_files = max_files
        self.process_callback = process_callback
        self.storage_file = "recent_files.json"

    def add_to_history(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:self.max_files]
        self.save_recent_files()

    def clear(self):
        self.recent_files = []
        self.save_recent_files()

    def load_recent_files(self):
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.recent_files = json.load(f)
                    # Validate file paths
                    self.recent_files = [f for f in self.recent_files if os.path.exists(f)]
        except Exception as e:
            print(f"Error loading recent files: {e}")

    def save_recent_files(self):
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.recent_files, f)
        except Exception as e:
            print(f"Error saving recent files: {e}")
