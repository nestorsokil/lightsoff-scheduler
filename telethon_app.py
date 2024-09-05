import asyncio
import ocr
import base64
import mail
import os
import logging

from telethon import TelegramClient, events


api_id = os.environ.get("TELEGRAM_API_ID")
api_hash = os.environ.get("TELEGRAM_API_HASH")
phone_number = os.environ.get("TELEGRAM_PHONE_NUMBER")
channel_username = os.environ.get("TELEGRAM_CHANNEL", '@lvivoblenergo')

subscribers = os.environ.get("EMAIL_SUBSCRIBERS").split(',')

client = TelegramClient('.telethon/session_name', api_id, api_hash)


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
            ics = ocr.ocr_image_to_ics(image_base64)
            #ics = ocr.mock_ocr_to_ics()
            mail.send_email_with_invite(ics, subscribers)
            # events, day = ocr.ocr_image_to_calendar_api(image_base64)
            # google.import_events('xxxx', day, events)
            # todo delete file


def main():
    logging.info("Starting client...")
    client.start(phone_number)
    client.run_until_disconnected()


if __name__ == '__main__':
    logging.basicConfig(
        level=os.environ.get('LOG_LEVEL', 'INFO').upper())
    asyncio.run(main())
