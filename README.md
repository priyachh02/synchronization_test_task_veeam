# Syncronization script
 
Features:
- One-way synchronization (source → replica)  
- Periodic sync with a user-defined interval  
- Logs changes (file creation, update, deletion) in an Excel file  
- Clear console messages  

Requirements: 
- Python 3.7+  
- Install dependencies:  
  ```sh
  pip install pandas openpyxl

Usage:
 
 python sync_script.py <source_folder> <replica_folder> <sync_interval> <log_file.xlsx>
