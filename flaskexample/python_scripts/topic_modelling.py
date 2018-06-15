from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
import os
import re
import glob
import nltk
nltk.download('words')

from sklearn.feature_extraction.text import CountVectorizer
from sklearn import decomposition
import operator
import numpy as np
from sklearn.externals import joblib

###### Helper Functions #######
def get_descriptor(terms, H, topic_index, top):
    # reverse sort the values to sort the indices
    top_indices = np.argsort( H[topic_index,:] )[::-1]
    # now get the terms corresponding to the top-ranked indices
    top_terms = []
    for term_index in top_indices[0:top]:
        top_terms.append( terms[term_index] )
    return top_terms

def rank_terms( A, terms ):
    # get the sums over each column
    sums = A.sum(axis=0)
    # map weights to the terms
    weights = {}
    for col, term in enumerate(terms):
        weights[term] = sums[0,col]
    # rank the terms by their weight over all documents
    return sorted(weights.items(), key=operator.itemgetter(1), reverse=True)

def clean_readme(readme, EngWords):
    preproc_text = open(readme, 'r', encoding='utf-8').read()
    preproc_text.replace('\n', '')
    preproc_text = re.sub(r'<.*?>\s*', '', preproc_text, flags=re.DOTALL)
    preproc_text = re.sub(r'\[.*?\]\s*', '', preproc_text, flags=re.DOTALL)
    preproc_text = re.sub(r'\(.*?\)\s*', '', preproc_text, flags=re.DOTALL)
    text = re.sub('[^A-Za-z0-9 /.]+', '', preproc_text).lower()
    cleaned_text = [token for token in simple_preprocess(text) if token not in STOPWORDS and token in EngWords]
    return " ".join(cleaned_text)

###################################

def get_corpus(dir):
    readmes = glob.glob('%s/*.txt'%dir)
    EngWords = set(nltk.corpus.words.words())
    
    corpus = []
    for r in readmes:
        if 'CORPUS.txt' in r:
            continue
        try:
            corpus.append(clean_readme(r, EngWords))
        except:
            print('couldnt process %s'%r)

    f = open('%s/CORPUS.txt'%dir, 'w')
    for doc in corpus:
        f.write(doc)
        f.write('\n')
    f.close()
    return corpus

def train_topic_model(dir='readmes', n_topics=3):
    corpus = get_corpus(dir)
    
    # base directory is from ./run.py
    vectorizer = CountVectorizer(min_df = 20)
    A = vectorizer.fit_transform(corpus)
    joblib.dump(vectorizer, 'models/vectorizer.pkl')

    terms = vectorizer.get_feature_names()
    ranking = rank_terms(A, terms)
    print("top ranked terms in corpus")
    for i, pair in enumerate(ranking[0:20]):
        print("%02d. %s (%.2f)"%(i+1, pair[0], pair[1]))

    n_topics = 3
    model = decomposition.NMF( init="nndsvd", n_components=n_topics)
    # apply the model and extract the two factor matrices
    W = model.fit_transform(A).round(3)
    H = model.components_
    joblib.dump(model, 'models/model.pkl')

    descriptors = []
    for topic_index in range(n_topics):
        descriptors.append(get_descriptor(terms, H, topic_index, 10))
        str_descriptor = ", ".join( descriptors[topic_index])
        print("Topic %02d: %s"%(topic_index+1, str_descriptor))

def get_topics_from_corpus(dir='candidate'):
    vectorizer = joblib.load('models/vectorizer.pkl')
    model = joblib.load('models/model.pkl')

    corpus = get_corpus(dir)
    return model.transform(vectorizer.transform(corpus))

if __name__ == '__main__':
    #train_topic_model()
    topics = get_topics_from_corpus('candidate')
    print(topics)

