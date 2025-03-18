import file_handling
import grid_info as grid_i
import image_utils
import user_interface
import sys
from process_input import process_input
from datetime import datetime

user_input = user_interface.MainWindow()
if (user_input.cancelled):
    sys.exit(0)

multi_page_image_file = user_input.multi_page_image_file
output_folder = user_input.output_folder
sort_results = user_input.sort_results
debug_mode_on = user_input.debug_mode
form_variant = grid_i.form_150q if user_input.form_variant == user_interface.FormVariantSelection.VARIANT_150_Q else grid_i.form_75q
files_timestamp = datetime.now().replace(microsecond=0)

images, images_name, images_type = image_utils.get_images([multi_page_image_file])
progress_tracker = user_input.create_and_pack_progress(maximum=len(images))

process_input(images,
              images_name,
              images_type,
              output_folder,
              sort_results,
              debug_mode_on,
              form_variant,
              progress_tracker,
              files_timestamp)
