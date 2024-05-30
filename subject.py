import os
import pandas as pd
import logging
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import GOOGLE_SHEETS_CREDENTIALS, SHEET_NAME, WORKSHEET_NAME
from openai import OpenAI
from config import OPENAI_API_KEY
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

oai = OpenAI(api_key=OPENAI_API_KEY)

# Setup Google Sheets API client
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

def authenticate_google_sheets():
    """Authenticate with Google Sheets API and return the client."""
    creds = None
    token_path = 'token.json'
    credentials_path = GOOGLE_SHEETS_CREDENTIALS

    if not credentials_path:
        raise ValueError("The credentials path is not set. Please check your .env file.")

    # Load token.json if it exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    client = gspread.authorize(creds)
    return client

def select_sheet(client):
    """Allow user to select the Google Sheet."""
    # Open the specified spreadsheet
    sheet = client.open(SHEET_NAME)
    return sheet

def fetch_sheet_data(worksheet):
    """Fetch data from the Google Sheet and return it as a DataFrame."""
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def extract_subject(response_content):
    """Extract the subject line from the GPT response."""
    # Define a robust regex pattern to match the subject line
    subject_pattern = re.compile(r"(?i)(?:subject(?: line)?:\s*)(.*?)|^(.+?)$")
    match = subject_pattern.search(response_content)
    if match:
        # Return the subject if found, strip quotes using capture groups with '?'
        subject = match.group(1).strip()[1:-1] if match.group(1) else match.group(2).strip()[1:-1]
        return subject
    else:
        # If no subject is found, return a default subject line
        return "No Subject Found"

def generate_subject_line(email_content):
    """Generate a subject line for the given email content using OpenAI's GPT-4 model."""
    prompt = f"""
    You are an email marketing expert. Generate an attention-grabbing subject line for the following email content. Use best practices, formulas, tricks, and techniques to optimize for open rates and engagement.
    Just respond with the subject line only. Write nothing else. 
    Email Content:
    {email_content}
    """

    response = oai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    response_content = response.choices[0].message.content.strip()
    return extract_subject(response_content)

def main():
    # Authenticate with Google Sheets API
    client = authenticate_google_sheets()
    
    # Select the Google Sheet
    logging.info("Triggered select sheet.")
    sheet = select_sheet(client)
    
    # Select the worksheet (sub-sheet) within the Google Sheet
    worksheet = sheet.worksheet(WORKSHEET_NAME)
    
    # Fetch data from the sheet
    df = fetch_sheet_data(worksheet)
    
    # Ensure the "Subject" column exists
    if "Subject" not in df.columns:
        df["Subject"] = ""
        worksheet.update_cell(1, df.columns.get_loc("Generated Email") + 2, "Subject")

    # Generate subject lines for each email content
    for i, row in df.iterrows():
        email_content = row.get("Generated Email")
        if email_content:
            subject_line = generate_subject_line(email_content)
            df.at[i, "Subject"] = subject_line
            worksheet.update_cell(i + 2, df.columns.get_loc("Subject") + 1, subject_line)
            logging.info(f"Iteration {i + 1}: Updated row {i + 1} with subject line: {subject_line}")

if __name__ == "__main__":
    main()
