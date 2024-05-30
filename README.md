# 🌟 Sales Automation Tool 🌟

Welcome to the Sales Automation Tool! 🚀 This tool is your new best friend for writing hyper-personalized and effective cold emails. By leveraging the power of Google Sheets and OpenAI, it automates the process of generating engaging emails for your prospects, saving you heaps of time and boosting your outreach efforts.

## 🛠️ Setting Up the Tool

### Step 1: Clone the Repository

First things first, let's get the code on your machine. Open your terminal and run:

```sh
git clone https://github.com/KrishnaKumarSoni/bulk-cold-mailer.git
cd sales-automation-tool
```

### Step 2: Install the Dependencies

Make sure you have Python installed. Then, install the required packages with:

```sh
pip install -r requirements.txt
```

### Step 3: Set Up Google Cloud Credentials

We need to set up Google Cloud credentials to use the Google Sheets API. Here’s how:

1. **Create a Project in Google Cloud**:
   - Head over to the [Google Cloud Console](https://console.cloud.google.com/).
   - Click on the project drop-down at the top and select "New Project".
   - Name your project something fun and click "Create".

2. **Enable the Google Sheets API and Google Drive API**:
   - In the Google Cloud Console, go to `APIs & Services` > `Library`.
   - Search for "Google Sheets API" and click on it, then click "Enable".
   - Search for "Google Drive API" and click on it, then click "Enable".

3. **Create Credentials**:
   - Go to `APIs & Services` > `Credentials`.
   - Click on "Create Credentials" and select "Service Account".
   - Fill in the service account details and click "Create".
   - On the next screen, click "Create Key" and select "JSON". This will download your credentials file.

4. **Set Up OAuth Consent Screen**:
   - Go to `APIs & Services` > `OAuth consent screen`.
   - Choose "External" for User Type and click "Create".
   - Fill in the required fields such as App Name, User Support Email, and Developer Contact Information.
   - Add `http://localhost:8888/` and `http://localhost:8501/` to the list of Authorized Redirect URIs.
   - Save and continue until the setup is complete.

5. **Assign Roles to the Service Account**:
   - Go back to `APIs & Services` > `Credentials`.
   - Click on the service account you created.
   - Under the "Permissions" tab, click "Add Member".
   - Add the email address of your service account (found in your `credentials.json` under `client_email`).
   - Assign the roles `Editor` and `Viewer`.

6. **Save the Credentials File**:
   - Rename the downloaded JSON file to `credentials.json`.
   - Place the `credentials.json` file in the root directory of this project.

### Step 4: Prepare Your Google Sheet

Create a Google Sheet with the following columns:

- `company_name`
- `company_domain`
- `full_name`
- `headline`
- `about`
- `company_about`

Share the sheet with the email address of your service account (found in your `credentials.json` under `client_email`).

### Step 5: Run the Application

Start the application by running:

```sh
streamlit run app.py --server.port=8501
```

### Step 6: Using the Tool

1. **Enter your OpenAI API Key**: Get your API key from the OpenAI website.
2. **Authenticate with Google**: Click the button to authenticate and access your Google Sheets.
3. **Enter the Google Sheet Name**: Provide the name of the Google Sheet you prepared.
4. **Select the Worksheet**: Choose the worksheet that contains your data.
5. **Specify Row Numbers (Optional)**: Specify the starting and ending row numbers for data processing.
6. **Fetch Data**: Click the button to fetch and display data from the selected worksheet.
7. **Generate Emails**: Click the button to generate personalized emails using the fetched data.
8. **Save Emails**: The generated emails will be written back to your Google Sheet.

### Getting Prospect Data

Need prospect data? We recommend using [Apollo.io](https://apollo.partnerlinks.io/fvf6vm0srxwb).

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We love contributions! Check out our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## 📧 Contact

Questions? Issues? Just want to say hi? Open an issue or reach out to us at [your-email@example.com].

Happy emailing! 📧✨
