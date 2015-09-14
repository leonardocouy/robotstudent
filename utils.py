from unicodedata import normalize
from Downloader import Downloader
import os


def remove_accents(string):
    return normalize('NFKD', string).encode('ASCII', 'ignore').decode('ASCII')

def create_folder(folder_name):
    try:
        os.mkdir(folder_name)
    except OSError:
        pass


def download(cookies, url, folder):
    downloader = Downloader(cookies, url, folder)
    downloader.run()
