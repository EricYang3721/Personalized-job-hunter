 import numpy as np
import pandas as pd
import csv
import pymysql
# Load data 
data = pd.read_csv('data/nyJobs.csv')

mydb = pymysql.connect(host='localhost',
                               user='root',
                               passwd='SOSCEO!helpsos0',
                               db='jobs_db')

data = data.fillna('not available')

cursor = mydb.cursor()
sql = """INSERT INTO jobs_new(job_title, employer, location, employer_id, 
    position_id, skills, description) VALUES(%s, %s, %s, %s, %s, %s, %s)"""

for i in range(0,1539):
    itr = (data.iloc[i, 0], data.iloc[i, 1], data.iloc[i,2], data.iloc[i,3],
           data.iloc[i,4], data.iloc[i,5], data.iloc[i,6])
    cursor.execute(sql,itr)
    mydb.commit()

mydb.close()