# .gemini/skills/filesystem-management/scripts/filesystem_watcher.py
import time
import shutil
import logging
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Robustly find the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "AI_Employee_Vault"
DROP_FOLDER = PROJECT_ROOT / "drop_zone"
INBOX_FOLDER = VAULT_PATH / "Inbox"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FileSystemWatcher")

class TaskHandler(FileSystemEventHandler):
    def __init__(self, target_folder: Path, source_type: str):
        self.target_folder = target_folder
        self.source_type = source_type
        
    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        
        # Avoid processing metadata files we might create
        if source.suffix == '.md' and ("FILE_" in source.name or "INBOX_" in source.name):
            return
            
        logger.info(f"[{self.source_type}] New file detected: {source.name}")
        
        prefix = "FILE_" if self.source_type == "DROP_ZONE" else "INBOX_"
        dest_name = f"{prefix}{source.name}"
        dest = self.target_folder / dest_name
        
        try:
            # Move or Copy based on source
            if self.source_type == "INBOX":
                # For Inbox, we move it directly to trigger processing
                shutil.move(str(source), str(dest))
                logger.info(f"Moved Inbox file: {source.name} -> {dest_name}")
            else:
                # For drop_zone, we copy it
                shutil.copy2(source, dest)
                logger.info(f"Copied drop_zone file: {source.name} -> {dest_name}")

            self.create_metadata(source, dest, self.source_type)
        except Exception as e:
            logger.error(f"Error processing {source.name}: {e}")
          
    def create_metadata(self, source: Path, dest: Path, source_type: str):
        meta_path = Path(str(dest) + ".md")
        meta_path.write_text(f'''---
type: {source_type.lower()}_task
original_name: {source.name}
status: pending
created: {time.strftime("%Y-%m-%dT%H:%M:%S")}
---

New {source_type.lower()} task ingested for processing.
Original Source: {source.absolute()}
Destination: {dest.absolute()}
''')

if __name__ == "__main__":
    # Ensure directories exist
    VAULT_PATH.mkdir(exist_ok=True)
    DROP_FOLDER.mkdir(exist_ok=True)
    INBOX_FOLDER.mkdir(exist_ok=True)
    NEEDS_ACTION.mkdir(exist_ok=True)
    
    observer = Observer()
    
    # Watcher for drop_zone
    drop_handler = TaskHandler(NEEDS_ACTION, "DROP_ZONE")
    observer.schedule(drop_handler, str(DROP_FOLDER), recursive=False)
    
    # Watcher for Inbox
    inbox_handler = TaskHandler(NEEDS_ACTION, "INBOX")
    observer.schedule(inbox_handler, str(INBOX_FOLDER), recursive=False)
    
    logger.info(f"Watching folders: {DROP_FOLDER} and {INBOX_FOLDER}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
