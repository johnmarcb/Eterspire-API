#!/usr/bin/env python3
"""
Eterspire API Data Generator - File Watcher
Automatically runs the data pipeline when files in manual-download folder change.
"""

import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from main import main as run_pipeline


class ManualDownloadHandler(FileSystemEventHandler):
    """Handles file system events in the manual-download folder"""
    
    def __init__(self, debounce_seconds=2):
        super().__init__()
        self.debounce_seconds = debounce_seconds
        self.last_modified = 0
        self.is_processing = False
    
    def should_process(self, event):
        """Check if we should process this event"""
        # Ignore directory events
        if event.is_directory:
            return False
        
        # Only process HTML files
        if not event.src_path.endswith('.html'):
            return False
        
        # Ignore temporary/hidden files
        filename = os.path.basename(event.src_path)
        if filename.startswith('.') or filename.startswith('~'):
            return False
        
        return True
    
    def trigger_pipeline(self, event_type, filepath):
        """Run the data pipeline with debouncing"""
        current_time = time.time()
        
        # Debounce: don't run if we just ran recently
        if current_time - self.last_modified < self.debounce_seconds:
            return
        
        # Don't run if already processing
        if self.is_processing:
            print(f"\n⏳ Pipeline already running, ignoring {event_type} event...")
            return
        
        self.last_modified = current_time
        self.is_processing = True
        
        try:
            filename = os.path.basename(filepath)
            print(f"\n{'=' * 60}")
            print(f"🔔 DETECTED: {event_type.upper()} - {filename}")
            print(f"{'=' * 60}")
            print(f"⚡ Auto-running pipeline...\n")
            
            # Run the pipeline
            run_pipeline()
            
            print(f"\n{'=' * 60}")
            print(f"✅ Pipeline completed for: {filename}")
            print(f"{'=' * 60}")
            print(f"\n👀 Watching for changes... (Press Ctrl+C to stop)")
            
        except Exception as e:
            print(f"\n❌ ERROR during pipeline execution: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_processing = False
    
    def on_created(self, event):
        """Called when a file is created"""
        if self.should_process(event):
            self.trigger_pipeline('created', event.src_path)
    
    def on_modified(self, event):
        """Called when a file is modified"""
        if self.should_process(event):
            self.trigger_pipeline('modified', event.src_path)


def watch_manual_download():
    """Start watching the manual-download folder"""
    
    watch_folder = 'manual-download'
    
    # Create the folder if it doesn't exist
    if not os.path.exists(watch_folder):
        print(f"📁 Creating {watch_folder} folder...")
        os.makedirs(watch_folder)
    
    print("\n" + "=" * 60)
    print("👀 ETERSPIRE API - FILE WATCHER")
    print("=" * 60)
    print(f"\n📂 Watching folder: {os.path.abspath(watch_folder)}")
    print(f"🔍 Monitoring for: .html files")
    print(f"⚡ Will auto-run pipeline on changes")
    print(f"\n{'=' * 60}")
    print("✅ Watcher started! Waiting for file changes...")
    print("   (Press Ctrl+C to stop)")
    print("=" * 60 + "\n")
    
    # Create event handler and observer
    event_handler = ManualDownloadHandler(debounce_seconds=2)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopping file watcher...")
        observer.stop()
    
    observer.join()
    print("✅ File watcher stopped\n")


if __name__ == "__main__":
    try:
        watch_manual_download()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

