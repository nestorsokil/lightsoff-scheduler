import anthropic
import logging
import json
from datetime import datetime


# TODO maybe will move this to Google Calendar API instead of emailing  .ics file
def ocr_image_to_calendar_api(image_b64, group="3.2"):
    text = _ocr_image(
        image_b64, f"I've uploaded an image of a power outage schedule table. Please analyze it and create Google Calendar API request to update calendar for the power outages for group {group}. The image shows hours of the day across the top and group numbers in the first column. Orange cells indicate 'no energy' periods. The date is highlighted at the top. Combine consecutive outage periods into single events. Add a 10-minute notification before each event. Only respond with Google API json requests as an array add a separator '->' and date in format '%Y-%m-%d'.")
    parts = text.split("->")
    return parts[0], parts[1]


def ocr_image_to_calendar_api_multi(image_b64, group="3.2"):
    text = _ocr_image(
        image_b64, f"Analyze image of a power outage schedule table which shows hours of the day across the top and group numbers in 1st column. Orange cells indicate 'no energy' periods. The date is highlighted at the top. Combine consecutive outage periods into single events. Only respond with a minified json object key - group number, value - array of pairs [start datetime, end], then add a separator '->' and date in format '%Y-%m-%d'.")
    parts = text.split("->")
    return json.loads(parts[0].strip()), datetime.strptime(parts[1].strip(), "%Y-%m-%d")



def ocr_image_to_ics(image_b64, group="3.2"):
    return _ocr_image(image_b64, f"I've uploaded an image of a power outage schedule table. Please analyze it and create an .ics file for the power outages for group {group}. The image shows hours of the day across the top and group numbers in the first column. Orange cells indicate 'no energy' periods. Combine consecutive outage periods into single events. Add a 10-minute notification before each event. Provide the .ics file content in a format I can easily copy and save. The date for these events is shown at the top of the image - please use that date when creating the events. Only send the .ics file content, no additional text.")


def mock_ocr_to_calendar_api_multi():
    text = '{"1.1":[["2024-09-05T00:00:00","2024-09-05T01:00:00"],["2024-09-05T11:00:00","2024-09-05T14:00:00"]],"1.2":[["2024-09-05T05:00:00","2024-09-05T07:00:00"],["2024-09-05T19:00:00","2024-09-05T21:00:00"]],"2.1":[["2024-09-05T07:00:00","2024-09-05T09:00:00"],["2024-09-05T21:00:00","2024-09-05T23:00:00"]],"2.2":[["2024-09-05T10:00:00","2024-09-05T12:00:00"],["2024-09-05T23:00:00","2024-09-06T01:00:00"]],"3.1":[["2024-09-05T01:00:00","2024-09-05T03:00:00"],["2024-09-05T14:00:00","2024-09-05T16:00:00"]],"3.2":[["2024-09-05T03:00:00","2024-09-05T05:00:00"],["2024-09-05T17:00:00","2024-09-05T19:00:00"]]}->2024-09-05'
    parts = text.split("->")
    return json.loads(parts[0].strip()), datetime.strptime(parts[1].strip(), "%Y-%m-%d")


def mock_ocr_to_calendar_api():
    text = """
[
  {
    "summary": "Power Outage",
    "description": "Scheduled power outage for group 3.2",
    "start": {
      "dateTime": "2024-09-05T03:00:00+03:00",
      "timeZone": "Europe/Kiev"
    },
    "end": {
      "dateTime": "2024-09-05T05:00:00+03:00",
      "timeZone": "Europe/Kiev"
    },
    "reminders": {
      "useDefault": false,
      "overrides": [
        {
          "method": "popup",
          "minutes": 10
        }
      ]
    }
  },
  {
    "summary": "Power Outage",
    "description": "Scheduled power outage for group 3.2",
    "start": {
      "dateTime": "2024-09-05T15:00:00+03:00",
      "timeZone": "Europe/Kiev"
    },
    "end": {
      "dateTime": "2024-09-05T17:00:00+03:00",
      "timeZone": "Europe/Kiev"
    },
    "reminders": {
      "useDefault": false,
      "overrides": [
        {
          "method": "popup",
          "minutes": 10
        }
      ]
    }
  }
]
->2024-09-05
"""
    parts = text.split("->")
    return parts[0].strip(), parts[1].strip()


def mock_ocr_to_ics():
    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Your Organization//EN
BEGIN:VEVENT
SUMMARY:Power Outage (Group 3.2)
DTSTART:20240905T030000
DTEND:20240905T050000
DTSTAMP:20240905T000000Z
UID:20240905T030000-poweroutage@example.com
DESCRIPTION:Scheduled power outage for Group 3.2
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Power outage starting in 10 minutes
TRIGGER:-PT10M
END:VALARM
END:VEVENT
BEGIN:VEVENT
SUMMARY:Power Outage (Group 3.2)
DTSTART:20240905T170000
DTEND:20240905T190000
DTSTAMP:20240905T000000Z
UID:20240905T170000-poweroutage@example.com
DESCRIPTION:Scheduled power outage for Group 3.2
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Power outage starting in 10 minutes
TRIGGER:-PT10M
END:VALARM
END:VEVENT
END:VCALENDAR
"""


def _ocr_image(image_b64, prompt):
    client = anthropic.Anthropic()  # defaults to os.environ.get("ANTHROPIC_API_KEY)
    logging.info("Sending image to Anthropics API for OCR...")
    message = client.messages.create(
        max_tokens=1000,
        temperature=0,
        system=prompt,
        model="claude-3-5-sonnet-20240620",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": str(image_b64)
                        }
                    }
                ]
            }
        ]
    )
    logging.info("Received response from Anthropics API.")
    return message.content[0].text
