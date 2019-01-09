import PyPDF2
from os import getcwd, mkdir, path, rename
import easygui
from nameparser import HumanName
import sys
import json

working_path = getcwd()


def get_config():
    try:
        with open('config.json') as f:
            data = json.load(f)
            root_path = data['config']['base_path']
            year_path = data['config']['year']
            return root_path, year_path
    except FileNotFoundError:
        print('Config not found')
        return None, None


def get_filename():
    if sys.argv[1:]:
        filename = sys.argv[1]
        return filename
    else:
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
    msg = 'Check name found is correct:'
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


def move_file(name, filename, root_path, year_path):
    try:
        rename(filename, '{}/{}/{}/{}'.format(root_path, year_path, name, filename))
    except FileExistsError:
        print('File name already exists, cannot move.')
        return 'File name exists'
    else:
        print('File has been moved.')
        return None


def make_dir(name, filename, root_path, year_path):
    # results = None
    if path.isdir('{}/{}'.format(root_path, year_path)) is True:
        if path.isdir('{}/{}/{}'.format(root_path, year_path, name)) is True:
            print('Folder already exists, moving file.')
            move_file(name, filename, root_path, year_path)
        else:
            try:
                mkdir('{}/{}/{}'.format(root_path, year_path, name))
            except OSError:
                print('Failed creating directory')
                return 'Failed to create folder'
            else:
                print('Created directory for', name)
                results = move_file(name, filename, root_path, year_path)
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


def main():
    root_path, year_path = get_config()
    if not root_path:
        return
    # filename = get_filename()
    filename = '2018_12_19_14_04_32.pdf'
    if not filename:
        return
    name = name_from_pdf(filename)
    if name:
        name = name_parse(name)
    name = dis_dialog(name)
    if not name:
        return
    results = make_dir(name, filename, root_path, year_path)
    print('Results:', results)


main()
