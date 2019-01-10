import PyPDF2
from os import mkdir, path, rename
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
from nameparser import HumanName
import sys
import json
import datetime


def get_config():
    try:
        with open('config.json') as f:
            data = json.load(f)
            root_path = data['config']['base_path']
            year_path = data['config']['year']
            confirm = data['config']['confirm']
            count = data['config']['count']
            return root_path, year_path, confirm, count
    except FileNotFoundError:
        print('Config not found')
        return None, None, None, None


def get_filename():
    if sys.argv[1:]:
        filename = sys.argv[1]
        return filename
    else:
        print('No filename specified')
        return None


def get_page(filename, page_num):
    try:
        with open(filename, 'rb') as f:
            pdf_reader = PyPDF2.PdfFileReader(f)
            qty = pdf_reader.numPages
            page_obj = pdf_reader.getPage(page_num)
            the_page = page_obj.extractText()
            return the_page, qty
    except FileNotFoundError:
        print('Filename specified was not found')
        return None, None


def name_from_pdf(filename):
    page_num = 0
    the_page, page_qty = get_page(filename, page_num)
    if page_qty is None:
        return False
    name = None
    if the_page:
        while page_num <= 50:       # Hardcoded max pages to look at, page_qty can be very slow if large pdf
            if the_page.find('8879') == 0:
                name_end = the_page.find("Spouse's name")
                name_start = the_page.find("Taxpayer's name") + 15
                name = the_page[name_start:name_end]
                break
            else:
                print('Page {} is not 8879, advancing'.format(page_num))
                page_num += 1
                if page_num == page_qty:
                    break
                the_page, page_qty = get_page(filename, page_num)
        return name
    else:
        return name


def name_parser(name):
    print('Done, Found name:', name)
    name_parse = HumanName(name)
    name = name_parse.last + ' ' + name_parse.first
    return name


def move_file(name, filename, root_path, year_path):
    now = datetime.datetime.now()
    global new_filename
    new_filename = name.upper() + now.strftime(' %m-%d-%Y %H%M.pdf')
    print(new_filename)
    try:
        rename(filename, '{}/{}/{}/{}'.format(root_path, year_path, name, new_filename))
    except FileExistsError:
        print('File name already exists, cannot move.')
        return 'File name exists'
    except FileNotFoundError:
        print('PDF File was not found, cannot move.')
        return 'File to move was missing'
    else:
        print('File has been moved.')
        return 'File has been moved'


def make_dir(name, filename, root_path, year_path, results=None):
    # results = None
    if path.isdir('{}/{}'.format(root_path, year_path)) is True:
        if path.isdir('{}/{}/{}'.format(root_path, year_path, name)) is True:
            print('Folder already exists, moving file.')
            results = move_file(name, filename, root_path, year_path)
            return results
        else:
            try:
                mkdir('{}/{}/{}'.format(root_path, year_path, name.upper()))
            except OSError:
                print('Failed creating directory')
                return 'Failed to create folder'
            else:
                print('Created directory for', name)
                results = move_file(name, filename, root_path, year_path)
                return results
    else:
        try:
            mkdir('{}/{}'.format(root_path, year_path))
        except OSError:
            print('Failed to create directory')
            return 'Failed to create folder'
        else:
            print('Created directory for', year_path)
            results = make_dir(name, filename, root_path, year_path)
    return results


def save_settings(root_path, year_path, confirm, count):
    try:
        with open('config.json', 'w') as f:
            count += 1
            data = dict()
            data['config'] = {}
            data['config']['base_path'] = root_path
            data['config']['year'] = year_path
            data['config']['confirm'] = confirm
            data['config']['count'] = count
            json.dump(data, f)
    except FileNotFoundError:
        print('Config not found')


class NameGUI:
    def __init__(self, master):
        master.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        # Top Heading Section
        heading = Frame(master, bg='white')
        heading.pack()
        heading.grid_rowconfigure(0, pad=20)

        self.title = Label(heading, text='Verify Settings & Client Name', font='bold', bg='white')
        self.title.grid(row=0)

        # Setting Section
        settings = LabelFrame(master, text='Settings:', bg='white')
        settings.pack(fill=X, padx=20)
        settings.grid_columnconfigure(0, minsize=70)
        settings.grid_columnconfigure(1, minsize=400)
        settings.grid_columnconfigure(2, minsize=70)
        settings.grid_rowconfigure(1, pad=5)
        settings.grid_rowconfigure(2, pad=5)

        self.tk_path = StringVar()
        self.tk_path.set(root_path)
        self.tk_year = IntVar()
        self.tk_year.set(year_path)
        self.tk_confirm = IntVar()
        self.tk_confirm.set(confirm)

        # Path Settings
        self.path_heading = Label(settings, text='Root Folder:', bg='white')
        self.path_heading.grid(row=1, column=0, sticky=E)

        self.path_entry = Label(settings, textvariable=self.tk_path, relief=SUNKEN, width=1)
        self.path_entry.grid(row=1, column=1, columnspan=1, sticky="ew")

        self.path_btn = Button(settings, text='Change', command=self.choose_folder, bg='light sky blue', bd=3)
        self.path_btn.grid(row=1, column=2)

        # Year Settings
        self.year_heading = Label(settings, text='Tax Year:', bg='white')
        self.year_heading.grid(row=2, column=0, sticky=E)

        self.year_entry = Label(settings, textvariable=self.tk_year, relief=SUNKEN)
        self.year_entry.grid(row=2, column=1, columnspan=1, sticky="ew")

        self.year_btn = Button(settings, text='Change', command=self.choose_year, bg='light sky blue', bd=3)
        self.year_btn.grid(row=2, column=2)

        # Confirmation Setting
        self.confirm_dlg = Checkbutton(settings, text='Confirmation Dialog', variable=self.tk_confirm, bg='white')
        self.confirm_dlg.grid(row=3, column=1)

        # Lower Section
        self.tk_name = StringVar()
        self.tk_name.set(name)

        bottom = Frame(master, bg='white')
        bottom.pack()
        bottom.grid_columnconfigure(0, minsize=70)
        bottom.grid_columnconfigure(1, minsize=300)
        bottom.grid_columnconfigure(2, minsize=120)
        bottom.grid_rowconfigure(0, minsize=10)

        self.client_format = Label(bottom, text='Format:', bg='white')
        self.client_format.grid(row=1, column=0, sticky=E)

        self.client_hint = Label(bottom, text='LAST FIRST', bg='white')
        self.client_hint.grid(row=1, column=1, sticky=W)

        self.client_heading = Label(bottom, text='Client Name:', font='bold', bg='white')
        self.client_heading.grid(row=2, column=0, sticky=E)

        self.client_entry = Entry(bottom, textvariable=self.tk_name, relief=SUNKEN, font='bold', bg='gray98', bd=2)
        self.client_entry.grid(row=2, column=1, columnspan=1, sticky="ew")

        self.client_btn = Button(bottom, text='Confirm & Move', command=self.confirm_client, bg='light green', bd=3)
        self.client_btn.grid(row=2, column=2)

        self.quit_btn = Button(bottom, text='Cancel', command=self.confirm_exit, bg='tomato', bd=3)
        self.quit_btn.grid(row=2, column=3)

        # Center Window On screen
        master.update_idletasks()
        width = master.winfo_width()
        frm_width = master.winfo_rootx() - master.winfo_x()
        win_width = width + 2 * frm_width
        height = master.winfo_height()
        win_height = height + frm_width
        x = master.winfo_screenwidth() // 2 - win_width // 2
        y = master.winfo_screenheight() // 2 - win_height // 2
        master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        master.deiconify()

        # Prevent Resize and min max buttons
        master.resizable(False, False)

    def choose_folder(self):
        global root_path
        root_path = filedialog.askdirectory(initialdir="/", title="Select Root Folder")
        print(root_path)
        if root_path is "":
            root_path = self.tk_path.get()
            print('No Root Set')
        else:
            self.tk_path.set(root_path)
            print('Root Set')
        print(root_path)

    def choose_year(self):
        global year_path
        year_path = simpledialog.askinteger(title='Set Year', prompt='Enter Year YYYY:', initialvalue=year_path)
        if year_path is None:
            year_path = self.tk_year.get()
            print('No Year Set')
        else:
            self.tk_year.set(year_path)
            print('Year Set')
        print(year_path)

    def confirm_client(self):
        global name, confirm, root_path, year_path, filename
        name = self.tk_name.get()
        confirm = self.tk_confirm.get()
        root_path = self.tk_path.get()
        year_path = self.tk_year.get()
        if name == "":
            messagebox.showinfo('Error', 'Need to enter a name')
            return

        results = make_dir(name, filename, root_path, year_path)
        lines = ['Moving file {}'.format(filename),
                 'Moving to folder:',
                 '{}/{}/{}/'.format(root_path, year_path, name.upper()),
                 'New filename:',
                 '{}'.format(new_filename),
                 '',
                 'Results: {}'.format(results)]

        if confirm == 1:
            print('Displaying Confirmation')
            messagebox.showinfo('Confirmation', '\n'.join(lines))
        # print(name, root_path, year_path, confirm)
        root.quit()

    def confirm_exit(self):
        response = messagebox.askokcancel('Confirm Exit', 'Do you really want to cancel?', default="cancel")
        if response is True:
            print('Canceling Move')
            root.quit()


def main():
    global root_path, year_path, confirm, name, root, filename
    root_path, year_path, confirm, count = get_config()
    if not root_path:
        return
    filename = get_filename()
    # filename = '2018_12_19_14_04_32.pdf'
    if not filename:
        return
    name = name_from_pdf(filename)
    if name:
        name = name_parser(name)

    # Run the GUI to confirm settings and name
    root = Tk()
    root.title('Scan Name & Mover')
    root.geometry('600x230')
    root.configure(bg='white')
    NameGUI(root)
    root.mainloop()

    if not name:
        return
    save_settings(root_path, year_path, confirm, count)


main()
