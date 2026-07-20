"""
File System & Archive Manager Module for X Assistant (Phase 3).
Handles file/folder creation, renaming, moving, copying, safety-gated deletion, and ZIP archiving.
"""

import os
import shutil
import zipfile
from pathlib import Path
from typing import Optional, List
from core.logger import logger
from core.database import db


class FileOrganizer:
    """Manages local Windows file system operations and ZIP archives."""

    def create_directory(self, dir_path: str) -> str:
        """Create new directory path."""
        try:
            target = Path(dir_path).resolve()
            target.mkdir(parents=True, exist_ok=True)
            msg = f"Created directory: '{target}'."
            logger.info(msg)
            db.log_command("create_dir", "SUCCESS", str(target))
            return msg
        except Exception as err:
            logger.error(f"Failed to create directory '{dir_path}': {err}")
            return f"Failed to create directory: {err}"

    def rename_item(self, source_path: str, new_name: str) -> str:
        """Rename file or folder."""
        try:
            src = Path(source_path).resolve()
            if not src.exists():
                return f"Source path '{source_path}' does not exist."

            dest = src.parent / new_name
            src.rename(dest)
            msg = f"Renamed '{src.name}' to '{new_name}'."
            logger.info(msg)
            db.log_command("rename_item", "SUCCESS", f"{src} -> {dest}")
            return msg
        except Exception as err:
            logger.error(f"Failed to rename item '{source_path}': {err}")
            return f"Failed to rename: {err}"

    def copy_item(self, source_path: str, destination_dir: str) -> str:
        """Copy file or directory."""
        try:
            src = Path(source_path).resolve()
            dest_dir = Path(destination_dir).resolve()
            dest_dir.mkdir(parents=True, exist_ok=True)

            if not src.exists():
                return f"Source path '{source_path}' does not exist."

            dest_path = dest_dir / src.name
            if src.is_dir():
                shutil.copytree(src, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest_path)

            msg = f"Copied '{src.name}' to '{dest_dir}'."
            logger.info(msg)
            db.log_command("copy_item", "SUCCESS", f"{src} -> {dest_path}")
            return msg
        except Exception as err:
            logger.error(f"Failed to copy item '{source_path}': {err}")
            return f"Failed to copy: {err}"

    def move_item(self, source_path: str, destination_dir: str) -> str:
        """Move file or directory."""
        try:
            src = Path(source_path).resolve()
            dest_dir = Path(destination_dir).resolve()
            dest_dir.mkdir(parents=True, exist_ok=True)

            if not src.exists():
                return f"Source path '{source_path}' does not exist."

            shutil.move(str(src), str(dest_dir))
            msg = f"Moved '{src.name}' to '{dest_dir}'."
            logger.info(msg)
            db.log_command("move_item", "SUCCESS", f"{src} -> {dest_dir}")
            return msg
        except Exception as err:
            logger.error(f"Failed to move item '{source_path}': {err}")
            return f"Failed to move item: {err}"

    def delete_item(self, path: str, confirmed: bool = False) -> str:
        """
        Delete file or directory with mandatory confirmation check.
        
        Args:
            path: Target file/folder path.
            confirmed: Must be True to proceed with deletion.
        """
        if not confirmed:
            return f"SECURITY ALERT: Deleting '{path}' requires user confirmation. Say confirm to proceed."

        try:
            target = Path(path).resolve()
            if not target.exists():
                return f"Target path '{path}' does not exist."

            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()

            msg = f"Deleted: '{target.name}'."
            logger.info(msg)
            db.log_audit_event("DELETE_FILE", str(target), user_confirmed=True, status="SUCCESS")
            return msg
        except Exception as err:
            logger.error(f"Failed to delete item '{path}': {err}")
            return f"Failed to delete item: {err}"

    def compress_to_zip(self, source_path: str, zip_output_name: Optional[str] = None) -> str:
        """Compress file or directory into a ZIP archive."""
        try:
            src = Path(source_path).resolve()
            if not src.exists():
                return f"Source path '{source_path}' does not exist."

            zip_name = zip_output_name or f"{src.name}.zip"
            zip_path = src.parent / zip_name

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                if src.is_dir():
                    for root, _, files in os.walk(src):
                        for file in files:
                            full_path = Path(root) / file
                            arcname = full_path.relative_to(src.parent)
                            zipf.write(full_path, arcname)
                else:
                    zipf.write(src, src.name)

            msg = f"Compressed '{src.name}' to archive: '{zip_path.name}'."
            logger.info(msg)
            db.log_command("compress_zip", "SUCCESS", str(zip_path))
            return msg
        except Exception as err:
            logger.error(f"Failed to compress to ZIP: {err}")
            return f"Failed to compress to ZIP: {err}"

    def extract_zip(self, zip_path: str, extract_to_dir: Optional[str] = None) -> str:
        """Extract ZIP archive contents."""
        try:
            zpath = Path(zip_path).resolve()
            if not zpath.exists():
                return f"ZIP archive file '{zip_path}' does not exist."

            target_dir = Path(extract_to_dir).resolve() if extract_to_dir else zpath.parent / zpath.stem
            target_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zpath, "r") as zipf:
                zipf.extractall(target_dir)

            msg = f"Extracted archive '{zpath.name}' to: '{target_dir}'."
            logger.info(msg)
            db.log_command("extract_zip", "SUCCESS", str(target_dir))
            return msg
        except Exception as err:
            logger.error(f"Failed to extract ZIP archive: {err}")
            return f"Failed to extract ZIP: {err}"


# Global File Organizer instance
file_organizer = FileOrganizer()
