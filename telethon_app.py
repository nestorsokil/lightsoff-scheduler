import asyncio
import ocr
import base64
import os
import logging
import gcal
import json

from telethon import TelegramClient, events
from telethon.sessions import StringSession

api_id = os.environ.get("TELEGRAM_API_ID")
api_hash = os.environ.get("TELEGRAM_API_HASH")
phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
channel_username = os.environ.get("TELEGRAM_CHANNEL", '@lvivoblenergo')
session_string = os.environ.get("TELEGRAM_SESSION_STRING")

calendars = json.loads(os.environ.get("CALENDARS_MAPPING_JSON"))

session = StringSession(session_string) if session_string else StringSession()
client = TelegramClient(session, api_id, api_hash)


def clean_downloads():
    import os
    import shutil
    folder = '.telethon/downloads'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error('Failed to delete %s. Reason: %s' % (file_path, e))

def to_str(_datetime):
    return _datetime.strftime("%Y-%m-%dT%H:%M:%S")

@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    message = event.message
    logging.info(f"New message from {channel_username}:")
    logging.info(f"Message ID: {message.id}")
    if message.photo and not message.text:
        photo_path = await message.download_media(file='.telethon/downloads/')
        with open(photo_path, "rb") as file:
            file_data = file.read()
            image_base64 = base64.b64encode(file_data).decode("ascii")
            # events, day = ocr.mock_ocr_to_calendar_api_multi()

            #events, day = ocr.ocr_image_to_calendar_api_multi(image_base64)
            events, day = ocr.ocr_image_to_timeframes(image_base64)
            logging.debug(f"OCR results: {events}, {day}")

            for group, timeframes in events.items():
                calendar_id = calendars[group]
                if calendar_id is None:
                    logging.warn(f"Calendar ID not found for group {group}. Skipping...")
                    continue
                gcal.clear_events_for_day(calendar_id, day)
                for timeframe in timeframes:
                    begin, end = timeframe[0], timeframe[1]
                    gcal.insert_outage(calendar_id=calendar_id, begin=begin, end=end,
                                       summary=f"Power Outage ({group})", description=f"Scheduled power outage for {group}")
            logging.info("Updated schedules in Google Calendar")
            logging.debug("Cleaning downloads folder...")
            clean_downloads()
            logging.debug("Done cleaning downloads folder...")

def main():
    logging.info("Starting client...")
    client.start(phone_number)
    logging.debug("Session string: %s", client.session.save())
    client.run_until_disconnected()


if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper())
    asyncio.run(main())
