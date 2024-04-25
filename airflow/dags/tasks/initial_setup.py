import os
import constants

# Check if the file exists before attempting to delete it
def delete_prev_scraped_file(**kwargs):
    file_path = constants.TEMP_SCRAPED_FILE_PATH
    if os.path.exists(file_path):
        # Attempt to delete the file
        try:
            os.remove(file_path)
            print(f"File '{file_path}' deleted successfully.")
        except OSError as e:
            print(f"Error: {file_path} : {e.strerror}")
    else:
        print(f"The file '{file_path}' does not exist.")
