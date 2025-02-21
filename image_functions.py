import os
import logging
from datetime import datetime
from typing import Union, List

from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ImageFile import ImageFile
import piexif


def get_jpg_files(directory: str) -> List[str]:
    """Collects all JPG files in a directory recursively.

    Args:
        directory (str): Path to the directory to search for JPG files.

    Returns:
        List[str]: List of full paths to JPG files in the directory and subdirectories.

    Example:
        >>> get_jpg_files("/path/to/photos")
        ['/path/to/photos/image1.jpg', '/path/to/photos/party/image2.jpg']
    """
    return [
        os.path.join(root, filename)
        for root, _, files in os.walk(directory)
        for filename in files
        if filename.lower().endswith('.jpg')
    ]


def print_metadata(image: ImageFile) -> None:
    """Prints all metadata entries from an image's EXIF data.

    Args:
        image (ImageFile): PIL ImageFile object to examine.

    Example:
        >>> with Image.open("image.jpg") as img:
        >>>     print_metadata(img)
    """
    exif_data = image.getexif()
    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, tag_id)
        print(f"{tag_name:25}: {value}")


def get_image_date(image: Union[ImageFile, str]) -> datetime:
    """Extracts and validates the creation date from an image's EXIF data.

    Args:
        image (Union[ImageFile, str]): Either a PIL ImageFile object or path string.

    Returns:
        datetime: Parsed creation datetime from EXIF metadata.

    Raises:
        RuntimeError: If no creation date found in EXIF data
        ValueError: If datetime format is invalid

    Example:
        >>> get_image_date("image.jpg")
        datetime.datetime(2023, 8, 15, 12, 30, 0)
    """
    path = None
    exif_data = None

    if isinstance(image, str):
        path = image
        with Image.open(path) as img:
            exif_data = img.getexif()
    else:
        exif_data = image.getexif()

    creation_date = exif_data.get(piexif.ImageIFD.DateTime)
    if not creation_date:
        raise RuntimeError(f"No creation date found for image: {path or 'provided ImageFile'}")

    if len(creation_date) >= 20 and creation_date[11:13] == "24":
        logging.warning(f"Invalid hour (24) in {creation_date} for {path}, correcting to 00")
        creation_date = f"{creation_date[:11]}00{creation_date[13:]}"

    try:
        return datetime.strptime(creation_date, "%Y:%m:%d %H:%M:%S")
    except ValueError as e:
        raise ValueError(f"Invalid datetime format '{creation_date}' in {path or 'image'}") from e


def compare_image_data(left: Union[ImageFile, str], right: datetime) -> bool:
    """Compares image creation date against a reference datetime.

    Args:
        left (Union[ImageFile, str]): Image to check (path or ImageFile object)
        right (datetime): Reference datetime for comparison

    Returns:
        bool: True if image date is earlier than or equal to reference datetime

    Example:
        >>> compare_image_data("image.jpg", datetime(2023, 12, 31))
        True
    """
    return get_image_date(left) <= right


def replace_exif(file: str, datetime_object: datetime) -> None:
    """Replaces EXIF datetime tags in an image file with specified datetime.

    Updates three EXIF datetime fields:
    - DateTimeOriginal (36867)
    - DateTimeDigitized (36868)
    - DateTime (306)

    Args:
        file (str): Path to image file
        datetime_object (datetime): Datetime to write to EXIF tags

    Raises:
        RuntimeError: If EXIF processing or file writing fails

    Example:
        >>> replace_exif("image.jpg", datetime(2023, 1, 1, 12, 0))
    """
    try:
        with Image.open(file) as img:
            try:
                exif_dict = piexif.load(img.info['exif'])
                logging.info(f"Loaded existing EXIF data from {file}")
            except KeyError:
                logging.warning(f"No EXIF data in {file}, creating new")
                exif_dict = {"0th": {}, "Exif": {}}
    except Exception as e:
        raise RuntimeError(f"Failed to process {file}") from e

    date_str = datetime_object.strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')

    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str
    exif_dict["0th"][piexif.ImageIFD.DateTime] = date_str

    try:
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file)
        logging.info(f"Successfully updated EXIF data in {file}")
    except Exception as e:
        raise RuntimeError(f"Failed to write EXIF data to {file}") from e
