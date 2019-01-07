import PyPDF2
from os import getcwd, mkdir, path, rename
import easygui
from nameparser import HumanName
import sys

working_path = getcwd()
filename = '2018_12_19_14_04_32.pdf'
base_storage_folder = '/Scans'


def get_filename():
    if sys.argv[1:]:
        filename = sys.argv[1]
        return filename


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
        return None, 0


def name_from_pdf(filename):
    page_num = 0
    the_page, page_qty = get_page(filename, page_num)
    name = None
    if the_page:
        while page_num <= page_qty:
            if the_page.find('8879') == 0:
                nameEnd = the_page.find("Spouse's name")
                nameStart = the_page.find("Taxpayer's name") + 15
                name = the_page[nameStart:nameEnd]
                break
            else:
                print('Page is not 8879, advancing')
                page_num += 1
                the_page, page_qty = get_page(filename, page_num)
        return name
    else:
        return name


def name_parse(name):
    print('Done, Found name:', name)
    name_parse = HumanName(name)
    name = name_parse.last + ' ' + name_parse.first
    return name


def dis_dialog(name):
    msg = 'Check that name found is correct:'
    title = 'Enter Name'
    fieldName = ['Name:']
    fieldValue = [name]
    fieldValue = easygui.multenterbox(msg, title, fieldName, fieldValue)

    while 1:
        if fieldValue is None:
            break
        errmsg = ""
        if fieldValue[0] == "":
            errmsg = 'Name is required'
        if errmsg == "":
            break
        fieldValue = easygui.multenterbox(errmsg, title, fieldName, fieldValue)

    if fieldValue is None:
        name = None
        print('Move Canceled')
    else:
        name = fieldValue[0]
        print('Name has been verified as:', name)
    return name


def move_file(name, filename):
    try:
        rename(filename, '/Scans/{}/{}'.format(name, filename))
    except FileExistsError:
        print('File name already exists, cannot move.')
    else:
        print('File has been moved.')


def make_dir(name):
    if path.isdir('/Scans/{}'.format(name)) is True:
        print('Folder already exists, moving file.')
        move_file(name, filename)
    else:
        try:
            mkdir('/Scans/{}'.format(name))
        except OSError:
            print('Failed creating directory')
        else:
            print('Created directory for', name)
            move_file(name, filename)


def main():
    # filename = get_filename()
    if filename:
        name = name_from_pdf(filename)
        if name:
            name = name_parse(name)
            name = dis_dialog(name)
            if not name:
                return
            make_dir(name)


main()
