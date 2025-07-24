import textwrap
import typing as tp
from pathlib import Path
from datetime import datetime

import data_exporting
import image_utils
import corner_finding
import numpy as np
import scoring
import grid_info as grid_i
import grid_reading as grid_r
from user_interface import ProgressTrackerWidget
from scored_handouts import create_pdfs

import imageio
from data_exporting import format_timestamp_for_file

def process_input(
        test_identifier: str,
        images: tp.List[np.ndarray],
        images_name: tp.List[str],
        output_folder: Path,
        sort_results: bool,
        debug_mode_on: bool,
        form_variant: grid_i.FormVariant,
        progress_tracker: tp.Optional[ProgressTrackerWidget],
        files_timestamp: tp.Optional[datetime]):
    """Takes input as parameters and process it for either gui or cli.
    
    Parameter progress_tracker determines whith interface in use.
    If progress_tracker is given, function runs in gui mode.
    If progress_tracker parameter is None, prints all progress statuses to stdout.
    """

    answers_results = data_exporting.OutputSheet([x for x in grid_i.Field],
                                                 form_variant.num_questions)
    keys_results = data_exporting.OutputSheet([grid_i.Field.TEST_FORM_CODE, grid_i.Field.IMAGE_FILE],
                                              form_variant.num_questions)
    unusable_sheets = []
    
    status_string = ""

    debug_dir = output_folder / (
            data_exporting.format_timestamp_for_file(files_timestamp) + "debug")
    if debug_mode_on:
        data_exporting.make_dir_if_not_exists(debug_dir)

    try:
        for i in range(len(images)):
            if debug_mode_on:
                debug_path = debug_dir / images_name[i]
                data_exporting.make_dir_if_not_exists(debug_path)
            else:
                debug_path = None

            if progress_tracker:
                progress_tracker.set_status(f"Processing {images_name[i]}")
            else:
                print(f"Processing {images_name[i]}")

            image = images[i]
            prepared_image = image_utils.prepare_scan_for_processing(
                image, save_path=debug_path)

            try:
                corners = corner_finding.find_corner_marks(prepared_image,
                                                       save_path=debug_path)
            except corner_finding.CornerFindingError:
                unusable_sheets.append(images[i])
                if progress_tracker:
                    progress_tracker.step_progress()
                continue

            # Dilates the image - removes black pixels from edges, which preserves
            # solid shapes while destroying nonsolid ones. By doing this after noise
            # removal and thresholding, it eliminates irregular things like W and M
            morphed_image = image_utils.dilate(prepared_image,
                                               save_path=debug_path)

            # Establish a grid
            grid = grid_r.Grid(corners,
                               grid_i.GRID_HORIZONTAL_CELLS,
                               grid_i.GRID_VERTICAL_CELLS,
                               morphed_image,
                               save_path=debug_path)

            # Calculate fill percent for every bubble
            field_fill_percents = {
                key: grid_r.get_group_from_info(value,
                                                grid).get_all_fill_percents()
                for key, value in form_variant.fields.items() if value is not None
            }
            answer_fill_percents = [
                grid_r.get_group_from_info(question, grid).get_all_fill_percents()
                for question in form_variant.questions
            ]

            # Calculate the fill threshold
            threshold = grid_r.calculate_bubble_fill_threshold(
                field_fill_percents,
                answer_fill_percents,
                save_path=debug_path,
                form_variant=form_variant)

            # Get the answers for questions
            answers = [
                grid_r.read_answer_as_string(i, grid,
                                             threshold, form_variant,
                                             answer_fill_percents[i])
                for i in range(form_variant.num_questions)
            ]

            field_data: tp.Dict[grid_i.RealOrVirtualField, str] = {
                grid_i.Field.IMAGE_FILE: images_name[i],
            }

            # Read the Student ID. If it indicates this exam is a key, treat it as such
            student_id = grid_r.read_field_as_string(
                grid_i.Field.STUDENT_ID, grid, threshold, form_variant,
                field_fill_percents[grid_i.Field.STUDENT_ID])
            if student_id == grid_i.KEY_STUDENT_ID:
                form_code_field = grid_i.Field.TEST_FORM_CODE
                field_data[form_code_field] = grid_r.read_field_as_string(
                    form_code_field, grid, threshold, form_variant,
                    field_fill_percents[form_code_field]) or ""
                keys_results.add(field_data, answers)

            else:
                for field in form_variant.fields.keys():
                    field_value = grid_r.read_field_as_string(
                        field, grid, threshold, form_variant,
                        field_fill_percents[field])
                    if field_value is not None:
                        field_data[field] = field_value
                answers_results.add(field_data, answers)
            if progress_tracker:
                progress_tracker.step_progress()

        answers_results.clean_up("")
        answers_results.save(output_folder,
                             "results",
                             sort_results,
                             timestamp=files_timestamp)

        if (keys_results.row_count == 0):
            status_string += "❌ No answer keys were found, so no scoring was performed."
            if progress_tracker:
                progress_tracker.set_status_label_alert()
        else:
            keys_results.save(output_folder,
                              "keys",
                              sort_results,
                              timestamp=files_timestamp)
            scores = scoring.score_results(answers_results, keys_results,
                                           form_variant.num_questions)
            scores.save(output_folder,
                        "scores",
                        sort_results,
                        timestamp=files_timestamp)

            create_pdfs(output_folder, files_timestamp, test_identifier, images, unusable_sheets)

            if unusable_sheets == []:
                status_string = "✔️ All exams processed and saved in the Output Folder.\n"
            else:
                path = str(output_folder) + "/" + f"{format_timestamp_for_file(files_timestamp)}"
                imageio.mimsave(path + "Unsueable_Sheets.tif", unusable_sheets)

                status_string = "❌ Partial Success --- Scores from readable Answer Sheets are reported\n"
                status_string += "in the Output Folder along with images of illegible sheets, which are\n"
                status_string += "collected in Unusable_Sheets.tif."
                if progress_tracker:
                    progress_tracker.set_status_label_alert()

    except (RuntimeError, ValueError) as e:
        wrapped_err = "\n".join(textwrap.wrap(str(e), 70))
        if progress_tracker: 
            progress_tracker.set_status(f"Error: {wrapped_err}", False)
        else:
            print(f'Error: {wrapped_err}')
        if debug_mode_on:
            raise

    if progress_tracker:
        progress_tracker.set_status(status_string, False)
        progress_tracker.show_exit_button_and_wait()
    else:
      print(status_string)
