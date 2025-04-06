import abc
import string
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, ttk
import typing as tp
import platform

import file_handling
import scoring
import str_utils

YPADDING = 4
XPADDING = 7
APP_NAME = "Kei Open-MCR"

PackTarget = tp.Union[tk.Tk, tk.Frame]


def prompt_folder(message: str = "Select Folder", default: str = "./") -> Path:
    """Prompt the user to select a folder."""
    folderpath = filedialog.askdirectory(initialdir=default, title=message)
    if type(folderpath) is str:
        return Path(folderpath)


def prompt_file(message: str = "Select File",
                default: str = "./",
                filetypes: tp.Optional[tp.List[tp.Tuple[str, str]]] = None
                ) -> Path:
    """Prompt the user to select a file."""
    filepath = filedialog.askopenfilename(initialdir=default,
                                          title=message,
                                          filetypes=filetypes)
    if type(filepath) is str:
        return Path(filepath)


T = tp.TypeVar("T", bound=tk.Widget)


def pack(widget: T, *args: tp.Any, **kwargs: tp.Any) -> T:
    """Pack the widget into its root and return it."""
    widget.pack(*args, **kwargs)
    return widget


def create_and_pack_label(parent: PackTarget,
                          text: str,
                          heading: bool = False,
                          inline: bool = False) -> ttk.Label:
    """Create a label using the predefined font settings, pack it, and return it."""
    font_opt = {"font": "TkDefaultFont 10 bold"} if heading else {}
    pady_opt = {"pady": (YPADDING * 2, 0)} if heading else {"pady": YPADDING}
    label = ttk.Label(parent,
                      text=text,
                      justify=tk.LEFT,
                      anchor="w",
                      **font_opt)
    return pack(label,
                fill=tk.X if not inline else None,
                expand=1,
                padx=XPADDING,
                side=tk.LEFT if inline else None,
                **pady_opt)

class TestIdentifierWidget():
    def __init__(self, 
                 parent: PackTarget):

        def __check_text_entry(event):
            text = self.__test_identifier_text.get("1.0", "end-1c")
            """Ignore returns and tabs."""
            if event.keysym in ("Return", "Tab"):
                return "break"
            """Limit text length."""
            if len(text) >= 50 and event.keysym not in ("BackSpace", "Delete"):
                return "break"
        
        create_and_pack_label(parent, "Test Title", heading=True)
        create_and_pack_label(
            parent,
            "Heading that will be printed at the top of the graded student handouts.")

        self.__test_identifier_text = tk.Text(parent, height=1, width=50, padx=XPADDING)
        self.__test_identifier_text.pack(padx=XPADDING)
        self.__test_identifier_text.bind("<KeyPress>", __check_text_entry)

    def get(self):
        return self.__test_identifier_text.get("1.0", "end-1c")

    def disable(self):
        self.__test_identifier_text.configure(state=tk.DISABLED)


class PickerWidget(abc.ABC):
    """File picker widget (browse button and file path)."""
    value: tp.Optional[Path]

    def __init__(self,
                 parent: PackTarget,
                 placeholder: str,
                 on_change: tp.Optional[tp.Callable] = None):
        internal_padding = int(XPADDING * 0.66)
        external_padding = XPADDING
        pack_opts = {"side": tk.LEFT, "pady": external_padding}

        self.__on_change = on_change
        self.__placeholder = placeholder

        container = tk.Frame(parent)
        self.__browse_button = pack(ttk.Button(container,
                                               text="Browse",
                                               command=self._prompt,
                                               padding=internal_padding),
                                    **pack_opts,
                                    padx=(external_padding, 0))

        self.__display_text = tk.StringVar()
        pack(ttk.Label(container,
                       textvariable=self.__display_text,
                       width=40,
                       justify=tk.LEFT,
                       anchor="w",
                       borderwidth=2,
                       relief="groove",
                       padding=internal_padding),
             **pack_opts,
             padx=external_padding)

        self.__display_text.set(placeholder)
        pack(container)
        self.value = None

    @abc.abstractmethod
    def _prompt(self):
        ...

    def _on_select(self, selection: Path):
        self.value = selection if str(selection).strip() != "." else None

        display_text = str_utils.trim_middle_to_len(
            str(selection), 45,
            3) if self.value is not None else self.__placeholder
        self.__display_text.set(display_text)

        if self.__on_change is not None:
            self.__on_change()

    def disable(self):
        self.__browse_button.configure(state=tk.DISABLED)


class FolderPickerWidget(PickerWidget):
    def __init__(self,
                 parent: PackTarget,
                 on_change: tp.Optional[tp.Callable] = None):
        super().__init__(parent, "No Folder Selected", on_change)

    def _prompt(self):
        super()._on_select(prompt_folder())


class FilePickerWidget(PickerWidget):
    def __init__(self,
                 parent: PackTarget,
                 filetypes: tp.Optional[tp.List[tp.Tuple[str, str]]] = None,
                 on_change: tp.Optional[tp.Callable] = None):
        self.__filetypes = filetypes
        super().__init__(parent, "No File Selected", on_change)

    def _prompt(self):
        super()._on_select(prompt_file(filetypes=self.__filetypes))


class CheckboxWidget():
    """File picker widget (browse button and file path)."""
    value: bool

    def __init__(self,
                 parent: PackTarget,
                 label: str,
                 on_change: tp.Optional[tp.Callable] = None,
                 reduce_padding_above: bool = False):
        self.__on_change = on_change
        self.__raw_value = tk.IntVar(parent, 0)

        internal_padding = int(XPADDING * 0.33)
        external_padding = XPADDING
        top_padding = external_padding if not reduce_padding_above else 0
        pack_opts = {"side": tk.LEFT, "pady": (top_padding, external_padding)}

        frame = tk.Frame(parent)
        self.__checkbox = pack(ttk.Checkbutton(frame,
                                               text=label,
                                               command=self.__on_update,
                                               variable=self.__raw_value,
                                               padding=internal_padding,
                                               width=50),
                               **pack_opts,
                               padx=(external_padding, 0))
        frame.pack()

        self.value = False

    def __on_update(self):
        self.value = bool(self.__raw_value.get())
        if self.__on_change is not None:
            self.__on_change()

    def disable(self):
        self.__checkbox.configure(state=tk.DISABLED)


class SelectWidget():
    """Select (combobox) dropdown menu widget."""
    value: str

    def __init__(self,
                 parent: PackTarget,
                 label: str,
                 options: tp.List[str],
                 on_change: tp.Optional[tp.Callable] = None):
        self.__raw_value = tk.StringVar()
        self.__on_change = on_change

        container = tk.Frame(parent)
        create_and_pack_label(container, label, True, inline=True)
        self.__combobox = pack(ttk.Combobox(container,
                                            width=35,
                                            textvariable=self.__raw_value,
                                            values=options),
                                            side=tk.RIGHT)
        self.__combobox.current(0)

        self.__raw_value.trace("w", self.__on_update)
        self.value = self.__raw_value.get()
        pack(container)

    def __on_update(self, *args: tp.Any):
        self.value = self.__raw_value.get()
        if (self.__on_change is not None):
            self.__on_change()

    def disable(self):
        self.__combobox.configure(state=tk.DISABLED)


class InputFilePickerWidget():
    file: tp.Optional[Path]
    all_files: bool

    def __init__(self,
                 parent: PackTarget,
                 on_change: tp.Optional[tp.Callable] = None):
        self.__on_change = on_change

        container = tk.Frame(parent)

        create_and_pack_label(container, "Multi-Page Image File", heading=True)
        create_and_pack_label(
            container,
            "Select the pdf or tiff file containing the multi-page image. Sheets with\na Student ID of '9999999999' will be treated as answer keys."
        )
        self.__image_file_picker = FilePickerWidget(
            container, [("Image File", ".tif"), ("Image File", ".tiff"), ("Image File", ".pdf")], self.__on_update)

        pack(container, fill=tk.X)

        self.file = None

    def __on_update(self, *args: tp.Any):
        self.file = self.__image_file_picker.value
        if self.__on_change is not None:
            self.__on_change()

    def disable(self):
        self.__image_file_picker.disable()

class OutputFolderPickerWidget():
    folder: tp.Optional[Path]
    sort_results: bool

    def __init__(self,
                 parent: PackTarget,
                 on_change: tp.Optional[tp.Callable] = None):
        self.__on_change = on_change

        container = tk.Frame(parent)

        create_and_pack_label(container, "Output Folder", heading=True)
        create_and_pack_label(container,
                              "Select the folder where output files will be saved.")

        self.__output_folder_picker = FolderPickerWidget(
            container, self.__on_update)
        self.__sort_results_checkbox = CheckboxWidget(
            container, "Sort results by students' names.",
            self.__on_sort_update)

        pack(container, fill=tk.X)

        self.folder = None
        self.sort_results = False

    def __on_sort_update(self):
        self.__on_update()

    def __on_update(self):
        self.folder = self.__output_folder_picker.value
        self.sort_results = self.__sort_results_checkbox.value

        if self.__on_change is not None:
            self.__on_change()

    def disable(self):
        self.__output_folder_picker.disable()
        self.__sort_results_checkbox.disable()


class ProgressTrackerWidget:
    def __init__(self, parent: tk.Tk, maximum: int):
        self.maximum = maximum
        self.value = 0
        self.parent = parent
        pack_opts = {
            "fill": tk.X,
            "expand": 1,
            "padx": XPADDING,
            "pady": YPADDING
        }
        self.status_text = tk.StringVar(parent)
        pack(ttk.Label(parent, textvariable=self.status_text, width=45),
             **pack_opts)
        self.progress_bar = pack(
            ttk.Progressbar(parent, maximum=maximum, mode="determinate"),
            **pack_opts)
        self.close_when_changes = tk.IntVar(parent, name="Ready to Close")

    def step_progress(self, step: int = 1):
        self.value += step
        self.progress_bar.step(step)
        self.parent.update()
        self.parent.update_idletasks()

    def set_status(self, status: str, show_count: bool = True):
        new_status = f"{status} ({self.value + 1}/{self.maximum})" if show_count else status
        self.status_text.set(new_status)

    def set_ready_to_close(self):
        self.close_when_changes.set(1)

    def show_exit_button_and_wait(self):
        self.parent.protocol("WM_DELETE_WINDOW", self.set_ready_to_close)        
        close_button = ttk.Button(self.parent,
                                  text="Close",
                                  command=self.set_ready_to_close)
        close_button.pack(padx=XPADDING, pady=YPADDING)
        close_button.wait_variable("Ready to Close")
        sys.exit(0)

class MainWindow:
    root: tk.Tk
    test_identifier: str
    multi_page_image_file: Path
    output_folder: Path
    sort_results: bool
    debug_mode: bool = False
    cancelled: bool = False

    def __init__(self):

        app: tk.Tk = tk.Tk()
        self.__app = app
        app.title(f"{APP_NAME} - Select Inputs")

        # Only windows supports ICO files. Linux and macOS support XBM files, but they are single-
        # color and not that pretty so we just don't set an icon on other platforms. It's a minor
        # UX thing that most people will never notice.
        if platform.system() == "Windows":
            iconpath = str(Path(__file__).parent / "assets" / "icon.ico")
            app.iconbitmap(iconpath)

        app.protocol("WM_DELETE_WINDOW", self.__on_close)

        self.__test_identifier_widget = TestIdentifierWidget(app)       

        self.__multi_page_image_file_picker = InputFilePickerWidget(
            app, self.__on_update)

        self.__output_folder_picker = OutputFolderPickerWidget(
            app, self.__on_update)

        self.__status_text = tk.StringVar()
        status = tk.Label(app, textvariable=self.__status_text)
        status.pack(fill=tk.X, expand=1, pady=(YPADDING * 2, 0))
        self.__on_update()

        buttons_frame = tk.Frame(app)
        
        # "Open Help" Button
        if platform.system() in ('Windows'):
            pack(ttk.Button(buttons_frame,
                            text="Help",
                            command=self.__show_help),
                            padx=XPADDING,
                            pady=YPADDING,
                            side=tk.LEFT)

        # "Open Sheet" button
        if platform.system() in ('Windows'):
            pack(ttk.Button(buttons_frame,
                            text="Print Form",
                            command=self.__show_sheet),
                            padx=XPADDING,
                            pady=YPADDING,
                            side=tk.LEFT)

        
        self.__confirm_button = pack(ttk.Button(buttons_frame,
                                                text="✔ Continue",
                                                command=self.__confirm,
                                                state=tk.DISABLED),
                                     padx=XPADDING,
                                     pady=YPADDING,
                                     side=tk.RIGHT)
        pack(buttons_frame, fill=tk.X, expand=1)

        self.__ready_to_continue = tk.IntVar(name="Ready to Continue")
        app.wait_variable("Ready to Continue")

    def __on_update(self):
        ok_to_submit = True
        new_status = ""

        self.test_identifier = self.__test_identifier_widget.get()

        multi_page_image_file = self.__multi_page_image_file_picker.file

        if multi_page_image_file is None:
            new_status += "❌ Input file is required.\n"
            ok_to_submit = False
        else:
            self.multi_page_image_file = multi_page_image_file
            new_status += f"✔ Image file selected.\n"
            ok_to_submit = True

        new_status += "Using 75-question form.\n"

        output_folder = self.__output_folder_picker.folder
        if output_folder is None:
            new_status += "❌ Output folder is required.\n"
            ok_to_submit = False
        else:
            self.output_folder = output_folder
            new_status += f"✔ Output folder selected.\n"

        self.sort_results = self.__output_folder_picker.sort_results
        if self.sort_results:
            new_status += f"Results will be sorted by name.\n"
        else:
            new_status += f"Input sort order will be maintained.\n"

        self.__status_text.set(new_status)
        if ok_to_submit:
            self.__confirm_button.configure(state=tk.NORMAL)
        return ok_to_submit

    def __disable_all(self):
        self.__test_identifier_widget.disable()
        self.__confirm_button.configure(state=tk.DISABLED)
        self.__multi_page_image_file_picker.disable()
        self.__output_folder_picker.disable()

    def __confirm(self):
        if self.__on_update():
            self.__disable_all()
            self.__ready_to_continue.set(1)
    
    def __show_help(self):
        helpfile = str(Path(__file__).parent / "assets" / "manual.pdf")
        if platform.system() in ('Darwin','Linux'):
            """
            subprocess.Popen(['open',helpfile])
            """
        elif platform.system() in ('Windows'):
            subprocess.Popen([helpfile], shell=True)

    def __show_sheet(self):
        helpfile = str(
            Path(__file__).parent / "assets" /
            "multiple_choice_sheet_75q.pdf")
        if platform.system() in ('Darwin','Linux'):
            """
            subprocess.Popen(['open', helpfile])
            """
        elif platform.system() in ('Windows'):
            subprocess.Popen([helpfile], shell=True)
    
    def __on_close(self):
        self.__app.destroy()
        self.__ready_to_continue.set(1)
        self.cancelled = True

    def create_and_pack_progress(self, maximum: int) -> ProgressTrackerWidget:
        return ProgressTrackerWidget(self.__app, maximum)
