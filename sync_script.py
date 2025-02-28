import os
import shutil
import time
import hashlib
import argparse
import pandas as pd
from datetime import datetime

try:
    import openpyxl
except ImportError:
    print("⚠️ Missing dependency: Installing 'openpyxl' for Excel support...")
    os.system("pip install openpyxl")

def calculate_md5(file_path):
    """Calculate MD5 checksum of a file to detect changes."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def log_to_excel(log_file, action, details):
    """Log synchronization actions to an Excel file with a timestamp."""
    
    if not log_file.endswith(".xlsx"):
        log_file = log_file.replace(".txt", ".xlsx")
    
    if os.path.exists(log_file):
        df = pd.read_excel(log_file, engine='openpyxl')
    else:
        df = pd.DataFrame(columns=["Timestamp", "Action", "Details"])

    new_entry = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Action": action,
        "Details": details
    }])

    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_excel(log_file, index=False, engine='openpyxl')

def sync_folders(source, replica, log_file):
    """Synchronize source folder to replica folder."""
    print("\n==================================================")
    print(f"🔹 Syncing: {source} -> {replica}")
    print("==================================================")

    changes_detected = False  

    if not os.path.exists(replica):
        os.makedirs(replica)
        log_to_excel(log_file, "Created Folder", f"Replica folder created: {replica}")
        changes_detected = True

    for root, _, files in os.walk(source):
        rel_path = os.path.relpath(root, source)
        target_path = os.path.join(replica, rel_path)

        if not os.path.exists(target_path):
            os.makedirs(target_path)
            log_to_excel(log_file, "Created Folder", f"Created: {target_path}")
            changes_detected = True

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(target_path, file)

            if not os.path.exists(replica_file) or calculate_md5(source_file) != calculate_md5(replica_file):
                shutil.copy2(source_file, replica_file)
                log_to_excel(log_file, "Copied File", f"Copied: {source_file} -> {replica_file}")
                print(f"✅ Copied: {source_file} -> {replica_file}")
                changes_detected = True

    for root, _, files in os.walk(replica, topdown=False):
        rel_path = os.path.relpath(root, replica)
        source_path = os.path.join(source, rel_path)

        if not os.path.exists(source_path):
            shutil.rmtree(root)
            log_to_excel(log_file, "Removed Folder", f"Deleted: {root}")
            print(f"❌ Removed Folder: {root}")
            changes_detected = True

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_path, file)

            if not os.path.exists(source_file):
                os.remove(replica_file)
                log_to_excel(log_file, "Removed File", f"Deleted: {replica_file}")
                print(f"❌ Removed File: {replica_file}")
                changes_detected = True

    if changes_detected:
        print("🔄 Sync Completed ✅")
    else:
        print("✅ No Changes Detected. Sync is Up-to-Date!")

def main():
    """Parse command-line arguments and start synchronization loop."""
    parser = argparse.ArgumentParser(description="Folder Synchronization Tool")
    parser.add_argument("source", help="Path to the source folder")
    parser.add_argument("replica", help="Path to the replica folder")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log", help="Path to log file (.xlsx for Excel logs)")

    args = parser.parse_args()

    print("\n🚀 Starting Folder Synchronization...")
    while True:
        try:
            sync_folders(args.source, args.replica, args.log)
            print(f"⏳ Waiting {args.interval} seconds before next sync...\n")
            time.sleep(args.interval)
        except Exception as e:
            log_to_excel(args.log, "Error", f"Unexpected error: {e}")
            print(f"⚠️ Error: {e}")
            time.sleep(args.interval)

if __name__ == "__main__":
    main()
