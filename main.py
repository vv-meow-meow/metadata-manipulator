from datetime import datetime

from image_utils import get_image_date, replace_exif, get_jpg_files

dir_path = ""  # /Users/user/Desktop/temp
max_date = datetime(2025, 1, 1, 1, 1, 1)
change_date = datetime(2025, 1, 1)

jpg_files = get_jpg_files(dir_path)
print(jpg_files)

for file in jpg_files:
    try:
        file_date = get_image_date(file)
    except RuntimeError:
        file_date = datetime(9999, 1, 1)
    except Exception as e:
        print(e)
        print(file)
        file_date = datetime(9999, 1, 1)

    if file_date > max_date:
        print("!!!!!", file_date, 'changed to', change_date)
        try:
            replace_exif(file, change_date)
        except Exception as e:
            print(e, file)
    else:
        print(file_date)
