import os
import re
import json
import time
import pandas as pd
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv
from selenium_stealth import stealth


load_dotenv()

class LinkedInJobScraper:
    def __init__(self, search_link):
        self.username = os.getenv('LINKEDIN_USERNAME')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.driver = self.configure_webdriver()
        self.search_link = search_link
        self.job_dicts = []

    def configure_webdriver(self):
        driver = Driver(uc=True, headless=False)
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="MacIntel",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
        )
        return driver

    def login(self):
        self.driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
        time.sleep(3)

        elementID = self.driver.find_element(By.ID, 'username')
        elementID.send_keys(self.username)
        time.sleep(2)

        elementID = self.driver.find_element(By.ID, 'password')
        elementID.send_keys(self.password)
        time.sleep(1)

        elementID.submit()

    def search_jobs(self):
        self.login()
        self.driver.get(self.search_link)
        job_ids = self.driver.find_elements(By.CLASS_NAME, 'jobs-search-results__list-item')

        for i, job_id in enumerate(job_ids):
            try:
                print(f"job N : {i}")
                job_dict = {}

                job_id.click()
                time.sleep(2)  # Wait for the job details to load

                src = self.driver.page_source
                soup = BeautifulSoup(src, 'lxml')

                job_dict['title'] = soup.find("h1", {"class": "jobs-details__main-content"}).text.strip()
                job_dict['company'] = soup.find("a", {"class": "jobs-details-top-card__company-url"}).text.strip()
                job_dict['location'] = soup.find("span", {"class": "jobs-details-top-card__bullet"}).text.strip()
                job_dict['description'] = soup.find("div", {"id": "job-details"}).text.strip()

                self.job_dicts.append(job_dict)
            except Exception as e:
                print(f"Error scraping job {i}: {e}")
                continue

    def scrape_job_data(self):
        df = pd.DataFrame(self.job_dicts)
        return df

    def clean_data(self, df):
        df['description'] = df['description'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())
        return df

    def save_csv(self, df, job_position, job_location):
        file_path = self.get_user_desktop_path(job_position, job_location)
        csv_file = '{}.csv'.format(file_path)
        df.to_csv(csv_file, index=False)
        return csv_file

    def get_user_desktop_path(self, job_position, job_location):
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "Desktop")
        return os.path.join(desktop_path, f'{job_position}_{job_location}')

    def send_email(self, df, sender_email, receiver_email, job_position, job_location, password):
        msg = MIMEMultipart()
        msg['Subject'] = 'New Jobs from LinkedIn'
        msg['From'] = sender_email
        msg['To'] = ','.join(receiver_email)

        attachment_filename = self.generate_attachment_filename(job_position, job_location)
        csv_content = df.to_csv(index=False).encode()

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(csv_content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{attachment_filename}"')
        msg.attach(part)

        self.send_email_message(sender_email, receiver_email, msg, password)

    def send_email_message(self, sender_email, receiver_email, msg, password):
        s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
        s.login(user=sender_email, password=password)
        s.sendmail(sender_email, receiver_email, msg.as_string())
        s.quit()

    def generate_attachment_filename(self, job_title, job_location):
        return f"{job_title.replace(' ', '_')}_{job_location.replace(' ', '_')}.csv"