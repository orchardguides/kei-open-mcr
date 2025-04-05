# Kei OpenMCR

## Basic Usage

Here's all you have to do to grade bubble tests with up to [75 questions](https://github.com/orchardguides/kei-open-mcr/blob/main/src/assets/multiple_choice_sheet_75q.pdf). 

1. Scan all sheets, including answer keys, into a single multi-page PDF or TIFF file. To create answer keys, simply fill out a normal sheet and and enter `9999999999` in the **Student ID** field.
2. Run the program.
3. Enter a description of the test in the program's **Test Title** field. This description will be printed at the top of the automatically generated PDF result student handouts.
4. Under **Select Input File**, click <kbd>Browse</kbd> and select the multi-page PDF or TIFF file created in Step 1.
5. Under **Select Output Folder**, click <kbd>Browse</kbd> and select the folder where you want to save the results.
6. If you select the **Sort results by students' name**, results will be sorted by the students' last, first, and middle names (in that order). Otherwise, results will be saved in the order processed.
7. Click <kbd>Continue</kbd>.

### Free and Open-Source Multiple Choice Exam Sheet Reader and Scorer

This is a fork of OpenMCR, a program developed by Ian Sanders, available at:

[Link to Ian Sander's original OpenMCR](https://github.com/iansan5653/open-mcr)

> **Warning** As per the license of this software, no warranty is implied. The software is stable but there still may be bugs. Given that students' grades are at stake, please be sure to audit the results - particularly when working with low-quality scans.

## Major changes to the original code include:

The overall goal in creating this fork was to make the program easier to use.

 1. The program now generates graded handouts for each test-taker. These handouts provide specific details about how each student's score was calculated.
 2. As input, the program now processes a single multi-page pdf or tiff that should contain all of the multiple choice sheet images. Previously, the applcation only accepted single page image files as input.
 3. Options to change the way that incorrect responses are reported have been eliminated.
 4. Answer keys can now only be entered using the multiple choice sheets.
 5. The graphical interface has been streamlined and now fits comfortably on low resolution screens.
 6. The program no longer works with 150 question sheets.

## Background

Commercially available OMR (optical mark recognition) exam sheets, scanners, and processing software can cost educators and educational institutions thousands of dollars per year. In response to this, OpenMCR has been developed as a free and easy-to-use alternative. The tool includes a multiple choice exam sheet and works with any scanner and printer.

This software and the corresponding multiple choice sheet were originally developed as an independent study project by Ian Sanders, a mechanical engineering student at the University of South Florida, under the direction of Dr. Autar Kaw.

## Installation Instructions

Currently, packaged executables are only provided for Windows. For other operating systems, see Running From Source below.

### Running Without Install

ZIP file packages are available for each release.

To launch the program in Windows, download the ZIP file and extract its contents to a folder anywhere on your machine. Then run the `kei-open-mcr.exe` file found in the dist_windows folder. This method should not require administrator priveleges.

### Running From Source / CLI

If you wish to customize the software or launch the program in a non-Windows environment, you can use the command line interface and run the Python program directly from the source files. This requires Python and Pip to be installed on your machine.

1. Clone the reposotory using Git, or download and extract the latest `Source code (zip)` file from releases.
2. Open a terminal / command prompt in the extracted directory.
3. On Mac machines with fresh Python installations, you will have to update TKinter from the default.
4. Run `pip3 install -r requirements.txt` to install dependencies.
5. Run `python3 src/main.py` for the CLI interface or `python3 src/main_gui.py` for the graphical interface.

> **Note**: On MacOS, if you see a black screen when running the GUI, you need to uninstall Python, install TKinter, and then reinstall Python.

> **Note**: On Linux machines, you may see an error message that `opencv` or `tkinter are not found. If you see this, install those dependencies by running `sudo apt-get install python3-opencv python3-tk` and then try again.

> **On Linux machines it is fairly easy to create a single exacutable file using the instructions described in** [build_instructions.md](./build_instructions.md)

## Printable Multiple Choice Sheet

The multiple choice sheet that must be used with this software is available for printing here:

* [75 Question Variant](https://github.com/orchardguides/kei-open-mcr/blob/main/src/assets/multiple_choice_sheet_75q.pdf)

## License

### Software License

Copyright (C) 2019 Ian Sanders

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

For the full license text, see [license.txt](./license.txt).

### Multiple Choice Sheet License

The multiple choice sheet distributed with this software is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license (CC BY-NC-SA 4.0). In summary, this means that you are free to distribute and modify the document so long as you share it under the same license, provide attribution, and do not use it for commercial purposes. For the full license, see
[the Creative Commons website](https://creativecommons.org/licenses/by-nc-sa/4.0/).

**Note**: You are explicitly _allowed_ to distribute the multiple choice sheet without attribution if using it unmodified for educational purpose and not in any way implying that it is your own work. This is an exception to the Creative Commons terms. 
