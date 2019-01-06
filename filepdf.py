import PyPDF2
from os import getcwd, mkdir, path, rename
import easygui
from nameparser import HumanName

working_path = getcwd()
file_name = '2018_12_19_14_04_32.pdf'
page = 0
base_storage_folder = '/Scans'


def get_page(file_name, page):
    with open(file_name, 'rb') as f:
        pdf_reader = PyPDF2.PdfFileReader(f)
        page_qty = pdf_reader.numPages
        page_obj = pdf_reader.getPage(page)
        the_page = page_obj.extractText()
        return the_page, page_qty


the_page, page_qty = get_page(file_name, page)

while page <= page_qty:
    if the_page.find('8879') == 0:
        nameEnd = the_page.find("Spouse's name")
        nameStart = the_page.find("Taxpayer's name") + 15
        name = the_page[nameStart:nameEnd]
        break
    else:
        print('Page is not 8879, advancing')
        page += 1
        the_page, page_qty = get_page(file_name, page)

print('Done, Found name:', name)
name_parse = HumanName(name)
name = name_parse.last + ' ' + name_parse.first
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
    print('Move Canceled')
else:
    name = fieldValue[0]
    print('Name has been verified as:', name)


def move_file(file_name):
    try:
        rename(file_name, '/Scans/{}/{}'.format(name, file_name))
    except FileExistsError:
        print('File name already exists, cannot move.')
    else:
        print('File has been moved.')


if path.isdir('/Scans/{}'.format(name)) is True:
    print('Folder already exists, moving file.')
    move_file(file_name)
else:
    try:
        mkdir('/Scans/{}'.format(name))
    except OSError:
        print('Failed creating directory')
    else:
        print('Created directory for', name)
        move_file(file_name)
