import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
import io
import re
import numpy as np

def pdfparser(data):
    fp = open(data, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        data =  retstr.getvalue()
    
    return data

def main():
    # base directory is from ./run.py
    python_packages = open('utils/popular_packages.txt', 'r').read().lower().split()
    preproc_text = pdfparser('utils/Insight_Resume.pdf')
    text = re.sub('[^A-Za-z0-9 /.-]+', '', preproc_text).lower().split()
    
    user_packages = []
    git_user = None
    git_user_flag = 0
    for t in text:
        if t in python_packages and t not in user_packages:
            user_packages.append(t)
        if 'github.com/' in t and git_user_flag == 0:
            git_user = t.split('/')[1]
            git_user_flag = 1

    return git_user, user_packages
