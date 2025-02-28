from indeed.indeed_job_scraper import IndeedJobScraper

def main():
    scraper = IndeedJobScraper()
    job_position = 'web developer'
    job_location = 'remote'
    date_posted = 20

    try:
        full_url = scraper.search_jobs(job_position, job_location, date_posted)
        df = scraper.scrape_job_data()

        if df.shape[0] == 0:
            print("No results found. Something went wrong.")
            print(f"Link: {full_url}")
        else:
            cleaned_df = scraper.clean_data(df)
            csv_file = scraper.save_csv(cleaned_df, job_position, job_location)
            print(cleaned_df)
    finally:
        scraper.driver.quit()

