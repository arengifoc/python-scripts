#!/usr/bin/env python3
"""
archive_logs.py - Archive logs older than 7 days
"""
import shutil
import sys
import zipfile
import logging

from datetime import datetime, timedelta
from pathlib import Path
from tempfile import mkdtemp

TEMP_BACKUP_DIR = Path('/tmp')

# Configurar logging
logger = logging.getLogger(__name__)  # Usar un logger con nombre específico
logger.setLevel(logging.DEBUG)  # Configurar el nivel del logger

# Crear manejadores
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
stderr_handler = logging.StreamHandler(sys.stderr)

# Configurar niveles de los manejadores
stdout_handler.setLevel(logging.DEBUG)
stderr_handler.setLevel(logging.WARNING)

# Crear formateador y agregarlo a los manejadores
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)
stderr_handler.setFormatter(formatter)

# Agregar los manejadores al logger
logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)


def compress_logs(backup_dir):
    """
    Compress logs into a zip file.

    Args:
        backup_dir (Path): Directory to backup
    """
    zip_file = 'backup_' + datetime.now().strftime("%Y%m%d") + '.zip'
    zip_file = Path('/tmp/' + zip_file)
    if zip_file.exists():
        logger.warning("%s already exists. Skipping.", zip_file)
        return
    with zipfile.ZipFile(zip_file, 'w') as zipf:
        for file in backup_dir.rglob('*.log'):
            arcname = file.relative_to(TEMP_BACKUP_DIR)
            zipf.write(file, arcname=arcname)
    try:
        shutil.rmtree(backup_dir)
    except FileNotFoundError as e:
        logger.error("Error: Cannot remove directory: %s", e)
        sys.exit(1)
    except PermissionError as e:
        logger.error("Error: Cannot remove directory: %s", e)
        sys.exit(1)
    logger.info("Logs compressed into %s", zip_file)
    logger.info("Backup directory %s removed", backup_dir)


def archive_logs(log_directory):
    """
    Find logs in a directory.

    Args:
        log_directory (Path): Directory to scan
    Returns:
        backup_dir (Path): Temporary directory created for backup
    """
    try:
        backup_dir = Path(mkdtemp(prefix="backup_logs_", dir=TEMP_BACKUP_DIR))
    except (PermissionError, FileExistsError, FileNotFoundError) as e:
        logger.error("Error: Cannot create temporary directory: %s", e)
        sys.exit(1)

    for file in log_directory.rglob('*.log'):
        try:
            file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
            time_interval = datetime.now() - timedelta(days=7)
            if file_mtime < time_interval:
                if (backup_dir / file.name).exists():
                    logger.warning("%s already exists in backup. Skipping.", file.name)
                    continue
                logger.info("Archiving %s", file)
                try:
                    shutil.copy2(file, backup_dir)
                except PermissionError as e:
                    logger.error("Error: Cannot move file: %s", e)
                    sys.exit(1)
            else:
                logger.info("Skipping %s newer than 7 days", file)
        except (PermissionError, IsADirectoryError, FileNotFoundError) as e:
            logger.error("Error: %s", e)
            sys.exit(1)

    return backup_dir


def main():
    """
    Main function
    """
    if len(sys.argv) < 2:
        logger.error("Must specify log directory to scan.")
        sys.exit(1)
    log_dir = Path(sys.argv[1])
    try:
        if not TEMP_BACKUP_DIR.is_dir():
            TEMP_BACKUP_DIR.mkdir()
    except FileExistsError as e:
        logger.error("Error: Cannot create backup directory: %s", e)
        sys.exit(1)
    if not log_dir.exists():
        logger.error("'%s' does not exist.", log_dir)
        sys.exit(1)
    if not log_dir.is_dir():
        logger.error("'%s' is not a directory.", log_dir)
        sys.exit(1)
    tmp_bkp_dir = archive_logs(log_dir)
    compress_logs(tmp_bkp_dir)


if __name__ == '__main__':
    main()
