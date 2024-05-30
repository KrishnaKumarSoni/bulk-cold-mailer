import streamlit as st
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import gspread
import os
import openai
from config import GOOGLE_SHEETS_CREDENTIALS
from sheets import fetch_sheet_data, update_sheet_with_emails, select_sheet
from openai_client import generate_personalized_email, convert_to_html
from scraper import scrape_company_info
import logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

st.title("🌟 Sales Automation Tool 🌟")

st.write("""
Welcome to the Sales Automation Tool! This tool is designed to help you write hyper-personalized and effective cold emails for your leads or prospects. By using the data from your Google Sheet, this tool automates the process of generating engaging emails for your prospects, saving you time and enhancing your outreach efforts.

### 🚀 How does this work?

- **Data Fetching**: Retrieves data from a specified Google Sheet.
- **Email Generation**: Uses the fetched data and the website data to generate personalized email content.
- **Email Writing**: Writes the generated emails back to the Google Sheet.

## 📋 Preparing Your Data (IMPORTANT)

Ensure your Google Sheet includes the following essential columns for the tool to function correctly:

1. **company_name**: Name of the company.
2. **company_domain**: Company's website domain.
3. **full_name**: Full name of the contact person.
4. **headline**: Contact person's headline.
5. **about**: Information about the contact person.
6. **company_about**: Brief information about the company.

## 🛠️ Steps to Use This Tool

1. Enter your OpenAI API key and click 'Submit API Key'.
2. Click the button below to authenticate with Google and access your Google Sheets.
3. Type the name of your prepared Google Sheet and select it from the list.
4. Choose the worksheet which has your prepared data that you want to work with.
5. Specify the starting row number and ending row number for data processing (both are optional).
6. Click the button to fetch and display data from the selected worksheet.
7. Generate personalized emails using the fetched data.
8. Save the generated emails back to your Google Sheet. Once all emails are generated, the table will be removed from the UI.

With these steps, you can effortlessly generate compelling cold emails and enhance your outreach process. Happy emailing! 📧✨
""")


# Initialize session state variables
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = None
if 'google_auth_done' not in st.session_state:
    st.session_state['google_auth_done'] = False
if 'current_row' not in st.session_state:
    st.session_state['current_row'] = 0
if 'data_fetched' not in st.session_state:
    st.session_state['data_fetched'] = False
if 'creds' not in st.session_state:
    st.session_state['creds'] = None
if 'generating_emails' not in st.session_state:
    st.session_state['generating_emails'] = False
if 'generate_email_btn' not in st.session_state:
    st.session_state['generate_email_btn'] = False
if 'stop_and_reset' not in st.session_state:
    st.session_state['stop_and_reset'] = False
if 'end_row' not in st.session_state:
    st.session_state['end_row'] = None
if 'generation_completed' not in st.session_state:
    st.session_state['generation_completed'] = False
if 'on_behalf_of' not in st.session_state:
    st.session_state['on_behalf_of'] = "Krishna Kumar Soni"
if 'background_info' not in st.session_state:
    st.session_state['background_info'] = """Kuberanix is a design agency where we develop brand identity, brand strategy, and UI/UX designs. 
We have helped 15+ founders grow their business using our product, branding, and design skills. We have worked with global brands and companies. 
My name is Krishna Kumar Soni. I am the founder of Kuberanix. The Kuberanix website is kuberanix.com."""
if 'call_to_action' not in st.session_state:
    st.session_state['call_to_action'] = "Ask the potential client if they'd be interested in a free 30-minute call to discuss a brand & UI/UX design audit of their company."
if 'closing' not in st.session_state:
    st.session_state['closing'] = """Warm Regards,
Krishna Kumar Soni
Indian Institute of Technology, Kharagpur
Founder, Kuberanix
www.kuberanix.com"""

# Function to validate OpenAI API key
def validate_openai_api_key(api_key):
    try:
        openai.api_key = api_key
        chat_completion = openai.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Respond with just this one word 'Connected!'.",
                }
            ],
            model="gpt-3.5-turbo",
        )
        st.success(chat_completion.choices[0].message.content.strip())
        return True
    except openai.APIError as e:
        logging.error(f"OpenAI API returned an API Error: {e}")
        pass
    except openai.APIConnectionError as e:
        logging.error(f"Failed to connect to OpenAI API: {e}")
        pass
    except openai.RateLimitError as e:
        logging.error(f"OpenAI API request exceeded rate limit: {e}")
        pass
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return False

# API key input in the sidebar
with st.sidebar:
    openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
    if st.button("Submit API Key"):
        if validate_openai_api_key(openai_api_key):
            st.session_state['openai_api_key'] = openai_api_key
            st.success("API Key set! You can now sign in with Google.")
        else:
            st.error("Invalid OpenAI API Key. Please try again.")

# Sidebar inputs for dynamic parts (only visible after API key is set)
if st.session_state['openai_api_key']:
    with st.sidebar:
        st.markdown("### Personalize your OpenAI prompt:")
        st.markdown("_Please customise the following prompts to write personalised emails. Don't forget to replace the sample prompts!_")

        st.session_state['on_behalf_of'] = st.text_input("On behalf of:", st.session_state['on_behalf_of'])
        st.session_state['background_info'] = st.text_area("Background info:", st.session_state['background_info'])
        st.session_state['call_to_action'] = st.text_input("Call to action:", st.session_state['call_to_action'])
        st.session_state['closing'] = st.text_area("Closing:", st.session_state['closing'])

def authenticate_google():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.metadata.readonly']
    if 'token.json' in os.listdir():
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_SHEETS_CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

if st.session_state['openai_api_key']:
    # Step 1: Authenticate with Google
    if st.button("Sign in with Google") and not st.session_state['google_auth_done']:
        creds = authenticate_google()
        st.session_state['creds'] = creds
        st.session_state['google_auth_done'] = True
        st.success("Authenticated successfully!")

if st.session_state['google_auth_done']:
    st.success("You are authenticated.")
    creds = st.session_state['creds']
    client = gspread.authorize(creds)

    # Function to check and add missing columns
    def check_and_add_missing_columns(worksheet):
        headers = worksheet.row_values(1)
        required_columns = ["Subject", "Generated Email HTML", "Generated Email", "Company Information", "Full Email"]
        missing_columns = [col for col in required_columns if col not in headers]

        if missing_columns:
            # Add missing columns
            headers.extend(missing_columns)
            worksheet.update('A1', [headers])  # Update the entire header row
            logging.info(f"Added missing columns: {missing_columns}")

    # Step 2: Enter Google Sheet Name
    if st.session_state['google_auth_done']:
        with st.form(key='sheet_form'):
            sheet_name = st.text_input("Enter the name of the Google Sheet")
            submit_sheet = st.form_submit_button("Submit")

        if submit_sheet:
            if sheet_name:
                try:
                    sheet_names, sheet_list = select_sheet(client, creds, sheet_name)
                    st.session_state['sheet_names'] = sheet_names
                    st.session_state['sheet_list'] = sheet_list
                except Exception as e:
                    st.error(f"Error fetching sheets: {e}")
            else:
                st.error("Please enter a valid Google Sheet name.")

    if 'sheet_names' in st.session_state:
        # Step 3: Select Worksheet
        sheet_idx = st.selectbox("Select the sheet number", range(len(st.session_state['sheet_names'])), format_func=lambda x: st.session_state['sheet_names'][x])
        sheet = client.open_by_key(st.session_state['sheet_list'][sheet_idx]['id'])
        
        worksheets = sheet.worksheets()
        worksheet_names = [ws.title for ws in worksheets]
        worksheet_name = st.selectbox("Select a worksheet", worksheet_names)

        if worksheet_name:
            worksheet = sheet.worksheet(worksheet_name)

            # Check and add missing columns
            check_and_add_missing_columns(worksheet)

            start_row_input = st.number_input("Enter the starting row number (optional)", min_value=2, placeholder="Row number as per Google Sheet")
            end_row_input = st.number_input("Enter the ending row number (optional)", value=None, placeholder="Row number as per Google Sheet", step=1)
            start_row = int(start_row_input) if start_row_input else 0
            end_row = int(end_row_input) if end_row_input else None

            st.session_state['start_row'] = start_row
            st.session_state['end_row'] = end_row

            # Step 4: Fetch Data
            if st.button("Fetch Data"):
                df = fetch_sheet_data(worksheet, start_row, end_row)
                st.session_state['df'] = df
                st.session_state['data_fetched'] = True
                st.session_state['generation_completed'] = False  # Reset generation completed flag

            # Step 5: Generate Emails
            
            if st.session_state['data_fetched'] and not st.session_state['generating_emails']:
                st.button("Generate Emails", key='generate_email_btn')
                if st.session_state['generate_email_btn']:
                    st.session_state['generating_emails'] = True  # Set the flag
                    df = st.session_state['df']
                    total_rows = len(df)

                    progress_bar = st.progress(0)
                    st.button("Stop Generations", key='stop_and_reset')
                    for idx in range(st.session_state['current_row'], total_rows):

                        if st.session_state['stop_and_reset'] and st.session_state['generating_emails']:
                            st.session_state['generating_emails'] = False
                            st.session_state['start_row'] = None
                            st.session_state['end_row'] = None
                            st.session_state['stop_and_reset'] = False
                            st.session_state['data_fetched'] = False
                            del st.session_state['df']
                            break

                        row = df.iloc[idx]
                        company_name = row['company_name']
                        company_url = row['company_domain']
                        contact_person = row['full_name']
                        person_headline = row['headline']
                        person_about = row['about']
                        company_about = row['company_about']

                        # Scrape company info if less than 300 characters
                        if len(company_about) < 300:
                            scraped_info = scrape_company_info(company_url)
                            company_about = scraped_info if scraped_info else company_about

                        email_data = generate_personalized_email(
                            company_name, company_url, contact_person, person_headline, person_about,
                            st.session_state['on_behalf_of'], st.session_state['background_info'], st.session_state['call_to_action'], st.session_state['closing']
                        )
                        subject = email_data['subject']
                        email_content = email_data['email']
                        html_email = convert_to_html(email_content)

                        # Log generated email data
                        logging.info(f"Generated email data: {email_data}")

                        # Update Google Sheet
                        try:
                            update_sheet_with_emails(worksheet, [(subject, email_content, html_email, company_about)], idx + (st.session_state['start_row'] or 0))
                        except Exception as e:
                            logging.error(f"Error updating sheet: {e}")
                            st.error(f"Error updating sheet: {e}")

                        # Update progress bar and current row
                        progress_bar.progress((idx + 1) / total_rows)
                        st.session_state['current_row'] = idx + 1
                        st.write(f"Row {idx + (st.session_state['start_row'] or 0)} updated.")

                        if st.session_state['end_row'] is not None and idx + (st.session_state['start_row'] or 0) >= st.session_state['end_row']:
                            break

                    st.session_state['generating_emails'] = False  # Reset the flag
                    st.session_state['generation_completed'] = True 
                    if st.session_state['current_row'] >= total_rows:
                        st.success("All emails have been written to the Google Sheet successfully!")
                        del st.session_state['stop_and_reset']
                        del st.session_state['df']  # Clear the dataframe from session state
                        st.session_state['start_row'] = None
                        st.session_state['end_row'] = None
                        st.session_state['data_fetched'] = False

# Error handling
if st.session_state['openai_api_key'] and st.session_state['google_auth_done'] and 'df' in st.session_state:
    try:
        st.dataframe(st.session_state['df'])
    except ValueError as e:
        st.error(f"Data processing error: {e}")
