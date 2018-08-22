# Data processing
import pandas as pd
import plotly.plotly as py
import seaborn as sns
import matplotlib.pyplot as plt
from nltk.stem.porter import PorterStemmer
import operator
import re
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from sklearn.neighbors import NearestNeighbors
from read_data_from_sql import read_data

data = read_data()
data = data.drop_duplicates()
data.location[data.location=='New York City, NY'] = 'New York, NY'
data.location[data.location=='Nyc, NY'] = 'New York, NY'
data.location[data.location=='Ny, NY'] = 'New York, NY'
skills = data[(data.skills != ' ') & (data.skills.notnull())]
descriptions = data[(data.description != ' ') & (data.description.notnull())]
skills_only = skills[['job_title', 'location', 'position_id', 'skills']]
descriptions = descriptions[['job_title', 'location', 'position_id', 'description']]
skills_only=skills_only.reset_index()
descriptions = descriptions.reset_index()

# KNN for based on skills
# Get the skills matrix 
ps =PorterStemmer()
skill_corpus=[]
for i in range(0,skills_only.shape[0]):
    skill = re.sub(pattern='[^a-zA-Z]', repl=' ', string=skills_only['skills'][i])
    skill=skill.lower()
    skill = skill.split()
    skill = [ps.stem(word) for word in skill]
    skill = ' '.join(skill)
    skill_corpus.append(skill)
cv = CountVectorizer()
X=cv.fit_transform(skill_corpus).toarray()

# Example, get closet jobs for a data scientist, 
# from a random Data Scientist resume online
# process the sample (Data Scitiest skill)
DS_skill = 'Algorithms, Analysis, Database, Data Mining, Excel, HTTP, Management, Metrics, Modeling, Python, Programming, SQL, SQL Server'
DS_skill = re.sub(pattern='[^a-zA-Z]', repl=' ', string=DS_skill)
DS_skill=DS_skill.lower()
DS_skill = DS_skill.split()
DS_skill = [ps.stem(word) for word in DS_skill]
DS_skill = ' '.join(DS_skill)
DS_skill = [DS_skill]
sample = cv.transform(DS_skill).toarray()
# Find the 5 nearset neighbors
neighbors = NearestNeighbors(n_neighbors=5)
neighbors.fit(X)
fetched = neighbors.kneighbors(sample)[1]
fetched_id = [skills_only.loc[idx, 'position_id'] for idx in fetched][0].tolist()
result = data[data.position_id.isin(fetched_id)]
