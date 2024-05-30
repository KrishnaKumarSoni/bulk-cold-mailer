import os
from dotenv import load_dotenv
import pandas as pd
import logging
from sheets import authenticate_google_sheets, select_sheet, fetch_sheet_data, update_sheet
from scraper import scrape_company_info
from email_generator import create_email

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

def main():
    client, creds = authenticate_google_sheets()
    worksheet = select_sheet(client, creds)
    df = fetch_sheet_data(worksheet)

    # Ensure the necessary columns exist
    required_columns = ['Generated Email', 'Generated Email HTML', 'Company Information', 'Full Email', 'Subject']
    for column in required_columns:
        if column not in df.columns:
            df[column] = ''

    # Update column headers
    for idx, column in enumerate(df.columns):
        if idx < worksheet.col_count:
            worksheet.update_cell(1, idx + 1, column)
        else:
            print(f"Column {column} exceeds the sheet's column limit and cannot be added.")

    # Get the starting row from the user
    start_row = int(input("Enter the starting row for writing emails: "))
    start_row = start_row - 1
    for i, (df_index, row) in enumerate(df.iloc[start_row-1:].iterrows(), start=start_row):
        actual_row = df_index + 2  # Adjusted for zero-based index to match Google Sheets row number

        company_name = row['company_name']
        company_url = row['company_domain']
        contact_person = row['full_name']
        person_headline = row['headline']
        person_about = row['about']
        person_position = row['position']
        company_about = row['company_about']

        logging.info(f'Initiated email number: {actual_row} for {company_name}')

        if not company_url.startswith("https://"):
            company_url = "https://" + company_url

        if len(company_about) < 100:
            company_info = scrape_company_info(company_url)
        else:
            company_info = company_about

        df.at[df_index, 'Company Information'] = company_info

        subject_line, email_body, html_email = create_email(company_name, company_info, contact_person, person_headline, person_about, person_position)

        df.at[df_index, 'Full Email'] = subject_line + "\n\n" + email_body
        df.at[df_index, 'Generated Email'] = email_body
        df.at[df_index, 'Generated Email HTML'] = html_email
        df.at[df_index, 'Subject'] = subject_line

        update_sheet(worksheet, actual_row, df.columns.get_loc('Generated Email') + 1, email_body)
        update_sheet(worksheet, actual_row, df.columns.get_loc('Generated Email HTML') + 1, html_email)
        update_sheet(worksheet, actual_row, df.columns.get_loc('Company Information') + 1, company_info)
        update_sheet(worksheet, actual_row, df.columns.get_loc('Full Email') + 1, subject_line + "\n\n" + email_body)
        update_sheet(worksheet, actual_row, df.columns.get_loc('Subject') + 1, subject_line)

        logging.info(f"Updated email and company information for {company_name}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
