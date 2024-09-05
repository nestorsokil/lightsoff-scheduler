
from datetime import datetime, time
import os
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account


SCOPES = ['https://www.googleapis.com/auth/calendar']
GOOGLE_API_KEY_NAME = os.environ.get("GOOGLE_API_KEY_NAME")

credentials = service_account.Credentials.from_service_account_file(GOOGLE_API_KEY_NAME, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)


def insert_outage(calendar_id, begin, end, summary="Power Outage", description="Scheduled power outage"):
    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": begin,
            "timeZone": "Europe/Kiev"
        },
        "end": {
            "dateTime": end,
            "timeZone": "Europe/Kiev"
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {
                    "method": "popup",
                    "minutes": 10
                }
            ]
        }
    }
    logging.info(f"Creating event: {event['summary']} (Start: {event['start']['dateTime']}, End: {event['end']['dateTime']})")
    service.events().insert(calendarId=calendar_id, body=event).execute()

def clear_events_for_day(calendar_id, date):
    """Clear all events for a specific day."""
    logging.info(f'Clearing day {date} for calendar {calendar_id}')
    start_time = datetime.combine(date, time.min).isoformat() + 'Z'
    end_time = datetime.combine(date, time.max).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=calendar_id, timeMin=start_time, timeMax=end_time, singleEvents=True, orderBy='startTime').execute()

    events = events_result.get('items', [])

    if not events:
        logging.info('No events found for this day.')
    else:
        for event in events:
            event_id = event['id']
            print(f"Deleting event: {event['summary']} (ID: {event_id})")
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
