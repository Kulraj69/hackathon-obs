# Hackathon Scout Agent

This agent scrapes the internet for hackathons from platforms like Devpost, Devfolio, Unstop, HackerEarth, and Hack2Skill. It uses SerpApi to find listings, extracts details using Llama 3.1 (via Hugging Face), and updates a Google Sheet.

## Prerequisites

To run this agent, you need to set up the following:

1.  **SerpApi Key**: You provided this (`a332f44acf4c2fa8ea196642a535584c4812527e01b20a9a572237fa18f6a2ed`).
2.  **Hugging Face Token**: You mentioned you will provide this. Please add it to a `.env` file or share it.
3.  **Google Sheets Credentials**:
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project.
    *   Enable the **Google Sheets API** and **Google Drive API**.
    *   Create a **Service Account**.
    *   Download the JSON key file for the service account.
    *   Save it as `service_account.json` in this directory.
    *   **Important**: Share your target Google Sheet with the email address found in the `client_email` field of the `service_account.json` file.

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Create a `.env` file:
    ```
    SERPAPI_KEY=a332f44acf4c2fa8ea196642a535584c4812527e01b20a9a572237fa18f6a2ed
    HF_TOKEN=your_hugging_face_token_here
    SPREADSHEET_ID=your_google_sheet_id_here
    ```

## Usage

Run the agent manually:
```bash
python main.py
```

## Automation (Cron Job)

To run the agent twice daily (e.g., at 9 AM and 9 PM), set up a cron job:

1.  Open your crontab:
    ```bash
    crontab -e
    ```
2.  Add the following line (adjust the path to your project):
    ```bash
    0 9,21 * * * /Users/kulraj/hackathon-diary/run_agent.sh
    ```
3.  Ensure `run_agent.sh` is executable:
    ```bash
    chmod +x /Users/kulraj/hackathon-diary/run_agent.sh
    ```

## Features

*   **Search**: Uses SerpApi to find hackathons on major platforms.
*   **Extraction**: Uses Llama 3.1 to parse unstructured text into structured data (Deadline, Tech Stack, etc.).
*   **Google Sheets**:
    *   Updates existing entries if the URL matches.
    *   Appends new entries.
    *   **Conditional Formatting**: Highlights deadlines within the next 7 days in red.
