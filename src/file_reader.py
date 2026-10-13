"""Reads plain-text files: documents from a folder, and single text files such as prompts.

The only module that reads these files (design section 2.1). Implements EXT-001 and JOB-001.
"""

from pathlib import Path

from src.records import Document


class InputFileError(Exception):
    """A folder or file the app needs is missing or cannot be read."""


class FileReader:
    """Reads text files as UTF-8."""

    def read_documents(self, folder: Path) -> list[Document]:
        """Reads every `.txt` file in a folder, sorted by file name.

        Args:
            folder: The folder to read.

        Returns:
            One document per file. The ID is the file name.

        Raises:
            InputFileError: The folder does not exist or a file cannot be read.
        """
        if not folder.is_dir():
            raise InputFileError(f"Input folder not found: {folder}")
        paths = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix == ".txt")
        return [Document(doc_id=p.name, text=self.read_text(p)) for p in paths]

    def read_text(self, path: Path) -> str:
        """Reads one text file.

        Args:
            path: The file to read.

        Returns:
            The file content.

        Raises:
            InputFileError: The file does not exist or is not valid UTF-8.
        """
        if not path.is_file():
            raise InputFileError(f"Input file not found: {path}")
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as err:
            raise InputFileError(f"Input file cannot be read as UTF-8 text: {path}") from err
