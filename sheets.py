import os
import pandas as pd
import logging
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import GOOGLE_SHEETS_CREDENTIALS
import time

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Setup Google Sheets API client
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

def authenticate_google_sheets():
    logging.info("Authenticating with Google Sheets API...")
    creds = None
    token_path = 'token.json'
    credentials_path = GOOGLE_SHEETS_CREDENTIALS

    if not credentials_path:
        raise ValueError("The credentials path is not set. Please check your .env file.")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        logging.info("Loaded credentials from token.json")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logging.info("Refreshed OAuth token")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=8080)
            logging.info("Created new OAuth token")
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            logging.info("Saved OAuth token to file")

    client = gspread.authorize(creds)
    logging.info("Authorized Google Sheets client")
    return client, creds

def search_sheets(creds, search_string):
    logging.info(f"Searching for Google Sheets containing '{search_string}'...")
    service = build('drive', 'v3', credentials=creds)
    query = f"name contains '{search_string}' and mimeType='application/vnd.google-apps.spreadsheet'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        logging.warning("No files found.")
    for idx, item in enumerate(items):
        logging.info(f"Found sheet: {item['name']} (ID: {item['id']})")

    return items

def select_sheet(client, creds, search_string):
    logging.info("Fetching your Google Sheets...")
    sheet_list = search_sheets(creds, search_string)
    if not sheet_list:
        return None

    sheet_names = [item['name'] for item in sheet_list]
    return sheet_names, sheet_list

def check_and_add_missing_columns(worksheet):
    headers = worksheet.row_values(1)
    required_columns = ["Subject", "Generated Email HTML", "Generated Email", "Company Information", "Full Email"]
    missing_columns = [col for col in required_columns if col not in headers]

    if missing_columns:
        # Add missing columns
        headers.extend(missing_columns)
        worksheet.update('A1', [headers])  # Update the entire header row
        logging.info(f"Added missing columns: {missing_columns}")

# def fetch_sheet_data(worksheet, start_row=None, end_row=None):
#     logging.info(f"Fetching data from worksheet starting at row {start_row} and ending at row {end_row}...")
    
#     rows = worksheet.get_all_values()
#     headers = rows[0]  # Assuming the first row contains headers
    
#     # Determine the start and end rows for slicing the data
#     data_start_row = start_row - 1 if start_row is not None else 1
#     data_end_row = end_row + 1 - 1 if end_row is not None else len(rows)
    
#     # Fetch data rows based on provided start and end row
#     data_start_row == 1 if data_start_row == 0 else data_start_row
#     data = rows[data_start_row:data_end_row]
    
#     # Create DataFrame
#     df = pd.DataFrame(data, columns=headers)
#     logging.info("Fetched data successfully")
#     return df

def fetch_sheet_data(worksheet, start_row=None, end_row=None):
    logging.info(f"Fetching data from worksheet starting at row {start_row} and ending at row {end_row}...")
    rows = worksheet.get_all_values()
    
    if start_row is None or start_row == 1:
        start_row = 2  # Skip header row
    if end_row is None:
        end_row = len(rows)+ 1  # Process till the last row

    if end_row <= start_row:
        raise ValueError("End row must be greater than start row")

    # Extract the header row and the data rows based on the specified start and end rows
    headers = rows[0]
    data = rows[start_row-1:end_row]  # Include end_row in the data slice
    df = pd.DataFrame(data, columns=headers)
    logging.info("Fetched data successfully")
    return df

def validate_and_set_row_indices(start_row, end_row, total_rows):
    if start_row is None or start_row == 1:
        start_row = 2  # Skip header row
    if end_row is None:
        end_row = total_rows + 1  # Process till the last row

    if end_row <= start_row:
        raise ValueError("End row must be greater than start row")

    return start_row, end_row



def update_sheet_with_emails(worksheet, emails, row_number):
    logging.info("Updating worksheet with generated emails...")

    headers = worksheet.row_values(1)
    if not headers:  # If headers are empty, raise an error
        raise ValueError("The worksheet does not have headers in the first row.")

    subject_col = headers.index("Subject") + 1 if "Subject" in headers else len(headers) + 1
    email_content_col = headers.index("Full Email") + 1 if "Full Email" in headers else len(headers) + 1
    html_email_col = headers.index("Generated Email HTML") + 1 if "Generated Email HTML" in headers else len(headers) + 1
    generated_email_col = headers.index("Generated Email") + 1 if "Generated Email" in headers else len(headers) + 1
    company_info_col = headers.index("Company Information") + 1 if "Company Information" in headers else len(headers) + 1

    # If columns are missing, add them to the header row
    if "Subject" not in headers:
        worksheet.update_cell(1, subject_col, "Subject")
    if "Full Email" not in headers:
        worksheet.update_cell(1, email_content_col, "Full Email")
    if "Generated Email HTML" not in headers:
        worksheet.update_cell(1, html_email_col, "Generated Email HTML")
    if "Generated Email" not in headers:
        worksheet.update_cell(1, generated_email_col, "Generated Email")
    if "Company Information" not in headers:
        worksheet.update_cell(1, company_info_col, "Company Information")

    for subject, email_content, html_email, company_about in emails:
        retries = 5
        for attempt in range(retries):
            try:
                if subject_col:
                    worksheet.update_cell(row_number, subject_col, subject)
                if generated_email_col:
                    worksheet.update_cell(row_number, generated_email_col, email_content)
                if html_email_col:
                    worksheet.update_cell(row_number, html_email_col, html_email)
                if email_content_col:
                    worksheet.update_cell(row_number, email_content_col, f"{subject}\n\n{email_content}")
                if company_info_col:
                    worksheet.update_cell(row_number, company_info_col, company_about)
                logging.info(f"Updated cell at row {row_number} with subject: {subject[:50]}{'...' if len(subject) > 50 else ''}")
                break
            except gspread.exceptions.APIError as e:
                if attempt < retries - 1:
                    wait = 2 ** attempt  # Exponential backoff
                    logging.warning(f"APIError: {e}. Retrying in {wait} seconds...")
                    time.sleep(wait)
                else:
                    logging.error(f"APIError: {e}. Failed after {retries} retries.")
                    raise
    logging.info("Worksheet updated successfully")
