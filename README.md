# Freestyle Notifier

A Python script to monitor and notify users about available sessions (e.g., "Freestyle" ice skating) at any facility using **DaySmart Recreation**.

## Features

- **Automated Monitoring**: Checks for available sessions for the upcoming month (targeting the first Sunday of the next month by default).
- **Smart Filtering**:
    - configurable **Facility ID** and **Sport ID**.
    - Filters for specific sessions (default: Freestyle) using "unconstrained" search parameters matching the web view.
- **Duplicate Prevention**: Uses a local SQLite database (`notifications.db`) to ensure you only receive one email per month/cycle.
- **Email Notifications**: Sends an HTML-formatted email with registration links via **Resend**.

## Project Structure

- `main.py`: The entry point. Handles argument parsing, database checks, and the main execution flow.
- `api_client.py`: Handles interactions with the DaySmart Recreation API. Contains logic for fetching events and filtering for availability.
- `db_client.py`: Manages the SQLite database for duplicate notification prevention.
- `date_utils.py`: Helper functions for calculating target dates (e.g., first Sunday of the next month).
- `.env`: (Not committed) Stores sensitive environment variables (API keys).

## Setup

1.  **Prerequisites**: Python 3.8+
2.  **Clone/Download** the repository.
3.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Environment Variables**:
    - Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    - Edit `.env` and fill in your details:
        - `RESEND_API_KEY`: Your Resend API key.
        - `FROM_EMAIL`: The email address to send from (must be verified in Resend).
        - `TARGET_EMAILS`: Comma-separated list of email addresses to receive notifications.
        
        **DaySmart Configuration** (Defaults set for Sharks Ice - SJ):
        - `COMPANY_SLUG`: The subdomain of the facility (e.g., `sharks` for https://apps.daysmartrecreation.com/dash/x/#/online/sharks).
        - `FACILITY_ID`: The internal ID of the specific rink/location.
        - `SPORT_ID`: The ID for the sport/activity type (e.g., `27` for specific skating sessions).

## Usage

### Basic Run
Checks for the default target date (first Sunday of the next month):
```bash
python3 main.py
# OR using the helper script
./run.sh
```

### Manual Date Override
Check for a specific date (YYYY-MM-DD):
```bash
./run.sh --date 2026-02-27
```

## Automation (Cron Job)

To run this script automatically (e.g., every hour), add a cron job:

1.  Open crontab:
    ```bash
    crontab -e
    ```
    2.  Add a line (replace `/path/to/project` with your actual project location):
    ```cron
    0 * * * * /path/to/project/run.sh >> /path/to/project/debug_output.txt 2>&1
    ```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
