import pymysql
import pandas as pd
def read_data():
    mydb = pymysql.connect(host='localhost',
                                   user='root',
                                   passwd='SOSCEO!helpsos0',
                                   db='jobs_db')
    
    cursor = mydb.cursor()
    sql = """SELECT * FROM jobs_new"""
    cursor.execute(sql)
    data_raw=cursor.fetchall()
    mydb.close()
    
    job_title =[]
    employer = []
    location =[]
    employer_id =[] 
    position_id=[] 
    skills= []
    description=[]
    for i in range(0,len(data_raw)):    
        job_title.append(data_raw[i][0])
        employer.append(data_raw[i][1])
        location.append(data_raw[i][2])
        employer_id.append(data_raw[i][3])
        position_id.append(data_raw[i][4])
        skills.append(data_raw[i][5])
        description.append(data_raw[i][6])
    dictionary = {'job_title' : job_title,
                  'employer' : employer,
                  'location' : location,
                  'employer_id' : employer_id, 
                  'position_id':position_id, 
                  'skills':skills,
                  'description':description}
    data = pd.DataFrame(data=dictionary)
    return data