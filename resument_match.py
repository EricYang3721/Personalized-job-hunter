# Data processing
import pandas as pd
import plotly.plotly as py
import seaborn as sns
import matplotlib.pyplot as plt
from nltk.stem.porter import PorterStemmer
import operator
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.neighbors import NearestNeighbors
from read_data_from_sql import read_data

# Load Dataset
data = read_data()
data = data.drop_duplicates()
data = data.reset_index()
data.location[data.location=='New York City, NY'] = 'New York, NY'
data.location[data.location=='Nyc, NY'] = 'New York, NY'
data.location[data.location=='Ny, NY'] = 'New York, NY'
for i in range(0, data.shape[0]):
    data.loc[i, 'description'] = str(data.loc[i, 'description'])
    data.loc[i, 'description'] = data.loc[i, 'description'].strip()

descriptions = data[(data.description != '') & (data.description != 'nan')]
descriptions = descriptions[['job_title', 'location', 'position_id', 'description']]
descriptions = descriptions.reset_index()

# KNN for based on description and resume
# Get the description matrix 
ps =PorterStemmer()
description_corpus=[]
for i in range(0,descriptions.shape[0]):
    desc = re.sub(pattern='[^a-zA-Z]', repl=' ', string=descriptions['description'][i])
    desc=desc.lower()
    desc = desc.split()
    desc = [ps.stem(word) for word in desc]
    desc = ' '.join(desc)
    description_corpus.append(desc)

tfidf_v = TfidfVectorizer(ngram_range=(1,2))
X=tfidf_v.fit_transform(description_corpus).toarray()

# Example, get closet jobs for a web developper, 
# from a random sample web developper resume online
# process the sample
with open('data/web_developper.txt','r') as myfile:
    sample_resume=myfile.read().replace('\n', ' ')

sr = re.sub(pattern='[^a-zA-Z]', repl=' ', string=sample_resume)
sr=sr.lower()
sr = sr.split()
sr = [ps.stem(word) for word in sr]
sr = ' '.join(sr)
sr = [sr]
sample = tfidf_v.transform(sr).toarray()

# Find the 5 nearset neighbors
neighbors = NearestNeighbors(n_neighbors=5)
neighbors.fit(X)
fetched = neighbors.kneighbors(sample)[1]
fetched_id = [descriptions.loc[idx, 'position_id'] for idx in fetched][0].tolist()
result = data[data.position_id.isin(fetched_id)]
