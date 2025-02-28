from linkedin.linkedin_job_scraper import LinkedInJobScraper

def main():
    job_position = "Data Scientist"
    job_location = "San Francisco, CA"
    search_link = f"https://www.linkedin.com/jobs/search/?keywords={job_position.replace(' ', '%20')}&location={job_location.replace(' ', '%20')}"

    scraper = LinkedInJobScraper(search_link)
    scraper.search_jobs()
    df = scraper.scrape_job_data()

    if df.shape[0] == 0:
        print("No results found. Something went wrong.")
    else:
        cleaned_df = scraper.clean_data(df)
        csv_file = scraper.save_csv(cleaned_df, 'job_position', 'job_location')
        print(cleaned_df)
