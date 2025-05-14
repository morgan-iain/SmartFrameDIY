import os
import shutil
import time
from datetime import datetime
import pyheif
from PIL import Image, UnidentifiedImageError

# Source and destination directories
source_dir = "/home/iain/pi"
# destination_dir = "/media/iain/FRAMEUSB"
destination_dir1 = "/media/iain/FRAMEUSB1" # Alternate location of directory due to mounting issue

# Log file 
log_file = "/home/iain/runFrame_log.txt"

# def check_destination():
#     """
#     Check to see if destination directory is empty. If it is, check if alt directory contains files, if it does, return True. Else false.

#     Args:
#         None

#     Returns:
#         bool
#     """
#     if len(os.listdir(destination_dir)) == 0:
#         # Logging
#         current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
#         log = open(log_file, "a")
#         log.write(f"[{current_time}] (file_transfer.py): {destination_dir} is empty. \n")
#         log.close()
#         if len(os.listdir(destination_dir1)) == 0:
#             # Logging
#             current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
#             log = open(log_file, "a")
#             log.write(f"[{current_time}] (file_transfer.py): Neither {destination_dir} nor {destination_dir1} are valid. \n")
#             log.close()
#             return False
#         else:
#             # Logging
#             current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
#             log = open(log_file, "a")
#             log.write(f"[{current_time}] (file_transfer.py): Now using {destination_dir1} as destination directory. \n")
#             log.close()
#             return True
#     else:
#         return False
    


def is_valid_image(file_name, file_path):
    """
    Check to see if an image file is valid. If heic is not valid, try it as jpg, and if that is valid, rename it.

    Args:
        file_name (str): File name only
        file_path (str): Path to image to validate

    Returns:
        bool
    """
    try:
        if file_path.lower().endswith('.heic'):
            # Attempt to decode the HEIC image
            pyheif.read(file_path)
            return True
        else:
            # Attempt to open the file with PIL
            with Image.open(file_path) as img:
                img.verify()  # Verify the image file is valid
            return True
    except (UnidentifiedImageError, Exception) as e:
        if file_name.startswith("._"):
            # Do not log "._" files if they are here
            return False
        else:
            if file_name.lower().endswith('.heic'):
                base_name = os.path.splitext(file_name)[0]  # Get filename without extension
                temp_name = base_name + ".jpg"
                temp_path = os.path.join(source_dir, temp_name)
                os.rename(file_path, temp_path) # Rename the image
                try:
                    # Attempt to open the file with PIL
                    with Image.open(temp_path) as img:
                        img.verify()  # Verify the image file is valid
                    # Logging
                    current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    log = open(log_file, "a")
                    log.write(f"[{current_time}] (file_transfer.py): Image {file_path} converted to jpg with name {temp_path}\n")
                    log.close()
                    return True
                except Exception as e:
                    # Logging
                    current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    log = open(log_file, "a")
                    log.write(f"[{current_time}] (file_transfer.py): Image {file_path} could not be converted to jpg: {e}\n")
                    log.close()
                    os.rename(temp_path, file_path) # Rename the image back to original
                    return False
            # Logging
            current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            log = open(log_file, "a")
            log.write(f"[{current_time}] (file_transfer.py): Transfer unsuccessful for {file_path} due to {e}\n")
            log.close()
            return False

def transfer_files(destination, file_extensions=('.jpg','.jpeg','.heic')):
    """
        Monitor a source directory for new files and move any new files to a destination directory and log activity

        Args:
            destination (String): directory of destination directory
            file_extensions (tuple): list of acceptable file extensions

        Returns:
            None
    """
    for root, _, files in os.walk(source_dir):
        for file in files:
            source_path = os.path.join(root, file)
            destination_path = os.path.join(destination, file)

            if file.lower().endswith(file_extensions) and os.path.isfile(source_path) and os.path.getsize(source_path) > 0:
                if is_valid_image(str(file), str(source_path)) is not True:
                    continue
                else:
                    try:
                        # Move the file to the destination
                        shutil.move(source_path, destination_path)
                        # Log the file moved to log_file
                        with open(log_file, "a") as log:
                            current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                            log = open(log_file, "a")
                            log.write(f"[{current_time}] (file_transfer.py): Transferred {source_path} to {destination_path}\n")
                            log.close()
                    except Exception as e:
                        # Log the error to a file
                        with open(log_file, "a") as log:
                            current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                            log = open(log_file, "a")
                            log.write(f"[{current_time}] (file_transfer.py): Failed to transfer {source_path}: {e}\n")
                            log.close()

# Run the script in a loop to monitor changes
if __name__ == "__main__":
    # if not check_destination():
    #     destination = destination_dir
    # else:
    #     destination = destination_dir1
    destination = destination_dir1

    current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    log = open(log_file, "a")
    log.write(f"[{current_time}] (file_transfer.py): Monitoring {source_dir} for new files...\n")
    log.close()
    try:
        while True:
            transfer_files(destination)
            time.sleep(30)  # Check for new files every 30 seconds
    except KeyboardInterrupt:
        print(f"\nMonitoring of {source_dir} stopped.")
    except Exception as e:
        print(f"An error occurred in file_transfer.py: {e}")


