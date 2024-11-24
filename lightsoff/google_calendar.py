
import os
import logging
from datetime import datetime, time, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account


SCOPES = ['https://www.googleapis.com/auth/calendar']
GOOGLE_API_KEY_NAME = os.environ.get("GOOGLE_API_KEY_NAME")

credentials = service_account.Credentials.from_service_account_file(GOOGLE_API_KEY_NAME, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)

def timestamp_obj(_datetime, all_day):
    if all_day:
        return {"date": _datetime.strftime("%Y-%m-%d"), "timeZone": "Europe/Kiev"}
    return {"dateTime": _datetime.strftime("%Y-%m-%dT%H:%M:%S"), "timeZone": "Europe/Kiev"}
    

def insert_event(calendar_id, begin, end, summary, description, all_day=False):
    event = {
        "summary": summary,
        "description": description,
        "transparency": "transparent", 
        "start": timestamp_obj(begin, all_day),
        "end": timestamp_obj(end, all_day)
    }
    logging.info(f"Creating event: {event})")
    service.events().insert(calendarId=calendar_id, body=event).execute()

def clear_events_for_day(calendar_id, date):
    """Clear all events for a specific day."""
    whole_day_cleared = True

    logging.info(f'Clearing day {date} for calendar {calendar_id}')

    start_time = (datetime.combine(date, time.min) - timedelta(seconds=1)).isoformat() + '+03:00'
    end_time = datetime.combine(date, time.max).isoformat() + '+03:00'

    today = datetime.now().date()
    if today > date:
        return False

    if date == today:
        # only clear future events
        start_time = datetime.now().isoformat() + '+03:00'
        whole_day_cleared = False

    events_result = service.events().list(
        calendarId=calendar_id, 
        timeMin=start_time, 
        timeMax=end_time, 
        singleEvents=True, 
        orderBy='startTime').execute()

    events = events_result.get('items', [])

    logging.info(f"Found {len(events)} remaining events for this day.")
    if not events:
        logging.info('No remaining events found for this day.')
        return False
    for event in events:
        event_id = event['id']
        logging.info(f"Deleting event: {event['summary']} (ID: {event_id})")
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    
    return whole_day_cleared
