# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from time import sleep
import random
import pymysql

class NyjobsSpider(scrapy.Spider):
    name = "nyJobs"
    allowed_domains = ["www.dice.com"]
    start_urls = ['https://www.dice.com/jobs?q=data&l=&djtype=Full+Time&searchid=5094911727947&stst=']
    self.iter = 0
    
    def parse(self, response):
        # Open the database 'jobs_db'
        self.mydb = pymysql.connect(host='localhost',
                               user='root',
                               passwd='SOSCEO!helpsos0',
                               db='jobs_db')
        self.cursor = self.mydb.cursor()
        self.sql = """INSERT INTO jobs_new(job_title, employer, location, employer_id, 
        position_id, skills, description) VALUES(%s, %s, %s, %s, %s, %s, %s)"""
        
        # extract urls on each page
        urls=response.xpath('//a[contains(@id, "position")]/@href').extract()
        
        # Extract informations by get into each url on each page
        for url in urls:
            sleep(random.randrange(5,10))
            yield Request(url, callback = self.parse_jobs)
        self.mydb.close()
        
        # get the link for next page of searched result, call self.parse to crawl data
        while self.iter < 100: 
            next_url = response.xpath('//link[@rel="next"]/@href').extract_first()
            sleep(random.randrange(5,20))
            yield Request(next_url, callback = self.parse)
        
        
            
        
    
    def parse_jobs(self, response):
        # crawl and preprocess data for input in database, 
        # if no data extracted, save it as 'not available'
        job_title = response.xpath('//h1[@class="jobTitle"]/text()').extract_first()
        if job_title=='': job_title = 'not available'
        
        employer = response.xpath('//*[@class="employer"]/a/text()').extract_first()
        if employer=='': employer = 'not available'
        
        location = response.xpath('//*[@class="location"]/text()').extract_first()
        if location=='': location = 'not available'
        
        employer_id = response.xpath('//*[@class="company-header-info"]/div/div[@class="col-md-12"]/text()')[0].extract()
        employer_id = employer_id.split()[3]
        if employer_id=='': employer_id = 'not available'
        
        position_id = response.xpath('//*[@class="company-header-info"]/div/div[@class="col-md-12"]/text()')[1].extract()
        position_id = position_id.split()[3]
        if position_id=='': position_id = 'not available'
        
        skills = response.xpath('//*[@class="row job-info"]/div[1]/div[2]/text()').extract_first()
        skills = re.sub('\s+', ' ', skills)
        if skills=='': skills = 'not available'
        
        description = response.xpath('//*[@id="jobdescSec"]/text()').extract()
        description = ' '.join(description)
        description = re.sub('[^A-Za-z0-9,. ]','',description)
        if description=='': description = 'not available'
        
        # export data into a database
        itr = (job_title, employer, location, employer_id, position_id, skills, description)
        self.cursor.execute(self.sql,itr)
        self.mydb.commit()
        
        
        '''yield{
                'job_title':job_title,
                'employer': employer,
                'location': location,
                #'employer_id': employer_id,
                #'position_id':position_id,
                'skills':skills,
                'descrition':description
                }'''
        