from openai_client import generate_personalized_email, convert_to_html
import logging

def create_email(company_name, company_info, contact_person, person_headline, person_about, person_position):
    # Generate personalized outreach email using GPT-4
    email_json = generate_personalized_email(company_name, company_info, contact_person, person_headline, person_about, person_position)
    logging.info(f"Generated personalized email for {company_name}")

    # Extract email content from JSON
    email_content = email_json['email']
    subject_line = email_json['subject']

    # Convert plain text email to HTML
    html_email = convert_to_html(email_content)
    return subject_line, email_content, html_email
