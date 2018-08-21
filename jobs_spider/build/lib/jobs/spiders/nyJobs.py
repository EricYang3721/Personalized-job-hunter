# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from time import sleep
import random

class NyjobsSpider(scrapy.Spider):
    name = "nyJobs"
    allowed_domains = ["www.dice.com"]
    start_urls = ['https://www.dice.com/jobs/q-data_OR_mechanical-jtype-Full+Time-startPage-15-jobs?searchid=8687435708472&stst=']

    def parse(self, response):
        urls=response.xpath('//a[contains(@id, "position")]/@href').extract()
        for url in urls:
            yield Request(url, callback = self.parse_jobs)
            sleep(random.randrange(1,3))
        for i in range(0,100): 
            next_url = response.xpath('//link[@rel="next"]/@href').extract_first()
            yield Request(next_url, callback = self.parse)
            sleep(random.randrange(5,20))
    
    def parse_jobs(self, response):
        job_title = response.xpath('//h1[@class="jobTitle"]/text()').extract_first()
        employer = response.xpath('//*[@class="employer"]/a/text()').extract_first()
        location = response.xpath('//*[@class="location"]/text()').extract_first()
        
        employer_id = response.xpath('//*[@class="company-header-info"]/div/div[@class="col-md-12"]/text()')[0].extract()
        employer_id = employer_id.split()[3]
        
        position_id = response.xpath('//*[@class="company-header-info"]/div/div[@class="col-md-12"]/text()')[1].extract()
        position_id = position_id.split()[3]
        
        skills = response.xpath('//*[@class="row job-info"]/div[1]/div[2]/text()').extract_first()
        skills = re.sub('\s+', ' ', skills)
        
        description = response.xpath('//*[@id="jobdescSec"]/text()').extract()
        description = ' '.join(description)
        description = re.sub('[^A-Za-z0-9,. ]','',description)
        
        yield{
                'job_title':job_title,
                'employer': employer,
                'location': location,
                'employer_id': employer_id,
                'position_id':position_id,
                'skills':skills,
                'descrition':description
                }
        