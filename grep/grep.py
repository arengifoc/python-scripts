#!/usr/bin/env python
'''
grep.py - Basic grep functionality
Usage: grep.py <pattern> <files>
'''

import argparse
import logging
import re
import sys

from pathlib import Path


def grep(regex_pattern, filename, file_prefix=False):
    '''Check if pattern is found in file

    Args:
        regex_pattern (re.Pattern): Regexp pattern
        filename (Path): File path
        file_prefix (Bool): Print file name before line
    '''
    prefix = filename + ': ' if file_prefix else ''
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            search = regex_pattern.search(line)
            if search:
                print(prefix + line, end='')


def config_logging():
    """
    Configure logging
    """
    # logger = logging.getLogger(__name__)
    # logger.setLevel(logging.DEBUG)
    # stdout_ch = logging.StreamHandler(sys.stdout)
    # stdout_ch.setLevel(logging.DEBUG)
    # stdout_ch.addFilter(lambda record: record.levelno <= logging.INFO)
    # stderr_ch = logging.StreamHandler(sys.stderr)
    # stderr_ch.setLevel(logging.WARNING)
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # stdout_ch.setFormatter(formatter)
    # stderr_ch.setFormatter(formatter)
    # logger.addHandler(stdout_ch)
    # logger.addHandler(stderr_ch)
    logging.basicConfig(level=logging.WARNING, format="%(message)s", stream=sys.stderr)
    logger = logging.getLogger(__name__)
    return logger


def main():
    """
    Main function
    """
    log = config_logging()
    parser = argparse.ArgumentParser(description='Basic grep functionality')
    parser.add_argument('pattern', metavar="PATTERN", help='Pattern to search')
    parser.add_argument('files', metavar="FILES", nargs='+', help='Files to search')
    parser.add_argument('-i', '--ignore-case', action='store_true',
                        help='Ignore case when searching')
    args = parser.parse_args()
    re_flags = re.IGNORECASE if args.ignore_case else 0

    for file in args.files:
        if file.startswith('/'):
            filepath = Path(file)
        else:
            filepath = Path('.', file)
        if not filepath.exists():
            log.warning("Warning. \"%s\" does not exist. Skipping.", filepath)
        elif not filepath.is_file():
            log.warning("Error. \"%s\" is not a file. Skipping.", filepath)
        else:
            regex = re.compile(args.pattern, flags=re_flags)
            grep(regex, file, len(args.files) > 1)


if __name__ == '__main__':
    main()
