<!-- NOTE: This file is used to generate the manual.pdf, which must be
done as part of the build process (see /build_instructions.md) -->

# Kei OpenMCR

# User Manual

## Basic Usage

1. Scan all sheets, including answer keys, into a single multi-page PDF or TIFF file. This includes answer keys. To create answer keys, simply print a normal sheet and and enter `9999999999` in the **Student ID** field.
2. Run the program.
3. Enter a description of the test in the program's **Test Title** field. This description will be printed at the top of the automatically generated PDF result handouts that may be distributed to students.
4. Under **Select Input File**, click <kbd>Browse</kbd> and select the multi-page PDF or TIFF file you stored the images in.
5. Under **Select Output Folder**, click <kbd>Browse</kbd> and select the folder where you would like to save the results.
6. If you select the **Sort results by students' name**, results will be sorted by the students' last, first, and middle names (in that order). Otherwise, results will be saved in the order processed.
7. Click <kbd>Continue</kbd>.

### Installation

For download and installation instructions, see the project homepage:
https://github.com/orchardguides/kei-open-mcr

### Printing Sheets

In order to use the OpenMCR software, students must use the provided multiple-
choice sheet:

- `multiple_choice_sheet_75q` (https://github.com/orchardguides/kei-open-mcr/blob/main/src/assets/multiple_choice_sheet_75q.pdf]: Has 75 questions as well as space for students' full names, course ID, student ID, and test form code.

### Filling Sheets

Students should be instructed to fill bubbles throughly and erase completely
if necessary. It is not necessary to require any specific type of pen or pencil
to be used.

### Creating Answer Keys

If you would like to take advantage of the automatic grading feature of the
software, you must provide it with one or more answer keys. To create an answer
key, simply print a normal sheet and put `9999999999` in the **Student ID**
field. Also, add a **Test Form Code** which will be used to match students' exams
with the correct answer key, and finally fill in the exam with the correct
answers.

### Scoring Results

In addition to reading scanned images, the software can automatically scores
the exam results. It does this by comparing the provided keys with the output.
There are three options for this, depending on which way you generate your exams:

#### One Exam Variant

If you give every exam-taker the exact same exam, you can instruct them to leave
the **Test Form Code** field blank on their sheets. In addition, leave that
field blank on the answer key sheet. All exam results will be compared to the
single answer key sheet provided.

#### Distinct Exam Variants

You can provide the exam-takers with multiple wholly distinct variants
of the same exam. In this case, each exam will be scored by selecting the answer
key with a matching **Test Form Code**.

### Output Files

After the program finishes processing, results will be saved as CSV files in
your selected output folder. These files can be opened in Excel or in any text
editor. Files will be saved with the time of processing to avoid overwriting any
existing files.

If you did not include any answer keys, one raw file will be saved with all of
the students' selected answers and no scoring is performed.

If you did include one or more answer keys, two more files will be saved in
addition to the aforementioned raw file. One of these files will have all of the
keys that were found, and the other will have the scored results. In the scored
file, questions are saved for each student as either `1` (correct) or `0`
(incorrect).

### PDF Handouts

After creating the CSV output files, the program automatically generates PDF result
sheets that can be distributed to students. These handouts report overall score and
list out incorrect responses with a corresponding correction.

A PDF file listing the correct response for every question in each of the Answer
Keys is also generated.
