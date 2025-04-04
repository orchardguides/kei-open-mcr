import argparse
import sys
from datetime import datetime
from pathlib import Path

import file_handling
import image_utils
from file_handling import parse_path_arg
import grid_info as grid_i
from process_input import process_input


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenMCR: An accurate and simple exam bubble sheet reading tool.\n'
                                                 'Reads sheets from input folder, process and saves result in output folder.',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--test_identifier',
                        help='Name of Test and Other Descriptive Information',
                        type=parse_path_arg)
    parser.add_argument('--input_file',
                        help='Path to a folder containing scanned input sheets.\n'
                             'Sheets with student ID of "9999999999" treated as keys. Ignores subfolders.',
                        type=parse_path_arg)
    parser.add_argument('--output_folder',
                        help='Path to a folder to save result to.',
                        type=parse_path_arg)
    parser.add_argument('--variant',
                        default='75',
                        choices=['75', '150'],
                        help='Form variant either 75 questions (default) or 150 questions.')
    parser.add_argument('-s', '--sort',
                        action='store_true',
                        help="Sort output by students' name.")
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Turn debug mode on. Additional directory with debug data will be created.')
    parser.add_argument('--disable-timestamps',
                        action='store_true',
                        help='Disable timestamps in file names. Useful when consistent file names are required. Existing files will be overwritten without warning!')

    # prints help and exits when called w/o arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    test_identifier = args.test_identifier,
    multi_page_image_file = Path(args.input_file)
    output_folder = Path(args.output_folder)
    sort_results = args.sort
    debug_mode_on = args.debug
    form_variant = grid_i.form_150q if args.variant == '150' else grid_i.form_75q
    files_timestamp = datetime.now().replace(microsecond=0) if not args.disable_timestamps else None

    images, images_name, images_type = image_utils.get_images([multi_page_image_file])

process_input(test_identifier,
              images,
              images_name,
              images_type,
              output_folder,
              sort_results,
              debug_mode_on,
              form_variant,
              None,
              files_timestamp)
