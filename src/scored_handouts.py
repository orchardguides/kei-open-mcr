'''
Created on Feb 22, 2025

@author: Kei G. Gauthier
'''
import csv
import typing as tp
from pathlib import Path
from datetime import datetime
from data_exporting import format_timestamp_for_file

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter

def create_answer_key_pdfs(output_folder: Path, files_timestamp: tp.Optional[datetime], test_identifier: str):
    path = str(output_folder) + "/" + f"{format_timestamp_for_file(files_timestamp)}"

    """Read open-mcr answer keys into python dictionaries"""   
    key_dictionaries = []
    keys_file_name = path + "keys.csv"
    if Path(keys_file_name).is_file():
        with open(keys_file_name, mode ='r') as file:
            keys_reader = csv.DictReader(file)
            for row in keys_reader:
                key_dictionaries.append(row)
    if len(key_dictionaries) == 0:
        print("❌ No answer keys found")
        return

    """Initialize pdf canvas"""   
    canvas = Canvas(path + "Keys.pdf", pagesize=letter)

    for key_dictionary in key_dictionaries:

        """Count questions in answer key"""
        questions_in_key = 0
        for q in range(1,75+1):
            if key_dictionary["Q" + str(q)] != "":
                questions_in_key = questions_in_key + 1
            else:
                break

        """Determine height needed to print the current answer key
            TOTAL HEIGHT OF:
                      space between answer keys
                plus: Test Version heading
                plus: Question: Correct Answer heading
                plus: question and answer lines
                plus: bottom of page margin"""
        answer_key_height = (  40 
                             + 24
                             + 24
                             + ((questions_in_key-1) // 8 + 1) * 18
                             + 60)

        """Eject page if there not enough room left on the page to print the current answer key
           and position the start of the printout"""
        x_axis = 60
        if key_dictionary == key_dictionaries[0]:
            y_axis = 720
        elif y_axis - answer_key_height < 0:
            canvas.save()
            y_axis = 720
        else:
            y_axis = y_axis-40

        """Print test description and version on canvas"""   
        canvas.setFont('Helvetica-Bold', 16)
        test_description = test_identifier;

        test_form_code = key_dictionary["Test Form Code"]
        if test_form_code != "":
            if test_description == "":
                test_description = test_description + "Version " + test_form_code
            else:
                test_description = test_description + " Version " + test_form_code
        if test_description != "":
            canvas.drawString(60, y_axis, test_description)

        canvas.setFont('Helvetica-Bold', 14)
        y_axis = y_axis-24

        """List the correct answers"""   
        canvas.drawCentredString(612/2, y_axis, "Question:  Correct Answer")
        y_axis = y_axis-24
        for q in range(1,75+1):
            if key_dictionary["Q" + str(q)] != "":
                canvas.setFont('Helvetica-Bold', 12)
                canvas.drawString(x_axis, y_axis, "Q" + str(q))
                x_axis = x_axis + 32

                canvas.setFont('Helvetica', 12)
                canvas.drawString(x_axis, y_axis, key_dictionary["Q" + str(q)])
                if x_axis >= 508:
                    x_axis = 60;
                    y_axis = y_axis - 18
                else:
                    x_axis = x_axis + 32
            else:
                break

    """Save answer keys in a multi-page pdf file"""
    canvas.save()


def create_scored_pdfs(output_folder, files_timestamp, test_identifier):
    path = str(output_folder) + "/" + f"{format_timestamp_for_file(files_timestamp)}"

    """Read open-mcr output files into python dictionaries"""   
    key_dictionaries = []
    result_dictionaries = []
    score_dictionaries = []

    keys_file_name = path + "keys.csv"
    if Path(keys_file_name).is_file():
        with open(keys_file_name, mode ='r') as file:
            keys_reader = csv.DictReader(file)
            for row in keys_reader:
                key_dictionaries.append(row)
    if len(key_dictionaries) == 0:
        print("❌ No answer keys found")
        return

    results_file_name = path + "results.csv"
    if Path(results_file_name).is_file():
        with open(results_file_name, mode ='r') as file:
            results_reader = csv.DictReader(file)
            for row in results_reader:
                result_dictionaries.append(row)
    if len(result_dictionaries) == 0:
        print("❌ No results found")
        return

    scores_file_name = path + "scores.csv"
    if Path(scores_file_name).is_file():
        with open(scores_file_name, mode ='r') as file:
            scores_reader = csv.DictReader(file)
            for row in scores_reader:
                score_dictionaries.append(row)
    if len(score_dictionaries) == 0:
        print("❌ No scores found")
        return

    """Initialize pdf canvas"""   
    canvas = Canvas(path + "Scores.pdf", pagesize=letter)

    """Loop through test results"""
    for i in range(0, len(result_dictionaries)):
        result_dictionary = result_dictionaries[i]

        """Match result with its corresponding Answer Key"""
        score_dictionary = score_dictionaries[i]
        matching_key_dictionary = None;
        for key_dictionary in key_dictionaries:
            if (key_dictionary["Test Form Code"] == result_dictionary["Test Form Code"]):
                matching_key_dictionary = key_dictionary
                break

        """Ignore results that lack a valid Test Form Code"""
        if matching_key_dictionary == None:
            print("❌ Unable to process result" + str(result_dictionary))        
            continue;

        """Print test description and version on canvas"""   
        canvas.setFont('Helvetica-Bold', 16)
        test_description = test_identifier;
        test_form_code = key_dictionary["Test Form Code"]
        if test_form_code != "":
            if test_description == "":
                test_description = test_description + "Version " + test_form_code
            else:
                test_description = test_description + " Version " + test_form_code
        if test_description != "":
            canvas.drawCentredString(612/2, 720, test_description)

        """Print name"""
        canvas.setFont('Helvetica-Bold', 16)
        name = result_dictionary["Last Name"]
        if result_dictionary["First Name"] != "":
            name = name  + " , " + result_dictionary["First Name"]
        if result_dictionary["Middle Name"] != "":
            name = name  + " , " + result_dictionary["Middle Name"]
        canvas.drawString(50, 680, name)


        """Count questions in answer key"""
        questions_in_key = 0
        for q in range(1,75+1):
            if matching_key_dictionary["Q" + str(q)] != "":
                questions_in_key = questions_in_key + 1
            else:
                break
  
        """Print overall results"""
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawString(50, 650, score_dictionary["Total Score (%)"] + "%  --  " + 
                          str(score_dictionary["Total Points"]) + 
                          " of " + str(questions_in_key) + 
                          " questions answered correcty")


        """Print corrections"""
        if int(score_dictionary["Total Points"]) != questions_in_key:
            canvas.setFont('Helvetica-Bold', 14)
            canvas.drawCentredString(612/2, 595, "Correct Answer:Chosen Answer")

            x_axis = 50;
            y_axis = 570
            for q in range(1,questions_in_key+1):

                correct_answer = matching_key_dictionary["Q" + str(q)]
                result_answer = result_dictionary["Q" + str(q)]
                if result_answer != correct_answer:
                    canvas.setFont('Helvetica-Bold', 12)
                    canvas.drawString(x_axis, y_axis, "Q" + str(q))
                    x_axis = x_axis + 32
                    canvas.setFont('Helvetica', 12)
                    canvas.drawString(x_axis, y_axis, correct_answer + ":" + result_answer)

                    if x_axis >= 440:
                        y_axis = y_axis - 14
                        x_axis = 50;
                    else:
                        x_axis = x_axis + 76

        """Print handouts on separate pages"""
        canvas.showPage()

    """Save handouts in a multi-page pdf file"""
    canvas.save()

def create_pdfs(output_folder, files_timestamp, test_identifier):
    create_answer_key_pdfs(output_folder, files_timestamp, test_identifier)
    create_scored_pdfs(output_folder, files_timestamp, test_identifier)

