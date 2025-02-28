import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from bs4 import BeautifulSoup
from seleniumbase import Driver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import time


class IndeedJobScraper:
    def __init__(self):
        self.driver = self.configure_webdriver()
        self.total_jobs = "Unknown"
        self.country = 'https://ma.indeed.com'

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

    def search_jobs(self, job_position, job_location, date_posted):
        full_url = f'{self.country}/jobs?q={"+".join(job_position.split())}&l={job_location}&fromage={date_posted}'
        print(full_url)
        self.driver.get(full_url)
        try:
            self.driver.uc_gui_click_captcha()
        except NoSuchElementException:
            print("No captcha found")
        try:
            job_count_element = self.driver.find_element(By.XPATH,
                                                         '//div[starts-with(@class, "jobsearch-JobCountAndSortPane-jobCount")]')
            self.total_jobs = job_count_element.find_element(By.XPATH, './span').text
            print(f"{self.total_jobs} found")
        except NoSuchElementException:
            print("No job count found")
            self.total_jobs = "Unknown"

        self.driver.save_screenshot('screenshot.png')
        return full_url

    def scrape_job_data(self):
        df = pd.DataFrame({'Link': [''], 'Job Title': [''], 'Company': [''],
                           'Employer Active': [''], 'Location': ['']})
        job_count = 0
        while True:
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            boxes = soup.find_all('div', class_='job_seen_beacon')

            for i in boxes:
                link_full = self.extract_link(i)
                job_title = self.extract_job_title(i)
                company = self.extract_company(i)
                employer_active = self.extract_employer_active(i)
                location = self.extract_location(i)

                new_data = pd.DataFrame({'Link': [link_full], 'Job Title': [job_title],
                                         'Company': [company],
                                         'Employer Active': [employer_active],
                                         'Location': [location]})

                df = pd.concat([df, new_data], ignore_index=True)
                job_count += 1

            print(f"Scraped {job_count} of {self.total_jobs}")

            if not self.go_to_next_page(soup):
                break

        return df

    def extract_link(self, box):
        try:
            link = box.find('a', {'data-jk': True}).get('href')
            return self.country + link
        except (AttributeError, TypeError):
            try:
                link = box.find('a', class_=lambda x: x and 'JobTitle' in x).get('href')
                return self.country + link
            except (AttributeError, TypeError):
                return None

    def extract_job_title(self, box):
        try:
            return box.find('a', class_=lambda x: x and 'JobTitle' in x).text.strip()
        except AttributeError:
            try:
                return box.find('span', id=lambda x: x and 'jobTitle-' in str(x)).text.strip()
            except AttributeError:
                return None

    def extract_company(self, box):
        try:
            return box.find('span', {'data-testid': 'company-name'}).text.strip()
        except AttributeError:
            try:
                return box.find('span', class_=lambda x: x and 'company' in str(x).lower()).text.strip()
            except AttributeError:
                return None

    def extract_employer_active(self, box):
        try:
            return box.find('span', class_='date').text.strip()
        except AttributeError:
            try:
                return box.find('span', {'data-testid': 'myJobsStateDate'}).text.strip()
            except AttributeError:
                return None

    def extract_location(self, box):
        try:
            location_element = box.find('div', {'data-testid': 'text-location'})
            if location_element:
                try:
                    return location_element.find('span').text.strip()
                except AttributeError:
                    return location_element.text.strip()
            else:
                raise AttributeError
        except AttributeError:
            try:
                location_element = box.find('div', class_=lambda x: x and 'location' in str(x).lower())
                if location_element:
                    try:
                        return location_element.find('span').text.strip()
                    except AttributeError:
                        return location_element.text.strip()
                else:
                    return ''
            except AttributeError:
                return ''

    def go_to_next_page(self, soup):
        try:
            next_page = soup.find('a', {'aria-label': 'Next Page'}).get('href')
            next_page = self.country + next_page
            self.driver.get(next_page)
            return True
        except:
            return False

    def clean_data(self, df):
        def posted(x):
            try:
                x = x.replace('EmployerActive', '').strip()
                return x
            except AttributeError:
                pass
        df['Employer Active'] = df['Employer Active'].apply(posted)
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
        msg['Subject'] = 'New Jobs from Indeed'
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

    def send_email_empty(self, sender_email, receiver_email, subject, body, password):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = ','.join(receiver_email)
        msg.attach(MIMEText(body, 'plain'))

        self.send_email_message(sender_email, receiver_email, msg, password)

    def send_email_message(self, sender_email, receiver_email, msg, password):
        s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
        s.login(user=sender_email, password=password)
        s.sendmail(sender_email, receiver_email, msg.as_string())
        s.quit()

    def generate_attachment_filename(self, job_title, job_location):
        return f"{job_title.replace(' ', '_')}_{job_location.replace(' ', '_')}.csv"
