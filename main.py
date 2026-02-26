import os
import sys
import resend
from dotenv import load_dotenv
from date_utils import get_first_sunday_of_next_month
from api_client import fetch_events, check_availability
from db_client import init_db, check_new_sessions, mark_sessions_as_notified

# Load environment variables
load_dotenv()

def send_email(subject, html_body):
    api_key = os.getenv('RESEND_API_KEY')
    from_email = os.getenv('FROM_EMAIL')
    target_emails_str = os.getenv('TARGET_EMAILS')

    if not all([api_key, from_email, target_emails_str]):
        print("Error: Missing Resend credentials or TARGET_EMAILS in .env file.")
        return

    resend.api_key = api_key
    
    # Parse emails
    to_emails = [email.strip() for email in target_emails_str.split(',') if email.strip()]

    try:
        # Resend allows sending to multiple recipients in one call if they are in the 'to' list
        # But for privacy/individual tracking, or just simplicity, we can pass the list directly
        # Resend 'to' parameter accepts a list of strings
        
        params = {
            "from": from_email,
            "to": to_emails,
            "subject": subject,
            "html": html_body,
        }
        
        email = resend.Emails.send(params)
        print(f"Email sent! ID: {email.get('id')}")
        return True
    except Exception as e:
        print(f"Failed to send Email: {e}")
        return False

import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Freestyle Notifier")
    parser.add_argument("-d", "--date", help="Target date in YYYY-MM-DD format", type=str)
    args = parser.parse_args()

    print("Starting Freestyle Notifier (Email Mode)...")
    
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
            print(f"Manual Date Override: {target_date}")
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD.")
            return
    else:
        target_date = get_first_sunday_of_next_month()
    
    print(f"Target Date: {target_date}")
    
    # Initialize DB
    init_db()

    events, included = fetch_events(target_date)
    available_sessions = check_availability(events, included)

    if available_sessions:
        print(f"Found {len(available_sessions)} available sessions!")
        
        session_ids = [s['id'] for s in available_sessions]
        if not check_new_sessions(session_ids):
            print("No new sessions found since last notification. Skipping email.")
            return
        
        # Construct Email Body
        # HTML format for better readability
        items_html = ""
        for session in available_sessions:
            items_html += f"<li><b>{session['name']}</b> at {session['start']} ({session['openings']} spots)<br><a href='{session['link']}'>Register Here</a></li>"
            
        html_body = f"""
        <h1>Freestyle Alert!</h1>
        <p>Found <b>{len(available_sessions)}</b> sessions on {target_date}:</p>
        <ul>
            {items_html}
        </ul>
        """
        
        subject = f"Freestyle Alert: {len(available_sessions)} sessions on {target_date}"
        
        print("Sending Email Notification...")
        if send_email(subject, html_body):
            mark_sessions_as_notified(session_ids)
            print("Marked sessions as notified in DB.")
    else:
        print("No sessions available.")

if __name__ == "__main__":
    main()
