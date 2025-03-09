#!/usr/bin/env python
'''
order_log_files.py - Organize log files and find number of error matches on them

Usage: order_log_files.py <log-directory>
'''
import sys
from pathlib import Path
import re
from shutil import move
from pyinputplus import inputYesNo

DEST_DIR = Path('/home/arengifo/logs/dest')
REPORT_FILE = Path.cwd() / 'reporte.txt'


def organize_logs(logs, log_regex):
    '''
    parse_log_files - Parse log files by name

    Args:
        logs (generator) - Log files iterator
    '''
    for log in logs:
        log_search = log_regex.search(str(log.name))
        log_service_name = log_search.group(1)
        log_dest = DEST_DIR / Path(log_service_name) / log.name
        log_service_dir = DEST_DIR / Path(log_service_name)
        log_service_dir.mkdir(exist_ok=True, parents=True)
        try:
            if log_dest.exists():
                print(
                    f"Warning: {log_dest} already exists. Skipping.", file=sys.stderr)
            else:
                move(log, log_dest)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
        except PermissionError as e:
            print(f"Error: {e}", file=sys.stderr)


def find_error_in_logs(new_logdir, error_regex, report_file):
    '''
    find_error_in_logs - Find number of error matches in log files

    Args:
        new_logdir (Path): Log directory to scan
        error_regex (re.Pattern): Error regex to search for
        report_file (Path): Report file to write results
    '''
    try:
        with open(report_file, 'w', encoding='utf-8') as file:
            new_logdir_path = Path(new_logdir)
            for logfile in new_logdir_path.rglob('*.log'):
                n = len(error_regex.findall(logfile.read_text()))
                file.write(f"{logfile.name}: {n} errores\n")
    except IsADirectoryError as e:
        print(f"Error: {e}", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: Must specify log directory to scan.", file=sys.stderr)
        sys.exit(1)

    script = Path(sys.argv[0]).name
    log_dir_path = Path(sys.argv[1])
    log_format_regex = re.compile("(.*)_([0-9]{4}-[0-9]{2}-[0-9]{2}).log")
    log_error_regex = re.compile(r"\berror\b", re.IGNORECASE)

    if not log_dir_path.exists():
        print(f"{script}: cannot access '{log_dir_path}': no such file or directory",
              file=sys.stderr)
        sys.exit(1)

    if not log_dir_path.is_dir():
        print(f"{script}: {log_dir_path}: Not a directory", file=sys.stderr)
        sys.exit(1)

    if REPORT_FILE.exists():
        answer = inputYesNo(
            f"Report file '{REPORT_FILE.name}' already exists. Overwrite? (yes/no): ")
        if answer == 'no':
            print("Aborted.")
            sys.exit(1)

    if not DEST_DIR.exists():
        print(f"{script}: cannot access log destination directory '{DEST_DIR}': \
              no such file or directory", file=sys.stderr)
        answer = inputYesNo(f"Create directory '{DEST_DIR}'? (yes/no): ")
        try:
            if answer == 'yes':
                DEST_DIR.mkdir(parents=True)
            else:
                print("Aborted.")
                sys.exit(1)
        except PermissionError as e:
            print(
                f"{script}: cannot create directory '{DEST_DIR}': {e}", file=sys.stderr)
            sys.exit(1)

    try:
        logs_found = log_dir_path.glob('*.log')
        if len(list(logs_found)) == 0:
            print(f"{script}: {log_dir_path}: No log files found", file=sys.stderr)
            sys.exit(1)
        else:
            for item in logs_found:
                print(item)
            print(list(logs_found))
            # First, organize logs in folders per service
            organize_logs(logs_found, log_format_regex)
            # Then, find errors in logs
            find_error_in_logs(DEST_DIR, log_error_regex, REPORT_FILE)
    except PermissionError as e:
        print(f"{script}: cannot access '{log_dir_path}': {e}", file=sys.stderr)
