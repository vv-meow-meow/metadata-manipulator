"""
Main EXIF processing script.

Handles batch processing of image files to:
- Check creation dates
- Update EXIF data for files beyond threshold date
"""

from datetime import datetime
from image_utils import EXIFHandler


class EXIFProcessor:
    """Main EXIF processing pipeline."""

    def __init__(self, max_date: datetime, change_date: datetime):
        """
        Args:
            max_date (datetime): Threshold date for comparison
            change_date (datetime): Date to set for exceeded files
        """
        self.max_date = max_date
        self.change_date = change_date
        self.exif_handler = EXIFHandler()

    def process_directory(self, directory: str) -> None:
        """Process all images in directory.

        Args:
            directory (str): Path to directory with images
        """
        file_count = 0
        updated_count = 0

        for file_path in self.exif_handler.find_images(directory):
            file_count += 1
            try:
                if self._needs_update(file_path):
                    self._update_file(file_path)
                    updated_count += 1
            except Exception as e:
                self._handle_error(file_path, e)

        print(f'Processed {file_count} files, updated {updated_count}')

    def _needs_update(self, file_path: str) -> bool:
        """Check if a file requires date update."""
        file_date = self.exif_handler.get_image_date(file_path)
        print(f"Found date {file_date} for {file_path}")
        return file_date > self.max_date

    def _update_file(self, file_path: str) -> None:
        """Perform EXIF update on file."""
        print(f"Updating {file_path} to {self.change_date}")
        self.exif_handler.update_exif_date(file_path, self.change_date)

    @staticmethod
    def _handle_error(file_path: str, error: Exception) -> None:
        """Handle processing errors."""
        print(f"Error processing {file_path}: {str(error)}")


def main():
    """Main execution flow."""
    DIR_PATH = "/path/to/images"
    MAX_DATE = datetime(2025, 1, 1, 1, 1, 1)
    CHANGE_DATE = datetime(2025, 1, 1)

    processor = EXIFProcessor(MAX_DATE, CHANGE_DATE)
    processor.process_directory(DIR_PATH)


if __name__ == '__main__':
    main()
