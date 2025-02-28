# Job Finder

*This Python script scrapes job data from Indeed for a specific job position and location. It uses Selenium for web scraping and BeautifulSoup for parsing HTML content. The script supports multiple countries and can send job results via email in CSV format. Additionally, it takes screenshots of the job search results.*

### Installation

1. Verify Python 3.x is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Run the script:
   ```bash
   python main.py
   ```

### Results

The script generates a CSV file with job results, takes screenshots of the job search results, and sends the results to the specified email address. If no results are found, an email with suggestions for refining the search criteria is sent. The email content is customized.

### Note

The script uses a headless Chrome browser for web scraping. Update the ChromeDriver version based on your Chrome browser version. Replace placeholder email addresses and passwords in the script with your own credentials. To enable the email feature, follow the instructions in this link: [How to Generate an App Password](https://support.google.com/mail/thread/205453566/how-to-generate-an-app-password?hl=en). Use this script responsibly.
