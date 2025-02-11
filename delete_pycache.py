import os
import shutil

def delete_pycache_dirs(root_dir):
    """Delete all __pycache__ directories recursively from the given root directory."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            if dirname == '__pycache__':
                pycache_dir = os.path.join(dirpath, dirname)
                print(f"Deleting {pycache_dir}")
                shutil.rmtree(pycache_dir)

def delete_files_with_zone(root_dir):
    """Delete all files with ':Zone.Identifier' in the filename recursively from the given root directory."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if ':Zone.Identifier' in filename:
                file_path = os.path.join(dirpath, filename)
                print(f"Deleting {file_path}")
                os.remove(file_path)

def delete_log_files(log_dir):
    """Delete all files in the specified log directory."""
    if not os.path.exists(log_dir):
        print(f"Log directory {log_dir} does not exist.")
        return

    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        if os.path.isfile(file_path):
            print(f"Deleting {file_path}")
            os.remove(file_path)
        elif os.path.isdir(file_path):
            print(f"Deleting directory {file_path}")
            shutil.rmtree(file_path)

if __name__ == "__main__":
    root_directory = "."  # Set your root directory here
    log_directory = os.path.join(root_directory, "logs")  # Construct the log directory path dynamically

    delete_pycache_dirs(root_directory)
    # delete_files_with_zone(root_directory)
    delete_log_files(log_directory)

    print("Completed deleting __pycache__ directories and log files.")
