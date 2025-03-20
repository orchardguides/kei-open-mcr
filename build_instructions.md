# Build Instructions

The following instructions show how to build the program into a single `.exe`
file that can be run to install the software.

1. Install the required modules from [`requirements.txt`](requirements.txt) if
   you haven't already.
2. Open a terminal in the root directory.
3. If you've made changes to the users manual, 'manual.md', use a markdown to PDF converter to generate a `manual.pdf` file and place it in `./src/assets`.
4. From within the folder that contains the 'src' folder, run the build command:
   `pyinstaller --onefile -p src --add-data="src:." -y -w --icon=src/assets/icon.ico --name=kei-open-mcr src/main_gui.py
   `
