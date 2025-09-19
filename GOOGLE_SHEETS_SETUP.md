# Google Sheets Integration Setup Guide

## Overview
This integration allows your student registration system to sync with a Google Sheet in real-time. When students register, their status is updated in both MongoDB and Google Sheets.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

## Step 2: Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in service account details:
   - Name: `student-registration-bot`
   - Description: `Service account for student registration system`
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

## Step 3: Generate Credentials

1. Find your new service account in the list
2. Click on it to open details
3. Go to "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Choose "JSON" format
6. Download the JSON file

## Step 4: Create Google Sheet

1. Create a new Google Sheet
2. Set up headers in row 1:
   ```
   A1: student_id
   B1: name
   C1: email
   D1: age
   E1: competition
   F1: registration_status
   ```
3. Add sample data (optional):
   ```
   Row 2: 124BTEX2008, John Doe, john@example.com, 25, TRUE, FALSE
   Row 3: 22UF17309EC077, Sid, sid@example.com, 25, FALSE, FALSE
   ```

## Step 5: Share Sheet with Service Account

1. Copy the service account email from the JSON file (looks like: `student-registration-bot@your-project.iam.gserviceaccount.com`)
2. In your Google Sheet, click "Share"
3. Add the service account email with "Editor" permissions
4. Copy the Google Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit
   ```

## Step 6: Configure Environment Variables

Add these to your `.env` file or Render environment variables:

```env
# Google Sheets Configuration
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_SHEET_RANGE=Sheet1!A:F
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project",...}
```

### For Local Development:
Save the downloaded JSON file as `credentials.json` in your project root, or set:
```env
GOOGLE_CREDENTIALS_FILE=path/to/credentials.json
```

### For Render Deployment:
Copy the entire contents of the JSON file and paste it as the value for `GOOGLE_CREDENTIALS_JSON` (as a single line).

## Step 7: Sheet Format

Your Google Sheet should have these columns:

| student_id | name | email | age | competition | registration_status |
|------------|------|-------|-----|-------------|-------------------|
| 124BTEX2008 | John Doe | john@example.com | 25 | TRUE | FALSE |
| 22UF17309EC077 | Sid | sid@example.com | 25 | FALSE | FALSE |

**Column Details:**
- `student_id`: Unique identifier for barcode scanning
- `name`: Student's full name
- `email`: Contact email
- `age`: Student age (number)
- `competition`: TRUE/FALSE for competition participation
- `registration_status`: TRUE/FALSE for registration status (auto-updated)

## How It Works

1. **Sync on Scan**: When a student is scanned, the system first syncs from Google Sheet to get latest data
2. **Real-time Updates**: When registration status changes, it's immediately updated in both MongoDB and Google Sheet
3. **Competition Status**: The `competition` field in the sheet controls whether "🏆 In Competition" appears in popups
4. **Bidirectional Sync**: You can update student data in the sheet, and it will be pulled into the system on next scan

## Testing

1. Add a student to your Google Sheet
2. Scan their student ID or enter manually
3. Check that the registration status updates to TRUE in the sheet
4. Verify competition status appears in popup if set to TRUE

## Troubleshooting

**"Google Sheets credentials not found"**
- Check your environment variables are set correctly
- Verify the JSON format is valid

**"Permission denied"**
- Make sure you shared the sheet with the service account email
- Check the service account has Editor permissions

**"Student not found"**
- Verify the student_id in the sheet matches exactly
- Check the sheet range includes your data

## Security Notes

- Keep your credentials JSON file secure and never commit it to git
- Use environment variables for production deployment
- The service account only has access to sheets you explicitly share with it