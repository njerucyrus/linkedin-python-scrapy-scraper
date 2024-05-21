import os
from time import sleep
from typing import Any

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep
import time
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from dotenv import load_dotenv
load_dotenv()

username = 'chao.liu@macaws.ai'
password = '123Warwick123*'

class LinkedInPeopleProfileSpider(scrapy.Spider):
    name = "linkedin_people_profile"

    custom_settings = {
        'FEEDS': {'data/%(name)s_%(time)s.jsonl': {'format': 'jsonlines', }}
    }

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.options = uc.ChromeOptions()
        self.options.add_argument("start-maximized")
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/80.0.3987.149 Safari/537.36"
        )
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        # Initializing the webdriver
        self.service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.scrapy_cookies = None
        self.login()

    def login(self):
        # login to linkedin
        self.driver.implicitly_wait(2)
        login_url = 'https://www.linkedin.com/login'
        self.driver.get(login_url)
        self.driver.implicitly_wait(2)
        print('- Finish initializing a driver')
        self.driver.implicitly_wait(2)
        email_field = self.driver.find_element("id", "username")
        email_field.send_keys(username)
        print('- Finish keying in email')
        self.driver.implicitly_wait(10)
        password_field = self.driver.find_element("name", "session_password")
        password_field.send_keys(password)
        print('- Password typed')
        self.driver.implicitly_wait(2)
        signin_field = self.driver.find_element(By.XPATH,
                                                '//button[@class="btn__primary--large from__button--floating"]')
        signin_field.click()
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(login_url)
        )

        print('- Login to LinkedIn')
        cookies = self.driver.get_cookies()
        print(f'OBTAINED COOKIES: {cookies}')
        scrapy_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
        #update_cookies
        self.scrapy_cookies = scrapy_cookies


    def start_requests(self):
        if self.scrapy_cookies is not None:

            profile_list = ['chao-liu-b9380925b']

            for profile in profile_list:
                linkedin_people_url = f'https://www.linkedin.com/in/{profile}/'
                yield scrapy.Request(url=linkedin_people_url, callback=self.parse_profile, cookies=self.scrapy_cookies,
                                     meta={'profile': profile, 'linkedin_url': linkedin_people_url})

            self.driver.quit()
        else:
            print('No cookies found. Needs login to continue')
            pass

    def parse_profile(self, response):


        item = {}
        item['profile'] = response.meta['profile']
        item['url'] = response.meta['linkedin_url']

        """
            SUMMARY SECTION
        """
        summary_box = response.css("section.top-card-layout")
        item['name'] = summary_box.css("h1::text").get().strip()
        item['description'] = summary_box.css("h2::text").get().strip()

        email = response.css('section.pv-contact-info__contact-type:nth-child(2) a::attr(href)').get()
        if email and email.startswith('mailto:'):
            email = email.replace('mailto:', '')
            item['email'] = email

        ## Location
        try:
            item['location'] = summary_box.css('div.top-card__subline-item::text').get()

        except:
            item['location'] = summary_box.css('span.top-card__subline-item::text').get().strip()
            if 'followers' in item['location'] or 'connections' in item['location']:
                item['location'] = ''

        item['followers'] = ''
        item['connections'] = ''

        for span_text in summary_box.css('span.top-card__subline-item::text').getall():
            if 'followers' in span_text:
                item['followers'] = span_text.replace(' followers', '').strip()
            if 'connections' in span_text:
                item['connections'] = span_text.replace(' connections', '').strip()

        """
            ABOUT SECTION
        """
        item['about'] = response.css('section.summary div.core-section-container__content p::text').get()

        """
            EXPERIENCE SECTION
        """
        item['experience'] = []
        experience_blocks = response.css('li.experience-item')
        for block in experience_blocks:
            experience = {}
            ## organisation profile url
            try:
                experience['organisation_profile'] = block.css('h4 a::attr(href)').get().split('?')[0]
            except Exception as e:
                print('experience --> organisation_profile', e)
                experience['organisation_profile'] = ''

            ## location
            try:
                experience['location'] = block.css('p.experience-item__location::text').get().strip()
            except Exception as e:
                print('experience --> location', e)
                experience['location'] = ''

            ## description
            try:
                experience['description'] = block.css('p.show-more-less-text__text--more::text').get().strip()
            except Exception as e:
                print('experience --> description', e)
                try:
                    experience['description'] = block.css('p.show-more-less-text__text--less::text').get().strip()
                except Exception as e:
                    print('experience --> description', e)
                    experience['description'] = ''

            ## time range
            try:
                date_ranges = block.css('span.date-range time::text').getall()
                if len(date_ranges) == 2:
                    experience['start_time'] = date_ranges[0]
                    experience['end_time'] = date_ranges[1]
                    experience['duration'] = block.css('span.date-range__duration::text').get()
                elif len(date_ranges) == 1:
                    experience['start_time'] = date_ranges[0]
                    experience['end_time'] = 'present'
                    experience['duration'] = block.css('span.date-range__duration::text').get()
            except Exception as e:
                print('experience --> time ranges', e)
                experience['start_time'] = ''
                experience['end_time'] = ''
                experience['duration'] = ''

            item['experience'].append(experience)

        """
            EDUCATION SECTION
        """
        item['education'] = []
        education_blocks = response.css('li.education__list-item')
        for block in education_blocks:
            education = {}

            ## organisation
            try:
                education['organisation'] = block.css('h3::text').get().strip()
            except Exception as e:
                print("education --> organisation", e)
                education['organisation'] = ''

            ## organisation profile url
            try:
                education['organisation_profile'] = block.css('a::attr(href)').get().split('?')[0]
            except Exception as e:
                print("education --> organisation_profile", e)
                education['organisation_profile'] = ''

            ## course details
            try:
                education['course_details'] = ''
                for text in block.css('h4 span::text').getall():
                    education['course_details'] = education['course_details'] + text.strip() + ' '
                education['course_details'] = education['course_details'].strip()
            except Exception as e:
                print("education --> course_details", e)
                education['course_details'] = ''

            ## description
            try:
                education['description'] = block.css('div.education__item--details p::text').get().strip()
            except Exception as e:
                print("education --> description", e)
                education['description'] = ''

            ## time range
            try:
                date_ranges = block.css('span.date-range time::text').getall()
                if len(date_ranges) == 2:
                    education['start_time'] = date_ranges[0]
                    education['end_time'] = date_ranges[1]
                elif len(date_ranges) == 1:
                    education['start_time'] = date_ranges[0]
                    education['end_time'] = 'present'
            except Exception as e:
                print("education --> time_ranges", e)
                education['start_time'] = ''
                education['end_time'] = ''

            item['education'].append(education)

        yield item
