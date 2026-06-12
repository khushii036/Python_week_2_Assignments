import os
import shutil
import logging
import argparse
from pathlib import Path

# File categories and extensions
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv", ".flv"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
    "Code": [".py", ".java", ".cpp", ".c", ".js", ".html", ".css", ".php"]
}


def setup_logging():
    logging.basicConfig(
        filename="organizer.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def get_category(extension):
    extension = extension.lower()

    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category

    return "Others"


def get_unique_filename(destination_folder, filename):
    """
    Handle duplicate filenames by appending a counter.
    Example:
    report.pdf -> report_1.pdf -> report_2.pdf
    """
    file_path = destination_folder / filename

    if not file_path.exists():
        return file_path

    stem = file_path.stem
    suffix = file_path.suffix
    counter = 1

    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = destination_folder / new_name

        if not new_path.exists():
            return new_path

        counter += 1


def organize_files(source_directory, dry_run=False):
    source_path = Path(source_directory)

    if not source_path.exists():
        print(f"Error: Directory '{source_directory}' does not exist.")
        return

    moved_files = 0

    for item in source_path.iterdir():

        # Skip directories
        if item.is_dir():
            continue

        # Skip hidden files
        if item.name.startswith('.'):
            continue

        category = get_category(item.suffix)

        destination_folder = source_path / category

        if not destination_folder.exists():
            if dry_run:
                print(f"[DRY RUN] Create folder: {destination_folder}")
            else:
                destination_folder.mkdir(exist_ok=True)

        destination_file = get_unique_filename(
            destination_folder,
            item.name
        )

        if dry_run:
            print(f"[DRY RUN] Move '{item.name}' -> '{category}/{destination_file.name}'")
        else:
            shutil.move(str(item), str(destination_file))

            logging.info(
                f"Moved '{item.name}' -> '{destination_file}'"
            )

        moved_files += 1

    print("\n========== SUMMARY ==========")
    print(f"Files processed: {moved_files}")
    print(f"Mode: {'DRY RUN' if dry_run else 'ACTUAL MOVE'}")
    print("=============================")


def main():
    parser = argparse.ArgumentParser(
        description="Organize files into categorized folders."
    )

    parser.add_argument(
        "directory",
        help="Source directory containing files"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without moving files"
    )

    args = parser.parse_args()

    setup_logging()

    organize_files(
        args.directory,
        args.dry_run
    )


if __name__ == "__main__":
    main()