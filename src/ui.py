from tkinter import Tk, Label, StringVar, Entry, Button, END, IntVar, Checkbutton
from tkinter.filedialog import askopenfilename

import os
import glob
import shutil

from file_management.compile import compile_c
from file_management.feedback import (
    create_docx_feedback,
    get_missing_names,
    format_names,
)
from file_management.zip_archives import unzip, unzip_outer


class App(object):
    def __init__(self):
        self.root = Tk()

        # set default dimensions, color and title
        self.grey = "#909296"
        self.yellow = "#f7f574"
        self.green = "#93b185"

        self.root.geometry("600x450")
        self.root.wm_title("CompCorrector")

        self.label = Label(self.root, text="path to zipfile")
        self.label.pack(pady=5)

        # text entry for zip path
        self.zip_dir = StringVar()
        self.entry_zip_dir = Entry(
            self.root, textvariable=self.zip_dir, width="400", bg=self.grey
        )
        self.entry_zip_dir.pack(pady=5)

        # open zip button
        self.buttontext = StringVar()
        self.buttontext.set("CHOOSE ZIP")
        Button(
            self.root,
            textvariable=self.buttontext,
            command=self.select_zip_file,
            bg=self.yellow,
        ).pack(pady=5)

        self.label = Label(self.root, text="list of names")
        self.label.pack(pady=5)

        # text entry for names
        self.names = StringVar()
        self.entry_names = Entry(
            self.root, textvariable=self.names, width="400", bg=self.grey
        )
        self.entry_names.pack(pady=5)

        # check-boxes
        self.rm_zips = IntVar()
        self.rm_zips.set(False)
        self.check_rm_zips = Checkbutton(
            self.root,
            variable=self.rm_zips,
            onvalue=True,
            offvalue=False,
            text="remove zips",
        )

        self.compile = IntVar()
        self.compile.set(False)
        self.check_compile = Checkbutton(
            self.root,
            variable=self.compile,
            onvalue=True,
            offvalue=False,
            text="compile files",
        )

        self.safe_mode = IntVar()
        self.safe_mode.set(False)
        self.check_safe_mode = Checkbutton(
            self.root,
            variable=self.safe_mode,
            onvalue=True,
            offvalue=False,
            text="safe mode",
        )

        self.feedback = IntVar()
        self.feedback.set(False)
        self.check_feedback = Checkbutton(
            self.root,
            variable=self.feedback,
            onvalue=True,
            offvalue=False,
            text="feedback.docx",
        )

        # have checkbox checked by default
        self.check_rm_zips.select()
        self.check_compile.select()
        self.check_safe_mode.select()
        self.check_feedback.select()

        # place checkboxes on gui
        self.check_safe_mode.pack()
        self.check_rm_zips.pack()
        self.check_compile.pack()
        self.check_feedback.pack()

        # set open dir button
        self.buttontext2 = StringVar()
        self.buttontext2.set("START")
        Button(
            self.root,
            textvariable=self.buttontext2,
            command=self.run_main,
            bg=self.green,
        ).pack(pady=5)

        # label for errors
        self.error_label = Label(self.root, text="", foreground="red", bg=self.grey)
        self.error_label.pack(pady=5)

        # label for warnings
        self.warning_label = Label(
            self.root, text="", foreground=self.yellow, bg=self.grey
        )
        self.warning_label.pack(pady=5)

        # label for completion
        self.completion_label = Label(self.root, text="", bg=self.grey)
        self.completion_label.pack(pady=5)

        self.root.mainloop()

    def append_warning(self, warning_text):
        self.warning_label.configure(
            text=f"{self.warning_label.cget('text')} {warning_text}\n"
        )

    def append_error(self, error_text):
        self.error_label.configure(
            text=f"{self.error_label.cget('text')} {error_text}\n"
        )

    def flush_labels(self):
        self.warning_label.configure(text="")
        self.error_label.configure(text="")
        self.completion_label.configure(text="")

    def select_zip_file(self):
        self.flush_labels()
        filename = askopenfilename()
        if filename.endswith(".zip"):
            # flush old text and insert new selected file
            self.entry_zip_dir.delete(0, END)
            self.entry_zip_dir.insert(0, filename)
        else:
            self.append_error(f"You must select a .zip file to begin. Got {filename}")

        file_dir = os.path.dirname(filename)
        if not self.safe_mode.get() and len(glob.glob(f"{file_dir}/*")) > 1:
            self.append_warning(
                f"Be careful, there are multiple items in the current directory: {file_dir}"
            )

    def setup_safe_mode(self, cwd, zip_path):
        # make dir same name as zip (remove file extension, add slash)
        safe_dirname = os.path.basename(zip_path).split(".")[0]
        safe_cwd = os.path.join(cwd, safe_dirname)
        # create safe dir if it doesn't exist
        if not os.path.exists(safe_cwd):
            os.mkdir(safe_cwd)

        safe_zip_path = os.path.join(safe_cwd, os.path.basename(zip_path))

        # copy zip into safe directory
        shutil.copy2(zip_path, safe_zip_path)
        print("safe mode enabled", zip_path)
        # should not return safe_zip_path. That would lead to extracting the copied zip, nesting the dir again.
        # which would in turn cause problems with compiling.
        # e.g. foo.zip -> copied to foo/foo.zip, then extrac foo/foo.zip, creates foo/foo/the_files, not foo/the_files.
        return safe_cwd, zip_path

    def run_compile(self, cwd):
        try:
            compiled = compile_c(cwd, "gcc")
            if compiled > 0:
                self.append_error(f"Error compiling {compiled} file(s)")
        except:
            self.append_error(f"Exception compiling file(s)")
            raise

    def run_feedbac(self, cwd, names, missing_names):
        try:
            create_docx_feedback(cwd, names, missing_names)
        except:
            self.append_error("Exception creating feedback.docx")
            raise

    def main(self):
        self.flush_labels()

        try:
            names = format_names(self.entry_names.get())
        except:
            self.append_error("Exception parsing names")
            print("Exception parsing names")
            return False

        zip_path = self.entry_zip_dir.get()
        if not zip_path.endswith(".zip"):
            self.append_error(f"You must select a .zip file to begin. Got {zip_path}")
            return False

        # at this point names are list of strings and directory is correct
        cwd = os.path.dirname(zip_path)

        if self.entry_names.get().strip() == "":
            self.append_warning(
                f"No names included. All files will be extracted and feedback.docx will be empty"
            )

        # TODO: remove concept of safemode. Always run this way, don't allow unsafe mode.
        if self.safe_mode.get():
            cwd, zip_path = self.setup_safe_mode(cwd, zip_path)

        # if safe mode is enabled, move zip to safe folder, then run.
        # otherwise run in directory zip already is.
        unzip_outer(zip_path, names)

        # get directory of zipfile, unzip and move files in subdirectories
        extraction_errors = unzip(cwd, rm_zips=self.rm_zips.get())
        if extraction_errors:
            self.append_error(f"Exception extracting: {extraction_errors}")

        missing_names = get_missing_names(cwd, names)
        if missing_names:
            self.append_warning(
                f"The following students seem to be missing files: {missing_names}"
            )

        if self.compile.get():
            self.run_compile(cwd)

        if self.feedback.get():
            self.run_feedbac(cwd, names, missing_names)

        self.completion_label.configure(text="Finished!")
        print("Finished!")

    def run_main(self):
        try:
            self.main()
        except:
            # catch exception to allow prompt within ui, then re-raise exception
            self.error_label.configure(
                text=f"{self.error_label.cget('text')} Unhandled Exception. Check the console\n"
            )
            raise


if __name__ == "__main__":
    App()
