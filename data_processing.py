# Data processing
import pandas as pd
import plotly.plotly as py
import seaborn as sns
import matplotlib.pyplot as plt
from nltk.stem.porter import PorterStemmer
import operator


data = pd.read_csv('data/nyJobs.csv')
data = data.drop_duplicates()
data.location[data.location=='New York City, NY'] = 'New York, NY'
data.location[data.location=='Nyc, NY'] = 'New York, NY'
data.location[data.location=='Ny, NY'] = 'New York, NY'
skills = data[(data.skills != ' ') & (data.skills.notnull())]
descriptions = data[(data.description != ' ') & (data.description.notnull())]
skills = skills[['job_title', 'location', 'position_id', 'skills']]
descriptions = descriptions[['job_title', 'location', 'position_id', 'description']]

job_distribution = data.location.value_counts().to_frame()
job_distribution.columns = ['counts']
job_distribution['location'] = job_distribution.index

# location distribution area new york
sns.barplot(y=job_distribution.location[0:10], x=job_distribution.counts[0:10], orient="h")
plt.title('Hottest job locations, Top 10')
plt.xlabel('Counts')
plt.ylabel('Cities')
plt.show()

# top skills needed
skills_only = skills.skills
skills_dict = {}
ps =PorterStemmer()
skills_only= skills_only.apply(lambda x: x.split(', '))
for item in skills_only:
    for skill in item:
        if ((skill == ' ') or (skill == '')): continue
        skill = skill.strip()
        skill = ps.stem(skill)
        if skill in skills_dict:
            skills_dict[skill] += 1
        else: skills_dict[skill] = 1

sorted_skills = sorted(skills_dict.items(), key=operator.itemgetter(1), reverse=True)

top20skills=[]
top20counts=[]
for item in sorted_skills:
    top20skills.append(item[0])
    top20counts.append(item[1])
top20 = pd.DataFrame({'skills':top20skills, 'counts':top20counts})
sns.barplot(y=top20.skills[0:20], x=top20.counts[0:20], orient="h")
plt.title('Most demanding skills, Top 20')
plt.xlabel('Counts')
plt.ylabel('Cities')
plt.show()

# Major needed
majors = pd.read_csv('data/major_list.csv')
majors['count'] = 0 
descriptions['description'] = descriptions['description'].apply(lambda x: x.lower())
majors.Major_Category = majors.Major_Category.apply(lambda x: x.lower())
for major in majors.Major_Category:
    for description in descriptions.description:
        if major in description:
            majors.loc[majors.Major_Category==major, 'count'] += 1;

majors = majors.sort(columns='count', ascending = False)
sns.barplot(y=majors.Major_Category[0:15], x=majors['count'][0:15], orient="h")
plt.title('Most demanding majors in great NYC area, Top 15')
plt.text(30, 13, '*Based on 1323 jobs description collected in NYC', style='italic')
plt.xlabel('Counts')
plt.ylabel('Majors')
plt.show()


