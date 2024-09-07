import asyncio
import ocr
import os
import logging
import gcal
import json

from telethon import TelegramClient, events
from telethon.sessions import StringSession, Session

api_id = os.environ.get("TELEGRAM_API_ID")
api_hash = os.environ.get("TELEGRAM_API_HASH")
phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
channel_username = os.environ.get("TELEGRAM_CHANNEL", '@lvivoblenergo')
session_string = os.environ.get("TELEGRAM_SESSION_STRING")

calendars = json.loads(os.environ.get("CALENDARS_MAPPING_JSON"))

session = StringSession(session_string) if session_string else StringSession()
client = TelegramClient(session, api_id, api_hash)


@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    logging.info(f"New message from {channel_username}:")
    logging.info(f"Message ID: {event.message.id}")
    if event.message.photo and not event.message.text:
        photo_path = await event.message.download_media(file='.telethon/downloads/')
        try:
            events, day = ocr.image_to_time_frames(photo_path)
            logging.info(f"OCR results: {events}, {day}")

            if events is None:
                logging.warn("No events found in the image. Skipping...")
                return

            for group, time_frames in events.items():
                calendar_id = calendars[group]
                if calendar_id is None:
                    logging.warn(
                        f"Calendar ID not found for group {group}. Skipping...")
                    continue
                gcal.clear_events_for_day(calendar_id, day)
                for timeframe in time_frames:
                    begin, end = timeframe[0], timeframe[1]
                    gcal.insert_event(
                        calendar_id=calendar_id,
                        begin=begin,
                        end=end,
                        summary=f"Power Outage ({group})",
                        description=f"Scheduled power outage for {group}")
            logging.info("Updated schedules in Google Calendar")
        finally:
            logging.debug("Deleting downloaded photo...")
            if os.path.exists(photo_path):
                os.remove(photo_path)


def main():
    logging.info("Starting client...")
    client.start(phone_number)
    logging.debug("Session string: %s", client.session.save())
    client.run_until_disconnected()


if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO').upper())
    asyncio.run(main())
