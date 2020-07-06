from bs4 import BeautifulSoup
import requests
import pdfquery
import urllib.request, urllib.error, urllib.parse


def get_pdf_txt(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup.prettify())


get_pdf_txt('https://agupubs.onlinelibrary.wiley.com/doi/pdfdirect/10.1029/2012JD017794')