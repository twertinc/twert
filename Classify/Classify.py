from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from bs4 import BeautifulSoup
import bs4 as bs4
from urllib.parse import urlparse
import requests
import pandas as pd
import spacy as sp
import pickle
import sqlite3
import time
from requests.models import MissingSchema
import threading
import os
import sys
import logging 
from pathlib import Path
import sklearn.calibration

print(sp.__version__)

application_path = ""
database_path = "nblocker.sqlite3"
bundle_dir = ""
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    database_path = os.path.join(application_path, database_path)
    bundle_dir = os.path.join(sys._MEIPASS, "en_core_web_sm\en_core_web_sm-3.5.0")
else:
    application_path = os.path.dirname(__file__)
    database_path = os.path.join(os.path.dirname(application_path),database_path)
    bundle_dir = os.path.join(os.path.dirname(application_path), r"env\Lib\site-packages\en_core_web_sm\en_core_web_sm-3.5.0")


print('application_path', application_path)
print('database_path', database_path)

bruh = application_path + ' '+database_path


sp.prefer_gpu()
#anconda prompt ko run as adminstrator and copy paste this:python -m spacy download en



nlp = sp.load(bundle_dir)


def clean_text(doc):
    '''
    Clean the document. Remove pronouns, stopwords, lemmatize the words and lowercase them
    '''
    doc = nlp(doc)
    tokens = []
    exclusion_list = ["nan"]
    for token in doc:
        if token.is_stop or token.is_punct or token.text.isnumeric() or (token.text.isalnum()==False) or token.text in exclusion_list :
            continue
        token = str(token.lemma_.lower().strip())
        tokens.append(token)
    return " ".join(tokens)
    
modelFilename = os.path.join(application_path, "urlClassificationModel.pkl")

with open(modelFilename, 'rb') as file:
    urlClassificationModel = pickle.load(file)

fitted_vectorizer_filename = os.path.join(application_path, "fitted_vectorizer.pkl")
with open(fitted_vectorizer_filename, 'rb') as file:
    fitted_vectorizer = pickle.load(file)

id_to_category_filename = os.path.join(application_path, "id_to_category.pkl")
with open(id_to_category_filename, 'rb') as file:
    id_to_category = pickle.load(file)



import re

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

def scrape_url(url):
    try:
        res = requests.get(url, headers=REQUEST_HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            [tag.decompose() for tag in soup("script")]
            [tag.decompose() for tag in soup("style")]
            text = soup.body.get_text(' ', strip = True)
            return text
        else:
            print(
                f'Request failed ({res.status_code}). Please check if website do not blocking or it is still existing')
            return False
    except Exception as e:
        print(f'Request to {url} failed. Error code:\n {e}')
        return False




websites=['https://github.com/MilaNLProc/contextualized-topic-models/issues/113', 
          'https://www.engineering.cornell.edu/students/undergraduate-students/advising/new-students', 
          'https://www.facebook.com/', 
          'https://www.sciencedaily.com/releases/2023/04/230427173454.htm']
def thread_run(): 
    while True:
        time.sleep(1)
        try:
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()
            rows = cursor.execute("""select id, domain
                            from domains
                            where category is null  
                            order by last_seen desc 
                            limit 30""").fetchall()
            print(rows)
            for i in rows:    
                # web=dict(scrapTool.visit_url(website))
                # text=(clean_text(web['website_text']))
                # print(text)

                id = i[0]
                url = i[1]
                url = "https://" + url
                text = scrape_url(url)
                print(text)
                result = 'undefined'
                if text != False:
                    text = (clean_text(text))
                    #print(text)
                    t=fitted_vectorizer.transform([text])
                    result = id_to_category[urlClassificationModel.predict(t)[0]]
                    print(result)
                cursor.execute("""update domains
                set CATEGORY = ? WHERE ID = ?""", (result, id))
                connection.commit()
            temp_rows = cursor.execute("""select id, domain, category
            from domains
            order by last_seen desc
            limit 30""").fetchall()
            ind = 1
            for i in temp_rows:
                print(ind, i)
                ind+=1
            connection.close()
        except Exception as e:
            print(e)


def start_thread():
    rThread = threading.Thread(target=thread_run,daemon=True)
    rThread.start()
    pass
