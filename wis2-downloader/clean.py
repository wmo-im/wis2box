import os
import time

# get download dir from environment variable
download_dir = os.environ.get('DOWNLOAD_DIR', '/app/downloads')
# get retention period from environment variable
retention_period_hours = int(os.environ.get('RETENTION_PERIOD_HOURS', 24))

def clean_directory(directory):
    # get the current time
    current_time = time.time()

    files_removed = 0
    directories_removed = 0
    # loop through the files in the directory, including subdirectories
    for file in os.listdir(directory):
        # get the full path of the file
        file_path = os.path.join(directory, file)
        # check if the path is a file or a directory
        if os.path.isfile(file_path):
            # get the time the file was last modified
            file_time = os.path.getmtime(file_path)
            # check if the file is older than the retention period
            if current_time - file_time > retention_period_hours * 3600:
                os.remove(file_path)
                files_removed += 1
        elif os.path.isdir(file_path):
            # recursively clean the directory
            clean_directory(file_path)
            # if the directory is empty, remove it
            if not os.listdir(file_path):
                os.rmdir(file_path)
                directories_removed += 1
    print(f'CLEANER: removed {files_removed} old files and {directories_removed} empty directories')

# start cleaning from the download directory
clean_directory(download_dir)
