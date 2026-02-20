# filesystem_watcher.py
import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FileSystemWatcher")

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str, drop_folder: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'
        self.drop_folder = Path(drop_folder)
        
    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        # Avoid processing metadata files we might create
        if source.suffix == '.md' and "FILE_" in source.name:
            return
            
        logger.info(f"New file detected: {source.name}")
        dest = self.needs_action / f'FILE_{source.name}'
        
        try:
            # Copy file to Needs_Action folder
            shutil.copy2(source, dest)
            self.create_metadata(source, dest)
            logger.info(f"Successfully processed: {source.name}")
        except Exception as e:
            logger.error(f"Error processing {source.name}: {e}")
          
    def create_metadata(self, source: Path, dest: Path):
        meta_path = dest.with_suffix('.md')
        meta_path.write_text(f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
status: pending
---

New file dropped for processing. Original source: {source.absolute()}
''')

if __name__ == "__main__":
    VAULT_PATH = "AI_Employee_Vault"
    DROP_FOLDER = "drop_zone"
    
    # Ensure directories exist
    Path(VAULT_PATH).mkdir(exist_ok=True)
    Path(DROP_FOLDER).mkdir(exist_ok=True)
    
    event_handler = DropFolderHandler(VAULT_PATH, DROP_FOLDER)
    observer = Observer()
    observer.schedule(event_handler, DROP_FOLDER, recursive=False)
    
    logger.info(f"Watching folder: {DROP_FOLDER}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
