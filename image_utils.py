"""
EXIF handling utilities for image processing.

Provides functionality for:
- Finding image files
- Reading/updating EXIF metadata
- Date comparisons and adjustments
"""

import logging
import os
from datetime import datetime
from typing import Union, Generator

import piexif
from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ImageFile import ImageFile


class EXIFHandler:
    """Handles EXIF operations for image files."""

    _VALID_HOURS = (
        "00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
        "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
        "20", "21", "22", "23"
    )

    def __init__(self, default_date: datetime = datetime(9999, 1, 1)):
        self.default_date = default_date

    @classmethod
    def print_metadata(cls, image: Union[ImageFile, str]) -> None:
        """Print all EXIF metadata for an image.

        Args:
            image (Union[ImageFile, str]): Image object or file path
        """
        img = cls._open_image(image)
        try:
            exif_data = img.getexif()
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                print(f"{tag_name:25}: {value}")
        finally:
            if isinstance(image, str):
                img.close()

    @staticmethod
    def find_images(directory: str) -> Generator[str, None, None]:
        """Find JPG/JPEG files recursively in a directory.

        Args:
            directory (str): Path to search for images

        Yields:
            str: Full path to found image files
        """
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.lower().endswith((".jpg", ".jpeg")):
                    yield os.path.join(root, filename)

    def get_image_date(self, image: Union[ImageFile, str]) -> datetime:
        """Extract and validate creation date from EXIF data.

        Args:
            image (Union[ImageFile, str]): Image object or file path

        Returns:
            datetime: Validated creation date, otherwise if not found EXIF returns self.default_date

        Raises:
            ValueError: If date format is invalid
        """
        img = self._open_image(image)
        try:
            exif_data = img.getexif()
            date_str = exif_data.get(piexif.ImageIFD.DateTime)
            # TODO: also check for DateTimeOriginal and DateTimeDigitized

            if not date_str:
                logging.warning(f"No EXIF date found for {image if isinstance(image, str) else 'image'}")
                return self.default_date

            date_str = self._fix_invalid_hours(date_str, image)
            return self._parse_datetime(date_str, image)
        finally:
            if isinstance(image, str):
                img.close()

    def update_exif_date(self, file_path: str, new_date: datetime) -> None:
        """Update EXIF datetime tags in an image file.

        Args:
            file_path (str): Path to image file
            new_date (datetime): New datetime to set

        Raises:
            RuntimeError: If EXIF update fails
        """
        try:
            exif_dict = self._load_exif_data(file_path)
            date_bytes = new_date.strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')

            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_bytes
            exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_bytes
            exif_dict["0th"][piexif.ImageIFD.DateTime] = date_bytes

            self._save_exif_data(file_path, exif_dict)
            logging.info(f"Updated EXIF date for {file_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to update {file_path}") from e

    @classmethod
    def _fix_invalid_hours(cls, date_str: str, image: Union[ImageFile, str]) -> str:
        """Fix invalid 24-hour format dates."""
        if date_str[11:13] not in cls._VALID_HOURS:
            logging.warning(f"Invalid hour in {date_str} for {image}, correcting to 00")
            return f"{date_str[:11]}00{date_str[13:]}"
        return date_str

    @staticmethod
    def _open_image(image: Union[ImageFile, str]) -> ImageFile:
        """Safe image opening helper."""
        return Image.open(image) if isinstance(image, str) else image

    @staticmethod
    def _parse_datetime(date_str: str, image: Union[ImageFile, str]) -> datetime:
        """Parse datetime string with validation."""
        try:
            return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        except ValueError as e:
            logging.error(f"Invalid date format {date_str} in {image}")
            raise ValueError(f"Invalid date format in {image}") from e

    @staticmethod
    def _load_exif_data(file_path: str) -> dict:
        """Load existing EXIF data or create new structure."""
        with Image.open(file_path) as img:
            try:
                return piexif.load(img.info["exif"])
            except (KeyError, ValueError):
                logging.info(f"Creating new EXIF data for {file_path}")
                return {"0th": {}, "Exif": {}}

    @staticmethod
    def _save_exif_data(file_path: str, exif_dict: dict) -> None:
        """Save EXIF data to file."""
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file_path)
