from dotenv import load_dotenv
import os

load_dotenv()

def send_email_empty(sender_email, receiver_email, subject, body, password):
    # Implement the function to send an email when no jobs are found
    pass

def send_email(cleaned_df, sender_email, receiver_email, job_position, job_location, password):
    # Implement the function to send an email with job data
    pass

def main():
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password = os.getenv("PASSWORD")

    # Example usage
    subject = 'No Jobs Found on Indeed'
    body = """
    No jobs were found for the given search criteria.
    Please consider the following:
    1. Try adjusting your search criteria.
    2. If you used English search keywords for non-English speaking countries,
       it might return an empty result. Consider using keywords in the country's language.
    3. Try more general keyword(s), check your spelling or replace abbreviations with the entire word

    Feel free to try a manual search with this link and see for yourself:
    Link {}
    """.format("example_link")

    try:
        send_email_empty(sender_email, receiver_email, subject, body, password)
    except Exception as e:
        print(f"Error sending email: {e}")

    # Example usage for sending email with job data
    cleaned_df = None  # Replace with actual DataFrame
    job_position = 'web developer'
    job_location = 'remote'

    try:
        send_email(cleaned_df, sender_email, receiver_email, job_position, job_location, password)
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    main()
