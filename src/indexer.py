import os
import re
import string
import gensim.parsing.preprocessing
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def clean_text(text):
    text = os.linesep.join([l for l in text.splitlines() if l])
    text = text.lower()
    text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'[0-9]', '', text)
    text = gensim.parsing.preprocessing.remove_stopwords(text)
    return text


def index_text(articles):
    freq_matrix = TfidfVectorizer(stop_words=None)
    table = freq_matrix.fit_transform(articles)
    table = table.T.toarray()
    fm_df = pd.DataFrame(table, index=freq_matrix.get_feature_names())
    return fm_df
