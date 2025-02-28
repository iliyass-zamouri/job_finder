import streamlit as st
from dotenv import load_dotenv
from indeed_job_scraper import IndeedJobScraper
import os

load_dotenv()

# List of countries url.
countries = {
    'Nigeria': 'https://ng.indeed.com',
    'United Kingdom': 'https://uk.indeed.com',
    'United States': 'https://www.indeed.com',
    'Canada': 'https://ca.indeed.com',
    'Germany': 'https://de.indeed.com',
    'Australia': 'https://au.indeed.com',
    'South Africa': 'https://za.indeed.com',
    'Sweden': 'https://se.indeed.com',
    'Singapore': 'https://www.indeed.com.sg',
    'Switzerland': 'https://www.indeed.ch',
    'United Arab Emirates': 'https://www.indeed.ae',
    'New Zealand': 'https://nz.indeed.com',
    'India': 'https://www.indeed.co.in',
    'France': 'https://www.indeed.fr',
    'Italy': 'https://it.indeed.com',
    'Spain': 'https://www.indeed.es',
    'Japan': 'https://jp.indeed.com',
    'South Korea': 'https://kr.indeed.com',
    'Brazil': 'https://www.indeed.com.br',
    'Mexico': 'https://www.indeed.com.mx',
    'China': 'https://cn.indeed.com',
    'Saudi Arabia': 'https://sa.indeed.com',
    'Egypt': 'https://eg.indeed.com',
    'Thailand': 'https://th.indeed.com',
    'Vietnam': 'https://vn.indeed.com',
    'Argentina': 'https://ar.indeed.com',
    'Ireland': 'https://ie.indeed.com'
}

def main():
    st.title("Indeed Job Scraper")

    with st.expander("Job Search Criteria"):
        country = st.selectbox("Select Country", list(countries.keys()))
        job_position = st.text_input("Job Position", "web developer")
        job_location = st.text_input("Job Location", "remote")
        date_posted = st.number_input("Date Posted (days)", min_value=1, max_value=30, value=20)

    if st.button("Search Jobs"):
        scraper = IndeedJobScraper()
        sender_email = os.getenv("SENDER_EMAIL")
        receiver_email = os.getenv("RECEIVER_EMAIL")
        password = os.getenv("PASSWORD")

        cleaned_df = None

        try:
            full_url = scraper.search_jobs(countries[country], job_position, job_location, date_posted)
            df = scraper.scrape_job_data(countries[country])

            if df.shape[0] == 1:
                st.error("No results found. Something went wrong.")
                subject = 'No Jobs Found on Indeed'
                body = f"""
                No jobs were found for the given search criteria.
                Please consider the following:
                1. Try adjusting your search criteria.
                2. If you used English search keywords for non-English speaking countries,
                   it might return an empty result. Consider using keywords in the country's language.
                3. Try more general keyword(s), check your spelling or replace abbreviations with the entire word

                Feel free to try a manual search with this link and see for yourself:
                Link {full_url}
                """
                scraper.send_email_empty(sender_email, receiver_email, subject, body, password)
            else:
                cleaned_df = scraper.clean_data(df)
                st.dataframe(cleaned_df)
                # csv_file = scraper.save_csv(cleaned_df, job_position, job_location)
        finally:
            try:
                scraper.send_email(cleaned_df, sender_email, receiver_email, job_position, job_location, password)
            except Exception as e:
                st.error(f"Error sending email: {e}")
            finally:
                scraper.driver.quit()

if __name__ == "__main__":
    main()
