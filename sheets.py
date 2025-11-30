import os
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'service_account.json'

def get_service():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Service account file '{SERVICE_ACCOUNT_FILE}' not found.")
        return None
    
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def update_sheet(data):
    """
    Updates the Google Sheet with the provided data.
    Checks for existing URLs to update rows instead of appending duplicates.
    data: List of dictionaries containing hackathon details.
    """
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    if not spreadsheet_id:
        print("SPREADSHEET_ID not found in environment variables.")
        return

    service = get_service()
    if not service:
        return

    # 1. Read existing data to find duplicates
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range="Sheet1!A:J").execute()
        existing_values = result.get('values', [])
    except Exception as e:
        print(f"Error reading sheet: {e}")
        return

    # Map URLs to row indices (0-based relative to the sheet)
    # Assuming URL is in column B (index 1)
    url_to_row = {}
    if len(existing_values) > 1: # Skip header
        for i, row in enumerate(existing_values[1:], start=2): # Sheet rows are 1-based, header is row 1
            if len(row) > 1:
                url_to_row[row[1]] = i

    new_rows = []
    updates = []

    for item in data:
        url = item.get('url', '')
        row_data = [
            item.get('name', ''),
            url,
            item.get('deadline', ''),
            item.get('start_date', ''),
            item.get('end_date', ''),
            str(item.get('tech_stack', '')),
            item.get('company', ''),
            item.get('description', ''),
            item.get('prize', ''),
            datetime.datetime.now().isoformat()
        ]

        if url in url_to_row:
            # Update existing row
            row_idx = url_to_row[url]
            updates.append({
                'range': f"Sheet1!A{row_idx}:J{row_idx}",
                'values': [row_data]
            })
        else:
            # Append new row
            new_rows.append(row_data)

    try:
        # Batch update for existing rows
        if updates:
            body = {
                'valueInputOption': 'USER_ENTERED',
                'data': updates
            }
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body).execute()
            print(f"Updated {len(updates)} existing entries.")

        # Append new rows
        if new_rows:
            body = {'values': new_rows}
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range="Sheet1!A1",
                valueInputOption="USER_ENTERED", body=body).execute()
            print(f"Added {len(new_rows)} new entries.")

        # Apply conditional formatting
        apply_conditional_formatting(service, spreadsheet_id)
        
    except Exception as e:
        print(f"Error updating sheet: {e}")

def apply_conditional_formatting(service, spreadsheet_id):
    """
    Applies conditional formatting to the Deadline column (C).
    Red background if the date is within the next 7 days.
    """
    # We need the sheetId (integer), not the spreadsheetId (string).
    # Assuming the first sheet (index 0).
    try:
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheet_id = sheets[0].get("properties", {}).get("sheetId", 0)
        
        requests = [
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 2, # Column C (0-indexed)
                                "endColumnIndex": 3,
                                "startRowIndex": 1 # Skip header
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "DATE_BEFORE",
                                "values": [
                                    {
                                        "relativeDate": "PAST_WEEK" # Just an example, ideally we want 'upcoming'
                                    }
                                ]
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 1.0,
                                    "green": 0.8,
                                    "blue": 0.8
                                }
                            }
                        }
                    },
                    "index": 0
                }
            }
        ]
        
        # Note: The above rule is a placeholder. 
        # Google Sheets API conditional formatting for "approaching deadline" 
        # is often easier done by a formula like =AND(C2<>"", C2-TODAY()<=7, C2>=TODAY())
        
        requests = [
             {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startColumnIndex": 2, # Column C
                                "endColumnIndex": 3,
                                "startRowIndex": 1
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": [
                                    {
                                        "userEnteredValue": '=AND(C2<>"", DATEVALUE(C2)-TODAY()<=7, DATEVALUE(C2)>=TODAY())'
                                    }
                                ]
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 1.0,
                                    "green": 0.8,
                                    "blue": 0.8
                                }
                            }
                        }
                    },
                    "index": 0
                }
            }
        ]

        body = {
            'requests': requests
        }
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body).execute()
        print("Conditional formatting applied.")
        
    except Exception as e:
        print(f"Error applying conditional formatting: {e}")


def setup_headers():
    """
    Sets up the headers if the sheet is empty.
    """
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    if not spreadsheet_id:
        return

    service = get_service()
    if not service:
        return

    headers = [["Name", "URL", "Deadline", "Start Date", "End Date", "Tech Stack", "Company", "Description", "Prize", "Last Updated"]]
    body = {'values': headers}
    
    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range="Sheet1!A1",
            valueInputOption="USER_ENTERED", body=body).execute()
        print("Headers initialized.")
    except Exception as e:
        print(f"Error setting headers: {e}")

if __name__ == "__main__":
    setup_headers()
