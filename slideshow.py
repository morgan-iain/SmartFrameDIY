import cv2
import os
import numpy as np
from PIL import Image, UnidentifiedImageError
import pyheif
import time
import random
import threading
from datetime import datetime

# Log file 
log_file = "/home/iain/runFrame_log.txt"

# File list
file_list = "/home/iain/file_list.txt"

# Directory for image directory
# source = "/media/iain/FRAMEUSB"
source1 = "/media/iain/FRAMEUSB1" # alternate due to mounting issue

# Global list for image paths to be accessed and updated by multiple functions/threads
image_paths = []
# Global list locker
list_lock = threading.Lock()

# def check_source():
#     """
#     Check to see if destination directory is empty. If it is, check if alt directory contains files, if it does, return True. Else false.

#     Args:
#         None

#     Returns:
#         bool
#     """
#     if len(os.listdir(source)) == 0:
#         # Logging
#         current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
#         log = open(log_file, "a")
#         log.write(f"[{current_time}] (file_transfer.py): {source} is empty. \n")
#         log.close()
#         if len(os.listdir(source1)) == 0:
#             # Logging
#             current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
#             log = open(log_file, "a")
#             log.write(f"[{current_time}] (file_transfer.py): Neither {source} nor {source1} are valid. \n")
#             log.close()
#             return False
#         else:
#             # Logging
#             current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
#             log = open(log_file, "a")
#             log.write(f"[{current_time}] (file_transfer.py): Now using {source1} as destination directory. \n")
#             log.close()
#             return True
#     else:
#         return False

def is_valid_image(file_name, directory):
    """
    Check to see if an image file is valid. If heic is not valid, try it as jpg, and if that is valid, rename it. 

    Args:
        file_name (str): File name only
        directory (str): Directory containing image files

    Returns:
        bool
    """
    file_path = os.path.join(directory, file_name)
    try:
        if file_name.lower().endswith('.heic'):
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
            # Do not log "._" files
            return False
        else:
            if file_name.lower().endswith('.heic'):
                base_name = os.path.splitext(file_name)[0]  # Get filename without extension
                temp_name = base_name + ".jpg"
                temp_path = os.path.join(directory, temp_name)
                os.rename(file_path, temp_path) # Rename the image
                try:
                    # Attempt to open the file with PIL
                    with Image.open(temp_path) as img:
                        img.verify()  # Verify the image file is valid
                    # Logging
                    current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    log = open(log_file, "a")
                    log.write(f"[{current_time}] (slideshow.py): Image {file_path} converted to jpg with name {temp_path}\n")
                    log.close()
                    return True
                except Exception as e:
                    # Logging
                    current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    log = open(log_file, "a")
                    log.write(f"[{current_time}] (slideshow.py): Image {file_path} could not be converted to jpg: {e}\n")
                    log.close()
                    os.rename(temp_path, file_path) # Rename the image back to original
                    return False
            else:
                # Logging
                current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                log = open(log_file, "a")
                log.write(f"[{current_time}] (slideshow.py): Image {file_path} will not be displayed due to {e}\n")
                log.close()
                return False

def load_current_paths(directory,file_extensions=('.jpg','.jpeg','.heic')):
    """
    Scan a directory and return a unique, shuffled list of file paths of files with given file extensions

    Args:
        directory (str): Path to the directory to scan.
        file_extensions (tuple): Extensions of files to monitor (e.g., .jpg, .heic).

    Returns:
        paths (list)
    """
    # Using global list 
    global image_paths
    prefix = "._"
    # Scan each file in a directory
    with os.scandir(directory) as files:
        for file in files:
            if file.name.lower().endswith(file_extensions) and os.path.isfile(os.path.join(directory, file.name)):
                if is_valid_image(file.name, directory) is not True:
                    continue
                else:
                    # Remove "._" prefix from file name; it's some weird macOS artifact from original file import from iPhoto; I found through testing that removing this is needed
                    if file.name.startswith(prefix):
                        clean_name = file.name.removeprefix(prefix)
                        clean_path_name = os.path.join(directory,clean_name)
                        with list_lock:
                            image_paths.append(clean_path_name)
                    else:
                        clean_path_name = os.path.join(directory,file.name)
                        with list_lock:
                            image_paths.append(clean_path_name)
    
    with list_lock:
        # Ensure item uniqueness within list
        image_paths = list(dict.fromkeys(image_paths))
        # Shuffle list
        random.shuffle(image_paths)
    
    listy = open(file_list, "a")
    for i in range(len(image_paths)):
        listy.write(f"[{i}]: {image_paths[i]}\n")
    listy.close()

    # Logging
    current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    log = open(log_file, "a")
    log.write(f"[{current_time}] (slideshow.py): {len(image_paths)} image paths successfully loaded in load_current_paths()\n")
    log.close()

def monitor_directory(directory, file_extensions=('.jpg','.jpeg','.heic'), check_interval=60):
    """
    Continuously monitor a directory for new files with specific extensions.

    Args:
        directory (str): Path to the directory to monitor.
        file_extensions (tuple): Extensions of files to monitor (e.g., .jpg, .heic).
        check_interval (int): Time interval (in seconds) between scans.

    Returns:
        None
    """
     # Using global list 
    global image_paths

    # Logging
    current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    log = open(log_file, "a")
    log.write(f"[{current_time}] (slideshow.py): Starting monitor_directory()\n")
    log.close()

    try:
        while True:
            i = 0
            current_files = []
            prefix = "._"
            # Get all matching files in the directory
            with os.scandir(directory) as files:
                for file in files:
                    if file.name.lower().endswith(file_extensions) and os.path.isfile(os.path.join(directory, file.name)):
                        # Remove "_." prefix from file name; it's some weird macOS artifact from original file import from iPhoto; I found through testing that removing this is needed
                        if file.name.startswith(prefix):
                            clean_name = file.name.removeprefix(prefix)
                            clean_path_name = current_files.append(os.path.join(directory,clean_name))
                            current_files.append(clean_path_name)
                            i += 1
                        else:
                            clean_path_name = current_files.append(os.path.join(directory,file.name))
                            current_files.append(clean_path_name)
                            i += 1
            # Ensure list of files is unique
            current_files = list(dict.fromkeys(current_files))
            # Create local copy of image_paths to avoid unwanted effects from converting global list to set and back
            tracked_files = image_paths

            new_files = set()
            # Find new files by comparing current list of files in directory to previous list; convert lists to sets to quickly find difference between them
            new_files = set(current_files) - set(tracked_files)

            if None in new_files and len(new_files) > 1:
                new_files.remove(None)

            if len(new_files) >= 1 and None not in new_files:
                with list_lock:
                    image_paths.extend(list(new_files))
                # Logging
                current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                log = open(log_file, "a")
                log.write(f"[{current_time}] (slideshow.py): {len(new_files)} images added to {directory} in monitor_directory()\n")
                log.write(f"[{current_time}] (slideshow.py): Files added are [{new_files}]\n")
                log.close()
            else:
                # Logging
                current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                log = open(log_file, "a")
                log.write(f"[{current_time}] (slideshow.py): No new files found in {directory} in monitor_directory()\n")
                log.close()
            
            # Wait before scanning again
            time.sleep(check_interval)
    except KeyboardInterrupt:
        print(f"\nMonitoring of {directory} stopped.")
    except Exception as e:
        print(f"An error occurred in slideshow.py: {e}")

def get_image(filepath):
    """
    Get .jpg or .heic image from a file path and return the image object

    Args:
        filepath (str): Image file path.

    Returns:
        img (Object)
    """
    if filepath.lower().endswith(".jpg") or filepath.lower().endswith(".jpeg"):
        img = cv2.imread(filepath)
        if img is None:
            # Logging
            current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            log = open(log_file, "a")
            log.write(f"[{current_time}] (slideshow.py): Failure in get_image() with: {filepath}\n")
            log.close()
            return img
        else:
            return img
    elif filepath.lower().endswith(".heic"):
        try:
            heif_file = pyheif.read(filepath)
            pil_image = Image.frombytes(
                heif_file.mode, 
                heif_file.size, 
                heif_file.data, 
                "raw", 
                heif_file.mode, 
                heif_file.stride
            )
            return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except pyheif.errors.HeifError as e:
            # Logging
            current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            log = open(log_file, "a")
            log.write(f"[{current_time}] (slideshow.py): Failure in get_image() with: {filepath} and error [{e}]\n")
            log.close()
    return None

def resize_and_center(image, screen_width, screen_height):
    """
    Resizes the image to fit within the screen dimensions while maintaining the aspect ratio. Adds black padding to fill the rest of the screen.

    Args:
        img (image object): Image data.
        screen_width (int): Number of pixels in screen width.
        screen_height (int): Number of pixels in screen height.

    Returns:
        canvas (np array)
    """
    img_height, img_width = image.shape[:2]

    # Calculate the scaling factor to fit the image within the screen
    scale = min(screen_width / img_width, screen_height / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    # Resize the image
    resized_image = cv2.resize(image, (new_width, new_height))

    # Create a black background
    canvas = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    # Center the resized image on the black background
    x_offset = (screen_width - new_width) // 2
    y_offset = (screen_height - new_height) // 2
    canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_image

    return canvas

def load_and_resize(filepath, screen_width, screen_height):
    """
    Loads and resizes an image to fit the screen

    Args:
        filepath (str): Image file path.
        width (int): Number of pixels in screen width.
        height (int): Number of pixels in screen height.

    Returns:
        canvas (np array) via call to resize_and_center()
    """
    img = get_image(filepath)
    if img is not None:
        return resize_and_center(img, screen_width, screen_height)
    return None

def slideshow(screen_width=1280, screen_height=800, display_time=8000, transition_steps=30, transition_delay=50):
    """
    Displays a slideshow with cross-fade transitions, ensuring images are centered with black background.

    Args:
        screen_width (int): Number of pixels in screen width.
        screen_height (int): Number of pixels in screen height.
        display_time (int): Image display time in milliseconds.
        transition_steps (int): Number of transition steps in cross-fade transition
        transition_delay (int): Time in milliseconds before transition can begin

    Returns:
        None
    """
    global image_paths
    # Logging
    current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    log = open(log_file, "a")
    log.write(f"[{current_time}] (slideshow.py): Slideshow beginning with {len(image_paths)} images\n")
    log.close()

    # Set up a full-screen window
    window_name = "Slideshow"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    i = 0
    while i < len(image_paths):
        # Load and process the current and next images; img2 handles restarting the loop due to % operator
        img1 = load_and_resize(image_paths[i % len(image_paths)], screen_width, screen_height)
        img2 = load_and_resize(image_paths[(i + 1) % len(image_paths)], screen_width, screen_height)

        curr_image_path = image_paths[i % len(image_paths)]
        next_image_path = image_paths[(i + 1) % len(image_paths)]
    
        if img1 is None:
            # Logging
            current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            log = open(log_file, "a")
            log.write(f"[{current_time}] (slideshow.py): Skipped img1 in slideshow() due to 'None': {curr_image_path}\n")
            log.close()
            i += 1
            continue
        elif img2 is None:
            # Logging
            current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            log = open(log_file, "a")
            log.write(f"[{current_time}] (slideshow.py): Skipped img2 in slideshow() due to 'None': {next_image_path}\n")
            log.close()
            i += 1
            continue

        # Display the current image
        cv2.imshow(window_name, img1)
        if cv2.waitKey(display_time) & 0xFF == 27:  # Exit on ESC key
            break

        # Perform cross-fade transition
        for alpha in np.linspace(0, 1, transition_steps):
            blended = cv2.addWeighted(img1, 1 - alpha, img2, alpha, 0)
            cv2.imshow(window_name, blended)
            if cv2.waitKey(transition_delay) & 0xFF == 27:  # Exit on ESC key
                break
        
        # Have the loop run indefinitely, until the raspi is power cycled or PID of .py file is killed
        if i > 0 and (i+1)%len(image_paths) == 0:
            # Logging
            current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            log = open(log_file, "a")
            log.write(f"[{current_time}] (slideshow.py): Slideshow restarting after image {curr_image_path}\n")
            log.close()
            i = 0
            continue
        
        i += 1

    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Directory to monitor for new images added to /media/iain/FRAMEUSB from /home/iain/pi samba server via file_transfer.py
    # if not check_source():
    #     directory_to_watch = source
    # else:
    #     directory_to_watch = source1
    directory_to_watch = source1

    listy = open(file_list, "w")
    listy.close()

    load_current_paths(directory_to_watch)

    if not image_paths:
        print("No images found in the specified directory!")
    else:
        print('slideshow execute')
        # Start monitoring via thread
        thread = threading.Thread(target=monitor_directory,args=(directory_to_watch,))
        thread.start()
        # Start slideshow
        slideshow()
