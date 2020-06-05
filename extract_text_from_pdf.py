from os import listdir
import os.path
from os.path import isfile, join
import glob
from io import StringIO
import json
import os
import shutil

from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter

def pdf_to_text(path):
    resource_manager = PDFResourceManager()
    fake_file_handle = StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    fh = open(path, 'rb')
    for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
        page_interpreter.process_page(page)

    text = fake_file_handle.getvalue()

    fh.close()
    # close open handles
    converter.close()
    fake_file_handle.close()

    return text

mypath = "/home/igerasim/Zotero/storage/"
txtpath = "/home/igerasim/allenai/data/input/files/text/"
co_path = "/home/igerasim/allenai/data/input/files/text_co/"

#onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
#onlyfiles = glob.glob('/home/igerasim/Zotero/storage/*/*.pdf',  recursive = True) 
json_publications_path = os.path.abspath("data/publications_co.json")
with open(json_publications_path) as json_publications_file:
  publications = json.load(json_publications_file)


#print(onlyfiles)
#quit()

for publication in publications :
  filename = publication["pdf_file_name"]
  outfile = txtpath+publication["text_file_name"]

  if os.path.isfile(outfile):
    continue
  print(filename, outfile)
  #continue
  text = pdf_to_text(filename)
  outfileObj = open(outfile, 'w')
  outfileObj.write(text)
  outfileObj.close()

